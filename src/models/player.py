"""
Player model for Wiffle Ball Manager (MLW rules)
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, List
from copy import deepcopy

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
            return round((self.er * 3) / self.ip, 2)  # MLW games are 3 innings
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
class CareerStats:
    """Career statistics that track season-by-season and totals"""
    # Season-by-season stats (key = season number)
    season_batting: Dict[int, BattingStats] = field(default_factory=dict)
    season_pitching: Dict[int, PitchingStats] = field(default_factory=dict) 
    season_fielding: Dict[int, FieldingStats] = field(default_factory=dict)
    
    # Career totals
    career_batting: BattingStats = field(default_factory=BattingStats)
    career_pitching: PitchingStats = field(default_factory=PitchingStats)
    career_fielding: FieldingStats = field(default_factory=FieldingStats)
    
    def add_season_stats(self, season: int, batting: BattingStats, pitching: PitchingStats, fielding: FieldingStats):
        """Add stats for a completed season and update career totals"""
        # Store season stats
        self.season_batting[season] = deepcopy(batting)
        self.season_pitching[season] = deepcopy(pitching)
        self.season_fielding[season] = deepcopy(fielding)
        
        # Update career totals
        self._update_career_batting(batting)
        self._update_career_pitching(pitching)
        self._update_career_fielding(fielding)
    
    def _update_career_batting(self, season_stats: BattingStats):
        """Update career batting totals"""
        c = self.career_batting
        s = season_stats
        c.gp += s.gp
        c.gs += s.gs
        c.pa += s.pa
        c.ab += s.ab
        c.r += s.r
        c.h += s.h
        c.doubles += s.doubles
        c.triples += s.triples
        c.hr += s.hr
        c.rbi += s.rbi
        c.bb += s.bb
        c.k += s.k
        c.hbp += s.hbp
        c.ibb += s.ibb
        c.lob += s.lob
        c.tb += s.tb
    
    def _update_career_pitching(self, season_stats: PitchingStats):
        """Update career pitching totals"""
        c = self.career_pitching
        s = season_stats
        c.gp += s.gp
        c.gs += s.gs
        c.ip += s.ip
        c.r += s.r
        c.er += s.er
        c.h += s.h
        c.bb += s.bb
        c.hbp += s.hbp
        c.ibb += s.ibb
        c.k += s.k
        c.cg += s.cg
        c.w += s.w
        c.l += s.l
        c.s += s.s
        c.hld += s.hld
        c.bs += s.bs
        c.pt += s.pt
        c.b += s.b
        c.st += s.st
        c.wp += s.wp
    
    def _update_career_fielding(self, season_stats: FieldingStats):
        """Update career fielding totals"""
        c = self.career_fielding
        s = season_stats
        c.po += s.po
        c.a += s.a
        c.e += s.e
        c.dp += s.dp
    
    def get_season_stats(self, season: int) -> tuple[BattingStats, PitchingStats, FieldingStats]:
        """Get stats for a specific season"""
        batting = self.season_batting.get(season, BattingStats())
        pitching = self.season_pitching.get(season, PitchingStats())
        fielding = self.season_fielding.get(season, FieldingStats())
        return batting, pitching, fielding
    
    def get_seasons_played(self) -> List[int]:
        """Get list of seasons this player has played"""
        return sorted(set(self.season_batting.keys()) | set(self.season_pitching.keys()) | set(self.season_fielding.keys()))

@dataclass
class Player:
    name: str
    team: Optional[str] = None
    age: int = 20  # Default age
    retired: bool = False  # Retirement status
    archetype: Optional[str] = None  # Player archetype (Power Hitter, Crafty Pitcher, etc.)
    
    # Hitting attributes
    power: int = 50
    contact: int = 50
    discipline: int = 50  # BB/K ratio
    speed: int = 50

    # Pitching attributes
    velocity: int = 50
    movement: int = 50
    control: int = 50
    stamina: int = 50
    deception: int = 50
    speed_control: int = 50  # Speed control for pitching

    # Fielding attributes
    range: int = 50
    arm_strength: int = 50
    hands: int = 50  # error rate
    reaction: int = 50
    accuracy: int = 50  # backward compatibility
    
    # Mental and personality traits
    potential: int = 50  # hidden rating that affects development
    leadership: int = 50
    work_ethic: int = 50
    durability: int = 50
    clutch: int = 50
    composure: int = 50
    
    # Physical attributes
    height: int = 70  # inches
    weight: int = 180  # pounds
    
    # Advanced derived attributes (calculated properties)
    @property
    def batting_eye(self) -> int:
        """Batting eye - combination of discipline and composure"""
        return min(100, (self.discipline + self.composure) // 2)
    
    @property
    def defensive_instincts(self) -> int:
        """Defensive instincts - combination of reaction and leadership"""
        return min(100, (self.reaction + self.leadership) // 2)
    
    @property
    def pitcher_mentality(self) -> int:
        """Pitcher mentality - combination of composure and leadership"""
        return min(100, (self.composure + self.leadership) // 2)
    
    # Fatigue tracking
    game_fatigue: float = 0.0  # Current game fatigue (0.0 to 1.0)
    season_fatigue: float = 0.0  # Cumulative season fatigue (0.0 to 1.0)
    rest_days: int = 0  # Days since last appearance
    appearances_this_week: int = 0  # Appearances in the last 7 days
    last_appearance_date: Optional[str] = None  # Track last game date
    
    # Current season stats (reset each season)
    batting_stats: BattingStats = field(default_factory=BattingStats)
    fielding_stats: FieldingStats = field(default_factory=FieldingStats)
    pitching_stats: PitchingStats = field(default_factory=PitchingStats)
    
    # Career/multi-season tracking
    career_stats: CareerStats = field(default_factory=CareerStats)
    seasons_played: List[int] = field(default_factory=list)
    
    def complete_season(self, season_number: int):
        """Complete a season by archiving current stats to career stats"""
        # Add current season stats to career tracking
        self.career_stats.add_season_stats(
            season_number,
            self.batting_stats,
            self.pitching_stats,
            self.fielding_stats
        )
        
        # Track which seasons this player has played
        if season_number not in self.seasons_played:
            self.seasons_played.append(season_number)
            self.seasons_played.sort()
    
    def reset_season_stats(self):
        """Reset current season stats for a new season"""
        self.batting_stats = BattingStats()
        self.pitching_stats = PitchingStats()
        self.fielding_stats = FieldingStats()
    
    def get_career_summary(self) -> str:
        """Get a summary of the player's career"""
        seasons = len(self.seasons_played)
        career_avg = self.career_stats.career_batting.avg
        career_era = self.career_stats.career_pitching.era
        
        summary = f"{self.name} (Age {self.age})"
        if seasons > 0:
            summary += f" - {seasons} seasons"
            if self.career_stats.career_batting.ab > 0:
                summary += f", .{int(career_avg * 1000):03d} BA"
            if self.career_stats.career_pitching.ip > 0:
                summary += f", {career_era:.2f} ERA"
        return summary 