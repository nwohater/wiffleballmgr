# Player Attribute Refactor Plan

## Executive Summary

Based on the comprehensive audit of player attributes across the codebase, this document outlines proposed changes to streamline and enhance the player attribute system in Wiffle Ball Manager. The audit revealed several underutilized and unused attributes that should be addressed for better gameplay balance and code maintainability.

## Audit Findings Summary

### Current Attribute Usage Matrix

| Player Attribute | game_sim.py | player_dev.py | season_sim.py | trading.py | UI | Status |
|------------------|-------------|---------------|---------------|------------|----|---------| 
| **Pitching Attributes** |
| velocity         | ✅ Heavy    | ✅ Heavy      | ✅ Heavy      | ✅ Heavy   | ✅ | **CORE** |
| control          | ✅ Heavy    | ✅ Heavy      | ✅ Heavy      | ✅ Heavy   | ✅ | **CORE** |
| stamina          | ❌ None     | ✅ Heavy      | ❌ None       | ✅ Light   | ✅ | **UNDERUSED** |
| speed_control    | ❌ None     | ✅ Heavy      | ❌ None       | ✅ Light   | ✅ | **UNDERUSED** |
| **Fielding Attributes** |
| range            | ✅ Medium   | ❌ None       | ❌ None       | ❌ None    | ✅ | **MODERATE** |
| arm_strength     | ✅ Medium   | ❌ None       | ❌ None       | ❌ None    | ✅ | **MODERATE** |
| accuracy         | ✅ Medium   | ❌ None       | ❌ None       | ❌ None    | ✅ | **MODERATE** |
| **Hitting Attributes** |
| power            | ❌ None     | ❌ None       | ❌ None       | ❌ None    | ❌ | **MISSING** |
| contact          | ✅ Light    | ✅ Light      | ❌ None       | ❌ None    | ❌ | **WEAK** |
| speed            | ❌ None     | ❌ None       | ❌ None       | ❌ None    | ❌ | **MISSING** |
| eye              | ❌ None     | ❌ None       | ❌ None       | ❌ None    | ❌ | **MISSING** |
| **Mental Attributes** |
| leadership       | ❌ None     | ❌ None       | ❌ None       | ❌ None    | ❌ | **UNUSED** |
| clutch           | ❌ None     | ❌ None       | ❌ None       | ❌ None    | ❌ | **UNUSED** |
| work_ethic       | ❌ None     | ❌ None       | ❌ None       | ❌ None    | ❌ | **UNUSED** |

### Key Issues Identified

1. **Missing Hitting System**: The game uses `velocity` and `control` for hitting calculations, but lacks dedicated hitting attributes
2. **Underutilized Pitching Attributes**: `stamina` and `speed_control` are only used in development, not gameplay
3. **Unused Mental Attributes**: `leadership`, `clutch`, and `work_ethic` are defined but never referenced
4. **Inconsistent Attribute Usage**: Some attributes appear in constants but not in actual player models

## Proposed Changes

### Phase 1: Core Attribute Restructuring

#### 1.1 Implement Proper Hitting Attributes
- [ ] **Add missing hitting attributes to Player model**
  - [ ] Add `power` attribute (replaces using velocity for hitting power)
  - [ ] Add `contact` attribute (distinct from pitching control)
  - [ ] Add `speed` attribute (baserunning and fielding positioning)
  - [ ] Add `eye` attribute (plate discipline, walk rate)

#### 1.2 Enhance Game Simulation Integration
- [ ] **Update `game_sim.py` to use hitting attributes**
  - [ ] Replace `batter.velocity + batter.control` with `batter.power + batter.contact`
  - [ ] Use `batter.eye` for walk probability calculations
  - [ ] Use `batter.speed` for baserunning decisions
  - [ ] Integrate `pitcher.stamina` for fatigue effects during games
  - [ ] Use `pitcher.speed_control` for speed limit violations

#### 1.3 Update Player Development System
- [ ] **Enhance `player_dev.py` attribute development**
  - [ ] Add development paths for new hitting attributes
  - [ ] Balance development rates between pitching/hitting/fielding
  - [ ] Add age-based development curves for all attributes
  - [ ] Implement attribute caps and floors

### Phase 2: Mental Attributes Integration

#### 2.1 Implement Clutch Performance System
- [ ] **Add clutch situations detection**
  - [ ] Define clutch scenarios (late innings, runners in scoring position)
  - [ ] Apply `clutch` attribute modifiers in pressure situations
  - [ ] Track clutch performance statistics

#### 2.2 Leadership and Chemistry System
- [ ] **Implement team chemistry mechanics**
  - [ ] Use `leadership` for team performance bonuses
  - [ ] Add captain/veteran player designations
  - [ ] Implement locker room influence on other players

#### 2.3 Work Ethic and Development
- [ ] **Integrate work ethic into development**
  - [ ] Use `work_ethic` to modify development rates
  - [ ] Add training camp and offseason improvement events
  - [ ] Link work ethic to injury recovery and stamina

### Phase 3: AI and Trading Enhancement

#### 3.1 Enhanced AI Decision Making
- [ ] **Update `trading.py` evaluation system**
  - [ ] Include all attributes in player value calculations
  - [ ] Add positional value modifiers
  - [ ] Implement team need analysis for all attribute types
  - [ ] Add age-curve projections for attribute decline

#### 3.2 Season Simulation Improvements
- [ ] **Update `season_sim.py` for comprehensive attribute usage**
  - [ ] Use stamina for pitcher usage limits
  - [ ] Implement platoon advantages based on attributes
  - [ ] Add injury risk based on usage and durability
  - [ ] Season-long performance tracking per attribute

### Phase 4: UI and Display Updates

#### 4.1 Enhanced Player Display
- [ ] **Update `team_management.py` attribute display**
  - [ ] Add hitting attributes to roster tables
  - [ ] Create attribute comparison tools
  - [ ] Add attribute-based player rankings
  - [ ] Implement scouting reports with all attributes

#### 4.2 Statistics Integration
- [ ] **Link attributes to performance metrics**
  - [ ] Show attribute influence on stats
  - [ ] Add attribute-based projections
  - [ ] Create development tracking charts
  - [ ] Historical attribute progression

### Phase 5: Game Balance and Testing

#### 5.1 Attribute Balance Testing
- [ ] **Balance attribute weights and impacts**
  - [ ] Test simulation outcomes with new attribute system
  - [ ] Adjust attribute scaling and modifiers
  - [ ] Validate realistic statistical distributions
  - [ ] Performance regression testing

#### 5.2 Documentation and Constants Update
- [ ] **Update game documentation**
  - [ ] Revise `constants.py` with new attribute definitions
  - [ ] Update help system with attribute explanations
  - [ ] Create attribute guide for players
  - [ ] Update development documentation

## Implementation Priority

### High Priority (Phase 1)
- **Hitting attributes implementation** - Critical for realistic gameplay
- **Game simulation updates** - Core functionality enhancement
- **Stamina integration** - Important for pitcher management

### Medium Priority (Phase 2-3)
- **Mental attributes** - Adds depth but not essential for basic functionality
- **AI enhancements** - Improves computer opponents but not player-facing
- **Advanced statistics** - Nice-to-have features

### Low Priority (Phase 4-5)
- **UI polish** - Quality of life improvements
- **Documentation** - Important but not gameplay-critical
- **Balance testing** - Ongoing process throughout development

## Technical Considerations

### Database Migration
- [ ] **Player model changes require data migration**
  - [ ] Add new attribute columns to existing players
  - [ ] Provide reasonable default values for new attributes
  - [ ] Maintain backward compatibility with save files
  - [ ] Version control for save file formats

### Performance Impact
- [ ] **Monitor performance with expanded attribute system**
  - [ ] Profile simulation speed with additional calculations
  - [ ] Optimize attribute lookup and calculations
  - [ ] Memory usage validation
  - [ ] Large league simulation testing

### Code Architecture
- [ ] **Maintain clean separation of concerns**
  - [ ] Keep attribute definitions centralized
  - [ ] Use consistent naming conventions
  - [ ] Implement attribute validation
  - [ ] Add unit tests for new attribute logic

## Success Metrics

### Gameplay Improvements
- More realistic statistical distributions
- Better correlation between attributes and performance
- Enhanced strategic depth in player management
- Improved AI decision making

### Code Quality
- Reduced code duplication in attribute handling
- Consistent attribute usage across all modules
- Comprehensive test coverage for attribute logic
- Clear documentation and maintainable code

## Risk Mitigation

### Backward Compatibility
- Implement graceful fallbacks for missing attributes
- Maintain save file compatibility through versioning
- Provide migration tools for existing games

### Balance Issues
- Extensive playtesting with new attribute system
- Adjustable configuration for attribute weights
- Rollback capabilities if balance issues arise

### Performance Concerns
- Profile-guided optimization of attribute calculations
- Lazy loading of complex attribute computations
- Efficient caching of frequently used attribute combinations

---

## Next Steps

1. **Review and discuss this plan** with stakeholders
2. **Prioritize phases** based on development timeline and resources
3. **Create detailed technical specifications** for Phase 1 implementation
4. **Set up testing framework** for attribute balance validation
5. **Begin implementation** with hitting attributes as the foundation

This plan provides a comprehensive roadmap for transforming the player attribute system from its current state into a robust, well-integrated system that enhances both gameplay depth and code maintainability.
