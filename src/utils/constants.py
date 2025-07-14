"""
Game constants and configuration values for MLW Wiffle Ball
"""

# Game Information
GAME_TITLE = "Wiffle Ball Manager"
VERSION = "1.0.0"

# MLW Game Settings
MAX_TEAMS = 12  # Typical MLW league size
MAX_PLAYERS_PER_TEAM = 8  # 6 active + 2 reserve
ACTIVE_PLAYERS_PER_TEAM = 6
RESERVE_PLAYERS_PER_TEAM = 2
GAMES_PER_SEASON = 15  # 5 series of 3 games each
INNINGS_PER_GAME = 3
PLAYOFF_TEAMS_PER_DIVISION = 3

# MLW Rules
PITCHING_SPEED_LIMIT = 75  # mph
PITCHING_WARNING_SPEED = 73  # mph
MERCY_RULE_RUNS = 6  # runs per inning
MERCY_RULE_INNINGS = 3  # no mercy rule after this inning
MAX_BATTERS_IN_LINEUP = 5
MIN_BATTERS_IN_LINEUP = 3
PLAYERS_ON_FIELD = 3  # including pitcher

# Player Attributes
MIN_ATTRIBUTE = 1
MAX_ATTRIBUTE = 100

# Player Types
PLAYER_TYPES = {
    "PITCHER": "P",
    "CATCHER": "C", 
    "FIRST_BASE": "1B",
    "SECOND_BASE": "2B",
    "THIRD_BASE": "3B",
    "SHORTSTOP": "SS",
    "LEFT_FIELD": "LF",
    "CENTER_FIELD": "CF",
    "RIGHT_FIELD": "RF",
    "DESIGNATED_HITTER": "DH"
}

# MLW-Specific Player Attributes
PITCHER_ATTRIBUTES = ["velocity", "control", "stamina", "speed_control"]
HITTER_ATTRIBUTES = ["power", "contact", "speed", "eye"]
FIELDER_ATTRIBUTES = ["range", "arm_strength", "accuracy"]
MENTAL_ATTRIBUTES = ["leadership", "clutch", "work_ethic"]

# Game States
GAME_STATES = {
    "MAIN_MENU": "main_menu",
    "NEW_GAME": "new_game",
    "LOAD_GAME": "load_game",
    "IN_GAME": "in_game",
    "SEASON_MENU": "season_menu",
    "TEAM_MENU": "team_menu",
    "PLAYER_MENU": "player_menu",
    "TRADE_MENU": "trade_menu",
    "SETTINGS": "settings",
    "QUIT": "quit"
}

# MLW Season Structure
SEASON_STRUCTURE = {
    "REGULAR_SEASON_GAMES": 15,
    "SERIES_PER_SEASON": 5,
    "GAMES_PER_SERIES": 3,
    "DIVISIONAL_SERIES": 3,
    "CROSS_DIVISIONAL_SERIES": 2
}

# MLW Playoff Structure
PLAYOFF_STRUCTURE = {
    "TEAMS_PER_DIVISION": 3,
    "FIRST_ROUND_BYE": True,  # Top seed gets bye
    "CHAMPIONSHIP_SERIES": True
}

# Colors for UI
COLORS = {
    "TITLE": "bold blue",
    "SUBTITLE": "cyan",
    "SUCCESS": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "INFO": "white",
    "HIGHLIGHT": "bold white",
    "DIM": "dim"
}

# File Paths
SAVE_DIR = "data/saves"
TEMPLATE_DIR = "data/templates"

# Database
DATABASE_NAME = "wiffle_ball_manager.db"

# MLW League Divisions
DIVISIONS = ["American", "National"]

# MLW Team Names (example)
TEAM_NAMES = {
    "American": [
        "Thunder",
        "Lightning", 
        "Storm",
        "Hurricane",
        "Tornado",
        "Cyclone"
    ],
    "National": [
        "Fire",
        "Flame",
        "Blaze",
        "Inferno",
        "Phoenix",
        "Dragon"
    ]
} 