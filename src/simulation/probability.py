"""
Probability calculations using logistic/odds-ratio approach for at-bat outcomes
"""
import math
import random
from typing import Dict, Tuple, Optional
from src.models.player import Player
from src.utils.config_loader import get_skill_config


def sigmoid(x: float) -> float:
    """Calculate sigmoid function, clamped to prevent overflow"""
    # Clamp x to prevent overflow in exp()
    x = max(-500, min(500, x))
    try:
        return 1 / (1 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0


def normalize_attribute(attribute: int) -> float:
    """Normalize attribute from 1-100 scale to 0-1 scale centered at 0.5"""
    return (attribute - 50) / 50.0


class AtBatProbabilityCalculator:
    """Calculate at-bat outcome probabilities using logistic regression approach"""
    
    def __init__(self):
        config = get_skill_config()
        self.factors = config.probability_factors
        self.hit_weights = config.hit_type_weights
    
    def calculate_outcome_probabilities(self, pitcher: Player, batter: Player, 
                                     situation: Optional[str] = None) -> Dict[str, float]:
        """
        Calculate probabilities for each at-bat outcome using logistic approach
        
        Returns dict with keys: 'strikeout', 'walk', 'ball_in_play', 'homerun'
        """
        # Normalize attributes to -1 to 1 scale (centered at 0)
        pitcher_velocity = normalize_attribute(pitcher.velocity)
        pitcher_movement = normalize_attribute(pitcher.movement) 
        pitcher_control = normalize_attribute(pitcher.control)
        pitcher_deception = normalize_attribute(pitcher.deception)
        
        batter_contact = normalize_attribute(batter.contact)
        batter_discipline = normalize_attribute(batter.discipline)
        batter_power = normalize_attribute(batter.power)
        batter_speed = normalize_attribute(batter.speed)
        
        # Calculate pitcher composite scores
        pitcher_stuff = (pitcher_velocity * self.factors["PITCHER_VELOCITY_WEIGHT"] +
                        pitcher_movement * self.factors["PITCHER_MOVEMENT_WEIGHT"] +
                        pitcher_control * self.factors["PITCHER_CONTROL_WEIGHT"])
        
        pitcher_command = (pitcher_control * 0.6 + pitcher_deception * 0.4)
        
        # Calculate batter composite scores  
        batter_hit_ability = (batter_contact * self.factors["HITTER_CONTACT_WEIGHT"] +
                             batter_discipline * 0.3)
        
        batter_plate_discipline = (batter_discipline * self.factors["HITTER_DISCIPLINE_WEIGHT"] +
                                  batter_contact * 0.3)
        
        # Calculate raw logistic inputs for each outcome
        strikeout_input = (self.factors["STRIKEOUT_FACTOR"] * 
                          (pitcher_stuff - batter_hit_ability) + 
                          self.factors["BASE_STRIKEOUT_ADJUSTMENT"])
        
        walk_input = (self.factors["WALK_FACTOR"] * 
                     (batter_plate_discipline - pitcher_command) + 
                     self.factors["BASE_WALK_ADJUSTMENT"])
        
        hit_input = (self.factors["HIT_FACTOR"] * 
                    (batter_hit_ability - pitcher_stuff * 0.8) + 
                    self.factors["BASE_HIT_ADJUSTMENT"])
        
        homerun_input = (self.factors["HOMERUN_FACTOR"] * 
                        (batter_power * self.factors["HITTER_POWER_WEIGHT"] - 
                         pitcher_stuff * 0.6) + 
                        self.factors["BASE_HOMERUN_ADJUSTMENT"])
        
        # Apply situational modifiers
        if situation:
            modifier = self._get_situational_modifier(situation, pitcher, batter)
            strikeout_input += modifier.get("strikeout", 0)
            walk_input += modifier.get("walk", 0)
            hit_input += modifier.get("hit", 0)
            homerun_input += modifier.get("homerun", 0)
        
        # Convert to probabilities using sigmoid
        p_strikeout_raw = sigmoid(strikeout_input)
        p_walk_raw = sigmoid(walk_input)
        p_hit_raw = sigmoid(hit_input)
        p_homerun_raw = sigmoid(homerun_input)
        
        # Separate homerun from general hit probability
        p_hit_no_hr = p_hit_raw * (1 - p_homerun_raw)
        
        # Normalize probabilities to sum to 1
        raw_total = p_strikeout_raw + p_walk_raw + p_hit_no_hr + p_homerun_raw
        
        # Handle case where total might be very small
        if raw_total < 0.1:
            # Fallback to ensure reasonable probabilities
            p_strikeout_raw = 0.25
            p_walk_raw = 0.08
            p_hit_no_hr = 0.15
            p_homerun_raw = 0.02
            raw_total = p_strikeout_raw + p_walk_raw + p_hit_no_hr + p_homerun_raw
        
        # Calculate final normalized probabilities
        p_strikeout = p_strikeout_raw / raw_total
        p_walk = p_walk_raw / raw_total
        p_ball_in_play = p_hit_no_hr / raw_total
        p_homerun = p_homerun_raw / raw_total
        
        # The remainder is "out" (fielded ball, foul out, etc.)
        p_out = 1.0 - (p_strikeout + p_walk + p_ball_in_play + p_homerun)
        p_out = max(0.0, p_out)  # Ensure non-negative
        
        return {
            "strikeout": p_strikeout,
            "walk": p_walk,
            "ball_in_play": p_ball_in_play,
            "homerun": p_homerun,
            "out": p_out
        }
    
    def calculate_hit_type_probabilities(self, pitcher: Player, batter: Player) -> Dict[str, float]:
        """Calculate probabilities for different hit types when ball is put in play"""
        
        # Normalize power attribute
        power_norm = normalize_attribute(batter.power)
        speed_norm = normalize_attribute(batter.speed)
        
        # Base weights from constants
        single_weight = self.hit_weights["SINGLE_WEIGHT"]
        double_weight = self.hit_weights["DOUBLE_WEIGHT"] 
        triple_weight = self.hit_weights["TRIPLE_WEIGHT"]
        hr_weight = self.hit_weights["HOMERUN_WEIGHT"]
        
        # Adjust weights based on power
        power_factor = power_norm * self.hit_weights["POWER_SCALING_FACTOR"]
        
        # Power increases extra base hits at expense of singles
        if batter.power >= self.hit_weights["HOMERUN_POWER_THRESHOLD"]:
            hr_weight *= (1 + power_factor)
            double_weight *= (1 + power_factor * 0.5)
            single_weight *= (1 - power_factor * 0.3)
        elif batter.power >= self.hit_weights["EXTRABASE_POWER_THRESHOLD"]:
            double_weight *= (1 + power_factor * 0.7)
            triple_weight *= (1 + power_factor * 0.3)
            single_weight *= (1 - power_factor * 0.2)
        
        # Speed helps with triples and infield singles
        if batter.speed >= 60:
            triple_weight *= (1 + speed_norm * 0.4)
            single_weight *= (1 + speed_norm * 0.1)
        
        # Pitcher stuff reduces extra base hits
        pitcher_stuff = (normalize_attribute(pitcher.velocity) * 0.4 + 
                        normalize_attribute(pitcher.movement) * 0.6)
        
        if pitcher_stuff > 0.2:  # Above average pitcher
            hr_weight *= (1 - pitcher_stuff * 0.3)
            double_weight *= (1 - pitcher_stuff * 0.2)
            triple_weight *= (1 - pitcher_stuff * 0.4)
        
        # Normalize to probabilities
        total_weight = single_weight + double_weight + triple_weight + hr_weight
        
        return {
            "single": single_weight / total_weight,
            "double": double_weight / total_weight, 
            "triple": triple_weight / total_weight,
            "homerun": hr_weight / total_weight
        }
    
    def _get_situational_modifier(self, situation: str, pitcher: Player, 
                                 batter: Player) -> Dict[str, float]:
        """Get situational modifiers for different game situations"""
        modifiers = {"strikeout": 0, "walk": 0, "hit": 0, "homerun": 0}
        
        if situation == "clutch":
            # Players with high clutch rating perform better under pressure
            pitcher_clutch = normalize_attribute(getattr(pitcher, 'clutch', 50))
            batter_clutch = normalize_attribute(getattr(batter, 'clutch', 50))
            
            clutch_diff = batter_clutch - pitcher_clutch
            clutch_modifier = clutch_diff * self.factors["CLUTCH_MODIFIER"]
            
            modifiers["hit"] += clutch_modifier
            modifiers["homerun"] += clutch_modifier * 0.5
            modifiers["strikeout"] -= clutch_modifier * 0.3
        
        elif situation == "fatigue":
            # Tired pitchers lose effectiveness
            fatigue_effect = self.factors["FATIGUE_MODIFIER"]
            modifiers["strikeout"] += fatigue_effect
            modifiers["walk"] -= fatigue_effect * 1.5
            modifiers["hit"] -= fatigue_effect * 0.8
        
        elif situation == "speed_limit_pressure":
            # Pitcher trying to stay under speed limit
            if pitcher.velocity >= 70:  # Close to limit
                pressure_effect = normalize_attribute(pitcher.velocity - 65) * 0.2
                modifiers["walk"] -= pressure_effect  # Less control
                modifiers["hit"] += pressure_effect * 0.5
        
        return modifiers
    
    def determine_at_bat_outcome(self, pitcher: Player, batter: Player, 
                                situation: Optional[str] = None) -> Tuple[str, str, Dict]:
        """
        Determine the outcome of an at-bat using probability calculations
        
        Returns: (outcome, details, extra_info)
        """
        # Get outcome probabilities
        probabilities = self.calculate_outcome_probabilities(pitcher, batter, situation)
        
        # Roll for outcome
        rand = random.random()
        cumulative = 0.0
        
        # Check each outcome in order
        for outcome, prob in probabilities.items():
            cumulative += prob
            if rand <= cumulative:
                if outcome == "strikeout":
                    return "strikeout", "Strikeout", {"bases_advanced": 0}
                
                elif outcome == "walk":
                    return "walk", "Walk", {"bases_advanced": 1}
                
                elif outcome == "homerun":
                    return "hit", "Home run", {"bases_advanced": 4, "runs_scored": 1}
                
                elif outcome == "ball_in_play":
                    # Determine hit type
                    hit_probs = self.calculate_hit_type_probabilities(pitcher, batter)
                    hit_rand = random.random()
                    hit_cumulative = 0.0
                    
                    for hit_type, hit_prob in hit_probs.items():
                        hit_cumulative += hit_prob
                        if hit_rand <= hit_cumulative:
                            if hit_type == "single":
                                return "hit", "Single", {"bases_advanced": 1}
                            elif hit_type == "double":
                                return "hit", "Double", {"bases_advanced": 2}
                            elif hit_type == "triple":
                                return "hit", "Triple", {"bases_advanced": 3}
                            elif hit_type == "homerun":
                                return "hit", "Home run", {"bases_advanced": 4, "runs_scored": 1}
                    
                    # Fallback
                    return "hit", "Single", {"bases_advanced": 1}
                
                elif outcome == "out":
                    return "out", "Ground out", {"bases_advanced": 0}
        
        # Fallback - should never reach here
        return "out", "Ground out", {"bases_advanced": 0}
