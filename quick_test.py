#!/usr/bin/env python3
"""
Quick test of Wiffle Ball Manager core functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.team import Team
from models.player import Player
from simulation.season_sim import SeasonSimulator
from simulation.mlw_rules import MLWRules
from simulation.player_dev import PlayerDevelopment
import random

def quick_test():
    print("=== Quick Wiffle Ball Manager Test ===\n")
    
    # 1. Test MLW Rules
    print("1. Testing MLW Rules:")
    rules = MLWRules()
    pitcher = Player(name="Test Pitcher", velocity=80)
    violation, msg = rules.check_speed_limit(pitcher)
    print(f"   {msg}")
    
    # 2. Test Player Creation
    print("\n2. Testing Player Creation:")
    player = Player(name="Star Player", age=25, velocity=75, control=80)
    print(f"   Created {player.name}: Age {player.age}, Velocity {player.velocity}")
    
    # 3. Test Team Management
    print("\n3. Testing Team Management:")
    team = Team(name="Test Team")
    team.add_player(player, active=True)
    print(f"   Team {team.name} has {len(team.active_roster)} active players")
    
    # 4. Test Player Development
    print("\n4. Testing Player Development:")
    dev = PlayerDevelopment()
    old_velocity = player.velocity
    dev.develop_player(player)
    print(f"   {player.name}: Velocity {old_velocity} → {player.velocity}")
    
    # 5. Test Single Game (simplified)
    print("\n5. Testing Single Game:")
    team1 = Team(name="Team A")
    team2 = Team(name="Team B")
    
    # Add players to teams
    for i in range(6):
        team1.add_player(Player(name=f"Player A{i+1}", velocity=random.randint(50, 80)), active=True)
        team2.add_player(Player(name=f"Player B{i+1}", velocity=random.randint(50, 80)), active=True)
    
    # Simulate one game
    from models.game import Game
    game = Game(team1, team2)
    game.play()
    
    print(f"   Game Result: {team1.name} {game.home_score} - {team2.name} {game.away_score}")
    
    # 6. Test Rookie Draft
    print("\n6. Testing Rookie Draft:")
    simulator = SeasonSimulator([team1, team2], games_per_season=3)  # Short season
    simulator.conduct_rookie_draft(rounds=1)
    
    print("\n✅ All core systems working!")

if __name__ == "__main__":
    quick_test() 