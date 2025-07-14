"""
Main game engine for Wiffle Ball Manager
"""

from typing import Optional, Dict, Any
from rich.console import Console
from utils.constants import GAME_STATES

class GameEngine:
    """Main game engine that manages game state and flow"""
    
    def __init__(self):
        self.console = Console()
        self.current_state = GAME_STATES["MAIN_MENU"]
        self.game_data: Dict[str, Any] = {}
        self.save_file: Optional[str] = None
        
    def change_state(self, new_state: str) -> None:
        """Change the current game state"""
        if new_state in GAME_STATES.values():
            self.current_state = new_state
        else:
            self.console.print(f"[red]Invalid game state: {new_state}[/red]")
    
    def get_state(self) -> str:
        """Get the current game state"""
        return self.current_state
    
    def set_game_data(self, key: str, value: Any) -> None:
        """Set a value in the game data dictionary"""
        self.game_data[key] = value
    
    def get_game_data(self, key: str, default: Any = None) -> Any:
        """Get a value from the game data dictionary"""
        return self.game_data.get(key, default)
    
    def clear_game_data(self) -> None:
        """Clear all game data"""
        self.game_data.clear()
    
    def set_save_file(self, filename: str) -> None:
        """Set the current save file"""
        self.save_file = filename
    
    def get_save_file(self) -> Optional[str]:
        """Get the current save file"""
        return self.save_file
    
    def is_new_game(self) -> bool:
        """Check if this is a new game"""
        return self.save_file is None
    
    def quit_game(self) -> None:
        """Quit the game"""
        self.change_state(GAME_STATES["QUIT"]) 