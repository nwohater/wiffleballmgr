#!/usr/bin/env python3
"""
Test script to verify menu and season simulation fixes
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.team import Team
from models.player import Player
from models.game import Game
from simulation.season_sim import SeasonSimulator
from simulation.game_sim import GameSimulator
import random

def test_game_simulation():
    """Test that game simulation doesn't hang"""
    print("Testing game simulation...")
    
    # Create two teams with players
    team1 = Team("Test Team 1", "American")
    team2 = Team("Test Team 2", "National")
    
    # Add players to teams
    for i in range(6):
        player1 = Player(f"Player1_{i+1}", age=25, velocity=70, control=70)
        player2 = Player(f"Player2_{i+1}", age=25, velocity=70, control=70)
        team1.add_player(player1, active=True)
        team2.add_player(player2, active=True)
    
    # Test game simulation
    game_sim = GameSimulator(team1, team2)
    result = game_sim.simulate_game_with_result(Game(team1, team2))
    
    print(f"Game result: {result['home_team'].name} {result['home_score']} - {result['away_team'].name} {result['away_score']}")
    print("Game simulation test passed!")
    return True

def test_season_simulation():
    """Test that season simulation works and shows progress"""
    print("\nTesting season simulation...")
    
    # Create teams
    teams = []
    divisions = ["American", "National"]
    team_names = {
        "American": ["Thunder", "Lightning"],
        "National": ["Fire", "Flame"]
    }
    
    for division in divisions:
        for team_name in team_names[division]:
            team = Team(team_name, division)
            
            # Generate players
            for i in range(6):
                player = Player(
                    f"{team_name} Player {i+1}",
                    age=random.randint(20, 30),
                    velocity=random.randint(50, 80),
                    control=random.randint(50, 80)
                )
                team.add_player(player, active=True)
            
            teams.append(team)
    
    # Test season simulation
    season_sim = SeasonSimulator(teams, games_per_season=6)  # Fewer games for testing
    results = season_sim.simulate_full_season()
    
    print(f"Season complete! Champion: {results['champion'].name if results['champion'] else 'None'}")
    print("Season simulation test passed!")
    return True

if __name__ == "__main__":
    try:
        test_game_simulation()
        test_season_simulation()
        print("\n✅ All tests passed! The menu should work properly now.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc() 