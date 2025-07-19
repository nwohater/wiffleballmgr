#!/usr/bin/env python3
"""Test script to verify multi-season progression with stat tracking"""

import sys
sys.path.insert(0, './src')

from simulation.season_sim import SeasonSimulator
from models.team import Team
from models.player import Player, BattingStats, PitchingStats
from rich.console import Console
import random

def create_test_teams_with_stats():
    """Create test teams with players that have some existing stats"""
    teams = []
    
    for i in range(4):
        team = Team(f"Team {i+1}")
        
        # Add players with varied ages and some season 1 stats
        for j in range(6):
            age = random.randint(22, 32)
            player = Player(
                name=f"Player {chr(65+j)}{i+1}",  # A1, B1, C1, etc.
                age=age,
                velocity=random.randint(40, 80),
                control=random.randint(40, 80),
                stamina=random.randint(40, 80),
                speed_control=random.randint(40, 80),
                range=random.randint(50, 85),
                arm_strength=random.randint(50, 85),
                accuracy=random.randint(50, 85)
            )
            
            # Add some batting stats
            batting = BattingStats()
            batting.ab = random.randint(30, 60)
            batting.h = random.randint(8, 30)
            batting.hr = random.randint(0, 5)
            batting.bb = random.randint(3, 12)
            batting.k = random.randint(8, 20)
            player.batting_stats = batting
            
            # Add some pitching stats
            pitching = PitchingStats()
            pitching.ip = random.randint(5, 25)
            pitching.k = random.randint(3, 20)
            pitching.bb = random.randint(1, 10)
            pitching.er = random.randint(1, 8)
            player.pitching_stats = pitching
            
            team.add_player(player, active=True)
        
        # Set team record
        team.wins = random.randint(6, 12)
        team.losses = 15 - team.wins
        teams.append(team)
    
    return teams

def test_multi_season_progression():
    """Test multi-season progression with stat tracking"""
    console = Console()
    
    console.print("\n[bold]Testing Multi-Season Progression System[/bold]\n")
    
    # Create teams with initial stats
    teams = create_test_teams_with_stats()
    console.print(f"[green]✓ Created {len(teams)} teams with players[/green]")
    
    # Create season simulator for Season 1
    season_sim = SeasonSimulator(teams, current_season=1)
    console.print(f"[green]✓ Created Season Simulator (Season {season_sim.current_season})[/green]")
    
    # Show initial player info
    console.print("\n[yellow]Initial Player Sample (Team 1):[/yellow]")
    sample_team = teams[0]
    for player in sample_team.get_all_players()[:3]:  # Show first 3 players
        console.print(f"  {player.name} (Age {player.age}) - BA: {player.batting_stats.avg:.3f}, ERA: {player.pitching_stats.era:.2f}")
    
    # Simulate multiple seasons
    for season in range(1, 4):  # Test seasons 1, 2, 3
        console.print(f"\n[bold cyan]{'='*50}[/bold cyan]")
        console.print(f"[bold cyan]SEASON {season}[/bold cyan]")
        console.print(f"[bold cyan]{'='*50}[/bold cyan]")
        
        # Show season info
        total_players = sum(len(team.get_all_players()) for team in teams)
        console.print(f"Active players: {total_players}")
        
        # Simulate some season activity by adding random stats to current season
        if season > 1:  # Don't override initial stats for season 1
            console.print(f"\n[yellow]Simulating Season {season} activity...[/yellow]")
            for team in teams:
                for player in team.get_all_players():
                    # Add some random season stats
                    player.batting_stats.ab += random.randint(10, 30)
                    player.batting_stats.h += random.randint(3, 15)
                    player.batting_stats.hr += random.randint(0, 3)
                    player.pitching_stats.ip += random.randint(3, 15)
                    player.pitching_stats.k += random.randint(2, 12)
        
        # Complete current season (archive stats)
        console.print(f"\n[yellow]Completing Season {season}...[/yellow]")
        season_sim.complete_season_for_all_players()
        
        # Show a player's season history
        sample_player = sample_team.get_all_players()[0]
        console.print(f"\n[cyan]{sample_player.name}'s Career:[/cyan]")
        console.print(f"  Seasons played: {sample_player.seasons_played}")
        console.print(f"  Career BA: {sample_player.career_stats.career_batting.avg:.3f}")
        console.print(f"  Career ERA: {sample_player.career_stats.career_pitching.era:.2f}")
        
        # Show season-by-season for this player
        for s in sample_player.seasons_played:
            bat, pitch, field = sample_player.career_stats.get_season_stats(s)
            console.print(f"    Season {s}: BA {bat.avg:.3f}, ERA {pitch.era:.2f}")
        
        if season < 3:  # Don't progress after the last season
            # Progress to next season
            console.print(f"\n[green]Progressing to Season {season + 1}...[/green]")
            result = season_sim.progress_to_next_season()
            
            # Show progression results
            console.print(f"New season: {result['new_season']}")
            console.print(f"Active players after progression: {result['total_active_players']}")
            
            if result['retired_players']:
                console.print(f"Retired players:")
                for retired in result['retired_players']:
                    console.print(f"  - {retired.name} (Age {retired.age})")
            else:
                console.print("No retirements this year")
            
            # Show age progression for sample players
            console.print(f"\n[yellow]Age progression (Team 1 sample):[/yellow]")
            for player in sample_team.get_all_players()[:3]:
                console.print(f"  {player.name}: Age {player.age}")
    
    # Final summary
    console.print(f"\n[bold green]{'='*50}[/bold green]")
    console.print("[bold green]MULTI-SEASON TEST COMPLETE[/bold green]")
    console.print(f"[bold green]{'='*50}[/bold green]")
    
    final_total = sum(len(team.get_all_players()) for team in teams)
    console.print(f"Final active players: {final_total}")
    
    # Show career summary for sample player
    sample_player = sample_team.get_all_players()[0]
    console.print(f"\n[cyan]Sample Career Summary:[/cyan]")
    console.print(f"{sample_player.get_career_summary()}")
    
    # Show all seasons played
    console.print(f"Seasons: {sample_player.seasons_played}")
    console.print(f"Career totals: {sample_player.career_stats.career_batting.h} hits, {sample_player.career_stats.career_pitching.k} strikeouts")

if __name__ == "__main__":
    test_multi_season_progression()