# Logistic Probability System for At-Bat Simulation

This document describes the new logistic/odds-ratio approach for simulating at-bat outcomes in the Wiffle Ball Manager game.

## Overview

The previous system used flat probability ranges that were modified by player attributes. The new system uses logistic regression (sigmoid functions) to create more realistic probability curves that pit pitcher attributes directly against hitter attributes.

## Core Formula

Each outcome probability is calculated using:

```
P(outcome) = sigmoid(K_factor * (pitcher_composite - hitter_composite) + base_adjustment)
```

Where:
- `sigmoid(x) = 1 / (1 + exp(-x))`
- `K_factor` is the outcome-specific scaling factor
- `pitcher_composite` and `hitter_composite` are weighted attribute combinations
- `base_adjustment` shifts the probability baseline

## Outcome Types

### 1. Strikeout
- **Formula**: `P(strikeout) = sigmoid(3.0 * (pitcher_stuff - batter_hit_ability))`
- **Pitcher attributes**: velocity (40%), movement (30%), control (30%)
- **Batter attributes**: contact (50%), discipline (30%)

### 2. Walk
- **Formula**: `P(walk) = sigmoid(2.5 * (batter_plate_discipline - pitcher_command) - 0.5)`
- **Pitcher attributes**: control (60%), deception (40%)
- **Batter attributes**: discipline (50%), contact (30%)

### 3. Ball in Play (Hit)
- **Formula**: `P(hit) = sigmoid(2.8 * (batter_hit_ability - pitcher_stuff * 0.8) - 0.3)`
- **Pitcher attributes**: velocity (40%), movement (30%), control (30%)
- **Batter attributes**: contact (50%), discipline (30%)

### 4. Home Run
- **Formula**: `P(homerun) = sigmoid(4.5 * (batter_power * 0.6 - pitcher_stuff * 0.6) - 2.0)`
- **Pitcher attributes**: velocity (40%), movement (30%), control (30%)
- **Batter attributes**: power (60%)

## Hit Type Distribution

When a ball is put in play, the hit type is determined by a separate probability calculation:

- **Singles**: 65% base weight
- **Doubles**: 20% base weight  
- **Triples**: 5% base weight
- **Home Runs**: 10% base weight

These weights are modified by:
- **Power**: Increases extra-base hits at the expense of singles
- **Speed**: Increases triples and infield singles
- **Pitcher Stuff**: Reduces extra-base hits across the board

## Situational Modifiers

The system includes situational contexts that modify base probabilities:

### Clutch Situations
- Triggered when: Late innings (3+) and close game (±1 run)
- Effect: Players with higher clutch ratings perform better under pressure

### Pitcher Fatigue
- Triggered when: High pitch count (60+ pitches)
- Effect: Reduces strikeout probability, increases walks and hits

### Speed Limit Pressure
- Triggered when: Pitcher velocity ≥ 70 mph (close to 75 mph limit)
- Effect: Reduces control, increases walks and hits

## Constants and Tuning

All probability factors are stored in `src/utils/constants.py` for easy tuning:

```python
PROBABILITY_FACTORS = {
    # Base factors for each outcome type
    "STRIKEOUT_FACTOR": 3.0,
    "WALK_FACTOR": 2.5,
    "HIT_FACTOR": 2.8,
    "HOMERUN_FACTOR": 4.5,
    
    # Pitcher attribute weights
    "PITCHER_VELOCITY_WEIGHT": 0.4,
    "PITCHER_MOVEMENT_WEIGHT": 0.3,
    "PITCHER_CONTROL_WEIGHT": 0.3,
    
    # Hitter attribute weights  
    "HITTER_CONTACT_WEIGHT": 0.5,
    "HITTER_DISCIPLINE_WEIGHT": 0.5,
    "HITTER_POWER_WEIGHT": 0.6,
    
    # Base probability adjustments
    "BASE_STRIKEOUT_ADJUSTMENT": 0.0,
    "BASE_WALK_ADJUSTMENT": -0.5,
    "BASE_HIT_ADJUSTMENT": -0.3,
    "BASE_HOMERUN_ADJUSTMENT": -2.0,
}
```

## Implementation Files

### Core Components
- `src/simulation/probability.py`: Main probability calculation engine
- `src/utils/constants.py`: Tunable probability constants
- `src/simulation/game_sim.py`: Updated to use new probability system

### Key Classes
- `AtBatProbabilityCalculator`: Main class for calculating outcome probabilities
- `sigmoid()`: Helper function for logistic calculations
- `normalize_attribute()`: Converts 1-100 attributes to -1 to 1 scale

## Example Results

For a Power Pitcher (75 velocity, 70 movement, 65 control) vs Contact Hitter (75 contact, 70 discipline, 45 power):

- **Strikeout**: 37.0%
- **Walk**: 30.1%
- **Ball in Play**: 30.6%
- **Home Run**: 2.3%

This creates realistic matchup dynamics where:
- Power pitchers get more strikeouts against weaker contact hitters
- Control pitchers minimize walks against disciplined hitters
- Power hitters have higher home run rates against weaker pitchers
- Contact hitters put more balls in play

## Benefits

1. **Realistic Curves**: Sigmoid functions create natural probability distributions
2. **Attribute Interaction**: Direct pitcher vs hitter attribute comparisons
3. **Situational Awareness**: Context-dependent probability modifications
4. **Easy Tuning**: All constants centralized for balance adjustments
5. **Scalable**: Can easily add new situational modifiers or outcome types

## Testing

Run `test_probability_system.py` to see the system in action with different player matchups and situational modifiers.
