#!/usr/bin/env python3
"""
UI Demo for Wiffle Ball Manager
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ui.team_management import TeamManagementUI
from models.team import Team
from models.player import Player
import random

def create_sample_team():
    """Create a sample team with realistic stats"""
    team = Team(name="Thunder", division="American")
    team.wins = 8
    team.losses = 4
    team.ties = 1
    team.runs_scored = 45
    team.runs_allowed = 32
    
    # Create players with realistic stats
    players = [
        ("Jordan Smith", 24, 75, 80, 70, 75, 18, 65, 2, 8),
        ("Alex Johnson", 26, 70, 85, 65, 80, 22, 58, 3, 12),
        ("Taylor Davis", 28, 65, 75, 80, 70, 15, 72, 1, 15),
        ("Casey Wilson", 22, 80, 70, 75, 65, 25, 45, 4, 6),
        ("Morgan Brown", 25, 72, 78, 68, 72, 20, 55, 2, 10),
        ("Riley Garcia", 23, 78, 75, 70, 78, 19, 60, 3, 9),
    ]
    
    for name, age, vel, con, sta, sc, hits, ab, hr, k in players:
        player = Player(name=name, age=age, velocity=vel, control=con, stamina=sta, speed_control=sc)
        player.batting_stats.h = hits
        player.batting_stats.ab = ab
        player.batting_stats.hr = hr
        player.batting_stats.k = k
        player.pitching_stats.ip = random.randint(10, 20)
        player.pitching_stats.er = random.randint(5, 15)
        team.add_player(player, active=True)
    
    # Add reserve players
    for i in range(2):
        player = Player(name=f"Reserve {i+1}", age=random.randint(20, 25))
        team.add_player(player, active=False)
    
    return team

def ui_demo():
    """Demonstrate the UI features"""
    print("=== Wiffle Ball Manager UI Demo ===\n")
    
    ui = TeamManagementUI()
    team = create_sample_team()
    
    print("1. Team Overview:")
    ui.show_team_overview(team)
    input("\nPress Enter to continue...")
    
    print("\n2. Team Roster (Active Players):")
    ui.show_roster(team, show_reserves=False)
    input("\nPress Enter to continue...")
    
    print("\n3. Team Roster (Including Reserves):")
    ui.show_roster(team, show_reserves=True)
    input("\nPress Enter to continue...")
    
    print("\n4. Player Details:")
    ui.show_player_details(team.active_roster[0])
    input("\nPress Enter to continue...")
    
    print("\n5. League Standings:")
    # Create some other teams for standings
    teams = [team]
    for name in ["Lightning", "Storm", "Hurricane"]:
        other_team = Team(name=name)
        other_team.wins = random.randint(3, 10)
        other_team.losses = random.randint(3, 10)
        other_team.ties = random.randint(0, 2)
        other_team.runs_scored = random.randint(20, 50)
        other_team.runs_allowed = random.randint(20, 50)
        teams.append(other_team)
    
    ui.show_league_standings(teams)
    input("\nPress Enter to continue...")
    
    print("\n6. Batting Leaders:")
    ui.show_stat_leaders(teams, "batting")
    input("\nPress Enter to continue...")
    
    print("\n7. Pitching Leaders:")
    ui.show_stat_leaders(teams, "pitching")
    
    print("\n✅ UI Demo Complete!")

if __name__ == "__main__":
    ui_demo() 