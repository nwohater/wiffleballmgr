#!/usr/bin/env python3
"""
Test MLW Rules and Features
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from simulation.mlw_rules import MLWRules
from models.player import Player
from models.team import Team
import random

def test_mlw_rules():
    print("=== MLW Rules Test ===\n")
    
    rules = MLWRules()
    
    # Test 1: Speed Limit Enforcement
    print("1. Speed Limit Testing:")
    pitchers = [
        Player(name="Speed Demon", velocity=80),
        Player(name="Control Artist", velocity=70),
        Player(name="Warning Zone", velocity=74),
        Player(name="Safe Pitcher", velocity=65)
    ]
    
    for pitcher in pitchers:
        violation, msg = rules.check_speed_limit(pitcher)
        print(f"   {pitcher.name}: {msg}")
    
    # Test 2: Roster Validation
    print("\n2. Roster Validation:")
    teams = [
        ("Valid Team", 6, 2),
        ("Too Many Active", 8, 2),
        ("Too Many Reserve", 6, 4),
        ("Too Many Total", 7, 3)
    ]
    
    for name, active, reserve in teams:
        team = Team(name=name)
        for i in range(active):
            team.add_player(Player(name=f"Player {i+1}"), active=True)
        for i in range(reserve):
            team.add_player(Player(name=f"Reserve {i+1}"), active=False)
        
        valid, msg = rules.validate_roster(team)
        print(f"   {name}: {msg}")
    
    # Test 3: Lineup Validation
    print("\n3. Lineup Validation:")
    lineups = [
        ([Player(name=f"P{i}") for i in range(2)], "Too Short"),
        ([Player(name=f"P{i}") for i in range(3)], "Valid"),
        ([Player(name=f"P{i}") for i in range(5)], "Valid"),
        ([Player(name=f"P{i}") for i in range(6)], "Too Long")
    ]
    
    for lineup, desc in lineups:
        valid, msg = rules.validate_lineup(lineup)
        print(f"   {desc}: {msg}")
    
    # Test 4: Weather Effects
    print("\n4. Weather Effects:")
    weather_types = ["clear", "windy", "rainy", "hot", "cold"]
    for weather in weather_types:
        effects = rules.apply_weather_effects(weather)
        print(f"   {weather.capitalize()}: {effects}")
    
    # Test 5: Injury Risk
    print("\n5. Injury Risk Assessment:")
    players = [
        Player(name="Young Star", age=22, velocity=75),
        Player(name="Veteran", age=32, velocity=70),
        Player(name="High Usage", age=28, velocity=80)
    ]
    
    for player in players:
        player.pitching_stats.pt = 120 if "High Usage" in player.name else 50
        risk, msg = rules.check_injury_risk(player, player.pitching_stats.pt)
        print(f"   {player.name}: {msg}")
    
    # Test 6: Mercy Rule
    print("\n6. Mercy Rule Testing:")
    scenarios = [
        (1, 5, "Early inning, under limit"),
        (1, 6, "Early inning, at limit"),
        (1, 7, "Early inning, over limit"),
        (3, 8, "Late inning, no mercy rule")
    ]
    
    for inning, runs, desc in scenarios:
        mercy = rules.check_mercy_rule(inning, runs)
        print(f"   {desc}: Mercy rule {'applies' if mercy else 'does not apply'}")
    
    print("\n✅ MLW Rules Test Complete!")

if __name__ == "__main__":
    test_mlw_rules() 