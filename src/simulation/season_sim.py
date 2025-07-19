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
    def __init__(self, teams: List[Team], games_per_season: int = 15, innings_per_game: int = 3, current_season: int = 1):
        self.teams = teams
        self.games_per_season = games_per_season
        self.innings_per_game = innings_per_game
        self.current_season = current_season
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
        
        # Rookie of the Year Award
        print("\n🌟 ROOKIE OF THE YEAR 🌟")
        self.show_rookie_of_year_award(all_players)
        
        if not qualified_hitters and not qualified_pitchers:
            print("No qualified players for leaderboards")

    def show_rookie_of_year_award(self, all_players: List):
        """Determine and display the Rookie of the Year award winner"""
        # Find all rookie players (first season players)
        rookies = []
        for player in all_players:
            # A rookie is someone who has only played in the current season
            if len(player.seasons_played) == 1:
                rookies.append(player)
        
        if not rookies:
            print("No eligible rookies this season")
            return
        
        # Calculate rookie value combining hitting and pitching performance
        rookie_candidates = []
        for rookie in rookies:
            value = self.calculate_rookie_value(rookie)
            if value > 0:  # Only include rookies with meaningful contributions
                team_name = next((team.name for team in self.teams if rookie in team.get_all_players()), 'Unknown')
                rookie_candidates.append({
                    'player': rookie,
                    'team': team_name,
                    'value': value,
                    'hitting_value': self.calculate_hitting_value(rookie),
                    'pitching_value': self.calculate_pitching_value(rookie)
                })
        
        if not rookie_candidates:
            print("No qualified rookie candidates this season")
            return
        
        # Sort by total value (highest first)
        rookie_candidates.sort(key=lambda x: x['value'], reverse=True)
        
        # Award winner
        winner = rookie_candidates[0]
        print(f"Rookie of the Year: {winner['player'].name} ({winner['team']}) - Value: {winner['value']:.1f}")
        
        # Show breakdown
        if winner['hitting_value'] > 0 and winner['pitching_value'] > 0:
            print(f"  Two-way player: {winner['hitting_value']:.1f} hitting + {winner['pitching_value']:.1f} pitching")
        elif winner['hitting_value'] > 0:
            print(f"  Hitter: {winner['hitting_value']:.1f} offensive value")
        else:
            print(f"  Pitcher: {winner['pitching_value']:.1f} pitching value")
        
        # Show runner-ups
        if len(rookie_candidates) > 1:
            print(f"  Runner-up: {rookie_candidates[1]['player'].name} ({rookie_candidates[1]['team']}) - Value: {rookie_candidates[1]['value']:.1f}")
        if len(rookie_candidates) > 2:
            print(f"  3rd place: {rookie_candidates[2]['player'].name} ({rookie_candidates[2]['team']}) - Value: {rookie_candidates[2]['value']:.1f}")
    
    def calculate_rookie_value(self, player) -> float:
        """Calculate overall rookie value combining hitting and pitching"""
        hitting_value = self.calculate_hitting_value(player)
        pitching_value = self.calculate_pitching_value(player)
        return hitting_value + pitching_value
    
    def calculate_hitting_value(self, player) -> float:
        """Calculate hitting value for rookie award"""
        if not hasattr(player, 'batting_stats') or not player.batting_stats:
            return 0.0
        
        stats = player.batting_stats
        
        # Minimum playing time requirement (at least 20 at-bats)
        if stats.ab < 20:
            return 0.0
        
        # Calculate hitting value based on production
        avg = stats.avg if stats.ab > 0 else 0.0
        obp = stats.calc_obp
        slg = stats.calc_slg
        
        # Base value from traditional stats
        value = 0.0
        value += avg * 30  # Batting average (0.300 = 9 points)
        value += obp * 25  # On-base percentage
        value += slg * 20  # Slugging percentage
        value += stats.hr * 2  # Home runs (2 points each)
        value += stats.rbi * 0.5  # RBIs (0.5 points each)
        value += stats.h * 0.3  # Hits (0.3 points each)
        
        # Playing time bonus (rewards regular players)
        if stats.gp >= 20:
            value *= 1.2  # 20% bonus for regulars
        elif stats.gp >= 15:
            value *= 1.1  # 10% bonus for semi-regulars
        
        return max(0.0, value)
    
    def calculate_pitching_value(self, player) -> float:
        """Calculate pitching value for rookie award"""
        if not hasattr(player, 'pitching_stats') or not player.pitching_stats:
            return 0.0
        
        stats = player.pitching_stats
        
        # Minimum playing time requirement (at least 5 games or 10 innings)
        if stats.gp < 5 and stats.ip < 10:
            return 0.0
        
        # Calculate pitching value based on performance
        value = 0.0
        
        # ERA (lower is better) - scale so 2.00 ERA = 10 points, 4.00 ERA = 5 points
        if stats.ip > 0:
            era = stats.era
            era_value = max(0, 15 - era * 2.5)  # 15 points for 0.00 ERA, decreasing
            value += era_value
        
        # Wins and strikeouts
        value += stats.w * 3  # 3 points per win
        value += stats.k * 0.2  # 0.2 points per strikeout
        
        # WHIP (walks + hits per inning) - lower is better
        if stats.ip > 0:
            whip = stats.whip
            whip_value = max(0, 5 - whip * 2)  # 5 points for 0.00 WHIP, decreasing
            value += whip_value
        
        # Innings pitched (durability)
        value += stats.ip * 0.1  # 0.1 points per inning
        
        # Usage bonus
        if stats.gp >= 15:
            value *= 1.3  # 30% bonus for workhorses
        elif stats.gp >= 10:
            value *= 1.2  # 20% bonus for regular starters
        elif stats.gp >= 5:
            value *= 1.1  # 10% bonus for part-time starters
        
        return max(0.0, value)

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
    
    def conduct_one_round_draft(self):
        """Conduct a 1-round draft where each team cuts their worst player and adds a drafted player"""
        print("\n" + "="*60)
        print("END OF SEASON DRAFT - 1 ROUND")
        print("Each team will cut their worst player and draft a new one")
        print("="*60)
        
        # Get draft order (worst teams pick first)
        draft_order = sorted(self.teams, key=lambda t: t.wins)
        
        # Generate draft prospects (mix of rookies and veterans)
        draft_prospects = self.generate_draft_prospects(len(self.teams))
        
        print(f"\nDraft Prospects Available:")
        for i, (prospect, prospect_type, ratings) in enumerate(draft_prospects, 1):
            print(f"{i:2d}. {prospect.name} [{prospect_type}] - {ratings}")
        
        # Conduct draft
        print(f"\nDraft Order (based on regular season record):")
        for i, team in enumerate(draft_order, 1):
            print(f"{i:2d}. {team.name} ({team.wins}-{team.losses})")
        
        print(f"\nDRAFT RESULTS:")
        print("-" * 60)
        
        for pick_num, team in enumerate(draft_order, 1):
            # Find worst player on team
            worst_player = self.find_worst_player(team)
            
            # Draft a prospect (teams pick in order)
            if pick_num <= len(draft_prospects):
                drafted_player, prospect_type, ratings = draft_prospects[pick_num - 1]
                
                # Cut worst player and add drafted player
                if worst_player:
                    team.remove_player(worst_player)
                    print(f"Pick {pick_num:2d}: {team.name}")
                    print(f"         ❌ Cut: {worst_player.name} (Value: {self.calculate_player_value(worst_player):.1f})")
                    print(f"         ✅ Drafted: {drafted_player.name} [{prospect_type}] - {ratings}")
                    
                    # Add drafted player to active roster
                    team.add_player(drafted_player, active=True)
                else:
                    print(f"Pick {pick_num:2d}: {team.name}")
                    print(f"         ✅ Drafted: {drafted_player.name} [{prospect_type}] - {ratings}")
                    print(f"         (No player cut - added to reserves)")
                    team.add_player(drafted_player, active=False)
                
                print()
        
        print("Draft completed! All teams have refreshed their rosters.")
    
    def generate_draft_prospects(self, num_prospects):
        """Generate a pool of draft prospects (mix of rookies and veterans)"""
        prospects = []
        
        for i in range(num_prospects):
            # 60% rookies, 40% veterans
            if random.random() < 0.6:
                prospect, prospect_type, ratings = self.generate_realistic_rookie()
            else:
                prospect, prospect_type, ratings = self.generate_veteran_prospect()
            
            prospects.append((prospect, prospect_type, ratings))
        
        return prospects
    
    def generate_veteran_prospect(self):
        """Generate a veteran free agent prospect"""
        first_names = ["Chris", "Mike", "John", "David", "Steve", "Tony", "Mark", "Paul"]
        last_names = ["Wilson", "Thompson", "Anderson", "Taylor", "Moore", "Jackson", "White", "Harris"]
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        
        # Veterans have better base stats but are older
        age = random.randint(26, 34)
        
        prospect_type = random.choices(
            ["Veteran Hitter", "Veteran Pitcher", "Veteran Utility"],
            weights=[0.4, 0.3, 0.3],
            k=1
        )[0]
        
        if prospect_type == "Veteran Hitter":
            batting = BattingStats()
            batting.h = random.randint(15, 30)
            batting.hr = random.randint(2, 8)
            batting.bb = random.randint(8, 15)
            batting.k = random.randint(10, 20)
            prospect = Player(
                name=name,
                age=age,
                velocity=random.randint(40, 60),
                control=random.randint(40, 60),
                stamina=random.randint(40, 60),
                speed_control=random.randint(40, 60),
                range=random.randint(70, 90),
                arm_strength=random.randint(60, 85),
                accuracy=random.randint(65, 90),
                batting_stats=batting
            )
            ratings = f"Age {age}, Bat: H={batting.h}, HR={batting.hr}, BB={batting.bb}"
        elif prospect_type == "Veteran Pitcher":
            pitching = PitchingStats()
            pitching.k = random.randint(15, 35)
            pitching.bb = random.randint(3, 12)
            prospect = Player(
                name=name,
                age=age,
                velocity=random.randint(65, 85),
                control=random.randint(65, 85),
                stamina=random.randint(65, 85),
                speed_control=random.randint(65, 85),
                range=random.randint(50, 70),
                arm_strength=random.randint(70, 90),
                accuracy=random.randint(55, 75),
                pitching_stats=pitching
            )
            ratings = f"Age {age}, Pitch: V={prospect.velocity}, C={prospect.control}, K={pitching.k}"
        else:  # Veteran Utility
            batting = BattingStats()
            batting.h = random.randint(10, 20)
            batting.hr = random.randint(1, 4)
            batting.bb = random.randint(5, 12)
            batting.k = random.randint(8, 15)
            pitching = PitchingStats()
            pitching.k = random.randint(8, 20)
            pitching.bb = random.randint(4, 12)
            prospect = Player(
                name=name,
                age=age,
                velocity=random.randint(55, 75),
                control=random.randint(55, 75),
                stamina=random.randint(55, 75),
                speed_control=random.randint(55, 75),
                range=random.randint(60, 80),
                arm_strength=random.randint(65, 85),
                accuracy=random.randint(60, 80),
                batting_stats=batting,
                pitching_stats=pitching
            )
            ratings = f"Age {age}, Utility: V={prospect.velocity}, H={batting.h}"
        
        return prospect, prospect_type, ratings
    
    def find_worst_player(self, team):
        """Find the worst player on a team based on overall value"""
        all_players = team.get_all_players()
        if not all_players:
            return None
        
        # Calculate value for each player and find the worst
        worst_player = None
        worst_value = float('inf')
        
        for player in all_players:
            value = self.calculate_player_value(player)
            if value < worst_value:
                worst_value = value
                worst_player = player
        
        return worst_player
    
    def calculate_player_value(self, player):
        """Calculate a player's overall value (simplified version of trading system)"""
        # Base value from attributes
        base_value = (player.velocity + player.control + player.stamina + player.speed_control) / 4.0
        
        # Age factor
        age_factor = 1.0
        if player.age < 25:
            age_factor = 1.2
        elif player.age > 30:
            age_factor = 0.8
        
        # Performance factor
        performance_factor = 1.0
        if hasattr(player, 'batting_stats') and player.batting_stats and player.batting_stats.ab > 0:
            if player.batting_stats.avg > 0.300:
                performance_factor += 0.2
            elif player.batting_stats.avg < 0.200:
                performance_factor -= 0.2
        
        if hasattr(player, 'pitching_stats') and player.pitching_stats and player.pitching_stats.ip > 0:
            if player.pitching_stats.era < 2.0:
                performance_factor += 0.2
            elif player.pitching_stats.era > 5.0:
                performance_factor -= 0.2
        
        # Retirement risk
        if player.age > 35:
            performance_factor *= 0.7
        
        return base_value * age_factor * performance_factor
    
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
    
    def progress_to_next_season(self):
        """Progress to the next season with roster continuity and player aging"""
        print("\n" + "="*60)
        print(f"PROGRESSING FROM SEASON {self.current_season} TO SEASON {self.current_season + 1}")
        print("="*60)
        
        # Complete current season for all players
        print(f"\nArchiving Season {self.current_season} statistics...")
        self.complete_season_for_all_players()
        
        # Age players and handle retirements
        print(f"\nProcessing player aging and retirements...")
        retired_players = self.age_players_and_handle_retirements()
        
        # Develop players for next season
        print(f"\nProcessing player development...")
        self.develop_players_for_next_season()
        
        # Conduct draft to refresh rosters
        print(f"\nConducting end-of-season draft...")
        self.conduct_one_round_draft()
        
        # Reset team records
        print(f"\nResetting team records for new season...")
        self.reset_team_records()
        
        # Increment season
        self.current_season += 1
        
        # Summary
        print(f"\n{'='*60}")
        print(f"READY FOR SEASON {self.current_season}")
        print(f"{'='*60}")
        print(f"Retired players: {len(retired_players)}")
        for player in retired_players:
            print(f"  - {player.get_career_summary()}")
        
        print(f"\nDraft completed and rosters refreshed. Season {self.current_season} ready to begin!")
        
        return {
            "new_season": self.current_season,
            "retired_players": retired_players,
            "total_active_players": sum(len(team.get_all_players()) for team in self.teams),
            "draft_completed": True
        }
    
    def complete_season_for_all_players(self):
        """Archive current season stats for all players"""
        for team in self.teams:
            for player in team.get_all_players():
                player.complete_season(self.current_season)
                player.reset_season_stats()
    
    def age_players_and_handle_retirements(self) -> List[Player]:
        """Age all players and handle retirements"""
        retired_players = []
        
        for team in self.teams:
            players_to_remove = []
            
            for player in team.get_all_players():
                # Age the player
                player.age += 1
                
                # Check for retirement
                if self.should_player_retire(player):
                    player.retired = True
                    retired_players.append(player)
                    players_to_remove.append(player)
            
            # Remove retired players from team
            for player in players_to_remove:
                team.remove_player(player)
        
        return retired_players
    
    def should_player_retire(self, player: Player) -> bool:
        """Determine if a player should retire based on age and performance"""
        if player.age < 35:
            return False
        
        # Retirement chances increase with age
        if player.age >= 40:
            return random.random() < 0.3  # 30% chance at 40+
        elif player.age >= 37:
            return random.random() < 0.15  # 15% chance at 37-39
        elif player.age >= 35:
            return random.random() < 0.05  # 5% chance at 35-36
        
        return False
    
    def develop_players_for_next_season(self):
        """Apply player development for the upcoming season"""
        from simulation.player_dev import PlayerDevelopment
        
        player_dev = PlayerDevelopment()
        for team in self.teams:
            players = team.get_all_players()
            if players:
                player_dev.develop_players(players)
    
    def reset_team_records(self):
        """Reset team win/loss records for new season"""
        for team in self.teams:
            team.wins = 0
            team.losses = 0
            # Reset playoff stats if they exist
            if hasattr(team, 'playoff_wins'):
                team.playoff_wins = 0
            if hasattr(team, 'playoff_losses'):
                team.playoff_losses = 0 