#!/usr/bin/env python3
"""Test the fixed career stats grid that includes current season"""

import sys
sys.path.insert(0, './src')

from models.player import Player, BattingStats, PitchingStats, FieldingStats
from ui.team_management import TeamManagementUI
from rich.console import Console
import random

def create_player_with_career_and_current_stats():
    """Create a player with career stats AND current season stats"""
    
    player = Player(
        name="Test Star Player",
        age=27,
        team="Test Team",
        velocity=78,
        control=82,
        stamina=75,
        speed_control=80,
        range=85,
        arm_strength=88,
        accuracy=83
    )
    
    # Add career stats for seasons 1 and 2
    for season in [1, 2]:
        # Season 1 and 2 batting stats
        batting = BattingStats()
        batting.gp = 15
        batting.ab = 55 + season * 5  # 60, 65
        batting.h = 18 + season * 2   # 20, 22
        batting.hr = 3 + season        # 4, 5
        # RBI should be realistic: roughly 60-80% of hits + some walks/HBP
        batting.rbi = int(batting.h * 0.7) + season  # ~14, ~17 (realistic)
        batting.bb = 8 + season        # 9, 10
        batting.k = 15 - season        # 14, 13
        
        # Season pitching stats
        pitching = PitchingStats()
        pitching.gp = 10 + season      # 11, 12
        pitching.gs = 5 + season       # 6, 7
        pitching.ip = 20.0 + season * 5  # 25.0, 30.0
        pitching.w = 4 + season        # 5, 6
        pitching.l = 2                 # 2, 2
        pitching.k = 18 + season * 3   # 21, 24
        pitching.bb = 6 - season       # 5, 4
        pitching.er = 3 + season       # 4, 5
        pitching.h = 15 + season * 2   # 17, 19
        
        # Season fielding stats
        fielding = FieldingStats()
        fielding.po = 12 + season * 3  # 15, 18
        fielding.a = 8 + season        # 9, 10
        fielding.e = 2 - season if season < 2 else 1  # 1, 1
        fielding.dp = 2
        
        # Add to career stats
        player.career_stats.add_season_stats(season, batting, pitching, fielding)
        player.seasons_played.append(season)
    
    # Now add CURRENT season stats (Season 3 in progress)
    player.batting_stats.gp = 8
    player.batting_stats.ab = 32
    player.batting_stats.h = 14  # Good .438 average
    player.batting_stats.hr = 3
    # Realistic RBI: roughly 70% of hits (14 * 0.7 = 9.8, round to 10)
    player.batting_stats.rbi = 10
    player.batting_stats.bb = 5
    player.batting_stats.k = 7
    
    player.pitching_stats.gp = 6
    player.pitching_stats.gs = 4
    player.pitching_stats.ip = 18.1
    player.pitching_stats.w = 3
    player.pitching_stats.l = 1
    player.pitching_stats.k = 15
    player.pitching_stats.bb = 3
    player.pitching_stats.er = 2
    player.pitching_stats.h = 10
    
    player.fielding_stats.po = 9
    player.fielding_stats.a = 6
    player.fielding_stats.e = 0  # Perfect fielding this season
    player.fielding_stats.dp = 1
    
    return player

def test_fixed_career_grid():
    """Test the fixed career stats grid with current season included"""
    console = Console()
    
    console.print("\n[bold]Testing Fixed Career Stats Grid (With Current Season)[/bold]\n")
    
    # Create player with career and current stats
    player = create_player_with_career_and_current_stats()
    
    console.print("[green]✓ Created player with career stats and current season stats[/green]")
    console.print(f"Player: {player.name} (Age {player.age})")
    console.print(f"Career seasons: {player.seasons_played}")
    console.print(f"Career BA: {player.career_stats.career_batting.avg:.3f}")
    console.print(f"Career ERA: {player.career_stats.career_pitching.era:.2f}")
    console.print(f"Current season BA: {player.batting_stats.avg:.3f}")
    console.print(f"Current season ERA: {player.pitching_stats.era:.2f}")
    
    console.print("\n[yellow]Expected results:[/yellow]")
    console.print("- Season 1 and Season 2 from career stats")
    console.print("- Season 3 * (with asterisk) from current stats")
    console.print("- TOTAL row combining all seasons")
    
    console.print("\n[cyan]Displaying career stats grid...[/cyan]\n")
    
    try:
        team_ui = TeamManagementUI()
        team_ui.show_player_details(player)
        
        console.print("\n[green]✓ Fixed career stats grid displayed successfully![/green]")
        console.print("[green]✓ Current season should now appear in the grid with an asterisk![/green]")
        
    except Exception as e:
        console.print(f"[red]✗ Error displaying fixed career stats: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_career_grid()