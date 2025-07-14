"""
Player model for Wiffle Ball Manager (MLW rules)
"""
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class BattingStats:
    gp: int = 0   # Games Played
    gs: int = 0   # Games Started
    pa: int = 0   # Plate Appearances
    ab: int = 0   # At Bats
    r: int = 0    # Runs
    h: int = 0    # Hits
    doubles: int = 0  # 2B
    triples: int = 0  # 3B
    hr: int = 0   # Home Runs
    rbi: int = 0  # Runs Batted In
    bb: int = 0   # Walks
    k: int = 0    # Strikeouts
    hbp: int = 0  # Hit By Pitch
    ibb: int = 0  # Intentional Walks
    lob: int = 0  # Left On Base
    tb: int = 0   # Total Bases
    obp: float = 0.0  # On-Base Percentage (calculated)
    slg: float = 0.0  # Slugging Percentage (calculated)
    ops: float = 0.0  # On-base Plus Slugging (calculated)

    @property
    def avg(self) -> float:
        if self.ab > 0:
            return round(self.h / self.ab, 3)
        return 0.0

    @property
    def calc_obp(self) -> float:
        denom = self.ab + self.bb + self.hbp
        if denom > 0:
            return round((self.h + self.bb + self.hbp) / denom, 3)
        return 0.0

    @property
    def calc_slg(self) -> float:
        if self.ab > 0:
            singles = self.h - self.doubles - self.triples - self.hr
            tb = singles + 2*self.doubles + 3*self.triples + 4*self.hr
            return round(tb / self.ab, 3)
        return 0.0

    @property
    def calc_ops(self) -> float:
        return round(self.calc_obp + self.calc_slg, 3)

@dataclass
class FieldingStats:
    po: int = 0   # Putouts
    a: int = 0    # Assists
    e: int = 0    # Errors
    dp: int = 0   # Double Plays
    fpct: float = 1.0  # Fielding Percentage (calculated)

    @property
    def calc_fpct(self) -> float:
        denom = self.po + self.a + self.e
        if denom > 0:
            return round((self.po + self.a) / denom, 3)
        return 1.0

@dataclass
class PitchingStats:
    gp: int = 0   # Games Pitched
    gs: int = 0   # Games Started
    ip: float = 0.0  # Innings Pitched
    r: int = 0    # Runs Allowed
    er: int = 0   # Earned Runs
    h: int = 0    # Hits Allowed
    bb: int = 0   # Walks Allowed
    hbp: int = 0  # Hit By Pitch
    ibb: int = 0  # Intentional Walks
    k: int = 0    # Strikeouts
    cg: int = 0   # Complete Games
    w: int = 0    # Wins
    l: int = 0    # Losses
    s: int = 0    # Saves
    hld: int = 0  # Holds
    bs: int = 0   # Blown Saves
    pt: int = 0   # Pitch Count
    b: int = 0    # Balls Thrown
    st: int = 0   # Strikes Thrown
    wp: int = 0   # Wild Pitches
    @property
    def era(self) -> float:
        if self.ip > 0:
            return round((self.er * 6) / self.ip, 2)
        return 0.0
    @property
    def whip(self) -> float:
        if self.ip > 0:
            return round((self.bb + self.h) / self.ip, 2)
        return 0.0
    @property
    def so_bb(self) -> float:
        if self.bb > 0:
            return round(self.k / self.bb, 2)
        return float(self.k)

@dataclass
class Player:
    name: str
    team: Optional[str] = None
    age: int = 20  # Default age
    retired: bool = False  # Retirement status
    # Core attributes (for simulation)
    velocity: int = 50
    control: int = 50
    stamina: int = 50
    speed_control: int = 50
    # Batting/fielding attributes can be added here
    batting_stats: BattingStats = field(default_factory=BattingStats)
    fielding_stats: FieldingStats = field(default_factory=FieldingStats)
    pitching_stats: PitchingStats = field(default_factory=PitchingStats) 