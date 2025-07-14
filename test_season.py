#!/usr/bin/env python3
"""
Test script for Wiffle Ball Manager season simulation
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.team import Team
from models.player import Player
from simulation.season_sim import SeasonSimulator
import random

def create_test_teams():
    """Create some test teams with players for demonstration."""
    teams = []
    team_names = ["Thunder", "Lightning", "Storm", "Hurricane", "Tornado", "Cyclone"]
    
    for i, name in enumerate(team_names):
        team = Team(name=name, division="Test")
        
        # Add some existing players to each team
        for j in range(6):  # 6 active players per team
            player = Player(
                name=f"Player {j+1}",
                velocity=random.randint(40, 80),
                control=random.randint(40, 80),
                stamina=random.randint(40, 80),
                speed_control=random.randint(40, 80)
            )
            team.add_player(player, active=True)
        
        # Add 2 reserve players
        for j in range(2):
            player = Player(
                name=f"Reserve {j+1}",
                velocity=random.randint(30, 70),
                control=random.randint(30, 70),
                stamina=random.randint(30, 70),
                speed_control=random.randint(30, 70)
            )
            team.add_player(player, active=False)
        
        teams.append(team)
    
    return teams

def main():
    """Run the season simulation test."""
    print("=== Wiffle Ball Manager - Season Simulation Test ===\n")
    
    # Create test teams
    print("Creating test teams...")
    teams = create_test_teams()
    for team in teams:
        print(f"  {team.name}: {len(team.active_roster)} active, {len(team.reserve_roster)} reserve players")
    
    print(f"\nStarting season simulation with {len(teams)} teams...")
    
    # Create and run season simulator
    simulator = SeasonSimulator(teams, games_per_season=15, innings_per_game=3)
    simulator.play_season()
    
    # Display final standings
    print("\n=== Final Standings ===")
    teams.sort(key=lambda t: t.wins, reverse=True)
    for i, team in enumerate(teams, 1):
        print(f"{i}. {team.name}: {team.wins}-{team.losses}-{team.ties} "
              f"(Runs: {team.runs_scored}-{team.runs_allowed})")
    
    print(f"\nSeason completed! Total games played: {len(simulator.results)}")

if __name__ == "__main__":
    main() 