# Wiffle Ball Manager

A text-driven console baseball management simulation game where you manage a wiffle ball team through seasons, making strategic decisions about players, games, and team development.

## Features

- **Team Management**: Manage your roster, trade players, and develop talent
- **Game Simulation**: Experience detailed play-by-play baseball action
- **Season Management**: Guide your team through full seasons with playoffs
- **League Structure**: Compete against AI-controlled teams in organized divisions
- **Financial System**: Manage budgets, contracts, and team finances
- **Cross-Platform**: Works seamlessly on both macOS and Windows

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup
1. Clone or download this repository
2. Navigate to the project directory
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Game
```bash
python run.py
```

### Game Controls
- Use arrow keys or number keys to navigate menus
- Press Enter to confirm selections
- Press 'q' or 'Q' to quit from most screens
- Press 'h' or 'H' for help in most menus

## Game Modes

### New Game
Start a fresh season with a new team and league.

### Load Game
Continue a previously saved game.

### Quick Game
Play a single game without season management.

## Gameplay

### Managing Your Team
- **Roster**: View and manage your 25-man roster
- **Lineups**: Set batting orders and defensive positions
- **Trades**: Negotiate trades with other teams
- **Free Agency**: Sign free agents during the off-season

### Game Strategy
- **Pitching**: Choose starting pitchers and manage bullpen
- **Batting**: Set lineups and make in-game decisions
- **Defense**: Position players and make defensive substitutions
- **Baserunning**: Control aggressive or conservative baserunning

### Season Management
- **Schedule**: Play through a 162-game regular season
- **Standings**: Track your team's position in the division
- **Playoffs**: Compete for the championship
- **Awards**: Win individual and team awards

## File Structure

```
wifflemgr/
├── src/                    # Source code
├── data/                   # Game data and saves
├── tests/                  # Test files
├── requirements.txt        # Python dependencies
├── run.py                  # Game launcher
└── README.md              # This file
```

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Style
This project follows PEP 8 style guidelines.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or suggestions, please open an issue on the project repository.

---

**Enjoy managing your wiffle ball dynasty!** ⚾ 