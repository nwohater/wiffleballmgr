"""
Season diary system for logging events and activities throughout the season
Provides a chronological record for UI display
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class DiaryEntryType(Enum):
    DEVELOPMENT_EVENT = "development_event"
    GAME_RESULT = "game_result"
    TRADE = "trade"
    INJURY = "injury"
    MILESTONE = "milestone"
    DRAFT = "draft"
    SEASON_END = "season_end"
    GENERAL = "general"

@dataclass
class DiaryEntry:
    """Represents a single entry in the season diary"""
    timestamp: datetime
    entry_type: DiaryEntryType
    title: str
    description: str
    player_name: Optional[str] = None
    team_name: Optional[str] = None
    game_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1  # 1=low, 2=medium, 3=high importance
    
    def get_display_summary(self) -> str:
        """Get a formatted summary for UI display"""
        timestamp_str = self.timestamp.strftime("%m/%d")
        
        if self.player_name and self.team_name:
            return f"[{timestamp_str}] {self.player_name} ({self.team_name}): {self.title}"
        elif self.player_name:
            return f"[{timestamp_str}] {self.player_name}: {self.title}"
        elif self.team_name:
            return f"[{timestamp_str}] {self.team_name}: {self.title}"
        else:
            return f"[{timestamp_str}] {self.title}"
    
    def get_full_description(self) -> str:
        """Get the full description with context"""
        context = ""
        if self.player_name and self.team_name:
            context = f"{self.player_name} ({self.team_name}) "
        elif self.player_name:
            context = f"{self.player_name} "
        elif self.team_name:
            context = f"{self.team_name} "
        
        return f"{context}{self.description}"

class SeasonDiary:
    """Manages the season diary system for logging events"""
    
    def __init__(self, season_number: int):
        self.season_number = season_number
        self.entries: List[DiaryEntry] = []
        self.current_game_week = 1
        self.current_date = datetime.now()
    
    def log_development_event(self, player, event, changes_made: Dict[str, int]):
        """Log a player development event"""
        # Create title based on event severity
        severity_icon = {
            "MINOR": "📈",
            "MODERATE": "⭐",
            "MAJOR": "🚀"
        }
        
        event_icon = {
            "positive": "✅",
            "negative": "❌"
        }
        
        icon = severity_icon.get(event.severity.name, "📈")
        type_icon = event_icon.get(event.event_type.value, "")
        
        title = f"{type_icon} {event.name}"
        
        # Create detailed description
        changes_str = []
        for attr, change in changes_made.items():
            if change > 0:
                changes_str.append(f"+{change} {attr}")
            elif change < 0:
                changes_str.append(f"{change} {attr}")
        
        changes_text = f" ({', '.join(changes_str)})" if changes_str else ""
        description = f"{event.description}{changes_text}"
        
        # Determine priority based on severity
        priority_map = {
            "MINOR": 1,
            "MODERATE": 2,
            "MAJOR": 3
        }
        
        priority = priority_map.get(event.severity.name, 1)
        
        # Get team name from player if available
        team_name = getattr(player, 'team', None)
        
        entry = DiaryEntry(
            timestamp=self.current_date,
            entry_type=DiaryEntryType.DEVELOPMENT_EVENT,
            title=title,
            description=description,
            player_name=player.name,
            team_name=team_name,
            priority=priority,
            metadata={
                "event_type": event.event_type.value,
                "severity": event.severity.name,
                "attribute_changes": changes_made,
                "event_name": event.name
            }
        )
        
        self.entries.append(entry)
    
    def log_game_result(self, home_team, away_team, home_score: int, away_score: int, game_id: str = None):
        """Log a game result"""
        winner = home_team if home_score > away_score else away_team
        loser = away_team if home_score > away_score else home_team
        winner_score = max(home_score, away_score)
        loser_score = min(home_score, away_score)
        
        title = f"{winner.name} defeats {loser.name}"
        description = f"defeated {loser.name} {winner_score}-{loser_score}"
        
        entry = DiaryEntry(
            timestamp=self.current_date,
            entry_type=DiaryEntryType.GAME_RESULT,
            title=title,
            description=description,
            team_name=winner.name,
            game_id=game_id,
            priority=2,
            metadata={
                "home_team": home_team.name,
                "away_team": away_team.name,
                "home_score": home_score,
                "away_score": away_score,
                "winner": winner.name,
                "loser": loser.name
            }
        )
        
        self.entries.append(entry)
    
    def log_injury(self, player, injury_type: str, expected_recovery: str = None):
        """Log a player injury"""
        title = f"🏥 {injury_type}"
        description = f"suffered a {injury_type.lower()}"
        
        if expected_recovery:
            description += f" (expected recovery: {expected_recovery})"
        
        team_name = getattr(player, 'team', None)
        
        entry = DiaryEntry(
            timestamp=self.current_date,
            entry_type=DiaryEntryType.INJURY,
            title=title,
            description=description,
            player_name=player.name,
            team_name=team_name,
            priority=3,
            metadata={
                "injury_type": injury_type,
                "expected_recovery": expected_recovery
            }
        )
        
        self.entries.append(entry)
    
    def log_milestone(self, player, milestone: str, details: str = ""):
        """Log a player milestone achievement"""
        title = f"🏆 {milestone}"
        description = f"achieved {milestone.lower()}"
        
        if details:
            description += f" ({details})"
        
        team_name = getattr(player, 'team', None)
        
        entry = DiaryEntry(
            timestamp=self.current_date,
            entry_type=DiaryEntryType.MILESTONE,
            title=title,
            description=description,
            player_name=player.name,
            team_name=team_name,
            priority=3,
            metadata={
                "milestone": milestone,
                "details": details
            }
        )
        
        self.entries.append(entry)
    
    def log_trade(self, player, from_team: str, to_team: str, trade_details: str = ""):
        """Log a trade transaction"""
        title = f"🔄 Traded to {to_team}"
        description = f"was traded from {from_team} to {to_team}"
        
        if trade_details:
            description += f" ({trade_details})"
        
        entry = DiaryEntry(
            timestamp=self.current_date,
            entry_type=DiaryEntryType.TRADE,
            title=title,
            description=description,
            player_name=player.name,
            team_name=to_team,
            priority=2,
            metadata={
                "from_team": from_team,
                "to_team": to_team,
                "trade_details": trade_details
            }
        )
        
        self.entries.append(entry)
    
    def log_draft_pick(self, player, team: str, round_num: int, pick_num: int):
        """Log a draft pick"""
        title = f"📋 Drafted by {team}"
        description = f"was selected by {team} in round {round_num}, pick {pick_num}"
        
        entry = DiaryEntry(
            timestamp=self.current_date,
            entry_type=DiaryEntryType.DRAFT,
            title=title,
            description=description,
            player_name=player.name,
            team_name=team,
            priority=2,
            metadata={
                "round": round_num,
                "pick": pick_num,
                "team": team
            }
        )
        
        self.entries.append(entry)
    
    def log_season_end(self, champion_team: str, standings: List):
        """Log season end results"""
        title = f"🏆 Season {self.season_number} Complete"
        description = f"{champion_team} wins the championship"
        
        entry = DiaryEntry(
            timestamp=self.current_date,
            entry_type=DiaryEntryType.SEASON_END,
            title=title,
            description=description,
            team_name=champion_team,
            priority=3,
            metadata={
                "champion": champion_team,
                "season": self.season_number,
                "final_standings": [{"team": team.name, "wins": team.wins, "losses": team.losses} for team in standings[:5]]
            }
        )
        
        self.entries.append(entry)
    
    def log_general_event(self, title: str, description: str, priority: int = 1, team_name: str = None, player_name: str = None):
        """Log a general event"""
        entry = DiaryEntry(
            timestamp=self.current_date,
            entry_type=DiaryEntryType.GENERAL,
            title=title,
            description=description,
            player_name=player_name,
            team_name=team_name,
            priority=priority
        )
        
        self.entries.append(entry)
    
    def advance_time(self, days: int = 1):
        """Advance the diary timeline"""
        from datetime import timedelta
        self.current_date += timedelta(days=days)
    
    def get_entries_by_type(self, entry_type: DiaryEntryType) -> List[DiaryEntry]:
        """Get all entries of a specific type"""
        return [entry for entry in self.entries if entry.entry_type == entry_type]
    
    def get_entries_by_player(self, player_name: str) -> List[DiaryEntry]:
        """Get all entries for a specific player"""
        return [entry for entry in self.entries if entry.player_name == player_name]
    
    def get_entries_by_team(self, team_name: str) -> List[DiaryEntry]:
        """Get all entries for a specific team"""
        return [entry for entry in self.entries if entry.team_name == team_name]
    
    def get_recent_entries(self, limit: int = 20) -> List[DiaryEntry]:
        """Get the most recent entries"""
        return sorted(self.entries, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_high_priority_entries(self) -> List[DiaryEntry]:
        """Get all high priority entries"""
        return [entry for entry in self.entries if entry.priority >= 3]
    
    def get_development_events_summary(self) -> Dict[str, int]:
        """Get a summary of development events"""
        dev_entries = self.get_entries_by_type(DiaryEntryType.DEVELOPMENT_EVENT)
        
        summary = {
            "total_events": len(dev_entries),
            "positive_events": 0,
            "negative_events": 0,
            "minor_events": 0,
            "moderate_events": 0,
            "major_events": 0
        }
        
        for entry in dev_entries:
            event_type = entry.metadata.get("event_type", "")
            severity = entry.metadata.get("severity", "")
            
            if event_type == "positive":
                summary["positive_events"] += 1
            elif event_type == "negative":
                summary["negative_events"] += 1
            
            if severity == "MINOR":
                summary["minor_events"] += 1
            elif severity == "MODERATE":
                summary["moderate_events"] += 1
            elif severity == "MAJOR":
                summary["major_events"] += 1
        
        return summary
    
    def export_diary_text(self) -> str:
        """Export the entire diary as formatted text"""
        sorted_entries = sorted(self.entries, key=lambda x: x.timestamp)
        
        text = f"Season {self.season_number} Diary\n"
        text += "=" * 40 + "\n\n"
        
        current_date = None
        for entry in sorted_entries:
            entry_date = entry.timestamp.strftime("%B %d, %Y")
            
            if entry_date != current_date:
                text += f"\n{entry_date}\n"
                text += "-" * len(entry_date) + "\n"
                current_date = entry_date
            
            text += f"• {entry.get_full_description()}\n"
        
        return text
