"""
Season simulation for Wiffle Ball Manager (MLW rules)
"""
from typing import List, Dict, Tuple
from models.team import Team
from models.game import Game, GameResult
from models.player import Player, BattingStats, PitchingStats
from simulation.game_sim import GameSimulator
import random

class SeasonSimulator:
    def __init__(self, teams: List[Team], games_per_season: int = 15, innings_per_game: int = 3):
        self.teams = teams
        self.games_per_season = games_per_season
        self.innings_per_game = innings_per_game
        self.schedule = []  # List of (home_team, away_team) tuples
        self.series_schedule = []  # List of series (3 games each)
        self.results: List[dict] = []
        # Track pitcher usage for regular season series
        self.series_pitcher_usage: Dict[str, Dict[str, int]] = {}  # series_id -> {player_id -> games_pitched}

    def generate_schedule(self):
        """Generate a triple round-robin schedule: each team plays every other team 3 times."""
        self.schedule = []
        num_teams = len(self.teams)
        games_per_pair = 3
        for i in range(num_teams):
            for j in range(i + 1, num_teams):
                for _ in range(games_per_pair):
                    self.schedule.append((self.teams[i], self.teams[j]))
        random.shuffle(self.schedule)

    def organize_series(self):
        """Organize the schedule into 3-game series for regular season."""
        self.series_schedule = []
        games_per_series = 3
        
        # Group games into series
        for i in range(0, len(self.schedule), games_per_series):
            series_games = self.schedule[i:i + games_per_series]
            if len(series_games) == games_per_series:
                self.series_schedule.append(series_games)
        
        # Initialize pitcher usage tracking for each series
        for i, series in enumerate(self.series_schedule):
            series_id = f"series_{i+1}"
            self.series_pitcher_usage[series_id] = {}

    def get_available_pitcher(self, team: Team, series_id: str, is_playoff: bool = False) -> Player:
        """Get the best available pitcher for a team, respecting usage limits in regular season."""
        if is_playoff:
            # In playoffs, use best pitcher without restrictions
            return max(team.active_roster, key=lambda p: p.velocity + p.control)
        
        # In regular season, check usage limits
        usage = self.series_pitcher_usage.get(series_id, {})
        
        # Get all pitchers sorted by skill (velocity + control)
        available_pitchers = []
        for player in team.active_roster:
            games_pitched = usage.get(str(id(player)), 0)
            if games_pitched < 2:  # Can only pitch 2 games per 3-game series
                available_pitchers.append((player, games_pitched))
        
        if not available_pitchers:
            # If no pitchers available, use the one with least usage
            least_used = min(team.active_roster, key=lambda p: usage.get(str(id(p)), 0))
            print(f"[WARNING] {team.name} has no available pitchers for series {series_id}, using {least_used.name}")
            return least_used
        
        # Sort by skill (velocity + control), then by games pitched (prefer less used)
        available_pitchers.sort(key=lambda x: (x[1], -(x[0].velocity + x[0].control)))
        
        selected_pitcher = available_pitchers[0][0]
        games_pitched = available_pitchers[0][1]
        
        # Log pitcher selection for debugging
        if games_pitched > 0:
            print(f"    {team.name} using {selected_pitcher.name} (game {games_pitched + 1} of series)")
        else:
            print(f"    {team.name} using {selected_pitcher.name} (first game of series)")
        
        return selected_pitcher

    def record_pitcher_usage(self, pitcher: Player, series_id: str):
        """Record that a pitcher was used in a series."""
        if series_id not in self.series_pitcher_usage:
            self.series_pitcher_usage[series_id] = {}
        
        pitcher_id = str(id(pitcher))
        self.series_pitcher_usage[series_id][pitcher_id] = self.series_pitcher_usage[series_id].get(pitcher_id, 0) + 1

    def play_season(self):
        """Simulate the full season with series-based pitcher usage limits."""
        self.generate_schedule()
        self.organize_series()
        self.results = []
        
        print(f"Simulating {len(self.schedule)} regular season games in {len(self.series_schedule)} series...")
        
        # Play each series
        for series_num, series_games in enumerate(self.series_schedule, 1):
            series_id = f"series_{series_num}"
            print(f"\n=== Series {series_num} ===")
            
            for game_num, (home_team, away_team) in enumerate(series_games, 1):
                print(f"Game {game_num}/3: {home_team.name} vs {away_team.name}")
                
                # Create game simulator with pitcher selection
                game_sim = GameSimulator(home_team, away_team)
                
                # Set pitchers based on availability for this series
                home_pitcher = self.get_available_pitcher(home_team, series_id, is_playoff=False)
                away_pitcher = self.get_available_pitcher(away_team, series_id, is_playoff=False)
                
                # Override the default pitcher selection
                game_sim.current_pitcher_home = home_pitcher
                game_sim.current_pitcher_away = away_pitcher
                
                # Record pitcher usage
                self.record_pitcher_usage(home_pitcher, series_id)
                self.record_pitcher_usage(away_pitcher, series_id)
                
                print(f"  {home_team.name} starting pitcher: {home_pitcher.name}")
                print(f"  {away_team.name} starting pitcher: {away_pitcher.name}")
                
                # Simulate the game
                result = game_sim.simulate_game_with_result(Game(home_team, away_team))
                
                if result:
                    self.results.append(result)
            
            # Show series pitcher usage summary
            print(f"  Series {series_num} pitcher usage:")
            for team in [home_team, away_team]:
                team_usage = {}
                for player in team.active_roster:
                    player_id = str(id(player))
                    games_pitched = self.series_pitcher_usage[series_id].get(player_id, 0)
                    if games_pitched > 0:
                        team_usage[player.name] = games_pitched
                
                if team_usage:
                    usage_str = ", ".join([f"{name}: {games} games" for name, games in team_usage.items()])
                    print(f"    {team.name}: {usage_str}")
        
        print("Regular season complete! Playing playoffs...")
        
        # Store regular season standings before playoffs
        regular_season_standings = sorted(self.teams, key=lambda t: t.wins, reverse=True)
        
        # Reset team records for playoffs (so playoff games don't affect regular season standings)
        for team in self.teams:
            team.playoff_wins = 0
            team.playoff_losses = 0
        
        # After season, sort teams by regular season wins for playoffs
        self.teams.sort(key=lambda t: t.wins, reverse=True)
        self.play_playoffs()
        self.show_season_leaders()
        self.conduct_rookie_draft(rounds=2)
        
        # Restore regular season standings for final results
        self.teams = regular_season_standings

    def play_playoffs(self):
        """Simulate playoffs with best-of-5 semifinals and best-of-7 championship series."""
        if len(self.teams) < 4:
            return  # Not enough teams for playoffs
        
        semifinalists = self.teams[:4]
        print("\n=== PLAYOFFS ===")
        
        # Semifinals (Best of 5)
        final_teams = []
        for i in range(0, 4, 2):
            team1 = semifinalists[i]
            team2 = semifinalists[i+1]
            print(f"\nSemifinal Series: {team1.name} vs {team2.name} (Best of 5)")
            
            winner = self.play_series(team1, team2, best_of=5, series_name="Semifinal")
            final_teams.append(winner)
                
        # Championship Series (Best of 7)
        print(f"\nChampionship Series: {final_teams[0].name} vs {final_teams[1].name} (Best of 7)")
        champion = self.play_series(final_teams[0], final_teams[1], best_of=7, series_name="Championship")
        
        print(f"\n🏆 CHAMPION: {champion.name} 🏆")

    def play_series(self, team1: Team, team2: Team, best_of: int, series_name: str = "Series"):
        """Play a best-of-N series between two teams (no pitcher restrictions in playoffs)."""
        wins_needed = (best_of // 2) + 1
        team1_wins = 0
        team2_wins = 0
        game_num = 1
        
        while team1_wins < wins_needed and team2_wins < wins_needed:
            # Alternate home field advantage
            home_team = team1 if game_num % 2 == 1 else team2
            away_team = team2 if home_team == team1 else team1
            
            print(f"  Game {game_num}: {home_team.name} vs {away_team.name}")
            
            # For playoff games, we need to simulate without updating regular season stats
            game_sim = GameSimulator(home_team, away_team)
            
            # In playoffs, use best available pitchers (no restrictions)
            home_pitcher = self.get_available_pitcher(home_team, "playoff", is_playoff=True)
            away_pitcher = self.get_available_pitcher(away_team, "playoff", is_playoff=True)
            
            game_sim.current_pitcher_home = home_pitcher
            game_sim.current_pitcher_away = away_pitcher
            
            print(f"    {home_team.name} starting pitcher: {home_pitcher.name}")
            print(f"    {away_team.name} starting pitcher: {away_pitcher.name}")
            
            # Simulate the game directly without using simulate_game_with_result
            # to avoid updating regular season wins/losses
            away_score, home_score = game_sim._simulate_full_game()
            
            # Determine winner manually
            if home_score > away_score:
                winner = home_team
                loser = away_team
            elif away_score > home_score:
                winner = away_team
                loser = home_team
            else:
                # Handle ties if needed
                winner = home_team  # Home team wins in playoffs
                loser = away_team
            
            if winner == team1:
                team1_wins += 1
            else:
                team2_wins += 1
            
            winner.playoff_wins += 1
            loser.playoff_losses += 1
            
            print(f"    {winner.name} wins! Series: {team1.name} {team1_wins}-{team2_wins} {team2.name}")
            
            game_num += 1
        
        # Determine series winner
        if team1_wins >= wins_needed:
            print(f"  {series_name} Winner: {team1.name} ({team1_wins}-{team2_wins})")
            return team1
        else:
            print(f"  {series_name} Winner: {team2.name} ({team2_wins}-{team1_wins})")
            return team2

    def show_season_leaders(self):
        """Show the season leaders in various categories with titles."""
        print("\n=== SEASON LEADERS ===")
        
        # Collect all players from all teams
        all_players = []
        for team in self.teams:
            all_players.extend(team.get_all_players())
        
        # HITTING LEADERS (min 33 at-bats)
        qualified_hitters = []
        for player in all_players:
            if hasattr(player, 'batting_stats') and player.batting_stats:
                at_bats = player.batting_stats.h + player.batting_stats.k  # hits + strikeouts
                if at_bats >= 33:
                    avg = player.batting_stats.h / at_bats if at_bats > 0 else 0.0
                    # Calculate RBI (simplified: hits + walks)
                    rbi = player.batting_stats.h + player.batting_stats.bb
                    qualified_hitters.append({
                        'player': player,
                        'team': next((team.name for team in self.teams if player in team.get_all_players()), 'Unknown'),
                        'avg': avg,
                        'hr': player.batting_stats.hr,
                        'rbi': rbi,
                        'hits': player.batting_stats.h,
                        'at_bats': at_bats
                    })
        
        # PITCHING LEADERS (min 5 games pitched, min innings based on season length for ERA)
        qualified_pitchers = []
        # Calculate minimum innings based on season length (roughly half the season games)
        season_games = len(self.teams) * 3  # Each team plays every other team 3 times
        min_innings = max(5, season_games // 2)  # At least 5 innings, or roughly half season games
        
        for player in all_players:
            if hasattr(player, 'pitching_stats') and player.pitching_stats and player.pitching_stats.gp >= 5:
                # Calculate ERA (simplified: earned runs per game)
                era = player.pitching_stats.er / player.pitching_stats.gp if player.pitching_stats.gp > 0 else 999.0
                
                qualified_pitchers.append({
                    'player': player,
                    'team': next((team.name for team in self.teams if player in team.get_all_players()), 'Unknown'),
                    'era': era,
                    'wins': player.pitching_stats.w,
                    'k': player.pitching_stats.k,
                    'gp': player.pitching_stats.gp,
                    'ip': player.pitching_stats.ip
                })
        
        # Display Hitting Leaders
        print("\n🏆 HITTING LEADERS 🏆")
        
        # Batting Average King
        if qualified_hitters:
            avg_leader = max(qualified_hitters, key=lambda x: x['avg'])
            print(f"Batting Average King: {avg_leader['player'].name} ({avg_leader['team']}) - {avg_leader['avg']:.3f}")
        
        # Home Run King
        if qualified_hitters:
            hr_leader = max(qualified_hitters, key=lambda x: x['hr'])
            print(f"Home Run King: {hr_leader['player'].name} ({hr_leader['team']}) - {hr_leader['hr']} HR")
        
        # RBI Leader
        if qualified_hitters:
            rbi_leader = max(qualified_hitters, key=lambda x: x['rbi'])
            print(f"RBI Leader: {rbi_leader['player'].name} ({rbi_leader['team']}) - {rbi_leader['rbi']} RBI")
        
        # Display Pitching Leaders
        print("\n⚾ PITCHING LEADERS ⚾")
        
        # ERA Leader (lowest ERA, min innings based on season length)
        era_qualified = [p for p in qualified_pitchers if p['ip'] >= min_innings]
        if era_qualified:
            era_leader = min(era_qualified, key=lambda x: x['era'])
            print(f"ERA Leader: {era_leader['player'].name} ({era_leader['team']}) - {era_leader['era']:.2f} ERA")
        else:
            print(f"ERA Leader: No qualified pitchers (min {min_innings} IP)")
        
        # Wins Leader
        if qualified_pitchers:
            wins_leader = max(qualified_pitchers, key=lambda x: x['wins'])
            print(f"Wins Leader: {wins_leader['player'].name} ({wins_leader['team']}) - {wins_leader['wins']} W")
        
        # Strikeout King
        if qualified_pitchers:
            k_leader = max(qualified_pitchers, key=lambda x: x['k'])
            print(f"Strikeout King: {k_leader['player'].name} ({k_leader['team']}) - {k_leader['k']} K")
        
        if not qualified_hitters and not qualified_pitchers:
            print("No qualified players for leaderboards")

    def conduct_rookie_draft(self, rounds: int = 2):
        """Conduct a rookie draft with the lowest-ranked teams picking first. Rookies can be hitter-only, pitcher-only, or two-way."""
        num_teams = len(self.teams)
        draft_order = sorted(self.teams, key=lambda t: t.wins)  # Lowest wins pick first
        for rnd in range(1, rounds+1):
            print(f"\nRookie Draft - Round {rnd}")
            for team in draft_order:
                rookie, rookie_type, ratings = self.generate_realistic_rookie()
                team.add_player(rookie, active=False)  # Add to reserve by default
                print(f"{team.name} selects rookie {rookie.name} [{rookie_type}] {ratings}")

    def generate_realistic_rookie(self):
        """Generate a rookie as hitter-only, pitcher-only, or two-way, with appropriate attributes."""
        first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Drew", "Skyler"]
        last_names = ["Smith", "Johnson", "Lee", "Brown", "Garcia", "Martinez", "Davis", "Clark"]
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        rookie_type = random.choices(
            ["Hitter-only", "Pitcher-only", "Two-way"],
            weights=[0.4, 0.3, 0.3],
            k=1
        )[0]
        if rookie_type == "Hitter-only":
            # Strong batting, weak pitching
            batting = BattingStats()
            batting.h = random.randint(10, 20)
            batting.hr = random.randint(1, 5)
            batting.bb = random.randint(5, 10)
            batting.k = random.randint(5, 15)
            rookie = Player(
                name=name,
                velocity=random.randint(30, 50),
                control=random.randint(30, 50),
                stamina=random.randint(30, 50),
                speed_control=random.randint(30, 50),
                range=random.randint(60, 85),  # Hitters tend to be better fielders
                arm_strength=random.randint(50, 80),
                accuracy=random.randint(55, 85),
                batting_stats=batting
            )
            ratings = f"Bat: H={batting.h}, HR={batting.hr}, BB={batting.bb}, K={batting.k}"
        elif rookie_type == "Pitcher-only":
            # Strong pitching, weak batting
            pitching = PitchingStats()
            pitching.k = random.randint(10, 25)
            pitching.bb = random.randint(2, 8)
            rookie = Player(
                name=name,
                velocity=random.randint(60, 80),
                control=random.randint(60, 80),
                stamina=random.randint(60, 80),
                speed_control=random.randint(60, 80),
                range=random.randint(40, 65),  # Pitchers are typically weaker fielders
                arm_strength=random.randint(60, 85),  # But have good arms
                accuracy=random.randint(45, 70),
                pitching_stats=pitching
            )
            ratings = f"Pitch: V={rookie.velocity}, C={rookie.control}, K={pitching.k}, BB={pitching.bb}"
        else:  # Two-way
            batting = BattingStats()
            batting.h = random.randint(7, 15)
            batting.hr = random.randint(1, 3)
            batting.bb = random.randint(3, 8)
            batting.k = random.randint(5, 12)
            pitching = PitchingStats()
            pitching.k = random.randint(5, 15)
            pitching.bb = random.randint(3, 10)
            rookie = Player(
                name=name,
                velocity=random.randint(50, 70),
                control=random.randint(50, 70),
                stamina=random.randint(50, 70),
                speed_control=random.randint(50, 70),
                range=random.randint(50, 75),  # Balanced fielding ability
                arm_strength=random.randint(55, 80),
                accuracy=random.randint(50, 75),
                batting_stats=batting,
                pitching_stats=pitching
            )
            ratings = f"Bat: H={batting.h}, HR={batting.hr} | Pitch: V={rookie.velocity}, K={pitching.k}"
        return rookie, rookie_type, ratings
    
    def get_next_opponent(self, team):
        """Get the next opponent for a team"""
        if not self.schedule:
            self.generate_schedule()
        
        # Find next game for this team
        for home_team, away_team in self.schedule:
            if home_team == team:
                return away_team
            elif away_team == team:
                return home_team
        
        return None
    
    def get_standings(self):
        """Get current standings sorted by wins"""
        return sorted(self.teams, key=lambda t: t.wins, reverse=True)
    
    def get_remaining_schedule(self, team):
        """Get remaining schedule for a team"""
        if not self.schedule:
            self.generate_schedule()
        
        remaining = []
        for home_team, away_team in self.schedule:
            if home_team == team or away_team == team:
                remaining.append(Game(home_team, away_team))
        
        return remaining
    
    def simulate_full_season(self):
        """Simulate the full season and return results"""
        self.play_season()
        
        # Get final standings
        standings = self.get_standings()
        champion = standings[0] if standings else None
        
        return {
            "champion": champion,
            "standings": standings
        } 