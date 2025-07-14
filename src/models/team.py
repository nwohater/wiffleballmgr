"""
Team model for Wiffle Ball Manager (MLW rules)
"""
from dataclasses import dataclass, field
from typing import List, Optional
from .player import Player

@dataclass
class Team:
    name: str
    division: Optional[str] = None
    active_roster: List[Player] = field(default_factory=list)  # 6 active players
    reserve_roster: List[Player] = field(default_factory=list) # 2 reserve players
    wins: int = 0
    losses: int = 0
    ties: int = 0
    # Playoff stats (separate from regular season)
    playoff_wins: int = 0
    playoff_losses: int = 0
    # Team stats (aggregate, can be expanded)
    runs_scored: int = 0
    runs_allowed: int = 0
    # Add more team-level stats as needed

    def add_player(self, player: Player, active: bool = True) -> bool:
        """Add a player to the active or reserve roster."""
        if active and len(self.active_roster) < 6:
            self.active_roster.append(player)
            player.team = self.name
            return True
        elif not active and len(self.reserve_roster) < 2:
            self.reserve_roster.append(player)
            player.team = self.name
            return True
        return False

    def remove_player(self, player: Player) -> bool:
        """Remove a player from the team."""
        if player in self.active_roster:
            self.active_roster.remove(player)
            player.team = None
            return True
        elif player in self.reserve_roster:
            self.reserve_roster.remove(player)
            player.team = None
            return True
        return False

    def get_all_players(self) -> List[Player]:
        """Return all players on the team (active + reserve)."""
        return self.active_roster + self.reserve_roster

    def record_game_result(self, runs_scored: int, runs_allowed: int, result: str):
        """Update team record and stats after a game."""
        self.runs_scored += runs_scored
        self.runs_allowed += runs_allowed
        if result == "win":
            self.wins += 1
        elif result == "loss":
            self.losses += 1
        elif result == "tie":
            self.ties += 1 