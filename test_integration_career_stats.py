#!/usr/bin/env python3
"""Test the career stats grid integration with the game interface"""

import sys
sys.path.insert(0, './src')

from game.engine import GameEngine
from ui.menus import MainMenu
from simulation.season_sim import SeasonSimulator
from models.team import Team
from models.player import Player, BattingStats, PitchingStats
from rich.console import Console
import random

def create_team_with_career_players():
    """Create a team with players that have career stats"""
    team = Team("Test Stars")
    
    for i in range(6):
        # Create player with varied ages and career histories
        age = random.randint(24, 32)
        seasons_played = age - 22  # Simulate they started at 22
        
        player = Player(
            name=f"Star Player {chr(65+i)}",  # A, B, C, etc.
            age=age,
            team="Test Stars",
            velocity=random.randint(50, 85),
            control=random.randint(50, 85),
            stamina=random.randint(50, 85),
            speed_control=random.randint(50, 85),
            range=random.randint(60, 90),
            arm_strength=random.randint(60, 90),
            accuracy=random.randint(60, 90)
        )
        
        # Add career stats for multiple seasons
        for season in range(1, seasons_played + 1):
            # Create varying stats per season
            batting = BattingStats()
            batting.gp = random.randint(10, 15)
            batting.ab = random.randint(35, 65)
            batting.h = random.randint(8, 30)
            batting.hr = random.randint(0, 8)
            batting.rbi = random.randint(3, 18)
            batting.bb = random.randint(2, 15)
            batting.k = random.randint(6, 25)
            
            pitching = PitchingStats()
            pitching.gp = random.randint(5, 12)
            pitching.gs = random.randint(2, 8)
            pitching.ip = random.randint(10, 40) + random.random()
            pitching.w = random.randint(1, 8)
            pitching.l = random.randint(1, 6)
            pitching.k = random.randint(5, 30)
            pitching.bb = random.randint(2, 15)
            pitching.er = random.randint(1, 15)
            pitching.h = random.randint(5, 25)
            
            from models.player import FieldingStats
            fielding = FieldingStats()
            fielding.po = random.randint(3, 25)
            fielding.a = random.randint(2, 18)
            fielding.e = random.randint(0, 4)
            fielding.dp = random.randint(0, 3)
            
            player.career_stats.add_season_stats(season, batting, pitching, fielding)
            player.seasons_played.append(season)
        
        # Add current season stats
        player.batting_stats.gp = random.randint(5, 10)
        player.batting_stats.ab = random.randint(15, 40)
        player.batting_stats.h = random.randint(3, 20)
        player.batting_stats.hr = random.randint(0, 4)
        player.batting_stats.rbi = random.randint(2, 12)
        player.batting_stats.bb = random.randint(1, 8)
        player.batting_stats.k = random.randint(3, 15)
        
        player.pitching_stats.gp = random.randint(3, 8)
        player.pitching_stats.gs = random.randint(1, 5)
        player.pitching_stats.ip = random.randint(8, 25) + random.random()
        player.pitching_stats.w = random.randint(1, 4)
        player.pitching_stats.l = random.randint(0, 3)
        player.pitching_stats.k = random.randint(3, 18)
        player.pitching_stats.bb = random.randint(1, 10)
        player.pitching_stats.er = random.randint(1, 8)
        player.pitching_stats.h = random.randint(3, 15)
        
        team.add_player(player, active=True)
    
    team.wins = 8
    team.losses = 4
    return team

def test_career_stats_integration():
    """Test career stats integration with the game menu system"""
    console = Console()
    
    console.print("\n[bold]Testing Career Stats Grid Integration[/bold]\n")
    
    # Create game engine
    engine = GameEngine()
    
    # Create teams with career players
    console.print("[yellow]Creating team with players who have career stats...[/yellow]")
    test_team = create_team_with_career_players()
    other_teams = [Team(f"Team {i}") for i in range(2, 5)]
    teams = [test_team] + other_teams
    
    # Create season simulator
    season_sim = SeasonSimulator(teams, current_season=4)  # Season 4 to show career history
    
    # Set up game data
    engine.set_game_data("teams", teams)
    engine.set_game_data("season_simulator", season_sim)
    engine.set_game_data("current_team", test_team)
    engine.set_game_data("current_season", 4)
    
    console.print(f"[green]✓ Created team '{test_team.name}' with {len(test_team.get_all_players())} players[/green]")
    
    # Show sample player info
    sample_player = test_team.get_all_players()[0]
    console.print(f"\nSample player: {sample_player.name}")
    console.print(f"  Age: {sample_player.age}")
    console.print(f"  Seasons played: {len(sample_player.seasons_played)}")
    console.print(f"  Career BA: {sample_player.career_stats.career_batting.avg:.3f}")
    console.print(f"  Career ERA: {sample_player.career_stats.career_pitching.era:.2f}")
    
    console.print(f"\n[bold green]Setup complete![/bold green]")
    console.print(f"[yellow]Now you can test the View Team option in the game:[/yellow]")
    console.print("1. Run the main game (python run.py)")
    console.print("2. Select 'New Game' to load teams")
    console.print("3. Go to 'View Team' (Option 1)")
    console.print("4. Select a team")
    console.print("5. Choose a player number to see their career stats grid")
    
    console.print(f"\n[cyan]The career stats grid will show:[/cyan]")
    console.print("- Season-by-season batting and pitching stats")
    console.print("- Career totals at the bottom")
    console.print("- Current season stats separately")
    console.print("- Colored tables with proper formatting")

if __name__ == "__main__":
    test_career_stats_integration()