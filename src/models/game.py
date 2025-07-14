"""
Game simulation for Wiffle Ball Manager (MLW rules)
"""
from dataclasses import dataclass, field
from typing import List, Optional
from .team import Team
from .player import Player
from src.simulation.game_sim import GameSimulator

@dataclass
class GameResult:
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    winner: Optional[str] = None
    loser: Optional[str] = None
    is_tie: bool = False

@dataclass
class Game:
    home_team: Team
    away_team: Team
    innings: int = 3
    home_score: int = 0
    away_score: int = 0
    inning: int = 1
    is_over: bool = False
    result: Optional[GameResult] = None

    def play(self):
        """Simulate a full MLW game using detailed simulation."""
        # Use the detailed game simulator
        simulator = GameSimulator(self.home_team, self.away_team)
        result = simulator.simulate_game_with_result(self)
        
        self.home_score = result["home_score"]
        self.away_score = result["away_score"]
        self.is_over = True
        
        # Determine winner
        if self.home_score > self.away_score:
            winner = self.home_team.name
            loser = self.away_team.name
            is_tie = False
        elif self.away_score > self.home_score:
            winner = self.away_team.name
            loser = self.home_team.name
            is_tie = False
        else:
            winner = None
            loser = None
            is_tie = True
            
        self.result = GameResult(
            home_team=self.home_team.name,
            away_team=self.away_team.name,
            home_score=self.home_score,
            away_score=self.away_score,
            winner=winner,
            loser=loser,
            is_tie=is_tie
        )
        
        # Update team records
        if is_tie:
            self.home_team.record_game_result(self.home_score, self.away_score, "tie")
            self.away_team.record_game_result(self.away_score, self.home_score, "tie")
        else:
            self.home_team.record_game_result(self.home_score, self.away_score, "win" if winner == self.home_team.name else "loss")
            self.away_team.record_game_result(self.away_score, self.home_score, "win" if winner == self.away_team.name else "loss") 