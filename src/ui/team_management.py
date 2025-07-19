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
        """Display detailed player information with career stats grid"""
        self.console.clear()
        
        # Player header
        header = Text()
        header.append(f"{player.name}", style=COLORS["TITLE"])
        if player.team:
            header.append(f" - {player.team}", style=COLORS["DIM"])
        
        panel = Panel(header, border_style=COLORS["TITLE"])
        self.console.print(panel)
        
        # Basic info
        seasons_played = len(player.seasons_played) if player.seasons_played else 0
        info_panel = Panel(
            f"Age: {player.age}\n"
            f"Seasons Played: {seasons_played}\n"
            f"Retired: {'Yes' if player.retired else 'No'}\n"
            f"Velocity: {player.velocity}\n"
            f"Control: {player.control}\n"
            f"Stamina: {player.stamina}\n"
            f"Speed Control: {player.speed_control}",
            title="Player Info",
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
        
        # Show career stats grid if player has played multiple seasons
        if player.seasons_played and len(player.seasons_played) > 0:
            self.show_career_stats_grid(player)
        
        # Show current season stats if any
        self.show_current_season_stats(player)
    
    def show_career_stats_grid(self, player: Player):
        """Display career stats in a season-by-season grid"""
        seasons = player.seasons_played.copy() if player.seasons_played else []
        
        # Get current season number from game engine if available
        try:
            from game.engine import GameEngine
            # This is a bit of a hack, but we need to get the current season
            # In a real implementation, this should be passed as a parameter
            pass
        except:
            pass
        
        # Add current season to the list if player has current stats
        current_season_num = max(seasons) + 1 if seasons else 1
        has_current_batting = player.batting_stats.ab > 0
        has_current_pitching = player.pitching_stats.ip > 0
        
        if has_current_batting or has_current_pitching:
            if current_season_num not in seasons:
                seasons.append(current_season_num)
        
        if not seasons:
            return
        
        self.console.print(f"\n[bold {COLORS['TITLE']}]CAREER STATISTICS[/bold {COLORS['TITLE']}]")
        
        # Batting Stats Grid
        has_batting_stats = any(
            (player.career_stats.season_batting.get(season, None) and 
             player.career_stats.season_batting[season].ab > 0) or
            (season == current_season_num and player.batting_stats.ab > 0)
            for season in seasons
        )
        
        if has_batting_stats:
            batting_table = Table(title="Career Batting Stats", show_header=True, header_style="bold cyan")
            batting_table.add_column("Season", style="cyan", width=8)
            batting_table.add_column("GP", style="white", width=4)
            batting_table.add_column("AB", style="white", width=4)
            batting_table.add_column("H", style="green", width=4)
            batting_table.add_column("HR", style="yellow", width=4)
            batting_table.add_column("RBI", style="white", width=4)
            batting_table.add_column("BB", style="blue", width=4)
            batting_table.add_column("K", style="red", width=4)
            batting_table.add_column("AVG", style="green", width=6)
            batting_table.add_column("OBP", style="cyan", width=6)
            batting_table.add_column("SLG", style="yellow", width=6)
            
            for season in seasons:
                # Use archived stats for completed seasons, current stats for current season
                if season == current_season_num and has_current_batting:
                    batting_stats = player.batting_stats
                    season_label = f"Season {season}"
                else:
                    batting_stats = player.career_stats.season_batting.get(season)
                    season_label = f"Season {season}"
                
                if batting_stats and batting_stats.ab > 0:
                    batting_table.add_row(
                        season_label,
                        str(batting_stats.gp),
                        str(batting_stats.ab),
                        str(batting_stats.h),
                        str(batting_stats.hr),
                        str(batting_stats.rbi),
                        str(batting_stats.bb),
                        str(batting_stats.k),
                        f"{batting_stats.avg:.3f}",
                        f"{batting_stats.calc_obp:.3f}",
                        f"{batting_stats.calc_slg:.3f}"
                    )
            
            # Add combined totals row (career + current season)
            career_batting = player.career_stats.career_batting
            current_batting = player.batting_stats if has_current_batting else None
            
            # Calculate combined totals
            total_gp = career_batting.gp + (current_batting.gp if current_batting else 0)
            total_ab = career_batting.ab + (current_batting.ab if current_batting else 0)
            total_h = career_batting.h + (current_batting.h if current_batting else 0)
            total_hr = career_batting.hr + (current_batting.hr if current_batting else 0)
            total_rbi = career_batting.rbi + (current_batting.rbi if current_batting else 0)
            total_bb = career_batting.bb + (current_batting.bb if current_batting else 0)
            total_k = career_batting.k + (current_batting.k if current_batting else 0)
            
            # Calculate combined averages
            total_avg = total_h / total_ab if total_ab > 0 else 0.0
            total_obp_num = total_h + total_bb + (current_batting.hbp if current_batting else 0) + career_batting.hbp
            total_obp_denom = total_ab + total_bb + (current_batting.hbp if current_batting else 0) + career_batting.hbp
            total_obp = total_obp_num / total_obp_denom if total_obp_denom > 0 else 0.0
            
            # Simplified SLG calculation (assumes singles = h - 2b - 3b - hr, but we don't track 2b/3b separately)
            total_slg = total_avg + (total_hr * 3 / total_ab) if total_ab > 0 else 0.0  # Rough approximation
            
            if total_ab > 0:
                batting_table.add_row(
                    "[bold]TOTAL[/bold]",
                    f"[bold]{total_gp}[/bold]",
                    f"[bold]{total_ab}[/bold]",
                    f"[bold]{total_h}[/bold]",
                    f"[bold]{total_hr}[/bold]",
                    f"[bold]{total_rbi}[/bold]",
                    f"[bold]{total_bb}[/bold]",
                    f"[bold]{total_k}[/bold]",
                    f"[bold]{total_avg:.3f}[/bold]",
                    f"[bold]{total_obp:.3f}[/bold]",
                    f"[bold]{total_slg:.3f}[/bold]",
                    style="bold white"
                )
            
            self.console.print(batting_table)
        
        # Pitching Stats Grid
        has_pitching_stats = any(
            (player.career_stats.season_pitching.get(season, None) and 
             player.career_stats.season_pitching[season].ip > 0) or
            (season == current_season_num and player.pitching_stats.ip > 0)
            for season in seasons
        )
        
        if has_pitching_stats:
            pitching_table = Table(title="Career Pitching Stats", show_header=True, header_style="bold magenta")
            pitching_table.add_column("Season", style="cyan", width=8)
            pitching_table.add_column("GP", style="white", width=4)
            pitching_table.add_column("GS", style="white", width=4)
            pitching_table.add_column("IP", style="blue", width=6)
            pitching_table.add_column("W", style="green", width=3)
            pitching_table.add_column("L", style="red", width=3)
            pitching_table.add_column("K", style="yellow", width=4)
            pitching_table.add_column("BB", style="red", width=4)
            pitching_table.add_column("ERA", style="cyan", width=6)
            pitching_table.add_column("WHIP", style="magenta", width=6)
            
            for season in seasons:
                # Use archived stats for completed seasons, current stats for current season
                if season == current_season_num and has_current_pitching:
                    pitching_stats = player.pitching_stats
                    season_label = f"Season {season}"
                else:
                    pitching_stats = player.career_stats.season_pitching.get(season)
                    season_label = f"Season {season}"
                
                if pitching_stats and pitching_stats.ip > 0:
                    pitching_table.add_row(
                        season_label,
                        str(pitching_stats.gp),
                        str(pitching_stats.gs),
                        f"{pitching_stats.ip:.1f}",
                        str(pitching_stats.w),
                        str(pitching_stats.l),
                        str(pitching_stats.k),
                        str(pitching_stats.bb),
                        f"{pitching_stats.era:.2f}",
                        f"{pitching_stats.whip:.2f}"
                    )
            
            # Add combined totals row (career + current season)
            career_pitching = player.career_stats.career_pitching
            current_pitching = player.pitching_stats if has_current_pitching else None
            
            # Calculate combined totals
            total_gp = career_pitching.gp + (current_pitching.gp if current_pitching else 0)
            total_gs = career_pitching.gs + (current_pitching.gs if current_pitching else 0)
            total_ip = career_pitching.ip + (current_pitching.ip if current_pitching else 0.0)
            total_w = career_pitching.w + (current_pitching.w if current_pitching else 0)
            total_l = career_pitching.l + (current_pitching.l if current_pitching else 0)
            total_k = career_pitching.k + (current_pitching.k if current_pitching else 0)
            total_bb = career_pitching.bb + (current_pitching.bb if current_pitching else 0)
            total_er = career_pitching.er + (current_pitching.er if current_pitching else 0)
            total_h = career_pitching.h + (current_pitching.h if current_pitching else 0)
            
            # Calculate combined ERA and WHIP
            total_era = (total_er * 3) / total_ip if total_ip > 0 else 0.0  # MLW games are 3 innings
            total_whip = (total_bb + total_h) / total_ip if total_ip > 0 else 0.0
            
            if total_ip > 0:
                pitching_table.add_row(
                    "[bold]TOTAL[/bold]",
                    f"[bold]{total_gp}[/bold]",
                    f"[bold]{total_gs}[/bold]",
                    f"[bold]{total_ip:.1f}[/bold]",
                    f"[bold]{total_w}[/bold]",
                    f"[bold]{total_l}[/bold]",
                    f"[bold]{total_k}[/bold]",
                    f"[bold]{total_bb}[/bold]",
                    f"[bold]{total_era:.2f}[/bold]",
                    f"[bold]{total_whip:.2f}[/bold]",
                    style="bold white"
                )
            
            self.console.print(pitching_table)
    
    def show_current_season_stats(self, player: Player):
        """Show current season stats panels"""
        self.console.print(f"\n[bold {COLORS['WARNING']}]CURRENT SEASON STATS[/bold {COLORS['WARNING']}]")
        
        # Current season batting stats
        if player.batting_stats.ab > 0:
            batting_panel = Panel(
                f"Games: {player.batting_stats.gp}\n"
                f"At Bats: {player.batting_stats.ab}\n"
                f"Hits: {player.batting_stats.h}\n"
                f"Home Runs: {player.batting_stats.hr}\n"
                f"RBI: {player.batting_stats.rbi}\n"
                f"Walks: {player.batting_stats.bb}\n"
                f"Strikeouts: {player.batting_stats.k}\n"
                f"Average: {player.batting_stats.avg:.3f}\n"
                f"OBP: {player.batting_stats.calc_obp:.3f}\n"
                f"SLG: {player.batting_stats.calc_slg:.3f}\n"
                f"OPS: {player.batting_stats.calc_ops:.3f}",
                title="Current Season Batting",
                border_style=COLORS["SUCCESS"]
            )
            self.console.print(batting_panel)
        
        # Current season pitching stats
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
                title="Current Season Pitching",
                border_style=COLORS["WARNING"]
            )
            self.console.print(pitching_panel)
        
        # Current season fielding stats
        if (player.fielding_stats.po + player.fielding_stats.a + player.fielding_stats.e) > 0:
            fielding_panel = Panel(
                f"Putouts: {player.fielding_stats.po}\n"
                f"Assists: {player.fielding_stats.a}\n"
                f"Errors: {player.fielding_stats.e}\n"
                f"Double Plays: {player.fielding_stats.dp}\n"
                f"Fielding Pct: {player.fielding_stats.calc_fpct:.3f}",
                title="Current Season Fielding",
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