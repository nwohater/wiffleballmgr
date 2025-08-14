# Skill Model Configuration

This directory contains YAML configuration files that allow designers to tweak game balance without modifying code.

## skill_model.yml

This file contains all the key parameters that control player skill interactions, probabilities, and development.

### Probability Factors

These control the base probability calculations for at-bat outcomes:

- `STRIKEOUT_FACTOR` (3.0): Base factor for strikeout probability
- `WALK_FACTOR` (2.5): Base factor for walk probability  
- `HIT_FACTOR` (2.8): Base factor for hit probability
- `HOMERUN_FACTOR` (4.5): Base factor for home run probability
- `EXTRABASE_FACTOR` (3.5): Base factor for extra base hits

**Player Attribute Weights:**
- `PITCHER_VELOCITY_WEIGHT` (0.4): How much velocity affects pitcher performance
- `PITCHER_MOVEMENT_WEIGHT` (0.3): How much movement affects pitcher performance
- `PITCHER_CONTROL_WEIGHT` (0.3): How much control affects pitcher performance
- `HITTER_CONTACT_WEIGHT` (0.5): How much contact affects hitting ability
- `HITTER_DISCIPLINE_WEIGHT` (0.5): How much discipline affects plate discipline
- `HITTER_POWER_WEIGHT` (0.6): How much power affects home run probability

**Base Adjustments:**
These shift the baseline probabilities before calculations:
- `BASE_STRIKEOUT_ADJUSTMENT` (0.0): Shifts strikeout baseline
- `BASE_WALK_ADJUSTMENT` (-0.5): Shifts walk baseline (negative = fewer walks)
- `BASE_HIT_ADJUSTMENT` (-0.3): Shifts hit baseline
- `BASE_HOMERUN_ADJUSTMENT` (-2.0): Shifts home run baseline (very negative = rare)

**Situational Modifiers:**
- `CLUTCH_MODIFIER` (0.1): How much clutch rating affects pressure situations
- `FATIGUE_MODIFIER` (-0.2): How much fatigue hurts pitcher performance
- `WEATHER_MODIFIER_RANGE` (0.15): Range of weather effects on performance

### Hit Type Weights

Controls the distribution of hit types when a ball is put in play:

- `SINGLE_WEIGHT` (0.65): Relative frequency of singles (65%)
- `DOUBLE_WEIGHT` (0.20): Relative frequency of doubles (20%) 
- `TRIPLE_WEIGHT` (0.05): Relative frequency of triples (5%)
- `HOMERUN_WEIGHT` (0.10): Relative frequency of home runs (10%)

**Power Thresholds:**
- `HOMERUN_POWER_THRESHOLD` (60): Power rating needed for home run bonus
- `EXTRABASE_POWER_THRESHOLD` (50): Power rating needed for extra base hit bonus
- `POWER_SCALING_FACTOR` (0.8): How much power affects hit type distribution

### Player Development

Controls how players age and develop over time:

- `peak_age` (25): Age when players perform at their best
- `decline_start` (30): Age when players start declining
- `retirement_age` (40): Age when players may retire

### Fatigue

Controls how pitcher fatigue accumulates and recovers:

- `game_fatigue_factor` (0.05): How much fatigue builds per inning pitched
- `fatigue_recovery_rate_per_day` (0.2): How much fatigue recovers per day of rest

### Event Odds

Controls the probability of random development events:

- `positive_event_chance` (0.12): 12% chance of positive development events per season
- `negative_event_chance` (0.08): 8% chance of negative development events per season

## Making Changes

1. Edit the `skill_model.yml` file with any text editor
2. Changes take effect immediately - no need to restart the game
3. Use the test script to verify your changes: `python test_config.py`

## Balance Guidelines

**Making the game more offense-friendly:**
- Increase `HIT_FACTOR` and `HOMERUN_FACTOR` 
- Decrease `STRIKEOUT_FACTOR`
- Reduce negative base adjustments

**Making the game more pitcher-friendly:**
- Increase `STRIKEOUT_FACTOR`
- Decrease `HIT_FACTOR` and `HOMERUN_FACTOR`
- Make base adjustments more negative

**Adjusting player development:**
- Change age thresholds to make peaks longer/shorter
- Adjust event chances to make careers more/less volatile

**Tuning fatigue:**
- Lower `game_fatigue_factor` to reduce fatigue buildup
- Increase `fatigue_recovery_rate_per_day` for faster recovery

## Backup

Always keep a backup of the original configuration before making changes. The default values have been tested for balance.
