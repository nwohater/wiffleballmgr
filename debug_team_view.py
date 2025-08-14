#!/usr/bin/env python3
"""
Debug script to test team viewing functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.team import Team
from models.player import Player
from ui.team_management import TeamManagementUI
import random

def create_test_team():
    """Create a test team with players"""
    team = Team(name="Test Team", division="Test")
    
    # Add 6 active players
    for i in range(6):
        player = Player(
            name=f"Player {i+1}",
            age=random.randint(20, 30),
            power=random.randint(50, 80),
            contact=random.randint(50, 80),
            discipline=random.randint(50, 80),
            speed=random.randint(50, 80),
            velocity=random.randint(50, 80),
            movement=random.randint(50, 80),
            control=random.randint(50, 80),
            stamina=random.randint(50, 80),
            deception=random.randint(50, 80),
            range=random.randint(50, 80),
            arm_strength=random.randint(50, 80),
            hands=random.randint(50, 80),
            reaction=random.randint(50, 80),
            leadership=random.randint(50, 80),
            clutch=random.randint(50, 80),
            speed_control=random.randint(50, 80)
        )
        
        # Add some stats
        player.batting_stats.h = random.randint(5, 25)
        player.batting_stats.ab = random.randint(20, 50)
        player.pitching_stats.ip = random.randint(5, 20)
        player.pitching_stats.er = random.randint(2, 10)
        
        team.add_player(player, active=True)
    
    # Add 2 reserve players
    for i in range(2):
        player = Player(
            name=f"Reserve {i+1}",
            age=random.randint(20, 30),
            power=random.randint(40, 70),
            contact=random.randint(40, 70),
            discipline=random.randint(40, 70),
            speed=random.randint(40, 70),
            velocity=random.randint(40, 70),
            movement=random.randint(40, 70),
            control=random.randint(40, 70),
            stamina=random.randint(40, 70),
            deception=random.randint(40, 70),
            range=random.randint(40, 70),
            arm_strength=random.randint(40, 70),
            hands=random.randint(40, 70),
            reaction=random.randint(40, 70),
            leadership=random.randint(40, 70),
            clutch=random.randint(40, 70),
            speed_control=random.randint(40, 70)
        )
        team.add_player(player, active=False)
    
    return team

def main():
    """Test team viewing"""
    print("=== Debug Team View Test ===")
    
    # Create test team
    team = create_test_team()
    
    print(f"Team: {team.name}")
    print(f"Active players: {len(team.active_roster)}")
    print(f"Reserve players: {len(team.reserve_roster)}")
    
    print("\nActive roster:")
    for i, player in enumerate(team.active_roster, 1):
        print(f"  {i}. {player.name} (Age: {player.age})")
    
    print("\nReserve roster:")
    for i, player in enumerate(team.reserve_roster, 1):
        print(f"  {i}. {player.name} (Age: {player.age})")
    
    # Test UI
    print("\n=== Testing UI ===")
    ui = TeamManagementUI()
    
    # Show team overview
    ui.show_team_overview(team)
    input("\nPress Enter to continue...")
    
    # Show roster
    ui.show_roster(team, show_reserves=True)
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    main() 