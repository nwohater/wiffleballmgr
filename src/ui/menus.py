"""
Menu system for Wiffle Ball Manager
"""

from typing import List, Callable, Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from src.utils.constants import GAME_STATES, COLORS

# Import game components
from src.models.player import Player
from src.models.team import Team
from src.models.game import Game
from src.simulation.season_sim import SeasonSimulator
from src.simulation.game_sim import GameSimulator
from src.ui.team_management import TeamManagementUI
import random

class MenuItem:
    """Represents a menu item"""
    
    def __init__(self, key: str, label: str, action: Callable, description: str = ""):
        self.key = key
        self.label = label
        self.action = action
        self.description = description

class BaseMenu:
    """Base class for all menus"""
    
    def __init__(self, engine):
        self.engine = engine
        self.console = Console()
        self.items: List[MenuItem] = []
        self.title = "Menu"
        
    def add_item(self, key: str, label: str, action: Callable, description: str = ""):
        """Add a menu item"""
        self.items.append(MenuItem(key, label, action, description))
    
    def display(self):
        """Display the menu"""
        self.console.clear()
        
        # Create title panel
        title_panel = Panel(
            self.title,
            border_style=COLORS["TITLE"],
            padding=(1, 2)
        )
        self.console.print(title_panel)
        self.console.print()
        
        # Create menu table
        table = Table(show_header=False, box=None)
        table.add_column("Key", style=COLORS["HIGHLIGHT"])
        table.add_column("Option", style=COLORS["INFO"])
        table.add_column("Description", style=COLORS["DIM"])
        
        for item in self.items:
            table.add_row(item.key, item.label, item.description)
        
        self.console.print(table)
        self.console.print()
    
    def get_choice(self) -> Optional[str]:
        """Get user choice"""
        choices = [item.key for item in self.items]
        choice = Prompt.ask(
            "Select an option",
            choices=choices,
            default=choices[0] if choices else None
        )
        return choice
    
    def run(self):
        """Run the menu loop"""
        while True:
            self.display()
            choice = self.get_choice()
            
            if choice is None:
                break
                
            # Find and execute the selected action
            for item in self.items:
                if item.key == choice:
                    result = item.action()
                    if result == "quit":
                        return
                    break

class MainMenu(BaseMenu):
    """Main menu for the game"""
    
    def __init__(self, engine):
        super().__init__(engine)
        self.title = "Wiffle Ball Manager - Main Menu"
        self.setup_items()
    
    def setup_items(self):
        """Setup menu items"""
        self.add_item("1", "New Game", self.new_game, "Start a new MLW season")
        self.add_item("2", "Load Game", self.load_game, "Continue a saved game")
        self.add_item("3", "Quick Game", self.quick_game, "Play a single game")
        self.add_item("4", "Settings", self.settings, "Game settings and options")
        self.add_item("5", "Help", self.help, "Game rules and instructions")
        self.add_item("q", "Quit", self.quit_game, "Exit the game")
    
    def new_game(self):
        """Start a new game"""
        self.engine.change_state(GAME_STATES["NEW_GAME"])
        self.console.print("[green]Starting new MLW season...[/green]")
        
        # Generate teams and players
        self.console.print("[yellow]Generating MLW teams and players...[/yellow]")
        teams = self.generate_teams()
        
        # Create a new season simulator
        season_sim = SeasonSimulator(teams)
        
        # Store in game engine
        self.engine.set_game_data("season_simulator", season_sim)
        self.engine.set_game_data("teams", teams)
        self.engine.set_game_data("current_team", teams[0])  # Default to first team
        self.engine.set_game_data("current_game", 1)
        self.engine.set_game_data("current_series", 1)
        
        # Show team selection
        self.select_team(teams)
        
        return "quit"
    
    def generate_teams(self):
        """Generate teams for the league with unique team names and unique player names."""
        teams = []
        divisions = ["American", "National"]
        num_teams_per_division = 6
        # New pool of sports-style team names (12 unique names)
        team_names_pool = [
            "Thunder", "Lightning", "Storm", "Hurricanes", "Tornadoes", "Cyclones",
            "Firebirds", "Blaze", "Inferno", "Phoenix", "Dragons", "Vipers"
        ]
        random.shuffle(team_names_pool)
        # Player name pools
        player_first_names = [
            "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Drew", "Skyler",
            "Jamie", "Avery", "Cameron", "Peyton", "Quinn", "Reese", "Rowan", "Sawyer",
            "Emerson", "Finley", "Harper", "Jesse", "Kai", "Logan", "Micah", "Parker",
            "Remy", "Sage", "Tatum", "Blake", "Charlie", "Dakota", "Elliot", "Frankie"
        ]
        player_last_names = [
            "Adams", "Baker", "Carter", "Diaz", "Evans", "Foster", "Gonzalez", "Hayes", "Irwin", "James",
            "Keller", "Lopez", "Morris", "Nguyen", "Owens", "Patel", "Quinn", "Reed", "Sanchez", "Turner",
            "Underwood", "Vasquez", "Wright", "Young", "Zimmerman", "Brooks", "Collins", "Edwards", "Fisher", "Griffin",
            "Henderson", "Jenkins", "Kim", "Long", "Mitchell", "Ortiz", "Perry", "Ramirez", "Russell", "Simmons",
            "Stewart", "Ward", "Watson", "Wood", "Price", "Porter", "Hughes", "Murray", "Ford", "Bennett"
        ]
        random.shuffle(player_first_names)
        random.shuffle(player_last_names)
        player_names = []
        for fn in player_first_names:
            for ln in player_last_names:
                player_names.append(f"{fn} {ln}")
        random.shuffle(player_names)
        player_name_iter = iter(player_names)
        # Assign teams to divisions
        for idx, team_name in enumerate(team_names_pool):
            division = divisions[idx // num_teams_per_division]
            team = Team(team_name, division)
            # Generate 6 active players
            for j in range(6):
                player = self.generate_random_player(next(player_name_iter))
                team.add_player(player, active=True)
            # Generate 2 reserve players
            for j in range(2):
                player = self.generate_random_player(next(player_name_iter))
                team.add_player(player, active=False)
            teams.append(team)
        return teams

    def generate_random_player(self, name):
        """Generate a random player with realistic skill ranges and a unique name."""
        return Player(
            name=name,
            age=random.randint(20, 30),
            velocity=random.randint(30, 70),
            control=random.randint(30, 70),
            stamina=random.randint(30, 70),
            speed_control=random.randint(30, 70),
            range=random.randint(40, 80),
            arm_strength=random.randint(40, 80),
            accuracy=random.randint(40, 80)
        )
    
    def select_team(self, teams):
        """Let player select their team"""
        self.console.print("\n[bold cyan]Select Your Team:[/bold cyan]")
        
        # Display teams in a table
        table = Table(title="MLW Teams")
        table.add_column("Division", style="cyan")
        table.add_column("Team Name", style="white")
        table.add_column("Record", style="yellow")
        
        for team in teams:
            table.add_row(team.division, team.name, "0-0")
        
        self.console.print(table)
        self.console.print()
        
        # Get team selection
        while True:
            team_name = Prompt.ask("Enter your team name")
            selected_team = None
            
            for team in teams:
                if team.name.lower() == team_name.lower():
                    selected_team = team
                    break
            
            if selected_team:
                self.engine.set_game_data("current_team", selected_team)
                self.console.print(f"[green]You selected the {selected_team.name}![/green]")
                break
            else:
                self.console.print("[red]Invalid team name. Please try again.[/red]")
        
        # Show season menu
        self.show_season_menu()
    
    def show_season_menu(self):
        """Show the season management menu"""
        season_menu = SeasonMenu(self.engine)
        season_menu.run()
    
    def load_game(self):
        """Load a saved game"""
        self.engine.change_state(GAME_STATES["LOAD_GAME"])
        self.console.print("[yellow]Load game functionality coming soon...[/yellow]")
        Prompt.ask("\nPress Enter to continue")
        return None
    
    def quick_game(self):
        """Play a quick single game"""
        self.console.print("[green]Setting up a quick game...[/green]")
        
        # Create two teams for a quick game
        team1 = Team("Home Team", "American")
        team2 = Team("Away Team", "National")
        
        # Generate players for both teams
        for i in range(6):  # 6 active players
            team1.add_player(self.generate_random_player(f"Player{i+1}"))
            team2.add_player(self.generate_random_player(f"Player{i+1}"))
        
        # Create game
        game = Game(team1, team2)
        game_sim = GameSimulator(team1, team2)
        
        # Store in engine
        self.engine.set_game_data("current_game", game)
        self.engine.set_game_data("game_simulator", game_sim)
        
        # Show game menu
        game_menu = QuickGameMenu(self.engine)
        game_menu.run()
        
        return None
    
    def settings(self):
        """Open settings menu"""
        self.console.print("[yellow]Settings functionality coming soon...[/yellow]")
        Prompt.ask("\nPress Enter to continue")
        return None
    
    def help(self):
        """Show help information"""
        self.show_help()
        return None
    
    def quit_game(self):
        """Quit the game"""
        if Confirm.ask("Are you sure you want to quit?"):
            self.engine.quit_game()
            return "quit"
        return None
    
    def show_help(self):
        """Display help information"""
        help_text = """
        [bold]MLW Wiffle Ball Manager[/bold]
        
        [bold]Game Rules:[/bold]
        • 3 players on field (including pitcher)
        • 3-5 players in batting lineup
        • 3 innings per game
        • 75 mph pitching speed limit
        • 6-run mercy rule per inning (before 3rd inning)
        • No stealing or leading off
        
        [bold]Controls:[/bold]
        • Use number keys or arrow keys to navigate
        • Press Enter to confirm selections
        • Press 'q' to quit from most screens
        • Press 'h' for help in most menus
        
        [bold]Season Structure:[/bold]
        • 15 regular season games
        • 5 series of 3 games each
        • Top 3 teams per division make playoffs
        • Championship series to determine winner
        """
        
        panel = Panel(
            help_text,
            title="Help & Rules",
            border_style=COLORS["INFO"],
            padding=(1, 2)
        )
        
        self.console.print(panel)
        Prompt.ask("\nPress Enter to continue")

class SeasonMenu(BaseMenu):
    """Menu for managing the season"""
    
    def __init__(self, engine):
        super().__init__(engine)
        self.title = "Season Management"
        self.setup_items()
    
    def setup_items(self):
        """Setup menu items"""
        self.add_item("1", "View Team", self.view_team, "View your team roster and stats")
        self.add_item("2", "Play Next Game", self.play_next_game, "Play the next scheduled game")
        self.add_item("3", "View Standings", self.view_standings, "View league standings")
        self.add_item("4", "View Schedule", self.view_schedule, "View remaining schedule")
        self.add_item("5", "Trade Players", self.trade_players, "Make trades with other teams")
        self.add_item("6", "Simulate Season", self.simulate_season, "Simulate the entire season")
        self.add_item("7", "Show Stats", self.show_stats, "View all team batting and pitching statistics")
        self.add_item("b", "Back to Main", self.back_to_main, "Return to main menu")
        self.add_item("q", "Quit", self.quit_game, "Exit the game")
    
    def view_team(self):
        """View team information"""
        teams = self.engine.get_game_data("teams")
        
        if not teams:
            self.console.print("[red]No teams found![/red]")
            Prompt.ask("\nPress Enter to continue")
            return None
        
        team_ui = TeamManagementUI()
        
        # Prompt user to select which team to view
        selected_team = team_ui.select_team_to_view(teams)
        
        if selected_team:
            # Show team overview
            team_ui.show_team_overview(selected_team)
            
            # Show full roster with stats
            self.console.print("\n")
            team_ui.show_roster(selected_team, show_reserves=True)
            
            # Allow player selection for detailed view
            while True:
                selected_player = team_ui.select_player_from_roster(selected_team)
                
                if selected_player:
                    # Show detailed player stats
                    team_ui.show_player_details(selected_player)
                    Prompt.ask("\nPress Enter to return to roster")
                    
                    # Redisplay roster
                    team_ui.show_team_overview(selected_team)
                    self.console.print("\n")
                    team_ui.show_roster(selected_team, show_reserves=True)
                else:
                    # User chose to go back
                    break
        
        return None
    
    def play_next_game(self):
        """Play the next scheduled game"""
        season_sim = self.engine.get_game_data("season_simulator")
        current_team = self.engine.get_game_data("current_team")
        
        if season_sim and current_team:
            # Get next opponent
            opponent = season_sim.get_next_opponent(current_team)
            if opponent:
                self.console.print(f"[green]Playing against {opponent.name}...[/green]")
                
                # Create and play game
                game = Game(current_team, opponent)
                game_sim = GameSimulator(current_team, opponent)
                
                # Store in engine
                self.engine.set_game_data("current_game", game)
                self.engine.set_game_data("game_simulator", game_sim)
                
                # Show game menu
                game_menu = GameMenu(self.engine)
                game_menu.run()
            else:
                self.console.print("[yellow]No more games scheduled this season![/yellow]")
                Prompt.ask("\nPress Enter to continue")
        return None
    
    def view_standings(self):
        """View league standings"""
        season_sim = self.engine.get_game_data("season_simulator")
        if season_sim:
            standings = season_sim.get_standings()
            
            table = Table(title="MLW Standings")
            table.add_column("Rank", style="cyan")
            table.add_column("Team", style="white")
            table.add_column("Division", style="yellow")
            table.add_column("GP", style="blue")
            table.add_column("W", style="green")
            table.add_column("L", style="red")
            table.add_column("PCT", style="blue")
            
            for i, team in enumerate(standings, 1):
                games_played = team.wins + team.losses
                pct = f"{team.wins / games_played:.3f}" if games_played > 0 else ".000"
                table.add_row(str(i), team.name, team.division, str(games_played), str(team.wins), str(team.losses), pct)
            
            self.console.print(table)
            Prompt.ask("\nPress Enter to continue")
        return None
    
    def view_schedule(self):
        """View remaining schedule"""
        season_sim = self.engine.get_game_data("season_simulator")
        current_team = self.engine.get_game_data("current_team")
        
        if season_sim and current_team:
            schedule = season_sim.get_remaining_schedule(current_team)
            
            table = Table(title=f"{current_team.name} Remaining Schedule")
            table.add_column("Game", style="cyan")
            table.add_column("Opponent", style="white")
            table.add_column("Home/Away", style="yellow")
            
            for i, game in enumerate(schedule, 1):
                home_away = "HOME" if game.home_team == current_team else "AWAY"
                opponent = game.away_team if game.home_team == current_team else game.home_team
                table.add_row(str(i), opponent.name, home_away)
            
            self.console.print(table)
            Prompt.ask("\nPress Enter to continue")
        return None
    
    def trade_players(self):
        """Trade players"""
        self.console.print("[yellow]Trade system coming soon...[/yellow]")
        Prompt.ask("\nPress Enter to continue")
        return None
    
    def simulate_season(self):
        """Simulate the entire season"""
        if Confirm.ask("Simulate the entire season?"):
            season_sim = self.engine.get_game_data("season_simulator")
            if season_sim:
                self.console.print("[green]Simulating season...[/green]")
                results = season_sim.simulate_full_season()
                
                # Show results
                self.show_season_results(results)
        return None
    
    def show_stats(self):
        """Show comprehensive batting and pitching statistics for all teams"""
        season_sim = self.engine.get_game_data("season_simulator")
        if not season_sim:
            self.console.print("[red]No season data available.[/red]")
            Prompt.ask("\nPress Enter to continue")
            return None
        
        teams = self.engine.get_game_data("teams")
        if not teams:
            self.console.print("[red]No team data available.[/red]")
            Prompt.ask("\nPress Enter to continue")
            return None
        
        # Show batting statistics first
        self.show_batting_stats(teams)
        
        # Show pitching statistics
        self.show_pitching_stats(teams)
        
        Prompt.ask("\nPress Enter to continue")
        return None
    
    def show_batting_stats(self, teams):
        """Show batting statistics for all teams"""
        self.console.print("\n[bold cyan]=== BATTING STATISTICS ===[/bold cyan]")
        
        # Collect all players with batting stats
        all_batters = []
        for team in teams:
            for player in team.get_all_players():
                if hasattr(player, 'batting_stats') and player.batting_stats:
                    # Calculate at-bats (hits + strikeouts + other outs)
                    at_bats = player.batting_stats.h + player.batting_stats.k + (player.batting_stats.ab - player.batting_stats.h - player.batting_stats.k)
                    if at_bats > 0:  # Only show players with at-bats
                        avg = player.batting_stats.h / at_bats if at_bats > 0 else 0.0
                        obp = (player.batting_stats.h + player.batting_stats.bb + player.batting_stats.hbp) / (at_bats + player.batting_stats.bb + player.batting_stats.hbp) if (at_bats + player.batting_stats.bb + player.batting_stats.hbp) > 0 else 0.0
                        
                        all_batters.append({
                            'player': player,
                            'team': team.name,
                            'avg': avg,
                            'obp': obp,
                            'h': player.batting_stats.h,
                            'hr': player.batting_stats.hr,
                            'rbi': player.batting_stats.h + player.batting_stats.bb,  # Simplified RBI calculation
                            'bb': player.batting_stats.bb,
                            'k': player.batting_stats.k,
                            'ab': at_bats,
                            'pa': player.batting_stats.pa
                        })
        
        # Sort by batting average (descending)
        all_batters.sort(key=lambda x: x['avg'], reverse=True)
        
        # Create batting stats table
        table = Table(title="Batting Statistics")
        table.add_column("Rank", style="cyan", width=4)
        table.add_column("Player", style="white", width=15)
        table.add_column("Team", style="yellow", width=10)
        table.add_column("AVG", style="blue", width=6)
        table.add_column("OBP", style="blue", width=6)
        table.add_column("H", style="green", width=4)
        table.add_column("HR", style="red", width=4)
        table.add_column("RBI", style="green", width=4)
        table.add_column("BB", style="blue", width=4)
        table.add_column("K", style="red", width=4)
        table.add_column("AB", style="blue", width=4)
        
        for i, batter in enumerate(all_batters, 1):
            table.add_row(
                str(i),
                batter['player'].name,
                batter['team'],
                f"{batter['avg']:.3f}",
                f"{batter['obp']:.3f}",
                str(batter['h']),
                str(batter['hr']),
                str(batter['rbi']),
                str(batter['bb']),
                str(batter['k']),
                str(batter['ab'])
            )
        
        self.console.print(table)
    
    def show_pitching_stats(self, teams):
        """Show pitching statistics for all teams"""
        self.console.print("\n[bold cyan]=== PITCHING STATISTICS ===[/bold cyan]")
        
        # Collect all players with pitching stats
        all_pitchers = []
        for team in teams:
            for player in team.get_all_players():
                if hasattr(player, 'pitching_stats') and player.pitching_stats and player.pitching_stats.gp > 0:
                    # Calculate ERA (earned runs per 6 innings, since MLW games are 3 innings)
                    era = (player.pitching_stats.er * 6) / player.pitching_stats.ip if player.pitching_stats.ip > 0 else 999.0
                    # Calculate WHIP (walks + hits per inning)
                    whip = (player.pitching_stats.bb + player.pitching_stats.h) / player.pitching_stats.ip if player.pitching_stats.ip > 0 else 999.0
                    
                    all_pitchers.append({
                        'player': player,
                        'team': team.name,
                        'era': era,
                        'whip': whip,
                        'w': player.pitching_stats.w,
                        'l': player.pitching_stats.l,
                        'k': player.pitching_stats.k,
                        'bb': player.pitching_stats.bb,
                        'ip': player.pitching_stats.ip,
                        'gp': player.pitching_stats.gp,
                        'gs': player.pitching_stats.gs
                    })
        
        # Sort by ERA (ascending - lower is better)
        all_pitchers.sort(key=lambda x: x['era'])
        
        # Create pitching stats table
        table = Table(title="Pitching Statistics")
        table.add_column("Rank", style="cyan", width=4)
        table.add_column("Player", style="white", width=15)
        table.add_column("Team", style="yellow", width=10)
        table.add_column("ERA", style="blue", width=6)
        table.add_column("WHIP", style="blue", width=6)
        table.add_column("W", style="green", width=4)
        table.add_column("L", style="red", width=4)
        table.add_column("K", style="green", width=4)
        table.add_column("BB", style="red", width=4)
        table.add_column("IP", style="blue", width=5)
        table.add_column("GP", style="blue", width=4)
        
        for i, pitcher in enumerate(all_pitchers, 1):
            table.add_row(
                str(i),
                pitcher['player'].name,
                pitcher['team'],
                f"{pitcher['era']:.2f}",
                f"{pitcher['whip']:.2f}",
                str(pitcher['w']),
                str(pitcher['l']),
                str(pitcher['k']),
                str(pitcher['bb']),
                f"{pitcher['ip']:.1f}",
                str(pitcher['gp'])
            )
        
        self.console.print(table)
    
    def show_season_results(self, results):
        """Show season results"""
        self.console.print("\n[bold green]Season Complete![/bold green]")
        
        # Show champion
        if results.get("champion"):
            self.console.print(f"[bold yellow]Champion: {results['champion'].name}[/bold yellow]")
        
        # Show final standings
        if results.get("standings"):
            table = Table(title="Final Standings")
            table.add_column("Rank", style="cyan")
            table.add_column("Team", style="white")
            table.add_column("GP", style="blue")
            table.add_column("W", style="green")
            table.add_column("L", style="red")
            table.add_column("PCT", style="blue")
            
            for i, team in enumerate(results["standings"], 1):
                games_played = team.wins + team.losses
                pct = f"{team.wins / games_played:.3f}" if games_played > 0 else ".000"
                table.add_row(str(i), team.name, str(games_played), str(team.wins), str(team.losses), pct)
            
            self.console.print(table)
        
        Prompt.ask("\nPress Enter to continue")
    
    def back_to_main(self):
        """Return to main menu"""
        return "quit"
    
    def quit_game(self):
        """Quit the game"""
        if Confirm.ask("Are you sure you want to quit?"):
            self.engine.quit_game()
            return "quit"
        return None

class GameMenu(BaseMenu):
    """Menu for managing a game"""
    
    def __init__(self, engine):
        super().__init__(engine)
        self.title = "Game Management"
        self.setup_items()
    
    def setup_items(self):
        """Setup menu items"""
        self.add_item("1", "View Lineups", self.view_lineups, "View both team lineups")
        self.add_item("2", "Set Lineup", self.set_lineup, "Set your team's lineup")
        self.add_item("3", "Play Game", self.play_game, "Start the game simulation")
        self.add_item("4", "Game Settings", self.game_settings, "Adjust game settings")
        self.add_item("b", "Back", self.back_to_season, "Return to season menu")
        self.add_item("q", "Quit", self.quit_game, "Exit the game")
    
    def view_lineups(self):
        """View both team lineups"""
        game = self.engine.get_game_data("current_game")
        if game:
            self.console.print(f"\n[bold cyan]{game.home_team.name} Lineup:[/bold cyan]")
            for i, player in enumerate(game.home_team.active_roster, 1):
                self.console.print(f"  {i}. {player.name}")
            
            self.console.print(f"\n[bold cyan]{game.away_team.name} Lineup:[/bold cyan]")
            for i, player in enumerate(game.away_team.active_roster, 1):
                self.console.print(f"  {i}. {player.name}")
            
            Prompt.ask("\nPress Enter to continue")
        return None
    
    def set_lineup(self):
        """Set team lineup"""
        game = self.engine.get_game_data("current_game")
        current_team = self.engine.get_game_data("current_team")
        
        if game and current_team:
            self.console.print("[yellow]Lineup setting coming soon...[/yellow]")
            Prompt.ask("\nPress Enter to continue")
        return None
    
    def play_game(self):
        """Play the game"""
        game = self.engine.get_game_data("current_game")
        game_sim = self.engine.get_game_data("game_simulator")
        
        if game and game_sim:
            self.console.print("[green]Starting game simulation...[/green]")
            
            # Simulate the game
            result = game_sim.simulate_game_with_result(game)
            
            # Show results
            self.show_game_results(result)
        return None
    
    def show_game_results(self, result):
        """Show game results"""
        self.console.print("\n[bold green]Game Complete![/bold green]")
        
        # Show final score
        if result.get("home_score") is not None and result.get("away_score") is not None:
            self.console.print(f"[bold]Final Score: {result['home_team'].name} {result['home_score']} - {result['away_team'].name} {result['away_score']}[/bold]")
        
        # Show winner
        if result.get("winner"):
            self.console.print(f"[bold yellow]Winner: {result['winner'].name}[/bold yellow]")
        
        # Show key stats
        if result.get("key_plays"):
            self.console.print("\n[bold]Key Plays:[/bold]")
            for play in result["key_plays"][:5]:  # Show first 5 plays
                self.console.print(f"• {play}")
        
        Prompt.ask("\nPress Enter to continue")
    
    def game_settings(self):
        """Game settings"""
        self.console.print("[yellow]Game settings coming soon...[/yellow]")
        Prompt.ask("\nPress Enter to continue")
        return None
    
    def back_to_season(self):
        """Return to season menu"""
        return "quit"
    
    def quit_game(self):
        """Quit the game"""
        if Confirm.ask("Are you sure you want to quit?"):
            self.engine.quit_game()
            return "quit"
        return None

class QuickGameMenu(BaseMenu):
    """Menu for quick game"""
    
    def __init__(self, engine):
        super().__init__(engine)
        self.title = "Quick Game"
        self.setup_items()
    
    def setup_items(self):
        """Setup menu items"""
        self.add_item("1", "View Teams", self.view_teams, "View both teams")
        self.add_item("2", "Set Lineups", self.set_lineups, "Set both team lineups")
        self.add_item("3", "Play Game", self.play_game, "Start the game")
        self.add_item("b", "Back to Main", self.back_to_main, "Return to main menu")
        self.add_item("q", "Quit", self.quit_game, "Exit the game")
    
    def view_teams(self):
        """View both teams"""
        game = self.engine.get_game_data("current_game")
        if game:
            self.console.print(f"\n[bold cyan]{game.home_team.name}[/bold cyan]")
            for player in game.home_team.active_players:
                self.console.print(f"  {player.name} - {player.position}")
            
            self.console.print(f"\n[bold cyan]{game.away_team.name}[/bold cyan]")
            for player in game.away_team.active_players:
                self.console.print(f"  {player.name} - {player.position}")
            
            Prompt.ask("\nPress Enter to continue")
        return None
    
    def set_lineups(self):
        """Set both team lineups"""
        game = self.engine.get_game_data("current_game")
        if game:
            # Set random lineups for quick game
            game.home_team.set_random_lineup()
            game.away_team.set_random_lineup()
            self.console.print("[green]Lineups set automatically for quick game![/green]")
            Prompt.ask("\nPress Enter to continue")
        return None
    
    def play_game(self):
        """Play the game"""
        game = self.engine.get_game_data("current_game")
        game_sim = self.engine.get_game_data("game_simulator")
        
        if game and game_sim:
            self.console.print("[green]Starting quick game...[/green]")
            
            # Simulate the game
            result = game_sim.simulate_game_with_result(game)
            
            # Show results
            self.show_game_results(result)
        return None
    
    def show_game_results(self, result):
        """Show game results"""
        self.console.print("\n[bold green]Game Complete![/bold green]")
        
        # Show final score
        if result.get("home_score") is not None and result.get("away_score") is not None:
            self.console.print(f"[bold]Final Score: {result['home_team'].name} {result['home_score']} - {result['away_team'].name} {result['away_score']}[/bold]")
        
        # Show winner
        if result.get("winner"):
            self.console.print(f"[bold yellow]Winner: {result['winner'].name}[/bold yellow]")
        
        Prompt.ask("\nPress Enter to continue")
    
    def back_to_main(self):
        """Return to main menu"""
        return "quit"
    
    def quit_game(self):
        """Quit the game"""
        if Confirm.ask("Are you sure you want to quit?"):
            self.engine.quit_game()
            return "quit"
        return None 