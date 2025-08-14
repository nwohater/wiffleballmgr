#!/usr/bin/env python3
"""
Quick Monte-Carlo Test for Wiffle Ball Manager

This is a lighter version of the full Monte-Carlo harness for:
- Development testing (100 seasons)
- CI validation (configurable via environment variable)
- Fast feedback on model changes
"""

import sys
import os
import json
import numpy as np
import random
from datetime import datetime
from typing import List, Dict, Tuple, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.team import Team
from models.player import Player
from simulation.season_sim import SeasonSimulator
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

# Configuration (can be overridden by environment variables)
NUM_SEASONS = int(os.environ.get('MONTE_CARLO_SEASONS', '100'))
TEAMS_PER_SEASON = 4  # Smaller for speed
PLAYERS_PER_TEAM = 6
MIN_AB_FOR_QUALIFICATION = 20  # Lower threshold for quick tests
MIN_IP_FOR_QUALIFICATION = 10
CORRELATION_THRESHOLD = 0.4    # More lenient for smaller sample
DRIFT_TOLERANCE = 0.25         # More lenient for development

class QuickMonteCarloTest:
    """Quick Monte-Carlo test for development and CI"""
    
    def __init__(self, console: Console = None):
        self.console = console or Console()
        self.results = []
    
    def create_test_player_pool(self) -> List[Player]:
        """Create a focused pool of players for testing"""
        players = []
        
        # Create three tiers of players for clear skill differentiation
        num_players = TEAMS_PER_SEASON * PLAYERS_PER_TEAM
        players_per_tier = num_players // 3
        
        for tier in range(3):
            # Tier 0: Low skills (30-50), Tier 1: Medium (50-70), Tier 2: High (70-90)
            skill_base = 30 + (tier * 20)
            skill_range = 20
            
            for i in range(players_per_tier):
                skill_level = random.randint(skill_base, skill_base + skill_range)
                variance = 10
                
                player = Player(
                    name=f"T{tier}_Player_{i:02d}",
                    age=random.randint(24, 32),
                    
                    # Batting attributes
                    power=max(20, min(90, skill_level + random.randint(-variance, variance))),
                    contact=max(20, min(90, skill_level + random.randint(-variance, variance))),
                    discipline=max(20, min(90, skill_level + random.randint(-variance, variance))),
                    
                    # Pitching attributes
                    velocity=max(20, min(90, skill_level + random.randint(-variance, variance))),
                    control=max(20, min(90, skill_level + random.randint(-variance, variance))),
                    stamina=max(20, min(90, skill_level + random.randint(-variance, variance))),
                    movement=max(20, min(90, skill_level + random.randint(-variance, variance))),
                    
                    # Fielding
                    range=max(20, min(90, skill_level + random.randint(-variance, variance))),
                    arm_strength=max(20, min(90, skill_level + random.randint(-variance, variance))),
                    hands=max(20, min(90, skill_level + random.randint(-variance, variance))),
                    accuracy=max(20, min(90, skill_level + random.randint(-variance, variance)))
                )
                players.append(player)
        
        # Fill remaining slots if any
        remaining = num_players - len(players)
        for i in range(remaining):
            skill_level = random.randint(40, 80)
            player = Player(
                name=f"Filler_{i:02d}",
                age=random.randint(24, 32),
                power=skill_level + random.randint(-15, 15),
                contact=skill_level + random.randint(-15, 15),
                discipline=skill_level + random.randint(-15, 15),
                velocity=skill_level + random.randint(-15, 15),
                control=skill_level + random.randint(-15, 15),
                stamina=skill_level + random.randint(-15, 15)
            )
            players.append(player)
        
        return players
    
    def create_balanced_teams(self, player_pool: List[Player]) -> List[Team]:
        """Create balanced teams by distributing skill levels evenly"""
        # Sort players by overall skill to enable balanced distribution
        def overall_skill(p):
            return (p.power + p.contact + p.discipline + p.velocity + p.control + p.stamina) / 6
        
        sorted_players = sorted(player_pool, key=overall_skill, reverse=True)
        
        teams = [Team(name=f"Team_{i+1}") for i in range(TEAMS_PER_SEASON)]
        
        # Snake draft: distribute players to balance teams
        for i, player in enumerate(sorted_players):
            if i // PLAYERS_PER_TEAM % 2 == 0:  # Forward direction
                team_idx = i % TEAMS_PER_SEASON
            else:  # Reverse direction
                team_idx = (TEAMS_PER_SEASON - 1) - (i % TEAMS_PER_SEASON)
            
            teams[team_idx].add_player(player, active=True)
        
        return teams
    
    def simulate_seasons(self) -> Dict[str, Any]:
        """Run the quick Monte-Carlo simulation"""
        all_batting_avgs = []
        all_home_runs = []
        all_eras = []
        all_hitting_skills = []
        all_pitching_skills = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=self.console
        ) as progress:
            
            task = progress.add_task(f"Running {NUM_SEASONS} seasons...", total=NUM_SEASONS)
            
            for season_id in range(NUM_SEASONS):
                # Create teams for this season
                player_pool = self.create_test_player_pool()
                teams = self.create_balanced_teams(player_pool)
                
                # Simulate season
                season_sim = SeasonSimulator(teams, games_per_season=12, innings_per_game=3)
                season_sim.play_season()
                
                # Collect stats
                for team in teams:
                    for player in team.get_all_players():
                        # Batting stats
                        if player.batting_stats.ab >= MIN_AB_FOR_QUALIFICATION:
                            all_batting_avgs.append(player.batting_stats.avg)
                            all_home_runs.append(player.batting_stats.hr)
                            hitting_skill = (player.power + player.contact + player.discipline) / 3
                            all_hitting_skills.append(hitting_skill)
                        
                        # Pitching stats  
                        if player.pitching_stats.ip >= MIN_IP_FOR_QUALIFICATION:
                            all_eras.append(player.pitching_stats.era)
                            pitching_skill = (player.velocity + player.control + player.stamina + player.movement) / 4
                            all_pitching_skills.append(pitching_skill)
                
                progress.advance(task)
        
        return {
            'batting_avgs': all_batting_avgs,
            'home_runs': all_home_runs,
            'eras': all_eras,
            'hitting_skills': all_hitting_skills,
            'pitching_skills': all_pitching_skills
        }
    
    def analyze_correlation(self, values: List[float], skills: List[float], stat_name: str) -> Dict[str, Any]:
        """Analyze correlation between skills and performance"""
        if len(values) == 0 or len(skills) == 0:
            return {
                'stat_name': stat_name,
                'sample_size': 0,
                'correlation': 0.0,
                'r_squared': 0.0,
                'passes_test': False,
                'error': 'No data available'
            }
        
        values_array = np.array(values)
        skills_array = np.array(skills)
        
        # Calculate correlation
        correlation = np.corrcoef(skills_array, values_array)[0, 1]
        r_squared = correlation ** 2
        
        # For ERA, we expect negative correlation (higher skill = lower ERA)
        if stat_name == 'era':
            correlation = -correlation
            r_squared = correlation ** 2
        
        passes_test = r_squared >= CORRELATION_THRESHOLD
        
        return {
            'stat_name': stat_name,
            'sample_size': len(values),
            'mean': np.mean(values_array),
            'std': np.std(values_array),
            'correlation': correlation,
            'r_squared': r_squared,
            'passes_test': passes_test,
            'skill_range': [np.min(skills_array), np.max(skills_array)]
        }
    
    def run_test(self) -> Tuple[bool, Dict[str, Any]]:
        """Run the complete quick test"""
        self.console.print(f"\n[bold blue]🚀 Quick Monte-Carlo Test ({NUM_SEASONS} seasons)[/bold blue]")
        self.console.print(f"Configuration: {TEAMS_PER_SEASON} teams, {PLAYERS_PER_TEAM} players/team")
        self.console.print(f"Thresholds: r² ≥ {CORRELATION_THRESHOLD}, drift ≤ {DRIFT_TOLERANCE:.1%}\n")
        
        # Run simulation
        data = self.simulate_seasons()
        
        self.console.print("[cyan]Analyzing correlations...[/cyan]")
        
        # Analyze each statistic
        analyses = {
            'batting_avg': self.analyze_correlation(
                data['batting_avgs'], data['hitting_skills'], 'batting_avg'
            ),
            'home_runs': self.analyze_correlation(
                data['home_runs'], data['hitting_skills'], 'home_runs'  
            ),
            'era': self.analyze_correlation(
                data['eras'], data['pitching_skills'], 'era'
            )
        }
        
        # Print results
        self.console.print("\n[bold green]📊 RESULTS[/bold green]")
        self.console.print("=" * 60)
        
        all_passed = True
        for stat_name, analysis in analyses.items():
            if analysis.get('error'):
                self.console.print(f"[red]❌ {stat_name}: {analysis['error']}[/red]")
                all_passed = False
                continue
            
            status = "✅ PASS" if analysis['passes_test'] else "❌ FAIL"
            color = "green" if analysis['passes_test'] else "red"
            
            self.console.print(f"[{color}]{status}[/{color}] {stat_name.upper()}")
            self.console.print(f"  Sample size: {analysis['sample_size']:,}")
            self.console.print(f"  Distribution: μ={analysis['mean']:.3f}, σ={analysis['std']:.3f}")
            self.console.print(f"  Correlation: r={analysis['correlation']:.3f}, r²={analysis['r_squared']:.3f}")
            self.console.print(f"  Skill range: [{analysis['skill_range'][0]:.0f}, {analysis['skill_range'][1]:.0f}]")
            
            if not analysis['passes_test']:
                all_passed = False
            
            self.console.print()
        
        return all_passed, analyses


def main():
    """Main entry point"""
    console = Console()
    
    # Check if we're in CI mode
    is_ci = os.environ.get('CI', '').lower() in ['true', '1', 'yes']
    if is_ci:
        console.print("[yellow]🔧 Running in CI mode[/yellow]")
    
    test = QuickMonteCarloTest(console)
    
    try:
        passed, results = test.run_test()
        
        if passed:
            console.print("[bold green]✅ ALL TESTS PASSED[/bold green]")
            console.print("[green]Skill-stat correlations are within acceptable bounds.[/green]")
            return 0
        else:
            console.print("[bold red]❌ SOME TESTS FAILED[/bold red]")
            console.print("[red]Model validation detected issues with skill-stat correlations.[/red]")
            
            if is_ci:
                console.print("[red]CI failure: Please review simulation parameters.[/red]")
            
            return 1
    
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Test interrupted by user[/yellow]")
        return 2
    except Exception as e:
        console.print(f"\n[red]❌ Test failed with error: {e}[/red]")
        if not is_ci:  # Only show traceback in non-CI mode
            import traceback
            traceback.print_exc()
        return 3


if __name__ == "__main__":
    sys.exit(main())
