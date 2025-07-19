"""
Detailed game simulation for Wiffle Ball Manager (MLW rules)
"""
import random
from typing import List, Tuple, Optional
from src.models.team import Team
from src.models.player import Player, BattingStats, PitchingStats, FieldingStats

class AtBatResult:
    """Result of a single at-bat"""
    def __init__(self, outcome: str, details: str = "", runs_scored: int = 0, 
                 outs: int = 0, bases_advanced: int = 0):
        self.outcome = outcome  # hit, walk, strikeout, out, hbp, etc.
        self.details = details  # "single to left", "strikeout swinging", etc.
        self.runs_scored = runs_scored
        self.outs = outs
        self.bases_advanced = bases_advanced

class GameSimulator:
    """Detailed game simulation engine"""
    
    def __init__(self, home_team: Team, away_team: Team):
        self.home_team = home_team
        self.away_team = away_team
        self.current_pitcher_home: Optional[Player] = None
        self.current_pitcher_away: Optional[Player] = None
        self.home_lineup: List[Player] = []
        self.away_lineup: List[Player] = []
        self.home_score = 0
        self.away_score = 0
        self.inning = 1
        self.is_home_batting = False
        self.outs = 0
        self.bases: List[Optional[str]] = [None, None, None]  # 1B, 2B, 3B
        self.game_over = False
        
    def _simulate_full_game(self) -> Tuple[int, int]:
        """Simulate a complete MLW game with extra innings if tied"""
        self.setup_game()
        
        while not self.game_over:
            # Away team bats (top of inning)
            self.is_home_batting = False
            away_runs = self.simulate_half_inning()
            self.away_score += away_runs
            
            # Check mercy rule (6 runs per inning, before 3rd inning)
            if self.inning < 3 and away_runs >= 6:
                self.game_over = True
                break
                
            # Home team bats (bottom of inning)
            self.is_home_batting = True
            home_runs = self.simulate_half_inning()
            self.home_score += home_runs
            
            # Check mercy rule
            if self.inning < 3 and home_runs >= 6:
                self.game_over = True
                break
            
            # Check if game is over (home team wins if ahead after bottom of inning)
            if self.inning >= 3 and self.home_score > self.away_score:
                self.game_over = True
                break
            elif self.inning >= 3 and self.away_score > self.home_score:
                self.game_over = True
                break
            # If tied after 3+ innings, continue to extra innings
                
            self.inning += 1
            
        return self.away_score, self.home_score
    
    def simulate_game_with_result(self, game):
        """Simulate a game and return results"""
        self.home_team = game.home_team
        self.away_team = game.away_team
        
        # Call the actual game simulation method (not recursively!)
        away_score, home_score = self._simulate_full_game()
        
        # Determine winner
        winner = None
        if home_score > away_score:
            winner = game.home_team
            game.home_team.wins += 1
            game.away_team.losses += 1
            # Award win to home pitcher, loss to away pitcher
            if self.current_pitcher_home:
                self.current_pitcher_home.pitching_stats.w += 1
            if self.current_pitcher_away:
                self.current_pitcher_away.pitching_stats.l += 1
        elif away_score > home_score:
            winner = game.away_team
            game.away_team.wins += 1
            game.home_team.losses += 1
            # Award win to away pitcher, loss to home pitcher
            if self.current_pitcher_away:
                self.current_pitcher_away.pitching_stats.w += 1
            if self.current_pitcher_home:
                self.current_pitcher_home.pitching_stats.l += 1
        else:
            game.home_team.ties += 1
            game.away_team.ties += 1
            # No wins/losses for pitchers in ties
        
        # Update team stats
        game.home_team.runs_scored += home_score
        game.home_team.runs_allowed += away_score
        game.away_team.runs_scored += away_score
        game.away_team.runs_allowed += home_score
        
        return {
            "home_team": game.home_team,
            "away_team": game.away_team,
            "home_score": home_score,
            "away_score": away_score,
            "winner": winner,
            "key_plays": ["Game simulated successfully"]
        }
    
    def setup_game(self):
        """Setup lineups and starting pitchers"""
        # Note: Pitchers are now selected at the season level to respect usage limits
        # If no pitchers are set, fall back to best available
        if self.current_pitcher_home is None:
            self.current_pitcher_home = max(self.home_team.active_roster, 
                                          key=lambda p: p.velocity + p.control)
        if self.current_pitcher_away is None:
            self.current_pitcher_away = max(self.away_team.active_roster, 
                                          key=lambda p: p.velocity + p.control)
        
        # Create batting lineups (3-5 players)
        self.home_lineup = random.sample(self.home_team.active_roster, 
                                       min(5, len(self.home_team.active_roster)))
        self.away_lineup = random.sample(self.away_team.active_roster, 
                                       min(5, len(self.away_team.active_roster)))
        
        # Update batting games played for lineup players
        for player in self.home_lineup:
            player.batting_stats.gp += 1
        for player in self.away_lineup:
            player.batting_stats.gp += 1
        
        # Update pitcher stats
        self.current_pitcher_home.pitching_stats.gp += 1
        self.current_pitcher_home.pitching_stats.gs += 1
        self.current_pitcher_away.pitching_stats.gp += 1
        self.current_pitcher_away.pitching_stats.gs += 1
        
        # Add innings pitched tracking (3 innings per MLW game)
        self.current_pitcher_home.pitching_stats.ip += 3.0
        self.current_pitcher_away.pitching_stats.ip += 3.0
    
    def simulate_half_inning(self) -> int:
        """Simulate a half-inning and return runs scored"""
        self.outs = 0
        self.bases = [None, None, None]
        runs_scored = 0
        lineup = self.home_lineup if self.is_home_batting else self.away_lineup
        pitcher = self.current_pitcher_away if self.is_home_batting else self.current_pitcher_home
        batter_index = 0  # Track which batter is up
        max_batters = 30  # Safety limit to prevent infinite loops
        batters_faced = 0
        
        while self.outs < 3:
            if batters_faced >= max_batters:
                print(f"[WARNING] Max batters faced in an inning reached. Forcing inning end to prevent infinite loop.")
                print(f"  Final state: outs={self.outs}, runs={runs_scored}, batters_faced={batters_faced}")
                self.outs = 3  # Forcibly end the inning
                break
            # Get next batter
            batter = lineup[batter_index % len(lineup)]
            
            # Simulate at-bat
            if pitcher is not None:
                at_bat = self.simulate_at_bat(batter, pitcher)
                
                # Calculate runs that will be scored to track RBIs
                additional_runs = 0
                if at_bat.outcome == "walk" or at_bat.outcome == "hbp":
                    additional_runs = self.count_runners_that_will_score(1)
                elif at_bat.outcome == "hit":
                    additional_runs = self.count_runners_that_will_score(at_bat.bases_advanced)
                
                # Update stats with RBI information
                self.update_stats(at_bat, batter, pitcher, additional_runs)
            else:
                # Fallback if no pitcher (shouldn't happen)
                at_bat = AtBatResult("out", "No pitcher available")
                self.outs += 1
            
            # Update game state
            if at_bat.outcome == "hit":
                runs_scored += at_bat.runs_scored
                runs_scored += self.advance_runners(at_bat.bases_advanced)
            elif at_bat.outcome == "walk":
                runs_scored += self.advance_runners(1)
            elif at_bat.outcome == "hbp":
                runs_scored += self.advance_runners(1)
            elif at_bat.outcome == "strikeout":
                self.outs += 1
            elif at_bat.outcome == "out":
                self.outs += 1
            else:
                # Fallback: treat any unknown outcome as an out
                self.outs += 1
            batter_index += 1  # Always move to next batter
            batters_faced += 1
        
        # Track runs allowed for pitcher
        pitcher = self.current_pitcher_away if self.is_home_batting else self.current_pitcher_home
        if pitcher and runs_scored > 0:
            pitcher.pitching_stats.r += runs_scored
            pitcher.pitching_stats.er += runs_scored  # Simplified: all runs are earned
        
        return runs_scored
    
    def simulate_at_bat(self, batter: Player, pitcher: Player) -> AtBatResult:
        """Simulate a single at-bat using player skills"""
        # Speed limit check (75 mph)
        if pitcher.velocity > 75:
            # Automatic ball for exceeding speed limit
            return AtBatResult("walk", "Speed limit violation - automatic ball")
        
        # Calculate skill-based probabilities
        pitcher_control = pitcher.control / 100.0
        pitcher_velocity = pitcher.velocity / 100.0
        batter_contact = (batter.velocity + batter.control) / 200.0  # Using existing attributes for contact
        
        # Base probabilities that get modified by skills
        base_walk = 0.08
        base_hbp = 0.02
        base_strikeout = 0.25
        base_out = 0.50
        base_hit = 0.15
        
        # Modify based on pitcher control (better control = fewer walks, more strikeouts)
        control_modifier = (pitcher_control - 0.5) * 0.3  # ±15% max
        base_walk = max(0.02, base_walk - control_modifier)
        base_strikeout = min(0.45, base_strikeout + control_modifier * 0.5)
        
        # Modify based on batter contact (better contact = fewer strikeouts, more hits)
        contact_modifier = (batter_contact - 0.5) * 0.2  # ±10% max
        base_strikeout = max(0.15, base_strikeout - contact_modifier)
        base_hit = min(0.25, base_hit + contact_modifier * 0.3)
        
        # Clamp hit probability
        base_hit = min(0.20, max(0.05, base_hit))
        # Clamp walk probability
        base_walk = min(0.12, max(0.02, base_walk))
        # Clamp strikeout probability
        base_strikeout = min(0.40, max(0.15, base_strikeout))
        # Now, force out probability to be at least 0.35
        base_out = 1.0 - base_walk - base_hbp - base_strikeout - base_hit
        if base_out < 0.35:
            # Reduce hit and walk to make room for outs
            needed = 0.35 - base_out
            base_hit = max(0.05, base_hit - needed * 0.5)
            base_walk = max(0.02, base_walk - needed * 0.5)
            base_out = 1.0 - base_walk - base_hbp - base_strikeout - base_hit
        
        # Determine outcome based on skill-modified probabilities
        rand = random.random()
        if rand < base_walk:
            return AtBatResult("walk", "Walk")
        elif rand < base_walk + base_hbp:
            return AtBatResult("hbp", "Hit by pitch")
        elif rand < base_walk + base_hbp + base_strikeout:
            return AtBatResult("strikeout", "Strikeout")
        elif rand < base_walk + base_hbp + base_strikeout + base_out:
            return self.perform_fielding_check(batter, "ground_ball")
        else:
            return self.determine_hit_type(batter, pitcher)
    
    def determine_hit_type(self, batter: Player, pitcher: Player) -> AtBatResult:
        """Determine the type of hit based on player attributes"""
        # Calculate power based on batter attributes
        power = (batter.velocity + batter.control) / 200.0
        
        rand = random.random()
        
        if rand < 0.12 and power > 0.4:  # 12% chance of HR for decent power hitters
            return AtBatResult("hit", "Home run", runs_scored=self.count_runners() + 1, bases_advanced=4)
        elif rand < 0.15:  # 10% chance of triple
            # Triples can be caught by outfielders
            return self.perform_fielding_check(batter, "fly_ball", 
                                             AtBatResult("hit", "Triple", bases_advanced=3))
        elif rand < 0.35:  # 20% chance of double
            # Doubles can be fielded
            return self.perform_fielding_check(batter, "line_drive", 
                                             AtBatResult("hit", "Double", bases_advanced=2))
        else:  # 60% chance of single
            # Singles can be fielded
            return self.perform_fielding_check(batter, "ground_ball", 
                                             AtBatResult("hit", "Single", bases_advanced=1))
    
    def count_runners(self) -> int:
        """Count runners on base"""
        return sum(1 for base in self.bases if base is not None)
    
    def count_runners_that_will_score(self, bases_advanced: int) -> int:
        """Count how many runners will score based on bases advanced"""
        runs = 0
        for i, runner in enumerate(self.bases):
            if runner is not None:
                final_base = i + bases_advanced
                if final_base >= 3:  # Scores if reaches home (base 3+)
                    runs += 1
        return runs
    
    def advance_runners(self, bases: int):
        """Advance runners on base and return runs scored"""
        runs_scored = 0
        new_bases: List[Optional[str]] = [None, None, None]
        
        # Move existing runners
        for i, runner in enumerate(self.bases):
            if runner is not None:
                new_pos = i + bases
                if new_pos >= 3:
                    # Runner scores
                    runs_scored += 1
                else:
                    new_bases[new_pos] = runner
        
        # Place new batter on the appropriate base
        if bases >= 1:
            batter_base = min(bases - 1, 2)  # Convert to 0-indexed, max at 2nd base (index 2)
            if bases == 4:  # Home run - batter scores, doesn't occupy a base
                runs_scored += 1
            else:
                new_bases[batter_base] = "batter"  # Placeholder for actual batter
        
        self.bases = new_bases
        return runs_scored
    
    def update_stats(self, at_bat: AtBatResult, batter: Player, pitcher: Player, additional_rbi: int = 0):
        """Update player statistics based on at-bat result"""
        # Update batter stats
        batter.batting_stats.pa += 1
        
        if at_bat.outcome == "hit":
            batter.batting_stats.h += 1
            batter.batting_stats.ab += 1
            # Track RBIs for runs scored
            if "home run" in at_bat.details.lower():
                # Home runs already include all RBIs in runs_scored
                batter.batting_stats.rbi += at_bat.runs_scored
            else:
                # Other hits: runs from the hit + additional runners driven in
                batter.batting_stats.rbi += at_bat.runs_scored + additional_rbi
            if "single" in at_bat.details.lower():
                pass  # Single
            elif "double" in at_bat.details.lower():
                batter.batting_stats.doubles += 1
            elif "triple" in at_bat.details.lower():
                batter.batting_stats.triples += 1
            elif "home run" in at_bat.details.lower():
                batter.batting_stats.hr += 1
        elif at_bat.outcome == "walk":
            batter.batting_stats.bb += 1
            # Track RBIs for walks that drive in runs
            batter.batting_stats.rbi += additional_rbi
        elif at_bat.outcome == "hbp":
            batter.batting_stats.hbp += 1
            # Track RBIs for HBP that drive in runs
            batter.batting_stats.rbi += additional_rbi
        elif at_bat.outcome == "strikeout":
            batter.batting_stats.k += 1
            batter.batting_stats.ab += 1
            # Strikeouts don't award fielding stats - they're pitcher achievements
        elif at_bat.outcome == "out":
            batter.batting_stats.ab += 1
        
        # Update pitcher stats
        pitcher.pitching_stats.pt += 1
        
        if at_bat.outcome == "hit":
            pitcher.pitching_stats.h += 1
        elif at_bat.outcome == "walk":
            pitcher.pitching_stats.bb += 1
        elif at_bat.outcome == "hbp":
            pitcher.pitching_stats.hbp += 1
        elif at_bat.outcome == "strikeout":
            pitcher.pitching_stats.k += 1
            pitcher.pitching_stats.st += 1
        else:
            pitcher.pitching_stats.st += 1
    
    def perform_fielding_check(self, batter: Player, play_type: str, 
                              hit_result: Optional[AtBatResult] = None) -> AtBatResult:
        """Perform a fielding check to determine if defenders make the play"""
        # Get defensive team
        fielding_team = self.home_team if not self.is_home_batting else self.away_team
        
        # Calculate fielding skill based on play type
        # For 3-player wiffle ball, use all 3 fielders including pitcher
        current_pitcher = self.current_pitcher_home if not self.is_home_batting else self.current_pitcher_away
        non_pitcher_fielders = [p for p in fielding_team.active_roster 
                               if p != current_pitcher][:2]  # 2 non-pitcher fielders
        fielders = [current_pitcher] + non_pitcher_fielders  # All 3 defensive players
        
        if not fielders:
            # No fielders available, default outcome
            return hit_result or AtBatResult("out", "Ground out")
        
        # Calculate average fielding skill based on play type
        if play_type == "ground_ball":
            # Ground balls favor range and accuracy
            avg_skill = sum(p.range * 0.6 + p.accuracy * 0.4 for p in fielders) / len(fielders)
            fielding_chance = 0.3  # 30% of ground balls involve fielding checks
        elif play_type == "fly_ball":
            # Fly balls favor range and arm strength
            avg_skill = sum(p.range * 0.7 + p.arm_strength * 0.3 for p in fielders) / len(fielders)
            fielding_chance = 0.4  # 40% of fly balls involve fielding checks
        elif play_type == "line_drive":
            # Line drives favor range
            avg_skill = sum(p.range * 0.8 + p.accuracy * 0.2 for p in fielders) / len(fielders)
            fielding_chance = 0.25  # 25% of line drives involve fielding checks
        else:
            avg_skill = sum(p.range + p.accuracy + p.arm_strength for p in fielders) / (len(fielders) * 3)
            fielding_chance = 0.2
        
        # Roll for fielding check
        if random.random() > fielding_chance:
            # No fielding check - don't award fielding stats for routine plays
            # Most outs don't involve impressive fielding that should be tracked
            return hit_result or AtBatResult("out", "Ground out")
        
        # Perform fielding check - higher skill = more likely to make the play
        fielding_roll = random.randint(1, 100)
        success_threshold = avg_skill  # 1-100 scale matches our attributes
        
        if fielding_roll <= success_threshold:
            # Successful fielding play
            fielding_details = {
                "ground_ball": "fielded by infield",
                "fly_ball": "caught by outfield", 
                "line_drive": "snagged on the line"
            }.get(play_type, "fielded")
            
            # Update fielding stats for successful play
            best_fielder = max(fielders, key=lambda p: getattr(p, 'range', 50))
            
            if play_type == "ground_ball" and len(fielders) > 1:
                # Ground ball - fielder gets assist, another gets putout
                fielder_with_ball = random.choice(fielders)
                other_fielders = [f for f in fielders if f != fielder_with_ball]
                if other_fielders:
                    receiving_fielder = random.choice(other_fielders)
                    fielder_with_ball.fielding_stats.a += 1  # Assist for throw
                    receiving_fielder.fielding_stats.po += 1  # Putout for catch
                else:
                    fielder_with_ball.fielding_stats.po += 1  # Unassisted
            else:
                # Fly ball or line drive - just a putout
                best_fielder.fielding_stats.po += 1
            
            return AtBatResult("out", f"Out - {fielding_details}")
        else:
            # Fielding attempt failed
            if hit_result:
                # Hit stands, but maybe advance extra base on error
                if random.random() < 0.3:  # 30% chance of fielding error
                    worst_fielder = min(fielders, key=lambda p: getattr(p, 'accuracy', 50))
                    worst_fielder.fielding_stats.e += 1
                    
                    # Advance runners one extra base on error
                    if hit_result.bases_advanced < 4:
                        hit_result.bases_advanced += 1
                        hit_result.details += " (fielding error)"
                
                return hit_result
            else:
                # Failed to convert potential out to actual out - becomes a single
                return AtBatResult("hit", "Single on fielding mistake", bases_advanced=1) 