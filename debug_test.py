#!/usr/bin/env python3
"""
Debug test for game simulation
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.team import Team
from models.player import Player
from models.game import Game
from simulation.game_sim import GameSimulator
import random

def test_single_game():
    """Test a single game with debug output"""
    print("=== DEBUG TEST: Single Game ===")
    
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
    print(f"Teams: {team1.name} vs {team2.name}")
    game_sim = GameSimulator(team1, team2)
    result = game_sim.simulate_game_with_result(Game(team1, team2))
    
    print(f"\n=== GAME RESULT ===")
    print(f"Final Score: {result['home_team'].name} {result['home_score']} - {result['away_team'].name} {result['away_score']}")
    print(f"Winner: {result['winner'].name if result['winner'] else 'Tie'}")
    
    return True

if __name__ == "__main__":
    try:
        test_single_game()
        print("\n✅ Debug test completed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc() 