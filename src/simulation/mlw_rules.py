"""
MLW-specific rule enforcement for Wiffle Ball Manager
"""
import random
from typing import List, Tuple, Optional
from models.player import Player
from models.team import Team

class MLWRules:
    """Enforces MLW-specific rules and features"""
    
    def __init__(self):
        self.speed_limit = 75  # mph
        self.warning_speed = 73  # mph
        self.mercy_rule_runs = 6  # runs per inning
        self.mercy_rule_innings = 3  # no mercy rule after this inning
        self.max_batters = 5
        self.min_batters = 3
        self.players_on_field = 3
        
    def check_speed_limit(self, pitcher: Player) -> Tuple[bool, str]:
        """Check if pitcher is exceeding speed limit"""
        if pitcher.velocity > self.speed_limit:
            return True, f"Speed limit violation! {pitcher.velocity} mph > {self.speed_limit} mph"
        elif pitcher.velocity >= self.warning_speed:
            return False, f"Warning: {pitcher.velocity} mph (close to limit)"
        else:
            return False, f"Speed OK: {pitcher.velocity} mph"
    
    def apply_speed_penalty(self, pitcher: Player) -> str:
        """Apply penalty for exceeding speed limit"""
        if pitcher.velocity > self.speed_limit:
            # Automatic ball
            pitcher.pitching_stats.b += 1
            pitcher.pitching_stats.pt += 1
            return f"Automatic ball - Speed limit violation ({pitcher.velocity} mph)"
        return ""
    
    def check_mercy_rule(self, inning: int, runs_scored: int) -> bool:
        """Check if mercy rule should be applied"""
        return inning < self.mercy_rule_innings and runs_scored >= self.mercy_rule_runs
    
    def validate_lineup(self, lineup: List[Player]) -> Tuple[bool, str]:
        """Validate that lineup meets MLW requirements"""
        if len(lineup) < self.min_batters:
            return False, f"Lineup too short: {len(lineup)} players (minimum {self.min_batters})"
        elif len(lineup) > self.max_batters:
            return False, f"Lineup too long: {len(lineup)} players (maximum {self.max_batters})"
        else:
            return True, f"Valid lineup: {len(lineup)} players"
    
    def validate_roster(self, team: Team) -> Tuple[bool, str]:
        """Validate that team roster meets MLW requirements"""
        active_count = len(team.active_roster)
        reserve_count = len(team.reserve_roster)
        total_count = active_count + reserve_count
        
        if active_count > 6:
            return False, f"Too many active players: {active_count} (maximum 6)"
        elif reserve_count > 2:
            return False, f"Too many reserve players: {reserve_count} (maximum 2)"
        elif total_count > 8:
            return False, f"Too many total players: {total_count} (maximum 8)"
        else:
            return True, f"Valid roster: {active_count} active, {reserve_count} reserve"
    
    def enforce_no_stealing(self) -> str:
        """Enforce no stealing rule"""
        return "No stealing allowed in MLW"
    
    def enforce_no_leading_off(self) -> str:
        """Enforce no leading off rule"""
        return "No leading off allowed in MLW"
    
    def calculate_pitch_count_penalty(self, pitcher: Player) -> Optional[str]:
        """Calculate penalties for high pitch counts"""
        pitch_count = pitcher.pitching_stats.pt
        
        if pitch_count > 100:
            return "High pitch count warning - consider relief pitcher"
        elif pitch_count > 150:
            return "Very high pitch count - pitcher fatigued"
        
        return None
    
    def check_defensive_substitutions(self, team: Team) -> List[str]:
        """Check for valid defensive substitutions (3 players on field)"""
        issues = []
        
        # Check if we have enough players for defense
        if len(team.active_roster) < 3:
            issues.append(f"Not enough active players for defense: {len(team.active_roster)}/3")
        
        return issues
    
    def validate_pitcher_reentry(self, pitcher: Player, has_pitched: bool) -> Tuple[bool, str]:
        """Validate pitcher re-entry rules"""
        if has_pitched and pitcher.pitching_stats.gp > 0:
            return False, "Pitcher cannot re-enter as pitcher after being removed"
        else:
            return True, "Pitcher re-entry allowed"
    
    def apply_weather_effects(self, weather: str) -> dict:
        """Apply weather effects to gameplay"""
        effects = {
            "clear": {"pitch_control": 1.0, "hit_power": 1.0},
            "windy": {"pitch_control": 0.9, "hit_power": 1.1},
            "rainy": {"pitch_control": 0.8, "hit_power": 0.9},
            "hot": {"pitch_control": 0.95, "hit_power": 1.05},
            "cold": {"pitch_control": 0.9, "hit_power": 0.95}
        }
        
        return effects.get(weather, effects["clear"])
    
    def generate_weather(self) -> str:
        """Generate random weather for a game"""
        weather_options = ["clear", "windy", "rainy", "hot", "cold"]
        weights = [0.6, 0.2, 0.1, 0.05, 0.05]  # Clear weather most common
        return random.choices(weather_options, weights=weights)[0]
    
    def check_injury_risk(self, player: Player, pitch_count: int) -> Tuple[bool, str]:
        """Check for injury risk based on usage and age"""
        risk_factors = []
        
        # Age factor
        if player.age > 30:
            risk_factors.append("age")
        
        # High pitch count
        if pitch_count > 100:
            risk_factors.append("pitch_count")
        
        # Fatigue from high velocity
        if player.velocity > 70:
            risk_factors.append("high_velocity")
        
        if risk_factors:
            risk_level = len(risk_factors)
            if risk_level >= 2 and random.random() < 0.1:  # 10% chance of injury
                return True, f"Injury risk: {', '.join(risk_factors)}"
        
        return False, "No injury risk"
    
    def apply_mlw_modifiers(self, player: Player, situation: str) -> dict:
        """Apply MLW-specific modifiers to player performance"""
        modifiers = {
            "velocity": 1.0,
            "control": 1.0,
            "stamina": 1.0,
            "speed_control": 1.0
        }
        
        # Clutch situations
        if situation == "clutch":
            if player.age < 25:
                modifiers["control"] *= 1.1  # Young players handle pressure well
            else:
                modifiers["control"] *= 0.95  # Older players may struggle
        
        # Late game fatigue
        if situation == "late_game":
            modifiers["velocity"] *= 0.95
            modifiers["stamina"] *= 0.9
        
        # Speed limit pressure
        if situation == "speed_limit":
            modifiers["speed_control"] *= 1.05  # Extra focus on speed control
        
        return modifiers 