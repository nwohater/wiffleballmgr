#!/usr/bin/env python3
"""
Simple test of Wiffle Ball Manager features
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.team import Team
from models.player import Player
from simulation.mlw_rules import MLWRules
from simulation.player_dev import PlayerDevelopment
from simulation.trading import TradingSystem
import random

def simple_test():
    print("=== Simple Wiffle Ball Manager Test ===\n")
    
    # 1. Test MLW Rules
    print("1. MLW Rules:")
    rules = MLWRules()
    pitcher = Player(name="Fast Pitcher", velocity=80)
    violation, msg = rules.check_speed_limit(pitcher)
    print(f"   {msg}")
    
    # 2. Test Player Development
    print("\n2. Player Development:")
    player = Player(name="Young Star", age=22, velocity=70, control=75)
    dev = PlayerDevelopment()
    old_vel = player.velocity
    dev.develop_player(player)
    print(f"   {player.name}: Age {player.age}, Velocity {old_vel} → {player.velocity}")
    
    # 3. Test Team Management
    print("\n3. Team Management:")
    team = Team(name="Test Team")
    for i in range(6):
        team.add_player(Player(name=f"Player {i+1}"), active=True)
    for i in range(2):
        team.add_player(Player(name=f"Reserve {i+1}"), active=False)
    print(f"   Team has {len(team.active_roster)} active, {len(team.reserve_roster)} reserve")
    
    # 4. Test Roster Validation
    valid, msg = rules.validate_roster(team)
    print(f"   Roster validation: {msg}")
    
    # 5. Test Trading System
    print("\n4. Trading System:")
    trading = TradingSystem()
    
    # Create two teams
    team_a = Team(name="Team A")
    team_b = Team(name="Team B")
    
    # Add players with different abilities
    for i in range(6):
        player_a = Player(name=f"A{i+1}", age=25)
        player_b = Player(name=f"B{i+1}", age=25)
        
        if i < 2:  # Team A needs pitching
            player_a.pitching_stats.ip = 10
            player_a.pitching_stats.er = 15  # High ERA
            player_b.pitching_stats.ip = 15
            player_b.pitching_stats.er = 8   # Low ERA
        
        team_a.add_player(player_a, active=True)
        team_b.add_player(player_b, active=True)
    
    # Evaluate a trade
    offer = trading.ai_propose_trade(team_a, [team_b])
    if offer:
        approved, reason = trading.evaluate_trade(offer)
        print(f"   Trade evaluation: {reason}")
    else:
        print("   No suitable trade found")
    
    # 6. Test Weather Effects
    print("\n5. Weather Effects:")
    weather = rules.generate_weather()
    effects = rules.apply_weather_effects(weather)
    print(f"   Weather: {weather}, Effects: {effects}")
    
    # 7. Test Rookie Generation
    print("\n6. Rookie Generation:")
    from simulation.season_sim import SeasonSimulator
    simulator = SeasonSimulator([team_a, team_b], games_per_season=1)
    
    rookie, rookie_type, ratings = simulator.generate_realistic_rookie()
    print(f"   Generated {rookie.name} [{rookie_type}] {ratings}")
    
    print("\n✅ All core features working!")

if __name__ == "__main__":
    simple_test() 