# Monte-Carlo Tuning Harness

This document describes the Monte-Carlo testing system for Wiffle Ball Manager, designed to validate the statistical realism and consistency of the simulation engine.

## Overview

The Monte-Carlo tuning harness simulates thousands of seasons to:

1. **Export statistical distributions** of key metrics (BA, HR, ERA, WHIP, etc.)
2. **Ensure realistic outputs** that match expected baseball-like statistics
3. **Validate skill-stat correlations** with r² ≥ 0.6 threshold
4. **Detect model drift** and fail CI if parameters drift beyond acceptable bounds
5. **Provide continuous validation** through automated CI testing

## Test Files

### `test_monte_carlo_tuning.py` - Full Validation Suite

The comprehensive Monte-Carlo harness that simulates 10,000 seasons by default.

**Features:**
- Comprehensive statistical analysis with percentile distributions
- Baseline comparison and drift detection
- Exportable results (JSON summaries + CSV distributions)
- Configurable thresholds and parameters
- Detailed correlation analysis

**Usage:**
```bash
# Run full validation (takes ~30-60 minutes)
python test_monte_carlo_tuning.py

# Results saved to monte_carlo_results/ directory
```

**Configuration Constants:**
```python
NUM_SEASONS = 10000            # Number of seasons to simulate
CORRELATION_THRESHOLD = 0.6    # Minimum r² for skill-stat correlation
DRIFT_TOLERANCE = 0.15         # Maximum drift from baseline (15%)
```

### `test_monte_carlo_quick.py` - Development & CI Testing

A lightweight version for rapid development feedback and CI validation.

**Features:**
- Fast execution (100-500 seasons, ~1-5 minutes)
- Environment variable configuration
- CI-friendly output and error handling
- Focused on core correlation validation

**Usage:**
```bash
# Quick development test
python test_monte_carlo_quick.py

# CI configuration via environment variables
MONTE_CARLO_SEASONS=500 python test_monte_carlo_quick.py
```

**Environment Variables:**
- `MONTE_CARLO_SEASONS`: Number of seasons (default: 100)
- `CI`: Set to 'true' for CI mode (suppresses verbose output)

## Statistical Validation Criteria

### 1. Skill-Stat Correlations

The system validates that player skills correlate with performance statistics:

| Statistic | Skill Correlation | Expected r² |
|-----------|------------------|-------------|
| Batting Average | Hitting Skills (Power + Contact + Discipline) | ≥ 0.6 |
| Home Runs | Power + Contact | ≥ 0.6 |
| ERA | Pitching Skills (Velocity + Control + Movement + Stamina) | ≥ 0.6 (negative) |
| WHIP | Control + Movement | ≥ 0.6 (negative) |
| Strikeouts | Velocity + Movement | ≥ 0.6 |

### 2. Statistical Distributions

Expected ranges for key statistics (scaled for wiffle ball):

```python
EXPECTED_STATS = {
    'batting_avg': {'mean': 0.250, 'std': 0.080, 'min': 0.000, 'max': 1.000},
    'home_runs': {'mean': 2.5, 'std': 3.0, 'min': 0, 'max': 15},
    'era': {'mean': 4.50, 'std': 2.50, 'min': 0.00, 'max': 20.00},
    'whip': {'mean': 1.50, 'std': 0.50, 'min': 0.00, 'max': 5.00},
    'strikeouts': {'mean': 15, 'std': 10, 'min': 0, 'max': 50}
}
```

### 3. Model Drift Detection

The system tracks drift from established baselines:
- **Acceptable drift**: ≤ 15% change in statistical means
- **CI failure**: > 15% drift triggers build failure
- **Baseline updates**: Automatically when correlations improve by >5%

## CI Integration

### GitHub Actions Workflow

The system includes a comprehensive CI workflow (`.github/workflows/monte-carlo-validation.yml`):

#### 1. Quick Validation (All PRs/Pushes)
- Runs on every push to main/develop branches
- Executes 200-season quick test
- Timeout: 15 minutes
- Uploads failure artifacts

#### 2. Full Validation (Nightly)
- Scheduled nightly at 2 AM UTC
- Runs 2,000+ season comprehensive test
- Timeout: 2 hours
- Creates GitHub issues on failure
- Archives results for 30 days

#### 3. Performance Benchmark (PRs only)
- Quick performance validation on pull requests
- Comments benchmark results on PR
- Helps detect performance regressions

### Failure Conditions

CI will fail if any of the following occur:

1. **Correlation failures**: r² < threshold for any statistic
2. **Drift detection**: >15% drift from baseline means
3. **Distribution failures**: Statistics outside expected bounds
4. **Simulation errors**: Runtime exceptions or crashes

### Interpreting Results

#### Successful Run Example:
```
📈 MONTE-CARLO SIMULATION RESULTS
================================================================================
Seasons simulated: 10,000
Qualified hitters analyzed: 89,543
Qualified pitchers analyzed: 67,221

BATTING AVERAGE
  Distribution: μ=0.247, σ=0.083
  Range: [0.000, 0.875]
  Percentiles: 10%=0.143, 50%=0.244, 90%=0.357
  Correlation with skill: r=0.782, r²=0.611
  Correlation test (r²≥0.6): ✓ PASS
  Distribution test: ✓ PASS

✅ ALL VALIDATION TESTS PASSED
```

#### Failure Example:
```
❌ CI FAILURE CONDITIONS MET
The following issues were detected:
  • batting_avg: r²=0.543 < 0.6
  • era: drift=18.7% > 15.0%
  
Model validation failed. Please review and tune the simulation parameters.
```

## Output Files

The system generates several output files in `monte_carlo_results/`:

### JSON Summary
```
monte_carlo_summary_YYYYMMDD_HHMMSS.json
```
Contains complete statistical analysis including:
- Distribution statistics (mean, std, percentiles)
- Correlation coefficients and r² values
- Test pass/fail status
- Drift measurements

### CSV Distributions
```
distribution_batting_avg_YYYYMMDD_HHMMSS.csv
distribution_home_runs_YYYYMMDD_HHMMSS.csv
distribution_era_YYYYMMDD_HHMMSS.csv
...
```
Raw distribution data for external analysis and visualization.

### Baseline File
```
baseline_stats.json
```
Current baseline statistics for drift detection.

## Development Workflow

### Making Changes to Simulation Logic

1. **Run quick test locally**:
   ```bash
   python test_monte_carlo_quick.py
   ```

2. **Check correlation impact**:
   - Ensure r² values remain above thresholds
   - Validate distribution changes are intentional

3. **Create PR**:
   - CI will run quick validation automatically
   - Review performance benchmark results

4. **Monitor nightly runs**:
   - Full validation runs nightly on main branch
   - GitHub issues created automatically on failures

### Tuning Statistical Parameters

If validation consistently fails, consider:

1. **Adjusting thresholds**:
   ```python
   CORRELATION_THRESHOLD = 0.5  # Reduce if needed
   DRIFT_TOLERANCE = 0.20       # Increase if needed
   ```

2. **Updating expected distributions**:
   ```python
   EXPECTED_STATS['batting_avg']['mean'] = 0.260  # Adjust based on analysis
   ```

3. **Reviewing simulation logic**:
   - Check player skill → performance conversion formulas
   - Validate probability calculations
   - Review game simulation mechanics

### Adding New Statistics

To add validation for new statistics:

1. **Collect the statistic** in `simulate_season()`:
   ```python
   qualified_hitters.append({
       # ... existing fields ...
       'new_stat': player.batting_stats.new_stat,
   })
   ```

2. **Add expected distribution**:
   ```python
   EXPECTED_STATS['new_stat'] = {
       'mean': 10.0, 'std': 5.0, 'min': 0, 'max': 50
   }
   ```

3. **Include in analysis**:
   ```python
   analyses['new_stat'] = self.analyze_statistic(
       all_new_stats, all_skills, 'new_stat'
   )
   ```

## Troubleshooting

### Common Issues

1. **Low correlations (r² < 0.6)**:
   - Check skill → performance conversion logic
   - Increase sample size (more seasons)
   - Review player generation diversity

2. **Distribution drift**:
   - Verify no unintended changes to game mechanics
   - Check if skill ranges have changed
   - Review probability calculations

3. **Performance issues**:
   - Reduce number of seasons for development
   - Use quick test for iterative development
   - Profile simulation bottlenecks

### Debugging Tips

1. **Enable verbose output**:
   ```python
   console = Console()
   console.print(f"Debug info: {analysis}")
   ```

2. **Export intermediate results**:
   ```python
   with open('debug_data.json', 'w') as f:
       json.dump(season_data, f, indent=2)
   ```

3. **Manual correlation checks**:
   ```python
   import matplotlib.pyplot as plt
   plt.scatter(skills, stats)
   plt.xlabel('Skill Level')
   plt.ylabel('Performance')
   plt.show()
   ```

## Best Practices

1. **Run quick tests frequently** during development
2. **Monitor nightly CI results** for drift detection
3. **Document statistical changes** in commit messages
4. **Update baselines intentionally** when improving the model
5. **Use environment variables** for CI configuration
6. **Archive results** for long-term trend analysis

## Future Enhancements

Potential improvements to the Monte-Carlo system:

1. **Advanced analytics**: More sophisticated statistical tests
2. **Visualization**: Automatic generation of distribution plots
3. **Historical tracking**: Long-term drift trend analysis
4. **A/B testing**: Compare different simulation parameters
5. **Player archetypes**: Validate specific player type behaviors
6. **League balance**: Team strength distribution analysis

---

For questions or issues with the Monte-Carlo system, refer to the test files or create a GitHub issue with relevant test results and failure logs.
