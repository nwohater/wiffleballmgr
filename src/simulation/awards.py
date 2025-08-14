"""
Awards System for Wiffle Ball Manager
Uses advanced statistics to determine season-end awards
"""
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from models.player import Player
from models.team import Team
from simulation.advanced_stats import AdvancedStatsCalculator, LeagueContext

@dataclass
class Award:
    """Represents an award given to a player"""
    name: str
    winner: Player
    team: str
    stats: Dict[str, float]
    description: str

@dataclass
class TeamAward:
    """Represents an award given to a team"""
    name: str
    winner: Team
    value: float
    description: str

class AwardsSystem:
    """Calculates and awards season-end honors based on advanced statistics"""
    
    def __init__(self):
        self.advanced_stats = AdvancedStatsCalculator()
        
    def calculate_all_awards(self, teams: List[Team], season: int) -> Tuple[List[Award], List[TeamAward]]:
        """Calculate all awards for the season"""
        # Calculate league context for advanced stats
        league_context = self.advanced_stats.calculate_league_context(teams)
        
        # Calculate advanced stats for all players
        all_players = []
        for team in teams:
            for player in team.get_all_players():
                # Calculate advanced stats
                batting_advanced, pitching_advanced, fielding_advanced, war = \
                    self.advanced_stats.calculate_all_advanced_stats(player, league_context)
                
                # Store in player object for awards calculation
                player.batting_advanced_stats = batting_advanced
                player.pitching_advanced_stats = pitching_advanced
                player.fielding_advanced_stats = fielding_advanced
                player.war = war
                
                all_players.append((player, team))
        
        # Calculate individual awards
        individual_awards = []
        individual_awards.extend(self._calculate_mvp_awards(all_players, league_context))
        individual_awards.extend(self._calculate_cy_young_awards(all_players, league_context))
        individual_awards.extend(self._calculate_rookie_awards(all_players, league_context))
        individual_awards.extend(self._calculate_statistical_awards(all_players, league_context))
        individual_awards.extend(self._calculate_fielding_awards(all_players, league_context))
        
        # Calculate team awards
        team_awards = []
        team_awards.extend(self._calculate_team_awards(teams, league_context))
        
        return individual_awards, team_awards
    
    def _calculate_mvp_awards(self, all_players: List[Tuple[Player, Team]], 
                             league_context: LeagueContext) -> List[Award]:
        """Calculate Most Valuable Player awards"""
        awards = []
        
        # Filter qualified players (minimum plate appearances/games)
        qualified_hitters = []
        for player, team in all_players:
            if (hasattr(player, 'batting_stats') and 
                player.batting_stats.ab >= 30 and  # Minimum at-bats
                hasattr(player, 'war')):
                qualified_hitters.append((player, team))
        
        if not qualified_hitters:
            return awards
        
        # MVP based on total WAR
        mvp_candidate = max(qualified_hitters, key=lambda x: x[0].war.total_war)
        mvp_player, mvp_team = mvp_candidate
        
        mvp_stats = {
            'WAR': mvp_player.war.total_war,
            'wOBA': mvp_player.batting_advanced_stats.woba,
            'OPS+': mvp_player.batting_advanced_stats.ops_plus,
            'Batting AVG': mvp_player.batting_stats.avg,
            'Home Runs': mvp_player.batting_stats.hr
        }
        
        awards.append(Award(
            name="Most Valuable Player (MVP)",
            winner=mvp_player,
            team=mvp_team.name,
            stats=mvp_stats,
            description=f"Leader in WAR ({mvp_player.war.total_war:.2f}) with exceptional offensive production"
        ))
        
        return awards
    
    def _calculate_cy_young_awards(self, all_players: List[Tuple[Player, Team]], 
                                  league_context: LeagueContext) -> List[Award]:
        """Calculate Cy Young Award (best pitcher)"""
        awards = []
        
        # Filter qualified pitchers
        qualified_pitchers = []
        for player, team in all_players:
            if (hasattr(player, 'pitching_stats') and 
                player.pitching_stats.ip >= 15 and  # Minimum innings
                hasattr(player, 'war')):
                qualified_pitchers.append((player, team))
        
        if not qualified_pitchers:
            return awards
        
        # Cy Young based on pitching WAR and FIP
        def pitching_value(player_team):
            player, team = player_team
            # Combine pitching WAR and FIP (lower FIP is better)
            fip_score = max(0, 6.0 - player.pitching_advanced_stats.fip)  # Convert FIP to positive score
            return player.war.pitching_war + (fip_score * 0.1)
        
        cy_candidate = max(qualified_pitchers, key=pitching_value)
        cy_player, cy_team = cy_candidate
        
        cy_stats = {
            'Pitching WAR': cy_player.war.pitching_war,
            'FIP': cy_player.pitching_advanced_stats.fip,
            'ERA-': cy_player.pitching_advanced_stats.era_minus,
            'ERA': cy_player.pitching_stats.era,
            'Strikeouts': cy_player.pitching_stats.k,
            'K Rate': cy_player.pitching_advanced_stats.k_rate
        }
        
        awards.append(Award(
            name="Cy Young Award",
            winner=cy_player,
            team=cy_team.name,
            stats=cy_stats,
            description=f"Outstanding pitching: {cy_player.war.pitching_war:.2f} WAR, {cy_player.pitching_advanced_stats.fip:.2f} FIP"
        ))
        
        return awards
    
    def _calculate_rookie_awards(self, all_players: List[Tuple[Player, Team]], 
                                league_context: LeagueContext) -> List[Award]:
        """Calculate Rookie of the Year awards"""
        awards = []
        
        # Filter rookies (first season players)
        rookies = []
        for player, team in all_players:
            if len(player.seasons_played) <= 1 and hasattr(player, 'war'):  # First season
                rookies.append((player, team))
        
        if not rookies:
            return awards
        
        # Rookie award based on total WAR
        rookie_candidate = max(rookies, key=lambda x: x[0].war.total_war)
        rookie_player, rookie_team = rookie_candidate
        
        rookie_stats = {
            'WAR': rookie_player.war.total_war,
            'Batting WAR': rookie_player.war.batting_war,
            'Pitching WAR': rookie_player.war.pitching_war,
            'wOBA': rookie_player.batting_advanced_stats.woba if rookie_player.batting_stats.ab > 0 else 0.0,
            'FIP': rookie_player.pitching_advanced_stats.fip if rookie_player.pitching_stats.ip > 0 else 0.0
        }
        
        awards.append(Award(
            name="Rookie of the Year",
            winner=rookie_player,
            team=rookie_team.name,
            stats=rookie_stats,
            description=f"Outstanding rookie season with {rookie_player.war.total_war:.2f} WAR"
        ))
        
        return awards
    
    def _calculate_statistical_awards(self, all_players: List[Tuple[Player, Team]], 
                                    league_context: LeagueContext) -> List[Award]:
        """Calculate statistical achievement awards"""
        awards = []
        
        # Filter qualified players for batting awards
        qualified_hitters = [(p, t) for p, t in all_players if p.batting_stats.ab >= 30]
        qualified_pitchers = [(p, t) for p, t in all_players if p.pitching_stats.ip >= 15]
        
        # wOBA Leader
        if qualified_hitters:
            woba_leader = max(qualified_hitters, key=lambda x: x[0].batting_advanced_stats.woba)
            woba_player, woba_team = woba_leader
            
            awards.append(Award(
                name="wOBA Leader",
                winner=woba_player,
                team=woba_team.name,
                stats={'wOBA': woba_player.batting_advanced_stats.woba,
                      'OPS+': woba_player.batting_advanced_stats.ops_plus,
                      'AVG': woba_player.batting_stats.avg},
                description=f"League-leading wOBA of {woba_player.batting_advanced_stats.woba:.3f}"
            ))
        
        # FIP Leader (lowest FIP)
        if qualified_pitchers:
            fip_leader = min(qualified_pitchers, key=lambda x: x[0].pitching_advanced_stats.fip)
            fip_player, fip_team = fip_leader
            
            awards.append(Award(
                name="FIP Leader",
                winner=fip_player,
                team=fip_team.name,
                stats={'FIP': fip_player.pitching_advanced_stats.fip,
                      'ERA-': fip_player.pitching_advanced_stats.era_minus,
                      'K Rate': fip_player.pitching_advanced_stats.k_rate},
                description=f"League-leading FIP of {fip_player.pitching_advanced_stats.fip:.2f}"
            ))
        
        # OPS+ Leader
        if qualified_hitters:
            ops_plus_leader = max(qualified_hitters, key=lambda x: x[0].batting_advanced_stats.ops_plus)
            ops_player, ops_team = ops_plus_leader
            
            awards.append(Award(
                name="OPS+ Leader",
                winner=ops_player,
                team=ops_team.name,
                stats={'OPS+': ops_player.batting_advanced_stats.ops_plus,
                      'wOBA': ops_player.batting_advanced_stats.woba,
                      'ISO': ops_player.batting_advanced_stats.iso},
                description=f"League-leading OPS+ of {ops_player.batting_advanced_stats.ops_plus}"
            ))
        
        return awards
    
    def _calculate_fielding_awards(self, all_players: List[Tuple[Player, Team]], 
                                  league_context: LeagueContext) -> List[Award]:
        """Calculate fielding awards based on defensive metrics"""
        awards = []
        
        # Filter players with fielding opportunities
        qualified_fielders = []
        for player, team in all_players:
            if (hasattr(player, 'fielding_stats') and 
                hasattr(player, 'fielding_advanced_stats') and
                (player.fielding_stats.po + player.fielding_stats.a) >= 10):  # Minimum fielding chances
                qualified_fielders.append((player, team))
        
        if not qualified_fielders:
            return awards
        
        # Gold Glove (best defensive player) based on DRS
        gold_glove_candidate = max(qualified_fielders, key=lambda x: x[0].fielding_advanced_stats.drs)
        gg_player, gg_team = gold_glove_candidate
        
        awards.append(Award(
            name="Gold Glove Award",
            winner=gg_player,
            team=gg_team.name,
            stats={'DRS': gg_player.fielding_advanced_stats.drs,
                  'UZR': gg_player.fielding_advanced_stats.uzr,
                  'Fielding %': gg_player.fielding_stats.calc_fpct},
            description=f"Outstanding defense with {gg_player.fielding_advanced_stats.drs:.1f} Defensive Runs Saved"
        ))
        
        return awards
    
    def _calculate_team_awards(self, teams: List[Team], 
                              league_context: LeagueContext) -> List[TeamAward]:
        """Calculate team-based awards"""
        awards = []
        
        # Best Record
        best_team = max(teams, key=lambda t: t.wins)
        awards.append(TeamAward(
            name="Best Regular Season Record",
            winner=best_team,
            value=best_team.wins,
            description=f"League-best {best_team.wins} wins"
        ))
        
        # Calculate team-wide advanced stats
        for team in teams:
            team_players = team.get_all_players()
            if team_players:
                # Team WAR (sum of all player WARs)
                team_war = sum(getattr(p, 'war', type('', (), {'total_war': 0})()).total_war 
                              for p in team_players)
                team.total_war = team_war
        
        # Best Team WAR
        if all(hasattr(team, 'total_war') for team in teams):
            best_war_team = max(teams, key=lambda t: t.total_war)
            awards.append(TeamAward(
                name="Best Team WAR",
                winner=best_war_team,
                value=best_war_team.total_war,
                description=f"League-leading team WAR of {best_war_team.total_war:.1f}"
            ))
        
        return awards
    
    def display_awards(self, individual_awards: List[Award], team_awards: List[TeamAward], 
                      season: int):
        """Display all awards in a formatted manner"""
        print(f"\n{'='*80}")
        print(f"🏆 SEASON {season} AWARDS CEREMONY 🏆")
        print(f"{'='*80}")
        
        # Individual Awards
        print(f"\n🌟 INDIVIDUAL AWARDS 🌟")
        print("-" * 80)
        
        for award in individual_awards:
            print(f"\n{award.name}")
            print(f"Winner: {award.winner.name} ({award.team})")
            print(f"Description: {award.description}")
            print("Key Statistics:")
            for stat, value in award.stats.items():
                if isinstance(value, float):
                    print(f"  • {stat}: {value:.3f}")
                else:
                    print(f"  • {stat}: {value}")
        
        # Team Awards
        print(f"\n🏟️ TEAM AWARDS 🏟️")
        print("-" * 80)
        
        for award in team_awards:
            print(f"\n{award.name}")
            print(f"Winner: {award.winner.name}")
            print(f"Description: {award.description}")
            if isinstance(award.value, float):
                print(f"Value: {award.value:.1f}")
            else:
                print(f"Value: {award.value}")
        
        print(f"\n{'='*80}")
        print("🎉 CONGRATULATIONS TO ALL AWARD WINNERS! 🎉")
        print(f"{'='*80}")
    
    def get_award_winners_summary(self, individual_awards: List[Award], 
                                 team_awards: List[TeamAward]) -> Dict[str, str]:
        """Get a summary of award winners for easy reference"""
        summary = {}
        
        for award in individual_awards:
            summary[award.name] = f"{award.winner.name} ({award.team})"
        
        for award in team_awards:
            summary[award.name] = award.winner.name
        
        return summary
    
    def calculate_player_award_points(self, player: Player) -> float:
        """Calculate total award points for a player (for Hall of Fame consideration)"""
        points = 0.0
        
        # Check if player has advanced stats calculated
        if not hasattr(player, 'war'):
            return points
        
        # WAR-based points (career achievements)
        career_war = player.war.total_war
        if career_war >= 3.0:
            points += 10.0  # MVP/Cy Young caliber season
        elif career_war >= 2.0:
            points += 5.0   # All-Star caliber season
        elif career_war >= 1.0:
            points += 2.0   # Above average season
        
        # Statistical achievements
        if hasattr(player, 'batting_advanced_stats'):
            if player.batting_advanced_stats.woba >= 0.400:
                points += 3.0  # Elite offensive season
            elif player.batting_advanced_stats.ops_plus >= 140:
                points += 2.0  # Excellent offensive season
        
        if hasattr(player, 'pitching_advanced_stats'):
            if player.pitching_advanced_stats.fip <= 2.50:
                points += 3.0  # Elite pitching season
            elif player.pitching_advanced_stats.era_minus <= 80:
                points += 2.0  # Excellent pitching season
        
        # Fielding excellence
        if hasattr(player, 'fielding_advanced_stats'):
            if player.fielding_advanced_stats.drs >= 5.0:
                points += 1.0  # Elite defensive season
        
        return points
