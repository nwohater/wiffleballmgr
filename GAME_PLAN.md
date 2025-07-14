# Wiffle Ball Manager - Game Plan (Updated for MLW Rules)

## Game Overview
A text-driven console wiffle ball management simulation game based on the MLW (Major League Wiffle) rules where players manage a wiffle ball team through seasons, making strategic decisions about players, games, and team development.

## MLW Rules Integration

### Team Structure
- **Roster Size**: 6 active players + 2 reserve players per team
- **Field Players**: Only 3 players on the field at once (including pitcher)
- **Batting Lineup**: 3-5 players in the lineup
- **Game Format**: 3 innings, extra innings for ties
- **Season**: 15 games (5 series of 3 games each)

### Gameplay Mechanics
- **Pitching**: Speed limit of 75 mph, warnings at 73-74 mph
- **Strike Zone**: Metal strike zone with PVC border
- **Mercy Rule**: 6 runs per inning (no mercy rule after 3rd inning)
- **Baserunning**: No stealing, no leading off
- **Defense**: 3 players including pitcher, outfielders can be interchanged
- **Outs**: Strikeouts, flyouts, force outs, tagging, pegging

## Core Features

### 1. Team Management
- **Roster Management**: Manage 8 total players (6 active + 2 reserve)
- **Player Attributes**: 
  - Hitting (Power, Contact, Speed)
  - Pitching (Velocity, Control, Stamina, Speed Control)
  - Fielding (Range, Arm Strength, Accuracy)
  - Mental (Leadership, Clutch, Work Ethic)
- **Player Development**: Training, aging, progression/regression
- **Trades**: Player trades with commissioner approval system

### 2. Game Simulation
- **Play-by-Play**: Detailed text descriptions of each play
- **Strategy Options**: 
  - Batting order management (3-5 players)
  - Pitching changes (pitcher cannot re-enter as pitcher)
  - Defensive positioning (3 players only)
  - Pinch hitting and pinch running
- **Game Modes**: 
  - Single game simulation (3 innings)
  - Series simulation (3 games)
  - Season simulation (15 games)
  - Playoff series
- **MLW Rules Integration**:
  - Speed limit enforcement
  - Mercy rule implementation
  - Proper strike zone mechanics
  - No stealing/leading off

### 3. Season Management
- **Schedule**: 15 regular season games (5 series of 3 games)
- **Divisions**: Organized league structure with cross-divisional play
- **Playoffs**: Top 3 teams per division, top seeds get bye
- **Draft**: 8-pick draft based on previous year results
- **Trade Deadline**: Before final slate of games

### 4. League Structure
- **Multiple Teams**: AI-controlled opponents
- **Divisions**: Organized league structure
- **Trading**: Player trades with commissioner approval
- **Free Agency**: Cut players become free agents
- **Draft System**: Annual 8-pick draft

### 5. Financial System (Simplified)
- **Team Budget**: Basic financial management
- **Player Contracts**: Simple contract system
- **Facilities**: Basic team facilities

### 6. User Interface
- **Menu System**: Clean, intuitive navigation
- **Statistics Display**: MLW-specific stat screens
- **Save/Load**: Game state persistence
- **Settings**: Customizable game options
- **Help System**: MLW rules reference

## Technical Architecture

### Technology Stack
- **Language**: Python 3.8+
- **Cross-Platform**: Works on macOS and Windows
- **Dependencies**: 
  - `colorama` (cross-platform colored output)
  - `rich` (rich text formatting)
  - `click` (command-line interface)
  - `pydantic` (data validation)
  - `sqlite3` (save game storage)

### Project Structure
```
wifflemgr/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── game/
│   │   ├── __init__.py
│   │   ├── engine.py           # Main game loop
│   │   ├── state.py            # Game state management
│   │   └── config.py           # Game configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── player.py           # Player class (8 per team)
│   │   ├── team.py             # Team class (6 active + 2 reserve)
│   │   ├── game.py             # Game simulation (3 innings)
│   │   └── league.py           # League structure
│   ├── simulation/
│   │   ├── __init__.py
│   │   ├── game_sim.py         # MLW game simulation logic
│   │   ├── season_sim.py       # 15-game season simulation
│   │   └── ai.py               # AI opponent logic
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── menus.py            # Menu system
│   │   ├── display.py          # Text display utilities
│   │   └── input.py            # User input handling
│   ├── data/
│   │   ├── __init__.py
│   │   ├── database.py         # Save game management
│   │   └── generators.py       # Random data generation
│   └── utils/
│       ├── __init__.py
│       ├── constants.py        # MLW game constants
│       └── helpers.py          # Utility functions
├── data/
│   ├── saves/                  # Save game files
│   └── templates/              # Game data templates
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_simulation.py
│   └── test_ui.py
├── requirements.txt
├── README.md
├── setup.py
└── run.py                      # Game launcher
```

## Development Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Project setup and structure
- [ ] Basic player and team models (8 players per team)
- [ ] Simple game simulation engine (3 innings)
- [ ] Basic console UI framework
- [ ] Save/load system

### Phase 2: Core Gameplay (Week 3-4)
- [ ] Complete MLW game simulation
- [ ] Season management (15 games)
- [ ] Player statistics tracking
- [ ] Basic AI opponents
- [ ] Menu system

### Phase 3: Advanced Features (Week 5-6)
- [ ] Trading system with commissioner approval
- [ ] Free agency (cut players)
- [ ] Player development
- [ ] Draft system (8 picks)
- [ ] Financial management

### Phase 4: Polish & Enhancement (Week 7-8)
- [ ] Advanced statistics
- [ ] Awards system
- [ ] MLW rules enforcement
- [ ] UI improvements
- [ ] Bug fixes and testing

## Game Mechanics

### Player Generation
- **Name Generation**: Realistic player names
- **Attribute Distribution**: Bell curve distribution for realistic stats
- **Personality Traits**: Affects team chemistry and performance
- **Speed Control**: Critical for pitchers (75 mph limit)

### Game Simulation
- **Dice-Based**: Uses weighted random numbers for realistic outcomes
- **MLW Rules**: 
  - 3 innings, extra innings for ties
  - 6-run mercy rule per inning (before 3rd inning)
  - Speed limit enforcement
  - No stealing/leading off
- **Situational Modifiers**: Clutch situations, fatigue
- **Momentum**: Streaks and slumps affect performance

### AI Decision Making
- **Strategy**: AI makes realistic managerial decisions
- **Trading**: AI evaluates trade offers based on team needs
- **Free Agency**: AI signs cut players strategically

## MLW-Specific Features

### Speed Limit System
- **Pitching Speed**: Track and enforce 75 mph limit
- **Warnings**: Issue warnings at 73-74 mph
- **Penalties**: Automatic balls for exceeding limit

### Roster Management
- **Active Players**: 6 players available for games
- **Reserve Players**: 2 additional players for depth
- **Lineup Flexibility**: 3-5 players in batting order
- **Defensive Substitutions**: 3 players on field, outfielders interchangeable

### Season Structure
- **15 Games**: 5 series of 3 games each
- **Divisional Play**: Play division opponents
- **Cross-Divisional**: 2 cross-divisional opponents
- **Playoffs**: Top 3 per division, top seeds get bye

## User Experience Goals
- **Authenticity**: True to MLW rules and format
- **Accessibility**: Easy to learn, hard to master
- **Depth**: Multiple seasons of gameplay
- **Replayability**: Random events and different strategies
- **Performance**: Fast simulation even for full seasons
- **Cross-Platform**: Consistent experience on Mac and Windows

## Future Enhancements (Post-Launch)
- **Multiplayer**: Online leagues with other players
- **Modding**: Custom leagues and player sets
- **Advanced Analytics**: MLW-specific statistics
- **Historical Mode**: Replay famous MLW seasons
- **Mobile Version**: Simplified mobile interface

## Success Metrics
- **Engagement**: Average session length > 30 minutes
- **Retention**: Players complete multiple seasons
- **Performance**: Season simulation completes in < 5 seconds
- **Compatibility**: Works seamlessly on both Mac and Windows
- **User Feedback**: Positive reviews for MLW authenticity 