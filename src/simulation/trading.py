"""
Trading system for Wiffle Ball Manager
"""
import random
from typing import List, Tuple, Optional
from models.team import Team
from models.player import Player
from simulation.advanced_stats import AdvancedStatsCalculator

class TradeOffer:
    """Represents a trade offer between teams"""
    def __init__(self, team_a: Team, team_b: Team, players_a: List[Player], players_b: List[Player]):
        self.team_a = team_a
        self.team_b = team_b
        self.players_a = players_a  # Players from team A to team B
        self.players_b = players_b  # Players from team B to team A
        self.approved = False
        self.reason = ""

class TradingSystem:
    """Handles player trades between teams"""
    
    def __init__(self, teams: List[Team] = None):
        self.trade_deadline = 10  # Games before end of season when trading closes
        self.advanced_stats = AdvancedStatsCalculator()
        self.league_context = None
        if teams:
            self.update_league_context(teams)
    
    def update_league_context(self, teams: List[Team]):
        """Update league context for advanced stats calculations"""
        self.league_context = self.advanced_stats.calculate_league_context(teams)
        
    def evaluate_trade(self, offer: TradeOffer) -> Tuple[bool, str]:
        """Evaluate a trade offer and return approval decision with reason"""
        # Calculate trade value for each team
        value_a = self.calculate_team_value(offer.players_a)
        value_b = self.calculate_team_value(offer.players_b)
        
        # Check if trade is fair (within 20% value difference)
        value_diff = abs(value_a - value_b) / max(value_a, value_b) if max(value_a, value_b) > 0 else 0
        
        if value_diff <= 0.2:  # 20% tolerance
            offer.approved = True
            offer.reason = f"Fair trade: Team A gets {value_b:.1f} value, Team B gets {value_a:.1f} value"
            return True, offer.reason
        else:
            offer.approved = False
            offer.reason = f"Unfair trade: Value difference too large ({value_diff:.1%})"
            return False, offer.reason
    
    def calculate_team_value(self, players: List[Player]) -> float:
        """Calculate the total value of a list of players using advanced metrics"""
        total_value = 0.0
        
        for player in players:
            total_value += self.calculate_player_value(player)
        
        return total_value
    
    def calculate_player_value(self, player: Player) -> float:
        """Calculate individual player value using advanced statistics and traditional metrics"""
        # Calculate advanced stats if not already done
        if self.league_context and not hasattr(player, 'war'):
            batting_advanced, pitching_advanced, fielding_advanced, war = \
                self.advanced_stats.calculate_all_advanced_stats(player, self.league_context)
            player.batting_advanced_stats = batting_advanced
            player.pitching_advanced_stats = pitching_advanced
            player.fielding_advanced_stats = fielding_advanced
            player.war = war
        
        # Base value from WAR if available
        base_value = 50.0  # Default baseline value
        if hasattr(player, 'war') and player.war:
            # WAR is the primary value driver (1 WAR ≈ 10 value points)
            war_value = player.war.total_war * 10.0
            base_value += war_value
        else:
            # Fallback to traditional attributes if no WAR available
            attr_value = (player.velocity + player.control + player.stamina + player.speed_control) / 4.0
            base_value = attr_value
        
        # Age factor (younger players worth more)
        age_factor = 1.0
        if player.age < 23:
            age_factor = 1.3  # Very young players worth 30% more
        elif player.age < 26:
            age_factor = 1.2  # Young players worth 20% more
        elif player.age > 30:
            age_factor = 0.9  # Older players worth 10% less
        elif player.age > 33:
            age_factor = 0.8  # Old players worth 20% less
        elif player.age > 36:
            age_factor = 0.6  # Very old players worth 40% less
        
        # Performance factor using advanced metrics
        performance_factor = 1.0
        
        # Batting performance
        if hasattr(player, 'batting_advanced_stats') and player.batting_stats.ab > 0:
            woba = player.batting_advanced_stats.woba
            ops_plus = player.batting_advanced_stats.ops_plus
            
            if woba >= 0.400 or ops_plus >= 140:  # Elite hitter
                performance_factor += 0.3
            elif woba >= 0.350 or ops_plus >= 120:  # Good hitter
                performance_factor += 0.2
            elif woba >= 0.320 or ops_plus >= 100:  # Average hitter
                performance_factor += 0.0
            else:  # Below average hitter
                performance_factor -= 0.2
        
        # Pitching performance
        if hasattr(player, 'pitching_advanced_stats') and player.pitching_stats.ip > 0:
            fip = player.pitching_advanced_stats.fip
            era_minus = player.pitching_advanced_stats.era_minus
            
            if fip <= 2.50 or era_minus <= 70:  # Elite pitcher
                performance_factor += 0.3
            elif fip <= 3.50 or era_minus <= 90:  # Good pitcher
                performance_factor += 0.2
            elif fip <= 4.50 or era_minus <= 110:  # Average pitcher
                performance_factor += 0.0
            else:  # Below average pitcher
                performance_factor -= 0.2
        
        # Fielding performance
        if hasattr(player, 'fielding_advanced_stats'):
            drs = player.fielding_advanced_stats.drs
            if drs >= 5.0:  # Elite defender
                performance_factor += 0.1
            elif drs >= 2.0:  # Good defender
                performance_factor += 0.05
            elif drs <= -5.0:  # Poor defender
                performance_factor -= 0.1
        
        # Retirement risk factor
        if player.age > 35:
            performance_factor *= 0.7  # High retirement risk
        elif player.age > 38:
            performance_factor *= 0.5  # Very high retirement risk
        
        # Two-way player bonus
        has_batting = hasattr(player, 'batting_stats') and player.batting_stats.ab > 0
        has_pitching = hasattr(player, 'pitching_stats') and player.pitching_stats.ip > 0
        if has_batting and has_pitching:
            performance_factor += 0.15  # Two-way players are valuable
        
        # Ensure minimum value
        final_value = max(10.0, base_value * age_factor * performance_factor)
        
        return final_value
    
    def ai_propose_trade(self, team: Team, other_teams: List[Team]) -> Optional[TradeOffer]:
        """AI proposes a trade to improve the team"""
        if not other_teams:
            return None
        
        # Find team needs
        needs = self.analyze_team_needs(team)
        if not needs:
            return None
        
        # Find potential trade partners
        for other_team in other_teams:
            if other_team == team:
                continue
                
            # Find players that match our needs
            available_players = self.find_available_players(other_team, needs)
            if not available_players:
                continue
            
            # Find players we can offer
            our_players = self.find_tradeable_players(team, available_players)
            if not our_players:
                continue
            
            # Create trade offer
            offer = TradeOffer(
                team_a=team,
                team_b=other_team,
                players_a=our_players,
                players_b=available_players
            )
            
            # Evaluate the trade
            approved, reason = self.evaluate_trade(offer)
            if approved:
                return offer
        
        return None
    
    def analyze_team_needs(self, team: Team) -> List[str]:
        """Analyze what a team needs most"""
        needs = []
        
        # Check pitching needs
        pitchers = [p for p in team.active_roster if p.pitching_stats.gp > 0]
        if len(pitchers) < 2:
            needs.append("pitching")
        
        # Check for good pitchers
        good_pitchers = [p for p in pitchers if p.pitching_stats.era < 3.0]
        if len(good_pitchers) < 1:
            needs.append("good_pitching")
        
        # Check for young players
        young_players = [p for p in team.active_roster if p.age < 25]
        if len(young_players) < 2:
            needs.append("youth")
        
        return needs
    
    def find_available_players(self, team: Team, needs: List[str]) -> List[Player]:
        """Find players on a team that match specific needs"""
        available = []
        
        for player in team.active_roster:
            if "pitching" in needs and player.pitching_stats.gp > 0:
                available.append(player)
            elif "good_pitching" in needs and player.pitching_stats.era < 3.0:
                available.append(player)
            elif "youth" in needs and player.age < 25:
                available.append(player)
        
        return available[:2]  # Limit to 2 players per trade
    
    def find_tradeable_players(self, team: Team, target_players: List[Player]) -> List[Player]:
        """Find players we can offer in trade"""
        # Don't trade our best players
        tradeable = []
        
        for player in team.active_roster:
            # Don't trade if we have few players
            if len(team.active_roster) <= 4:
                continue
            
            # Don't trade our best pitcher
            if player.pitching_stats.gp > 0 and player.pitching_stats.era < 2.0:
                continue
            
            # Don't trade young promising players
            if player.age < 22:
                continue
            
            tradeable.append(player)
        
        return tradeable[:2]  # Limit to 2 players per trade
    
    def execute_trade(self, offer: TradeOffer) -> bool:
        """Execute an approved trade"""
        if not offer.approved:
            return False
        
        # Move players between teams
        for player in offer.players_a:
            offer.team_a.remove_player(player)
            offer.team_b.add_player(player, active=True)
        
        for player in offer.players_b:
            offer.team_b.remove_player(player)
            offer.team_a.add_player(player, active=True)
        
        print(f"Trade executed: {offer.team_a.name} <-> {offer.team_b.name}")
        print(f"  {offer.team_a.name} receives: {[p.name for p in offer.players_b]}")
        print(f"  {offer.team_b.name} receives: {[p.name for p in offer.players_a]}")
        
        return True 