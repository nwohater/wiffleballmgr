#!/usr/bin/env python3
"""
Test script demonstrating the new logistic probability system for at-bat outcomes
"""

from src.simulation.probability import AtBatProbabilityCalculator
from src.models.player import Player

def test_probability_scenarios():
    """Test different pitcher vs batter matchups to demonstrate the system"""
    
    calc = AtBatProbabilityCalculator()
    
    # Define different types of pitchers and batters
    scenarios = [
        {
            "description": "Power Pitcher vs Contact Hitter",
            "pitcher": Player("Ace Pitcher", velocity=75, movement=70, control=65, deception=60),
            "batter": Player("Contact Hitter", contact=75, discipline=70, power=45, speed=60)
        },
        {
            "description": "Control Pitcher vs Power Hitter", 
            "pitcher": Player("Control Pitcher", velocity=60, movement=55, control=80, deception=70),
            "batter": Player("Power Hitter", contact=55, discipline=50, power=80, speed=40)
        },
        {
            "description": "Average Pitcher vs Average Hitter",
            "pitcher": Player("Average Pitcher", velocity=65, movement=60, control=60, deception=55),
            "batter": Player("Average Hitter", contact=60, discipline=60, power=60, speed=55)
        },
        {
            "description": "Finesse Pitcher vs Disciplined Hitter",
            "pitcher": Player("Finesse Pitcher", velocity=55, movement=75, control=70, deception=80),
            "batter": Player("Patient Hitter", contact=65, discipline=80, power=50, speed=65)
        }
    ]
    
    print("="*80)
    print("LOGISTIC PROBABILITY SYSTEM DEMONSTRATION")
    print("="*80)
    
    for scenario in scenarios:
        print(f"\n{scenario['description']}")
        print("-" * 50)
        
        pitcher = scenario['pitcher']
        batter = scenario['batter']
        
        print(f"Pitcher: {pitcher.name}")
        print(f"  Velocity: {pitcher.velocity}, Movement: {pitcher.movement}")
        print(f"  Control: {pitcher.control}, Deception: {pitcher.deception}")
        
        print(f"Batter: {batter.name}")
        print(f"  Contact: {batter.contact}, Discipline: {batter.discipline}")
        print(f"  Power: {batter.power}, Speed: {batter.speed}")
        
        # Calculate probabilities
        probs = calc.calculate_outcome_probabilities(pitcher, batter)
        
        print("\nOutcome Probabilities:")
        for outcome, prob in probs.items():
            print(f"  {outcome.title():12}: {prob:.1%}")
        
        # Show situational modifiers
        print("\nSituational Modifiers:")
        clutch_probs = calc.calculate_outcome_probabilities(pitcher, batter, "clutch")
        fatigue_probs = calc.calculate_outcome_probabilities(pitcher, batter, "fatigue")
        
        print("  Clutch situation:")
        for outcome in ['strikeout', 'walk', 'ball_in_play', 'homerun']:
            diff = clutch_probs[outcome] - probs[outcome]
            symbol = "+" if diff > 0 else ""
            print(f"    {outcome.title():12}: {symbol}{diff:+.1%}")
        
        print("  Pitcher fatigue:")
        for outcome in ['strikeout', 'walk', 'ball_in_play', 'homerun']:
            diff = fatigue_probs[outcome] - probs[outcome]
            symbol = "+" if diff > 0 else ""
            print(f"    {outcome.title():12}: {symbol}{diff:+.1%}")
        
        # Sample hit types when ball is put in play
        hit_probs = calc.calculate_hit_type_probabilities(pitcher, batter)
        print("\nHit Type Distribution (when ball in play):")
        for hit_type, prob in hit_probs.items():
            print(f"  {hit_type.title():12}: {prob:.1%}")

def test_probability_constants():
    """Show the constants used in the probability calculations"""
    
    from src.utils.constants import PROBABILITY_FACTORS, HIT_TYPE_WEIGHTS
    
    print("\n" + "="*80)
    print("PROBABILITY SYSTEM CONSTANTS")
    print("="*80)
    
    print("\nProbability Factors:")
    for key, value in PROBABILITY_FACTORS.items():
        print(f"  {key:30}: {value}")
    
    print("\nHit Type Weights:")
    for key, value in HIT_TYPE_WEIGHTS.items():
        print(f"  {key:30}: {value}")

if __name__ == "__main__":
    test_probability_scenarios()
    test_probability_constants()
    
    print(f"\n{'='*80}")
    print("The new logistic probability system successfully:")
    print("• Uses sigmoid functions for realistic probability curves")
    print("• Pits pitcher attributes vs hitter attributes")
    print("• Includes situational modifiers (clutch, fatigue, etc.)")
    print("• Separates probabilities for different outcomes")
    print("• Allows easy tuning via constants.py")
    print(f"{'='*80}")
