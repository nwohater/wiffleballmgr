"""
Advanced Statistics Calculator for Wiffle Ball Manager
Implements wOBA, FIP, OPS+, ERA-, Defensive Runs Saved, and WAR-like metric
"""
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from models.player import Player, BattingStats, PitchingStats, FieldingStats
from models.team import Team
import math

@dataclass
class LeagueContext:
    """Context for league-wide statistics needed for advanced metrics"""
    league_avg_obp: float = 0.0
    league_avg_slg: float = 0.0
    league_avg_era: float = 0.0
    league_avg_ops: float = 0.0
    park_factor: float = 1.0  # Neutral park
    league_fip_constant: float = 3.2  # Typical FIP constant

@dataclass
class AdvancedBattingStats:
    """Advanced batting statistics"""
    woba: float = 0.0       # Weighted On-Base Average
    ops_plus: int = 100     # OPS+ (100 = league average)
    wrc: float = 0.0        # Weighted Runs Created
    wrc_plus: int = 100     # WRC+ (100 = league average)
    babip: float = 0.0      # Batting Average on Balls in Play
    iso: float = 0.0        # Isolated Power

@dataclass
class AdvancedPitchingStats:
    """Advanced pitching statistics"""
    fip: float = 0.0        # Fielding Independent Pitching
    era_minus: int = 100    # ERA- (100 = league average, lower is better)
    xfip: float = 0.0       # Expected FIP
    k_rate: float = 0.0     # Strikeout Rate (K/TBF)
    bb_rate: float = 0.0    # Walk Rate (BB/TBF)
    hr_rate: float = 0.0    # Home Run Rate (HR/TBF)

@dataclass
class AdvancedFieldingStats:
    """Advanced fielding statistics"""
    drs: float = 0.0        # Defensive Runs Saved
    uzr: float = 0.0        # Ultimate Zone Rating
    range_factor: float = 0.0  # (PO + A) * 9 / IP
    zone_rating: float = 0.0   # Percentage of balls in zone converted to outs

@dataclass
class WarComponents:
    """Components of WAR calculation"""
    batting_runs: float = 0.0
    baserunning_runs: float = 0.0
    fielding_runs: float = 0.0
    positional_adjustment: float = 0.0
    replacement_level: float = 0.0
    runs_per_win: float = 10.0  # Adjusted for MLW shorter games

@dataclass
class PlayerWAR:
    """Complete WAR calculation for a player"""
    batting_war: float = 0.0    # WAR from batting
    pitching_war: float = 0.0   # WAR from pitching
    fielding_war: float = 0.0   # WAR from fielding
    total_war: float = 0.0      # Total WAR
    components: WarComponents = None

class AdvancedStatsCalculator:
    """Calculates advanced statistics for players and teams"""
    
    def __init__(self):
        # wOBA weights (adjusted for MLW shorter games)
        self.woba_weights = {
            'bb': 0.69,      # Walks
            'hbp': 0.72,     # Hit by pitch
            '1b': 0.89,      # Singles (calculated as H - 2B - 3B - HR)
            '2b': 1.27,      # Doubles
            '3b': 1.62,      # Triples
            'hr': 2.10       # Home runs
        }
        
        # FIP constants (adjusted for MLW)
        self.fip_constants = {
            'hr': 13,        # Home runs coefficient
            'bb_hbp': 3,     # Walks + HBP coefficient  
            'k': 2           # Strikeouts coefficient
        }
        
    def calculate_league_context(self, teams: List[Team]) -> LeagueContext:
        """Calculate league-wide statistics for context"""
        total_obp = total_slg = total_era = total_ops = 0.0
        total_players = 0
        total_ip = 0.0
        total_er = 0
        
        for team in teams:
            for player in team.get_all_players():
                if player.batting_stats.ab > 0:
                    total_obp += player.batting_stats.calc_obp
                    total_slg += player.batting_stats.calc_slg
                    total_ops += player.batting_stats.calc_ops
                    total_players += 1
                    
                if player.pitching_stats.ip > 0:
                    total_ip += player.pitching_stats.ip
                    total_er += player.pitching_stats.er
        
        context = LeagueContext()
        if total_players > 0:
            context.league_avg_obp = total_obp / total_players
            context.league_avg_slg = total_slg / total_players  
            context.league_avg_ops = total_ops / total_players
            
        if total_ip > 0:
            context.league_avg_era = (total_er * 3) / total_ip  # MLW uses 3 innings
            
        return context
    
    def calculate_woba(self, batting: BattingStats) -> float:
        """Calculate Weighted On-Base Average"""
        if batting.ab == 0:
            return 0.0
            
        # Calculate singles (hits minus extra-base hits)
        singles = batting.h - batting.doubles - batting.triples - batting.hr
        
        woba_numerator = (
            self.woba_weights['bb'] * batting.bb +
            self.woba_weights['hbp'] * batting.hbp +
            self.woba_weights['1b'] * singles +
            self.woba_weights['2b'] * batting.doubles +
            self.woba_weights['3b'] * batting.triples +
            self.woba_weights['hr'] * batting.hr
        )
        
        woba_denominator = batting.ab + batting.bb + batting.hbp
        
        if woba_denominator == 0:
            return 0.0
            
        return round(woba_numerator / woba_denominator, 3)
    
    def calculate_ops_plus(self, batting: BattingStats, context: LeagueContext) -> int:
        """Calculate OPS+ (100 = league average)"""
        if batting.ab == 0 or context.league_avg_ops == 0:
            return 100
            
        player_ops = batting.calc_ops
        ops_plus = int((player_ops / context.league_avg_ops) * 100)
        return max(0, ops_plus)  # Ensure non-negative
    
    def calculate_babip(self, batting: BattingStats) -> float:
        """Calculate Batting Average on Balls in Play"""
        balls_in_play = batting.ab - batting.k - batting.hr
        hits_in_play = batting.h - batting.hr
        
        if balls_in_play <= 0:
            return 0.0
            
        return round(hits_in_play / balls_in_play, 3)
    
    def calculate_iso(self, batting: BattingStats) -> float:
        """Calculate Isolated Power (SLG - AVG)"""
        if batting.ab == 0:
            return 0.0
            
        return round(batting.calc_slg - batting.avg, 3)
    
    def calculate_fip(self, pitching: PitchingStats, context: LeagueContext) -> float:
        """Calculate Fielding Independent Pitching"""
        if pitching.ip == 0:
            return 0.0
            
        fip = (
            (self.fip_constants['hr'] * pitching.h +  # Using hits as HR proxy for MLW
             self.fip_constants['bb_hbp'] * (pitching.bb + pitching.hbp) -
             self.fip_constants['k'] * pitching.k) / pitching.ip
        ) + context.league_fip_constant
        
        return round(max(0.0, fip), 2)
    
    def calculate_era_minus(self, pitching: PitchingStats, context: LeagueContext) -> int:
        """Calculate ERA- (100 = league average, lower is better)"""
        if pitching.ip == 0 or context.league_avg_era == 0:
            return 100
            
        era_minus = int((pitching.era / context.league_avg_era) * 100)
        return max(1, era_minus)  # Minimum of 1
    
    def calculate_k_rate(self, pitching: PitchingStats) -> float:
        """Calculate strikeout rate per total batters faced"""
        total_batters = self._estimate_batters_faced(pitching)
        if total_batters == 0:
            return 0.0
            
        return round((pitching.k / total_batters) * 100, 1)
    
    def calculate_bb_rate(self, pitching: PitchingStats) -> float:
        """Calculate walk rate per total batters faced"""
        total_batters = self._estimate_batters_faced(pitching)
        if total_batters == 0:
            return 0.0
            
        return round((pitching.bb / total_batters) * 100, 1)
    
    def _estimate_batters_faced(self, pitching: PitchingStats) -> int:
        """Estimate total batters faced from available stats"""
        # Rough estimate: IP * 3 + H + BB + HBP
        return int(pitching.ip * 3 + pitching.h + pitching.bb + pitching.hbp)
    
    def calculate_defensive_runs_saved(self, player: Player, fielding: FieldingStats, 
                                     position: str = "OF") -> float:
        """Calculate Defensive Runs Saved (simplified for MLW)"""
        if fielding.po + fielding.a + fielding.e == 0:
            return 0.0
            
        # Base DRS on fielding percentage and play rate
        expected_fpct = 0.970  # League average fielding percentage
        actual_fpct = fielding.calc_fpct
        
        # Adjust for player's range attribute
        range_factor = (player.range - 50) / 50.0  # Normalize around league average
        
        # Calculate plays made above/below average
        total_chances = fielding.po + fielding.a + fielding.e
        fpct_diff = actual_fpct - expected_fpct
        
        # DRS calculation (simplified)
        drs = (fpct_diff * total_chances * 0.8) + (range_factor * 2.0)
        
        return round(drs, 1)
    
    def calculate_uzr(self, player: Player, fielding: FieldingStats) -> float:
        """Calculate Ultimate Zone Rating (simplified)"""
        # Similar to DRS but focuses more on range and positioning
        if fielding.po + fielding.a == 0:
            return 0.0
            
        # Factor in player attributes
        range_factor = (player.range - 50) / 50.0
        reaction_factor = (player.reaction - 50) / 50.0
        
        # Base UZR on plays made and player skills
        base_uzr = (fielding.po + fielding.a) * 0.1
        skill_adjustment = (range_factor + reaction_factor) * 1.5
        
        return round(base_uzr + skill_adjustment, 1)
    
    def calculate_war_components(self, player: Player, context: LeagueContext) -> WarComponents:
        """Calculate WAR components for a player"""
        components = WarComponents()
        
        # Batting runs (based on wOBA and plate appearances)
        if player.batting_stats.ab > 0:
            woba = self.calculate_woba(player.batting_stats)
            league_woba = 0.320  # Estimated league average
            pa = player.batting_stats.ab + player.batting_stats.bb + player.batting_stats.hbp
            
            # Runs above average from batting
            woba_scale = 1.24  # Converts wOBA to runs per PA
            components.batting_runs = (woba - league_woba) / woba_scale * pa
        
        # Fielding runs (from DRS)
        if hasattr(player, 'fielding_stats'):
            components.fielding_runs = self.calculate_defensive_runs_saved(
                player, player.fielding_stats
            )
        
        # Positional adjustment (simplified - MLW has less positional differentiation)
        components.positional_adjustment = 0.0  # Neutral for MLW
        
        # Replacement level (games played factor)
        games_played = max(player.batting_stats.gp, player.pitching_stats.gp)
        components.replacement_level = games_played * 0.3  # 0.3 runs per game
        
        return components
    
    def calculate_pitching_war(self, player: Player, context: LeagueContext) -> float:
        """Calculate WAR for pitchers"""
        if player.pitching_stats.ip == 0:
            return 0.0
            
        # Runs allowed above/below average
        league_era = context.league_avg_era or 4.0
        era_diff = league_era - player.pitching_stats.era
        
        # Convert ERA difference to runs
        runs_above_avg = era_diff * (player.pitching_stats.ip / 3.0)  # MLW adjustment
        
        # Add replacement level
        replacement_runs = player.pitching_stats.ip * 0.1  # 0.1 runs per inning
        
        total_runs = runs_above_avg + replacement_runs
        
        # Convert to WAR (10 runs = 1 win in MLW)
        return round(total_runs / 10.0, 2)
    
    def calculate_total_war(self, player: Player, context: LeagueContext) -> PlayerWAR:
        """Calculate total WAR for a player"""
        war = PlayerWAR()
        war.components = self.calculate_war_components(player, context)
        
        # Batting WAR
        if player.batting_stats.ab > 0:
            total_batting_runs = (
                war.components.batting_runs +
                war.components.baserunning_runs +
                war.components.positional_adjustment -
                war.components.replacement_level
            )
            war.batting_war = total_batting_runs / war.components.runs_per_win
        
        # Pitching WAR
        if player.pitching_stats.ip > 0:
            war.pitching_war = self.calculate_pitching_war(player, context)
        
        # Fielding WAR (separate component)
        war.fielding_war = war.components.fielding_runs / war.components.runs_per_win
        
        # Total WAR
        war.total_war = war.batting_war + war.pitching_war + war.fielding_war
        
        return war
    
    def calculate_all_advanced_stats(self, player: Player, context: LeagueContext) -> Tuple[AdvancedBattingStats, AdvancedPitchingStats, AdvancedFieldingStats, PlayerWAR]:
        """Calculate all advanced stats for a player"""
        
        # Advanced batting stats
        batting_advanced = AdvancedBattingStats()
        if player.batting_stats.ab > 0:
            batting_advanced.woba = self.calculate_woba(player.batting_stats)
            batting_advanced.ops_plus = self.calculate_ops_plus(player.batting_stats, context)
            batting_advanced.babip = self.calculate_babip(player.batting_stats)
            batting_advanced.iso = self.calculate_iso(player.batting_stats)
        
        # Advanced pitching stats
        pitching_advanced = AdvancedPitchingStats()
        if player.pitching_stats.ip > 0:
            pitching_advanced.fip = self.calculate_fip(player.pitching_stats, context)
            pitching_advanced.era_minus = self.calculate_era_minus(player.pitching_stats, context)
            pitching_advanced.k_rate = self.calculate_k_rate(player.pitching_stats)
            pitching_advanced.bb_rate = self.calculate_bb_rate(player.pitching_stats)
        
        # Advanced fielding stats
        fielding_advanced = AdvancedFieldingStats()
        if hasattr(player, 'fielding_stats') and player.fielding_stats.po + player.fielding_stats.a > 0:
            fielding_advanced.drs = self.calculate_defensive_runs_saved(player, player.fielding_stats)
            fielding_advanced.uzr = self.calculate_uzr(player, player.fielding_stats)
        
        # WAR calculation
        war = self.calculate_total_war(player, context)
        
        return batting_advanced, pitching_advanced, fielding_advanced, war
