"""
Main entry point for Wiffle Ball Manager
"""

import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from colorama import init

from game.engine import GameEngine
from ui.menus import MainMenu
from utils.constants import GAME_TITLE, VERSION

# Initialize colorama for cross-platform colored output
init()

def print_banner():
    """Display the game banner"""
    console = Console()
    
    title = Text(GAME_TITLE, style="bold blue")
    version = Text(f"v{VERSION}", style="dim")
    
    banner_text = Text()
    banner_text.append(title)
    banner_text.append("\n")
    banner_text.append(version)
    banner_text.append("\n\n")
    banner_text.append("⚾ Wiffle Ball Management Simulation ⚾", style="green")
    
    panel = Panel(
        banner_text,
        border_style="blue",
        padding=(1, 2)
    )
    
    console.print(panel)
    console.print()

def main():
    """Main game entry point"""
    try:
        # Clear screen and show banner
        os.system('cls' if os.name == 'nt' else 'clear')
        print_banner()
        
        # Initialize game engine
        engine = GameEngine()
        
        # Show main menu
        main_menu = MainMenu(engine)
        main_menu.run()
        
    except KeyboardInterrupt:
        print("\n\nThanks for playing Wiffle Ball Manager!")
        sys.exit(0)
    except Exception as e:
        console = Console()
        console.print(f"[red]Error: {e}[/red]")
        console.print("[yellow]Please report this error to the development team.[/yellow]")
        sys.exit(1)

if __name__ == "__main__":
    main() 