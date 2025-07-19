#!/usr/bin/env python3
"""Test script to verify the career stats grid display"""

import sys
sys.path.insert(0, './src')

from models.player import Player, BattingStats, PitchingStats, FieldingStats
from ui.team_management import TeamManagementUI
from rich.console import Console
import random

def create_player_with_career_stats():
    """Create a player with multi-season career stats"""
    
    # Create a player
    player = Player(
        name="Test Player",
        age=28,
        team="Test Team",
        velocity=75,
        control=80,
        stamina=70,
        speed_control=78,
        range=82,
        arm_strength=85,
        accuracy=79
    )
    
    # Simulate 3 seasons of stats
    for season in range(1, 4):
        # Create season batting stats
        batting = BattingStats()
        batting.gp = random.randint(12, 15)
        batting.ab = random.randint(40, 60)
        batting.h = random.randint(10, 25)
        batting.hr = random.randint(1, 6)
        batting.rbi = random.randint(5, 15)
        batting.bb = random.randint(3, 12)
        batting.k = random.randint(8, 20)
        
        # Create season pitching stats
        pitching = PitchingStats()
        pitching.gp = random.randint(8, 12)
        pitching.gs = random.randint(3, 8)
        pitching.ip = random.randint(15, 35) + random.random()
        pitching.w = random.randint(1, 6)
        pitching.l = random.randint(1, 5)
        pitching.k = random.randint(8, 25)
        pitching.bb = random.randint(3, 12)
        pitching.er = random.randint(2, 12)
        pitching.h = random.randint(8, 20)
        
        # Create season fielding stats
        fielding = FieldingStats()
        fielding.po = random.randint(5, 20)
        fielding.a = random.randint(3, 15)
        fielding.e = random.randint(0, 3)
        fielding.dp = random.randint(0, 2)
        
        # Add to career stats
        player.career_stats.add_season_stats(season, batting, pitching, fielding)
        player.seasons_played.append(season)
    
    # Set current season stats (Season 4)
    player.batting_stats.gp = 8
    player.batting_stats.ab = 32
    player.batting_stats.h = 12
    player.batting_stats.hr = 2
    player.batting_stats.rbi = 7
    player.batting_stats.bb = 4
    player.batting_stats.k = 9
    
    player.pitching_stats.gp = 6
    player.pitching_stats.gs = 3
    player.pitching_stats.ip = 18.2
    player.pitching_stats.w = 2
    player.pitching_stats.l = 1
    player.pitching_stats.k = 15
    player.pitching_stats.bb = 6
    player.pitching_stats.er = 4
    player.pitching_stats.h = 12
    
    player.fielding_stats.po = 8
    player.fielding_stats.a = 5
    player.fielding_stats.e = 1
    player.fielding_stats.dp = 1
    
    return player

def test_career_stats_display():
    """Test the career stats grid display"""
    console = Console()
    
    console.print("\n[bold]Testing Career Stats Grid Display[/bold]\n")
    
    # Create player with career stats
    player = create_player_with_career_stats()
    
    console.print("[green]✓ Created player with 3 seasons of career stats[/green]")
    console.print(f"Player: {player.name} (Age {player.age})")
    console.print(f"Seasons played: {player.seasons_played}")
    console.print(f"Career batting average: {player.career_stats.career_batting.avg:.3f}")
    console.print(f"Career ERA: {player.career_stats.career_pitching.era:.2f}")
    
    # Test the display
    console.print("\n[yellow]Displaying career stats grid...[/yellow]\n")
    
    try:
        team_ui = TeamManagementUI()
        team_ui.show_player_details(player)
        
        console.print("\n[green]✓ Career stats grid displayed successfully![/green]")
        
    except Exception as e:
        console.print(f"[red]✗ Error displaying career stats: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_career_stats_display()