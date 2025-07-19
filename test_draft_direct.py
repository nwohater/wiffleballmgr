#!/usr/bin/env python3
"""Direct test of the 1-round draft functionality"""

import sys
sys.path.insert(0, './src')

from simulation.season_sim import SeasonSimulator
from models.team import Team
from models.player import Player, BattingStats, PitchingStats
from rich.console import Console
import random

def create_test_teams():
    """Create a few test teams with players"""
    teams = []
    
    # Create 4 test teams
    for i in range(4):
        team = Team(f"Team {i+1}")
        
        # Add some players to each team
        for j in range(6):  # 6 players per team (active roster size)
            # Create varied players with different skill levels
            player = Player(
                name=f"Player {j+1}",
                age=random.randint(20, 35),
                velocity=random.randint(30, 80),
                control=random.randint(30, 80), 
                stamina=random.randint(30, 80),
                speed_control=random.randint(30, 80),
                range=random.randint(40, 85),
                arm_strength=random.randint(40, 85),
                accuracy=random.randint(40, 85)
            )
            
            # Add some stats to make the value calculation work
            batting = BattingStats()
            batting.ab = random.randint(20, 50)
            batting.h = random.randint(5, 25)
            player.batting_stats = batting
            
            team.add_player(player, active=True)
        
        # Set some wins/losses for draft order
        team.wins = random.randint(5, 12)
        team.losses = 15 - team.wins
        
        teams.append(team)
    
    return teams

def test_draft_direct():
    """Test the draft functionality directly"""
    console = Console()
    
    console.print("\n[bold]Testing 1-Round Draft System (Direct)[/bold]\n")
    
    # Create test teams
    teams = create_test_teams()
    console.print(f"[green]✓ Created {len(teams)} test teams[/green]")
    
    # Show team records for draft order
    console.print("\nTeam records:")
    for team in teams:
        players = team.get_all_players()
        console.print(f"{team.name}: {team.wins}-{team.losses} ({len(players)} players)")
    
    # Create season simulator
    season_sim = SeasonSimulator(teams)
    console.print("[green]✓ Created season simulator[/green]")
    
    # Show initial player values
    console.print("\nInitial player values (showing worst player per team):")
    for team in teams:
        worst_player = season_sim.find_worst_player(team)
        if worst_player:
            value = season_sim.calculate_player_value(worst_player)
            console.print(f"{team.name}: {worst_player.name} (Value: {value:.1f})")
    
    # Test the draft
    console.print("\n[yellow]Running 1-round draft...[/yellow]")
    try:
        season_sim.conduct_one_round_draft()
        console.print("\n[green]✓ Draft completed successfully![/green]")
        
        # Verify rosters after draft
        console.print("\nRosters after draft:")
        for team in teams:
            players = team.get_all_players()
            console.print(f"{team.name}: {len(players)} players")
            
    except Exception as e:
        console.print(f"[red]✗ Draft failed: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_draft_direct()