#!/usr/bin/env python3
"""Test script to verify the 1-round draft functionality"""

import sys
sys.path.insert(0, './src')

from game.engine import GameEngine
from ui.menus import MainMenu
from rich.console import Console

def test_draft():
    """Test the draft functionality by simulating a season"""
    console = Console()
    engine = GameEngine()
    
    console.print("\n[bold]Testing 1-Round Draft System...[/bold]\n")
    
    # Create main menu and start new game
    main_menu = MainMenu(engine)
    
    # Trigger new game setup
    console.print("[yellow]Setting up new season...[/yellow]")
    main_menu.new_game()
    
    # Get the season simulator
    season_sim = engine.get_game_data("season_simulator")
    teams = engine.get_game_data("teams")
    
    if not season_sim or not teams:
        console.print("[red]✗ Failed to set up season[/red]")
        return
    
    console.print(f"[green]✓ Season set up with {len(teams)} teams[/green]")
    
    # Test the draft method directly
    console.print("\n[yellow]Testing draft functionality...[/yellow]")
    
    # Show initial roster sizes
    console.print("\nInitial roster sizes:")
    for team in teams[:3]:  # Show first 3 teams
        players = team.get_all_players()
        console.print(f"{team.name}: {len(players)} players")
        if players:
            for player in players[:2]:  # Show first 2 players
                value = season_sim.calculate_player_value(player)
                console.print(f"  - {player.name} (Value: {value:.1f})")
    
    # Test the draft
    try:
        season_sim.conduct_one_round_draft()
        console.print("\n[green]✓ Draft completed successfully![/green]")
        
        # Verify roster sizes after draft
        console.print("\nRoster sizes after draft:")
        for team in teams[:3]:
            players = team.get_all_players()
            console.print(f"{team.name}: {len(players)} players")
            
    except Exception as e:
        console.print(f"[red]✗ Draft failed: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_draft()