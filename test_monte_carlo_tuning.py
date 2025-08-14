#!/usr/bin/env python3
"""
Monte-Carlo Tuning Harness for Wiffle Ball Manager

This test simulates 10,000 seasons to:
1. Export distributions of key statistics (BA, HR, ERA)
2. Ensure realistic statistical outputs
3. Verify that higher skills correlate with better stats (r²>0.6)
4. Fail CI if model drifts beyond acceptable bounds
"""

import sys
import os
import json
import numpy as np
import random
from datetime import datetime
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
from scipy import stats
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.team import Team
from models.player import Player, BattingStats, PitchingStats
from simulation.season_sim import SeasonSimulator
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

# Configuration constants
NUM_SEASONS = 10000
TEAMS_PER_SEASON = 6
PLAYERS_PER_TEAM = 6
MIN_AB_FOR_QUALIFICATION = 30  # Minimum at-bats to qualify for BA analysis
MIN_IP_FOR_QUALIFICATION = 15  # Minimum innings pitched for ERA analysis
CORRELATION_THRESHOLD = 0.6    # Minimum r² for skill-stat correlation
DRIFT_TOLERANCE = 0.15         # Maximum drift from baseline (15%)

# Statistical expectations (based on MLB-like distributions scaled for wiffle ball)
EXPECTED_STATS = {
    'batting_avg': {'mean': 0.250, 'std': 0.080, 'min': 0.000, 'max': 1.000},
    'home_runs': {'mean': 2.5, 'std': 3.0, 'min': 0, 'max': 15},
    'era': {'mean': 4.50, 'std': 2.50, 'min': 0.00, 'max': 20.00},
    'whip': {'mean': 1.50, 'std': 0.50, 'min': 0.00, 'max': 5.00},
    'strikeouts': {'mean': 15, 'std': 10, 'min': 0, 'max': 50}
}

@dataclass
class StatisticalResults:
    """Container for statistical analysis results"""
    stat_name: str
    distribution: List[float]
    mean: float
    std: float
    min_val: float
    max_val: float
    percentiles: Dict[int, float]
    correlation_with_skill: float
    correlation_r_squared: float
    passes_correlation_test: bool
    passes_distribution_test: bool
    drift_from_baseline: float

@dataclass
class SeasonResult:
    """Container for a single season's aggregated results"""
    season_id: int
    qualified_hitters: List[Dict[str, Any]]
    qualified_pitchers: List[Dict[str, Any]]
    team_records: List[Dict[str, Any]]

class MonteCarloTuningHarness:
    """Monte-Carlo simulation harness for statistical validation"""
    
    def __init__(self, console: Console = None):
        self.console = console or Console()
        self.results: List[SeasonResult] = []
        self.baseline_stats: Dict[str, Any] = {}
        self.output_dir = Path("monte_carlo_results")
        self.output_dir.mkdir(exist_ok=True)
        
        # Load baseline if it exists
        self._load_baseline()
    
    def _load_baseline(self):
        """Load baseline statistics from previous runs"""
        baseline_file = self.output_dir / "baseline_stats.json"
        if baseline_file.exists():
            with open(baseline_file, 'r') as f:
                self.baseline_stats = json.load(f)
            self.console.print("[green]✓ Loaded baseline statistics[/green]")
        else:
            self.console.print("[yellow]⚠ No baseline found - will create new baseline[/yellow]")
    
    def _save_baseline(self, stats: Dict[str, Any]):
        """Save current run as new baseline"""
        baseline_file = self.output_dir / "baseline_stats.json"
        with open(baseline_file, 'w') as f:
            json.dump(stats, f, indent=2)
        self.console.print(f"[green]✓ Saved new baseline to {baseline_file}[/green]")
    
    def create_diverse_player_pool(self) -> List[Player]:
        """Create a diverse pool of players with varied skill levels"""
        players = []
        
        # Create skill distribution that covers full range (20-90)
        for i in range(TEAMS_PER_SEASON * PLAYERS_PER_TEAM):
            # Generate correlated skills with some randomness
            base_skill = random.randint(20, 90)
            skill_variance = 15
            
            player = Player(
                name=f"Player_{i:03d}",
                age=random.randint(22, 35),  # Varied ages
                
                # Batting skills (correlated but with variance)
                power=max(20, min(90, base_skill + random.randint(-skill_variance, skill_variance))),
                contact=max(20, min(90, base_skill + random.randint(-skill_variance, skill_variance))),
                discipline=max(20, min(90, base_skill + random.randint(-skill_variance, skill_variance))),
                speed=max(20, min(90, base_skill + random.randint(-skill_variance, skill_variance))),
                
                # Pitching skills (correlated but with variance)
                velocity=max(20, min(90, base_skill + random.randint(-skill_variance, skill_variance))),
                movement=max(20, min(90, base_skill + random.randint(-skill_variance, skill_variance))),
                control=max(20, min(90, base_skill + random.randint(-skill_variance, skill_variance))),
                stamina=max(20, min(90, base_skill + random.randint(-skill_variance, skill_variance))),
                deception=max(20, min(90, base_skill + random.randint(-skill_variance, skill_variance))),
                
                # Fielding skills
                range=max(20, min(90, base_skill + random.randint(-skill_variance, skill_variance))),
                arm_strength=max(20, min(90, base_skill + random.randint(-skill_variance, skill_variance))),
                hands=max(20, min(90, base_skill + random.randint(-skill_variance, skill_variance))),
                reaction=max(20, min(90, base_skill + random.randint(-skill_variance, skill_variance))),
                accuracy=max(20, min(90, base_skill + random.randint(-skill_variance, skill_variance)))
            )
            players.append(player)
        
        return players
    
    def create_teams_from_pool(self, player_pool: List[Player]) -> List[Team]:
        """Create teams by distributing players from the pool"""
        teams = []
        players_per_team = len(player_pool) // TEAMS_PER_SEASON
        
        for i in range(TEAMS_PER_SEASON):
            team = Team(name=f"Team_{i+1}")
            start_idx = i * players_per_team
            end_idx = start_idx + players_per_team
            
            # Assign players to team
            team_players = player_pool[start_idx:end_idx]
            for player in team_players:
                team.add_player(player, active=True)
            
            teams.append(team)
        
        return teams
    
    def simulate_season(self, season_id: int) -> SeasonResult:
        """Simulate a single season and collect statistics"""
        # Create fresh player pool for this season
        player_pool = self.create_diverse_player_pool()
        teams = self.create_teams_from_pool(player_pool)
        
        # Run season simulation
        season_sim = SeasonSimulator(teams, games_per_season=15, innings_per_game=3)
        season_sim.play_season()
        
        # Collect qualified hitters
        qualified_hitters = []
        for team in teams:
            for player in team.get_all_players():
                if player.batting_stats.ab >= MIN_AB_FOR_QUALIFICATION:
                    qualified_hitters.append({
                        'name': player.name,
                        'team': team.name,
                        'batting_avg': player.batting_stats.avg,
                        'home_runs': player.batting_stats.hr,
                        'hits': player.batting_stats.h,
                        'at_bats': player.batting_stats.ab,
                        'rbi': player.batting_stats.rbi,
                        'walks': player.batting_stats.bb,
                        'strikeouts': player.batting_stats.k,
                        # Include skills for correlation analysis
                        'power_skill': player.power,
                        'contact_skill': player.contact,
                        'discipline_skill': player.discipline,
                        'overall_hitting_skill': (player.power + player.contact + player.discipline) / 3
                    })
        
        # Collect qualified pitchers
        qualified_pitchers = []
        for team in teams:
            for player in team.get_all_players():
                if player.pitching_stats.ip >= MIN_IP_FOR_QUALIFICATION:
                    qualified_pitchers.append({
                        'name': player.name,
                        'team': team.name,
                        'era': player.pitching_stats.era,
                        'whip': player.pitching_stats.whip,
                        'strikeouts': player.pitching_stats.k,
                        'walks': player.pitching_stats.bb,
                        'innings_pitched': player.pitching_stats.ip,
                        'wins': player.pitching_stats.w,
                        'losses': player.pitching_stats.l,
                        # Include skills for correlation analysis
                        'velocity_skill': player.velocity,
                        'control_skill': player.control,
                        'movement_skill': player.movement,
                        'stamina_skill': player.stamina,
                        'overall_pitching_skill': (player.velocity + player.control + player.movement + player.stamina) / 4
                    })
        
        # Collect team records
        team_records = []
        for team in teams:
            team_records.append({
                'name': team.name,
                'wins': team.wins,
                'losses': team.losses,
                'runs_scored': team.runs_scored,
                'runs_allowed': team.runs_allowed
            })
        
        return SeasonResult(
            season_id=season_id,
            qualified_hitters=qualified_hitters,
            qualified_pitchers=qualified_pitchers,
            team_records=team_records
        )
    
    def analyze_statistic(self, values: List[float], skills: List[float], stat_name: str) -> StatisticalResults:
        """Analyze a single statistic and its correlation with skills"""
        values_array = np.array(values)
        skills_array = np.array(skills)
        
        # Basic statistics
        mean_val = np.mean(values_array)
        std_val = np.std(values_array)
        min_val = np.min(values_array)
        max_val = np.max(values_array)
        
        # Percentiles
        percentiles = {
            10: np.percentile(values_array, 10),
            25: np.percentile(values_array, 25),
            50: np.percentile(values_array, 50),
            75: np.percentile(values_array, 75),
            90: np.percentile(values_array, 90)
        }
        
        # Correlation analysis
        correlation_coeff = np.corrcoef(skills_array, values_array)[0, 1]
        r_squared = correlation_coeff ** 2
        
        # Test passes
        passes_correlation = r_squared >= CORRELATION_THRESHOLD
        
        # Distribution test (check if within expected bounds)
        expected = EXPECTED_STATS.get(stat_name, {})
        passes_distribution = True
        if expected:
            expected_mean = expected.get('mean', mean_val)
            expected_std = expected.get('std', std_val)
            # Allow some tolerance in distribution matching
            if abs(mean_val - expected_mean) > expected_mean * 0.3:  # 30% tolerance
                passes_distribution = False
            if abs(std_val - expected_std) > expected_std * 0.5:    # 50% tolerance
                passes_distribution = False
        
        # Calculate drift from baseline
        drift = 0.0
        if self.baseline_stats and stat_name in self.baseline_stats:
            baseline_mean = self.baseline_stats[stat_name].get('mean', mean_val)
            if baseline_mean != 0:
                drift = abs(mean_val - baseline_mean) / baseline_mean
        
        return StatisticalResults(
            stat_name=stat_name,
            distribution=values,
            mean=mean_val,
            std=std_val,
            min_val=min_val,
            max_val=max_val,
            percentiles=percentiles,
            correlation_with_skill=correlation_coeff,
            correlation_r_squared=r_squared,
            passes_correlation_test=passes_correlation,
            passes_distribution_test=passes_distribution,
            drift_from_baseline=drift
        )
    
    def run_monte_carlo_simulation(self) -> Dict[str, StatisticalResults]:
        """Run the full Monte-Carlo simulation"""
        self.console.print(f"\n[bold blue]🎲 Starting Monte-Carlo Simulation ({NUM_SEASONS:,} seasons)[/bold blue]\n")
        
        all_results = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            
            task = progress.add_task("Simulating seasons...", total=NUM_SEASONS)
            
            for season_id in range(NUM_SEASONS):
                # Simulate season
                season_result = self.simulate_season(season_id)
                self.results.append(season_result)
                
                # Update progress
                if season_id % 100 == 0:
                    progress.update(task, advance=100, description=f"Simulated {season_id:,} seasons...")
                elif season_id == NUM_SEASONS - 1:
                    progress.update(task, advance=NUM_SEASONS % 100, description=f"Completed {NUM_SEASONS:,} seasons!")
        
        self.console.print(f"\n[green]✓ Completed {NUM_SEASONS:,} season simulations[/green]")
        self.console.print(f"[cyan]📊 Analyzing statistical distributions...[/cyan]\n")
        
        # Aggregate all data for analysis
        all_batting_avgs = []
        all_home_runs = []
        all_eras = []
        all_whips = []
        all_strikeouts = []
        
        all_hitting_skills = []
        all_pitching_skills = []
        
        for result in self.results:
            for hitter in result.qualified_hitters:
                all_batting_avgs.append(hitter['batting_avg'])
                all_home_runs.append(hitter['home_runs'])
                all_hitting_skills.append(hitter['overall_hitting_skill'])
            
            for pitcher in result.qualified_pitchers:
                all_eras.append(pitcher['era'])
                all_whips.append(pitcher['whip'])
                all_strikeouts.append(pitcher['strikeouts'])
                all_pitching_skills.append(pitcher['overall_pitching_skill'])
        
        # Analyze each statistic
        analyses = {
            'batting_avg': self.analyze_statistic(all_batting_avgs, all_hitting_skills, 'batting_avg'),
            'home_runs': self.analyze_statistic(all_home_runs, all_hitting_skills, 'home_runs'),
            'era': self.analyze_statistic(all_eras, all_pitching_skills, 'era'),
            'whip': self.analyze_statistic(all_whips, all_pitching_skills, 'whip'),
            'strikeouts': self.analyze_statistic(all_strikeouts, all_pitching_skills, 'strikeouts')
        }
        
        return analyses
    
    def export_results(self, analyses: Dict[str, StatisticalResults]):
        """Export detailed results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export statistical summary
        summary = {
            'timestamp': timestamp,
            'num_seasons': NUM_SEASONS,
            'total_qualified_hitters': sum(len(r.qualified_hitters) for r in self.results),
            'total_qualified_pitchers': sum(len(r.qualified_pitchers) for r in self.results),
            'statistics': {}
        }
        
        for stat_name, analysis in analyses.items():
            summary['statistics'][stat_name] = {
                'mean': analysis.mean,
                'std': analysis.std,
                'min': analysis.min_val,
                'max': analysis.max_val,
                'percentiles': analysis.percentiles,
                'correlation_with_skill': analysis.correlation_with_skill,
                'r_squared': analysis.correlation_r_squared,
                'passes_correlation_test': analysis.passes_correlation_test,
                'passes_distribution_test': analysis.passes_distribution_test,
                'drift_from_baseline': analysis.drift_from_baseline
            }
        
        # Save summary
        summary_file = self.output_dir / f"monte_carlo_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Export distributions as CSV
        import csv
        
        for stat_name, analysis in analyses.items():
            csv_file = self.output_dir / f"distribution_{stat_name}_{timestamp}.csv"
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['value'])
                for value in analysis.distribution:
                    writer.writerow([value])
        
        # If this is the first run or significantly better, save as baseline
        if not self.baseline_stats or self._should_update_baseline(analyses):
            self._save_baseline(summary['statistics'])
        
        self.console.print(f"[green]✓ Results exported to {self.output_dir}[/green]")
        return summary_file
    
    def _should_update_baseline(self, analyses: Dict[str, StatisticalResults]) -> bool:
        """Determine if we should update the baseline with current results"""
        if not self.baseline_stats:
            return True
        
        # Update baseline if correlation tests improve significantly
        current_avg_r2 = np.mean([a.correlation_r_squared for a in analyses.values()])
        baseline_r2_values = [self.baseline_stats[stat].get('r_squared', 0) 
                             for stat in analyses.keys() if stat in self.baseline_stats]
        
        if baseline_r2_values:
            baseline_avg_r2 = np.mean(baseline_r2_values)
            return current_avg_r2 > baseline_avg_r2 + 0.05  # 5% improvement threshold
        
        return True
    
    def print_results(self, analyses: Dict[str, StatisticalResults]):
        """Print detailed results to console"""
        self.console.print("\n[bold green]📈 MONTE-CARLO SIMULATION RESULTS[/bold green]")
        self.console.print("=" * 80)
        
        # Overall summary
        total_hitters = sum(len(r.qualified_hitters) for r in self.results)
        total_pitchers = sum(len(r.qualified_pitchers) for r in self.results)
        
        self.console.print(f"[cyan]Seasons simulated:[/cyan] {NUM_SEASONS:,}")
        self.console.print(f"[cyan]Qualified hitters analyzed:[/cyan] {total_hitters:,}")
        self.console.print(f"[cyan]Qualified pitchers analyzed:[/cyan] {total_pitchers:,}")
        self.console.print()
        
        # Statistical results for each metric
        for stat_name, analysis in analyses.items():
            self.console.print(f"[bold yellow]{stat_name.upper().replace('_', ' ')}[/bold yellow]")
            self.console.print(f"  Distribution: μ={analysis.mean:.3f}, σ={analysis.std:.3f}")
            self.console.print(f"  Range: [{analysis.min_val:.3f}, {analysis.max_val:.3f}]")
            self.console.print(f"  Percentiles: 10%={analysis.percentiles[10]:.3f}, 50%={analysis.percentiles[50]:.3f}, 90%={analysis.percentiles[90]:.3f}")
            self.console.print(f"  Correlation with skill: r={analysis.correlation_with_skill:.3f}, r²={analysis.correlation_r_squared:.3f}")
            
            # Test results
            correlation_status = "✓ PASS" if analysis.passes_correlation_test else "✗ FAIL"
            distribution_status = "✓ PASS" if analysis.passes_distribution_test else "✗ FAIL"
            
            correlation_color = "green" if analysis.passes_correlation_test else "red"
            distribution_color = "green" if analysis.passes_distribution_test else "red"
            
            self.console.print(f"  Correlation test (r²≥{CORRELATION_THRESHOLD}): [{correlation_color}]{correlation_status}[/{correlation_color}]")
            self.console.print(f"  Distribution test: [{distribution_color}]{distribution_status}[/{distribution_color}]")
            
            if analysis.drift_from_baseline > 0:
                drift_color = "red" if analysis.drift_from_baseline > DRIFT_TOLERANCE else "yellow"
                self.console.print(f"  Drift from baseline: [{drift_color}]{analysis.drift_from_baseline:.1%}[/{drift_color}]")
            
            self.console.print()
    
    def check_ci_failure_conditions(self, analyses: Dict[str, StatisticalResults]) -> Tuple[bool, List[str]]:
        """Check if conditions warrant CI failure"""
        failures = []
        
        # Check correlation thresholds
        for stat_name, analysis in analyses.items():
            if not analysis.passes_correlation_test:
                failures.append(f"{stat_name}: r²={analysis.correlation_r_squared:.3f} < {CORRELATION_THRESHOLD}")
        
        # Check drift from baseline
        for stat_name, analysis in analyses.items():
            if analysis.drift_from_baseline > DRIFT_TOLERANCE:
                failures.append(f"{stat_name}: drift={analysis.drift_from_baseline:.1%} > {DRIFT_TOLERANCE:.1%}")
        
        # Check for extreme distribution problems
        for stat_name, analysis in analyses.items():
            if stat_name in EXPECTED_STATS:
                expected = EXPECTED_STATS[stat_name]
                # Flag if mean is way outside expected bounds
                if analysis.mean < expected['min'] or analysis.mean > expected['max']:
                    failures.append(f"{stat_name}: mean={analysis.mean:.3f} outside expected range [{expected['min']}, {expected['max']}]")
        
        return len(failures) > 0, failures


def main():
    """Main entry point for Monte-Carlo tuning harness"""
    console = Console()
    
    console.print("[bold blue]🎲 Wiffle Ball Manager - Monte-Carlo Tuning Harness[/bold blue]")
    console.print("=" * 80)
    console.print(f"Configuration:")
    console.print(f"  • Seasons to simulate: {NUM_SEASONS:,}")
    console.print(f"  • Teams per season: {TEAMS_PER_SEASON}")
    console.print(f"  • Players per team: {PLAYERS_PER_TEAM}")
    console.print(f"  • Correlation threshold: r² ≥ {CORRELATION_THRESHOLD}")
    console.print(f"  • Drift tolerance: ≤ {DRIFT_TOLERANCE:.1%}")
    console.print()
    
    # Initialize and run simulation
    harness = MonteCarloTuningHarness(console)
    
    try:
        # Run the simulation
        analyses = harness.run_monte_carlo_simulation()
        
        # Export results
        summary_file = harness.export_results(analyses)
        
        # Print results
        harness.print_results(analyses)
        
        # Check for CI failure conditions
        should_fail_ci, failure_reasons = harness.check_ci_failure_conditions(analyses)
        
        if should_fail_ci:
            console.print("\n[bold red]❌ CI FAILURE CONDITIONS MET[/bold red]")
            console.print("[red]The following issues were detected:[/red]")
            for reason in failure_reasons:
                console.print(f"  • [red]{reason}[/red]")
            console.print(f"\n[red]Model validation failed. Please review and tune the simulation parameters.[/red]")
            return 1
        else:
            console.print("\n[bold green]✅ ALL VALIDATION TESTS PASSED[/bold green]")
            console.print("[green]Model performance is within acceptable bounds.[/green]")
            console.print(f"[green]Results saved to: {summary_file}[/green]")
            return 0
    
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Simulation interrupted by user[/yellow]")
        return 2
    except Exception as e:
        console.print(f"\n[red]❌ Simulation failed with error: {e}[/red]")
        import traceback
        traceback.print_exc()
        return 3


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
