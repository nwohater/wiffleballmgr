"""
Team management UI for Wiffle Ball Manager
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from typing import List, Optional
from models.team import Team
from models.player import Player
from utils.constants import COLORS

class TeamManagementUI:
    """UI for managing teams and viewing stats"""
    
    def __init__(self):
        self.console = Console()
    
    def show_team_overview(self, team: Team):
        """Display team overview with record and key stats"""
        self.console.clear()
        
        # Team header
        header = Text()
        header.append(f"{team.name}", style=COLORS["TITLE"])
        header.append(f" ({team.division})", style=COLORS["DIM"])
        
        panel = Panel(header, border_style=COLORS["TITLE"])
        self.console.print(panel)
        
        # Team record and run differential
        record_text = f"Record: {team.wins}-{team.losses}-{team.ties}"
        runs_text = f"Runs For: {team.runs_scored} | Runs Against: {team.runs_allowed}"
        
        # Calculate run differential
        run_diff = team.runs_scored - team.runs_allowed
        diff_text = f"Run Differential: {run_diff:+d}"  # + shows positive sign
        
        stats_panel = Panel(
            f"{record_text}\n{runs_text}\n{diff_text}",
            title="Season Stats",
            border_style=COLORS["INFO"]
        )
        self.console.print(stats_panel)
        
        # Roster summary
        active_count = len(team.active_roster)
        reserve_count = len(team.reserve_roster)
        
        roster_panel = Panel(
            f"Active Players: {active_count}/6\nReserve Players: {reserve_count}/2",
            title="Roster",
            border_style=COLORS["INFO"]
        )
        self.console.print(roster_panel)
    
    def show_roster(self, team: Team, show_reserves: bool = False):
        """Display team roster with player stats"""
        self.console.clear()
        
        # Create roster table
        table = Table(title=f"{team.name} Roster")
        table.add_column("#", style=COLORS["SUBTITLE"])
        table.add_column("Name", style=COLORS["HIGHLIGHT"])
        table.add_column("Age", style=COLORS["INFO"])
        table.add_column("V", style=COLORS["INFO"])
        table.add_column("C", style=COLORS["INFO"])
        table.add_column("S", style=COLORS["INFO"])
        table.add_column("SC", style=COLORS["INFO"])
        table.add_column("R", style=COLORS["SUCCESS"])
        table.add_column("AS", style=COLORS["SUCCESS"])
        table.add_column("A", style=COLORS["SUCCESS"])
        table.add_column("AVG", style=COLORS["INFO"])
        table.add_column("ERA", style=COLORS["INFO"])
        table.add_column("FPCT", style=COLORS["SUCCESS"])
        table.add_column("Status", style=COLORS["SUBTITLE"])
        
        # Add active players
        player_num = 1
        for player in team.active_roster:
            avg = f"{player.batting_stats.avg:.3f}" if player.batting_stats.ab > 0 else "N/A"
            era = f"{player.pitching_stats.era:.2f}" if player.pitching_stats.ip > 0 else "N/A"
            fpct = f"{player.fielding_stats.calc_fpct:.3f}" if (player.fielding_stats.po + player.fielding_stats.a + player.fielding_stats.e) > 0 else "N/A"
            
            table.add_row(
                str(player_num),
                player.name,
                str(player.age),
                str(player.velocity),
                str(player.control),
                str(player.stamina),
                str(player.speed_control),
                str(player.range),
                str(player.arm_strength),
                str(player.accuracy),
                avg,
                era,
                fpct,
                "Active"
            )
            player_num += 1
        
        # Add reserve players if requested
        if show_reserves:
            for player in team.reserve_roster:
                avg = f"{player.batting_stats.avg:.3f}" if player.batting_stats.ab > 0 else "N/A"
                era = f"{player.pitching_stats.era:.2f}" if player.pitching_stats.ip > 0 else "N/A"
                fpct = f"{player.fielding_stats.calc_fpct:.3f}" if (player.fielding_stats.po + player.fielding_stats.a + player.fielding_stats.e) > 0 else "N/A"
                
                table.add_row(
                    str(player_num),
                    player.name,
                    str(player.age),
                    str(player.velocity),
                    str(player.control),
                    str(player.stamina),
                    str(player.speed_control),
                    str(player.range),
                    str(player.arm_strength),
                    str(player.accuracy),
                    avg,
                    era,
                    fpct,
                    "Reserve"
                )
                player_num += 1
        
        self.console.print(table)
    
    def show_player_details(self, player: Player):
        """Display detailed player information"""
        self.console.clear()
        
        # Player header
        header = Text()
        header.append(f"{player.name}", style=COLORS["TITLE"])
        if player.team:
            header.append(f" - {player.team}", style=COLORS["DIM"])
        
        panel = Panel(header, border_style=COLORS["TITLE"])
        self.console.print(panel)
        
        # Basic info
        info_panel = Panel(
            f"Age: {player.age}\n"
            f"Retired: {'Yes' if player.retired else 'No'}\n"
            f"Velocity: {player.velocity}\n"
            f"Control: {player.control}\n"
            f"Stamina: {player.stamina}\n"
            f"Speed Control: {player.speed_control}",
            title="Attributes",
            border_style=COLORS["INFO"]
        )
        self.console.print(info_panel)
        
        # Fielding attributes
        fielding_attr_panel = Panel(
            f"Range: {player.range}\n"
            f"Arm Strength: {player.arm_strength}\n"
            f"Accuracy: {player.accuracy}",
            title="Fielding Attributes",
            border_style=COLORS["SUCCESS"]
        )
        self.console.print(fielding_attr_panel)
        
        # Batting stats
        if player.batting_stats.ab > 0:
            batting_panel = Panel(
                f"Games: {player.batting_stats.gp}\n"
                f"At Bats: {player.batting_stats.ab}\n"
                f"Hits: {player.batting_stats.h}\n"
                f"Home Runs: {player.batting_stats.hr}\n"
                f"Walks: {player.batting_stats.bb}\n"
                f"Strikeouts: {player.batting_stats.k}\n"
                f"Average: {player.batting_stats.avg:.3f}\n"
                f"OBP: {player.batting_stats.calc_obp:.3f}\n"
                f"SLG: {player.batting_stats.calc_slg:.3f}\n"
                f"OPS: {player.batting_stats.calc_ops:.3f}",
                title="Batting Stats",
                border_style=COLORS["SUCCESS"]
            )
            self.console.print(batting_panel)
        
        # Pitching stats
        if player.pitching_stats.ip > 0:
            pitching_panel = Panel(
                f"Games: {player.pitching_stats.gp}\n"
                f"Starts: {player.pitching_stats.gs}\n"
                f"Innings: {player.pitching_stats.ip:.1f}\n"
                f"Wins: {player.pitching_stats.w}\n"
                f"Losses: {player.pitching_stats.l}\n"
                f"Strikeouts: {player.pitching_stats.k}\n"
                f"Walks: {player.pitching_stats.bb}\n"
                f"ERA: {player.pitching_stats.era:.2f}\n"
                f"WHIP: {player.pitching_stats.whip:.2f}\n"
                f"K/BB: {player.pitching_stats.so_bb:.2f}",
                title="Pitching Stats",
                border_style=COLORS["WARNING"]
            )
            self.console.print(pitching_panel)
        
        # Fielding stats
        if (player.fielding_stats.po + player.fielding_stats.a + player.fielding_stats.e) > 0:
            fielding_panel = Panel(
                f"Putouts: {player.fielding_stats.po}\n"
                f"Assists: {player.fielding_stats.a}\n"
                f"Errors: {player.fielding_stats.e}\n"
                f"Double Plays: {player.fielding_stats.dp}\n"
                f"Fielding Pct: {player.fielding_stats.calc_fpct:.3f}",
                title="Fielding Stats",
                border_style=COLORS["SUCCESS"]
            )
            self.console.print(fielding_panel)
    
    def show_league_standings(self, teams: List[Team]):
        """Display league standings"""
        self.console.clear()
        
        # Sort teams by wins
        teams_sorted = sorted(teams, key=lambda t: t.wins, reverse=True)
        
        table = Table(title="League Standings")
        table.add_column("Rank", style=COLORS["HIGHLIGHT"])
        table.add_column("Team", style=COLORS["TITLE"])
        table.add_column("W", style=COLORS["SUCCESS"])
        table.add_column("L", style=COLORS["ERROR"])
        table.add_column("T", style=COLORS["WARNING"])
        table.add_column("PCT", style=COLORS["INFO"])
        table.add_column("RS", style=COLORS["INFO"])
        table.add_column("RA", style=COLORS["INFO"])
        
        for i, team in enumerate(teams_sorted, 1):
            total_games = team.wins + team.losses + team.ties
            pct = team.wins / total_games if total_games > 0 else 0.0
            
            table.add_row(
                str(i),
                team.name,
                str(team.wins),
                str(team.losses),
                str(team.ties),
                f"{pct:.3f}",
                str(team.runs_scored),
                str(team.runs_allowed)
            )
        
        self.console.print(table)
    
    def show_stat_leaders(self, teams: List[Team], stat_type: str = "batting"):
        """Display league leaders in various categories"""
        self.console.clear()
        
        all_players = []
        for team in teams:
            all_players.extend(team.active_roster)
            all_players.extend(team.reserve_roster)
        
        if stat_type == "batting":
            self.show_batting_leaders(all_players)
        elif stat_type == "pitching":
            self.show_pitching_leaders(all_players)
        elif stat_type == "fielding":
            self.show_fielding_leaders(all_players)
    
    def show_batting_leaders(self, players: List[Player]):
        """Show batting leaders"""
        # Filter players with at-bats
        batters = [p for p in players if p.batting_stats.ab > 0]
        
        if not batters:
            self.console.print("No batting stats available")
            return
        
        # Sort by different categories
        avg_leaders = sorted(batters, key=lambda p: p.batting_stats.avg, reverse=True)[:10]
        hr_leaders = sorted(batters, key=lambda p: p.batting_stats.hr, reverse=True)[:10]
        rbi_leaders = sorted(batters, key=lambda p: p.batting_stats.rbi, reverse=True)[:10]
        
        # Display tables
        self.console.print(Panel("Batting Average Leaders", style=COLORS["TITLE"]))
        table = Table()
        table.add_column("Rank")
        table.add_column("Player")
        table.add_column("Team")
        table.add_column("AVG")
        table.add_column("AB")
        
        for i, player in enumerate(avg_leaders, 1):
            table.add_row(
                str(i),
                player.name,
                player.team or "FA",
                f"{player.batting_stats.avg:.3f}",
                str(player.batting_stats.ab)
            )
        
        self.console.print(table)
    
    def show_pitching_leaders(self, players: List[Player]):
        """Show pitching leaders"""
        # Filter players with innings pitched
        pitchers = [p for p in players if p.pitching_stats.ip > 0]
        
        if not pitchers:
            self.console.print("No pitching stats available")
            return
        
        # Sort by different categories
        era_leaders = sorted(pitchers, key=lambda p: p.pitching_stats.era)[:10]
        k_leaders = sorted(pitchers, key=lambda p: p.pitching_stats.k, reverse=True)[:10]
        whip_leaders = sorted(pitchers, key=lambda p: p.pitching_stats.whip)[:10]
        
        # Display tables
        self.console.print(Panel("ERA Leaders", style=COLORS["TITLE"]))
        table = Table()
        table.add_column("Rank")
        table.add_column("Player")
        table.add_column("Team")
        table.add_column("ERA")
        table.add_column("IP")
        
        for i, player in enumerate(era_leaders, 1):
            table.add_row(
                str(i),
                player.name,
                player.team or "FA",
                f"{player.pitching_stats.era:.2f}",
                f"{player.pitching_stats.ip:.1f}"
            )
        
        self.console.print(table)
    
    def show_fielding_leaders(self, players: List[Player]):
        """Show fielding leaders"""
        # Filter players with fielding chances
        fielders = [p for p in players if (p.fielding_stats.po + p.fielding_stats.a + p.fielding_stats.e) > 0]
        
        if not fielders:
            self.console.print("No fielding stats available")
            return
        
        # Sort by fielding percentage (minimum 5 chances)
        fpct_leaders = sorted([p for p in fielders if (p.fielding_stats.po + p.fielding_stats.a + p.fielding_stats.e) >= 5], 
                             key=lambda p: p.fielding_stats.calc_fpct, reverse=True)[:10]
        
        # Display fielding percentage leaders
        self.console.print(Panel("Fielding Percentage Leaders", style=COLORS["TITLE"]))
        table = Table()
        table.add_column("Rank")
        table.add_column("Player")
        table.add_column("Team")
        table.add_column("FPCT")
        table.add_column("PO")
        table.add_column("A")
        table.add_column("E")
        
        for i, player in enumerate(fpct_leaders, 1):
            table.add_row(
                str(i),
                player.name,
                player.team or "FA",
                f"{player.fielding_stats.calc_fpct:.3f}",
                str(player.fielding_stats.po),
                str(player.fielding_stats.a),
                str(player.fielding_stats.e)
            )
        
        self.console.print(table)
    
    def select_team_to_view(self, teams: List[Team]) -> Optional[Team]:
        """Display team selection interface and return selected team"""
        self.console.clear()
        
        # Display teams in a table
        table = Table(title="Select Team to View")
        table.add_column("Number", style=COLORS["HIGHLIGHT"])
        table.add_column("Team", style=COLORS["TITLE"])
        table.add_column("Division", style=COLORS["SUBTITLE"])
        table.add_column("Record", style=COLORS["INFO"])
        
        for i, team in enumerate(teams, 1):
            record = f"{team.wins}-{team.losses}-{team.ties}"
            table.add_row(
                str(i),
                team.name,
                team.division,
                record
            )
        
        self.console.print(table)
        
        # Get user selection
        while True:
            try:
                choice = Prompt.ask(
                    f"\nSelect team (1-{len(teams)}) or 'b' to go back",
                    default="b"
                )
                
                if choice.lower() == 'b':
                    return None
                
                team_num = int(choice)
                if 1 <= team_num <= len(teams):
                    return teams[team_num - 1]
                else:
                    self.console.print(f"[{COLORS['ERROR']}]Please enter a number between 1 and {len(teams)}[/]")
            except ValueError:
                self.console.print(f"[{COLORS['ERROR']}]Please enter a valid number or 'b' to go back[/]")
    
    def select_player_from_roster(self, team: Team) -> Optional[Player]:
        """Allow user to select a player from the team roster for detailed view"""
        all_players = team.active_roster + team.reserve_roster
        
        if not all_players:
            self.console.print("[red]No players found on this team![/red]")
            return None
        
        while True:
            try:
                choice = Prompt.ask(
                    f"\nSelect player number (1-{len(all_players)}) for details, or 'b' to go back",
                    default="b"
                )
                
                if choice.lower() == 'b':
                    return None
                
                player_num = int(choice)
                if 1 <= player_num <= len(all_players):
                    return all_players[player_num - 1]
                else:
                    self.console.print(f"[{COLORS['ERROR']}]Please enter a number between 1 and {len(all_players)}[/]")
            except ValueError:
                self.console.print(f"[{COLORS['ERROR']}]Please enter a valid number or 'b' to go back[/]") 