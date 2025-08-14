# Skill Model Parameterization Summary

## Overview
Successfully moved hardcoded game balance values to external YAML configuration at `data/config/skill_model.yml`.

## What Was Parameterized

### Probability Calculations
- **Base factors**: Strikeout, walk, hit, and home run probability factors
- **Attribute weights**: How much each player attribute affects calculations
- **Base adjustments**: Baseline probability shifts before sigmoid calculations
- **Situational modifiers**: Clutch, fatigue, and weather effects

### Hit Type Distribution  
- **Weights**: Relative frequency of singles, doubles, triples, home runs
- **Power thresholds**: Rating needed for home run and extra base hit bonuses
- **Scaling factors**: How much power affects hit type distribution

### Player Development
- **Age curves**: Peak age, decline start, retirement age
- **Event probabilities**: Chances for positive and negative development events

### Fatigue System
- **Accumulation rate**: How much fatigue builds per inning pitched
- **Recovery rate**: How much fatigue recovers per day of rest

### Additional Balance Parameters
- **Hit-by-pitch rate**: Base probability of HBP
- **Fielding checks**: Chances for fielding plays on different ball types
- **Error rates**: Probability of fielding errors
- **Experience thresholds**: Games/stats needed for development bonuses

## Files Modified

### New Files
- `data/config/skill_model.yml` - Main configuration file
- `src/utils/config_loader.py` - YAML configuration loader
- `data/config/README.md` - Documentation for designers

### Modified Files
- `src/simulation/probability.py` - Uses YAML config instead of constants
- `src/simulation/player_dev.py` - Uses YAML config for aging and events
- `src/simulation/game_sim.py` - Uses YAML config for fatigue calculations
- `src/utils/constants.py` - Removed hardcoded probability constants

## Benefits for Designers

1. **No Code Changes Required**: All balance tweaks can be made by editing YAML
2. **Immediate Effect**: Changes take effect without restarting the game
3. **Clear Documentation**: Each parameter is documented with purpose and defaults
4. **Easy Backup**: Simple to save/restore configuration states
5. **Version Control Friendly**: YAML files work well with git diff/merge

## Usage Instructions

1. Edit `data/config/skill_model.yml` with any text editor
2. Refer to `data/config/README.md` for parameter descriptions
3. Test changes with existing scripts to verify balance
4. Keep backups of working configurations

## Technical Implementation

- Uses PyYAML for safe configuration loading
- Singleton pattern ensures config is loaded once and reused
- Graceful fallbacks to default values if config is missing
- Type hints and clear property accessors for all parameters

This parameterization allows designers to rapidly iterate on game balance without requiring programmer intervention for common tuning tasks.
