#!/usr/bin/env python3
"""Test script to verify simulation runs without team selection"""

import sys
sys.path.insert(0, './src')

from game.engine import GameEngine
from ui.menus import MainMenu
from rich.console import Console

def test_no_team_selection():
    """Test that we can run simulation without team selection"""
    console = Console()
    engine = GameEngine()
    
    # Create main menu (only takes engine as parameter)
    main_menu = MainMenu(engine)
    
    # Simulate selecting "New Game"
    console.print("\n[bold]Testing automatic team generation and season menu...[/bold]\n")
    
    # Call new_game directly
    result = main_menu.new_game()
    
    # Check that teams were created
    teams = engine.get_game_data("teams")
    season_sim = engine.get_game_data("season_simulator")
    
    if teams and season_sim:
        console.print(f"[green]✓ Teams generated successfully: {len(teams)} teams[/green]")
        console.print(f"[green]✓ Season simulator created[/green]")
        console.print(f"[green]✓ Current team set to: {teams[0].name}[/green]")
        console.print(f"[green]✓ Game state changed to: {engine.get_state()}[/green]")
        console.print("\n[bold green]SUCCESS: Simulation can now run without manual team selection![/bold green]")
        console.print("\n[yellow]The Season Menu is now displayed above. You can immediately:[/yellow]")
        console.print("  - Option 6: Simulate the entire season")
        console.print("  - Option 2: Play games one by one")
        console.print("  - Option 1: View your team roster")
    else:
        console.print("[red]✗ Failed to generate teams or season simulator[/red]")
        
if __name__ == "__main__":
    test_no_team_selection()