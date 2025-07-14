#!/usr/bin/env python3
"""
Debug script for season simulation
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.team import Team
from models.player import Player
from models.game import Game
from simulation.game_sim import GameSimulator
from simulation.season_sim import SeasonSimulator
import random

def test_season_debug():
    """Test season simulation with debug output"""
    print("=== DEBUG SEASON TEST ===")
    
    # Create teams like the main menu does
    teams = []
    divisions = ["American", "National"]
    team_names = {
        "American": ["Thunder", "Lightning"],
        "National": ["Fire", "Flame"]
    }
    
    for division in divisions:
        for team_name in team_names[division]:
            team = Team(team_name, division)
            
            # Generate players with the same logic as main menu
            for i in range(6):
                player = Player(
                    f"{team_name} Player {i+1}",
                    age=random.randint(20, 30),
                    velocity=random.randint(50, 80),
                    control=random.randint(50, 80),
                    stamina=random.randint(50, 80),
                    speed_control=random.randint(50, 80)
                )
                team.add_player(player, active=True)
            
            teams.append(team)
    
    print(f"Created {len(teams)} teams:")
    for team in teams:
        print(f"  {team.name}: {len(team.active_roster)} players")
        for player in team.active_roster:
            print(f"    {player.name}: V={player.velocity}, C={player.control}")
    
    # Test a single game first
    print(f"\n=== TESTING SINGLE GAME ===")
    team1, team2 = teams[0], teams[1]
    game_sim = GameSimulator(team1, team2)
    
    # Add debug output to see what's happening
    print(f"Testing {team1.name} vs {team2.name}")
    result = game_sim.simulate_game_with_result(Game(team1, team2))
    
    print(f"Game result: {result['home_team'].name} {result['home_score']} - {result['away_team'].name} {result['away_score']}")
    
    return True

if __name__ == "__main__":
    try:
        test_season_debug()
        print("\n✅ Debug season test completed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc() 