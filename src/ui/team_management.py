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
        
        # Team record
        record_text = f"Record: {team.wins}-{team.losses}-{team.ties}"
        runs_text = f"Runs: {team.runs_scored}-{team.runs_allowed}"
        
        stats_panel = Panel(
            f"{record_text}\n{runs_text}",
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
        table.add_column("Name", style=COLORS["HIGHLIGHT"])
        table.add_column("Age", style=COLORS["INFO"])
        table.add_column("V", style=COLORS["INFO"])
        table.add_column("C", style=COLORS["INFO"])
        table.add_column("S", style=COLORS["INFO"])
        table.add_column("SC", style=COLORS["INFO"])
        table.add_column("AVG", style=COLORS["INFO"])
        table.add_column("ERA", style=COLORS["INFO"])
        table.add_column("Status", style=COLORS["SUBTITLE"])
        
        # Add active players
        for player in team.active_roster:
            avg = f"{player.batting_stats.avg:.3f}" if player.batting_stats.ab > 0 else "N/A"
            era = f"{player.pitching_stats.era:.2f}" if player.pitching_stats.ip > 0 else "N/A"
            
            table.add_row(
                player.name,
                str(player.age),
                str(player.velocity),
                str(player.control),
                str(player.stamina),
                str(player.speed_control),
                avg,
                era,
                "Active"
            )
        
        # Add reserve players if requested
        if show_reserves:
            for player in team.reserve_roster:
                avg = f"{player.batting_stats.avg:.3f}" if player.batting_stats.ab > 0 else "N/A"
                era = f"{player.pitching_stats.era:.2f}" if player.pitching_stats.ip > 0 else "N/A"
                
                table.add_row(
                    player.name,
                    str(player.age),
                    str(player.velocity),
                    str(player.control),
                    str(player.stamina),
                    str(player.speed_control),
                    avg,
                    era,
                    "Reserve"
                )
        
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