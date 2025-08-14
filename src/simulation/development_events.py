"""
Enhanced player development events system for Wiffle Ball Manager
Features weighted tables for positive/negative events with severity tiers
"""
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class EventType(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"

class EventSeverity(Enum):
    MINOR = 1
    MODERATE = 2
    MAJOR = 3

@dataclass
class DevelopmentEvent:
    """Represents a player development event"""
    name: str
    description: str
    event_type: EventType
    severity: EventSeverity
    weight: float  # Probability weight
    attribute_changes: Dict[str, Tuple[int, int]]  # attribute -> (min_change, max_change)
    duration: int = 0  # How long the effect lasts (0 = permanent)
    requires_conditions: Optional[Dict[str, any]] = None  # Conditions for event to trigger
    
    def apply_to_player(self, player, season_diary=None):
        """Apply the event effects to a player"""
        changes_made = {}
        
        for attribute, (min_change, max_change) in self.attribute_changes.items():
            if hasattr(player, attribute):
                current_value = getattr(player, attribute, 50)
                change = random.randint(min_change, max_change)
                new_value = max(1, min(100, current_value + change))
                setattr(player, attribute, new_value)
                changes_made[attribute] = change
        
        # Log to season diary if provided
        if season_diary:
            season_diary.log_development_event(player, self, changes_made)
        
        return changes_made

class DevelopmentEventSystem:
    """Manages the enhanced player development events system"""
    
    def __init__(self):
        self.positive_events = self._create_positive_events()
        self.negative_events = self._create_negative_events()
        
    def _create_positive_events(self) -> List[DevelopmentEvent]:
        """Create weighted table of positive development events"""
        return [
            # MINOR POSITIVE EVENTS (Higher frequency, smaller gains)
            DevelopmentEvent(
                name="Extra Batting Practice",
                description="spent extra time in the batting cage working on fundamentals",
                event_type=EventType.POSITIVE,
                severity=EventSeverity.MINOR,
                weight=15.0,
                attribute_changes={"power": (1, 3), "contact": (1, 2)}
            ),
            DevelopmentEvent(
                name="Pitching Form Adjustment",
                description="made a small adjustment to their pitching mechanics",
                event_type=EventType.POSITIVE,
                severity=EventSeverity.MINOR,
                weight=15.0,
                attribute_changes={"control": (1, 3), "movement": (0, 2)}
            ),
            DevelopmentEvent(
                name="Conditioning Routine",
                description="improved their physical conditioning",
                event_type=EventType.POSITIVE,
                severity=EventSeverity.MINOR,
                weight=12.0,
                attribute_changes={"stamina": (1, 3), "speed": (0, 2)}
            ),
            DevelopmentEvent(
                name="Mental Focus Training",
                description="worked with a sports psychologist on mental toughness",
                event_type=EventType.POSITIVE,
                severity=EventSeverity.MINOR,
                weight=10.0,
                attribute_changes={"discipline": (1, 2), "leadership": (1, 2)}
            ),
            DevelopmentEvent(
                name="Fielding Drills",
                description="dedicated extra time to defensive practice",
                event_type=EventType.POSITIVE,
                severity=EventSeverity.MINOR,
                weight=12.0,
                attribute_changes={"range": (1, 2), "hands": (1, 3), "reaction": (0, 2)}
            ),
            
            # MODERATE POSITIVE EVENTS (Medium frequency, good gains)
            DevelopmentEvent(
                name="Breakout Camp Performance",
                description="had an exceptional performance at a specialized training camp",
                event_type=EventType.POSITIVE,
                severity=EventSeverity.MODERATE,
                weight=8.0,
                attribute_changes={"power": (2, 4), "contact": (2, 4), "confidence": (3, 5)},
                requires_conditions={"age": ("<=", 26)}
            ),
            DevelopmentEvent(
                name="New Pitch Development",
                description="successfully developed a new pitch in their repertoire",
                event_type=EventType.POSITIVE,
                severity=EventSeverity.MODERATE,
                weight=6.0,
                attribute_changes={"movement": (3, 5), "deception": (2, 4), "control": (1, 2)}
            ),
            DevelopmentEvent(
                name="Veteran Mentorship",
                description="received valuable guidance from an experienced player",
                event_type=EventType.POSITIVE,
                severity=EventSeverity.MODERATE,
                weight=7.0,
                attribute_changes={"discipline": (2, 4), "leadership": (2, 3), "work_ethic": (1, 3)}
            ),
            DevelopmentEvent(
                name="Equipment Upgrade",
                description="found new equipment that better suits their style",
                event_type=EventType.POSITIVE,
                severity=EventSeverity.MODERATE,
                weight=5.0,
                attribute_changes={"power": (1, 3), "control": (1, 3), "accuracy": (2, 4)}
            ),
            DevelopmentEvent(
                name="Advanced Analytics Study",
                description="studied video and analytics to improve their approach",
                event_type=EventType.POSITIVE,
                severity=EventSeverity.MODERATE,
                weight=6.0,
                attribute_changes={"discipline": (2, 4), "contact": (1, 3), "control": (1, 3)}
            ),
            
            # MAJOR POSITIVE EVENTS (Low frequency, significant gains)
            DevelopmentEvent(
                name="Career Revival",
                description="experienced a dramatic turnaround in their career",
                event_type=EventType.POSITIVE,
                severity=EventSeverity.MAJOR,
                weight=2.0,
                attribute_changes={"power": (3, 6), "control": (3, 6), "stamina": (2, 4), "leadership": (3, 5)},
                requires_conditions={"age": (">=", 28)}
            ),
            DevelopmentEvent(
                name="Prospect Breakthrough",
                description="made a major developmental leap that exceeded expectations",
                event_type=EventType.POSITIVE,
                severity=EventSeverity.MAJOR,
                weight=3.0,
                attribute_changes={"potential": (5, 8), "power": (3, 5), "velocity": (3, 5), "contact": (2, 4)},
                requires_conditions={"age": ("<=", 24)}
            ),
            DevelopmentEvent(
                name="Perfect Game Achievement",
                description="threw a perfect game, boosting confidence and recognition",
                event_type=EventType.POSITIVE,
                severity=EventSeverity.MAJOR,
                weight=1.0,
                attribute_changes={"control": (4, 6), "deception": (3, 5), "stamina": (2, 4), "leadership": (3, 4)},
                requires_conditions={"pitching_stats.gp": (">=", 5)}
            ),
            DevelopmentEvent(
                name="Rookie Sensation",
                description="took the league by storm as an outstanding rookie",
                event_type=EventType.POSITIVE,
                severity=EventSeverity.MAJOR,
                weight=2.0,
                attribute_changes={"power": (3, 5), "contact": (3, 5), "velocity": (2, 4), "confidence": (4, 6)},
                requires_conditions={"seasons_played": ("==", 0)}
            )
        ]
    
    def _create_negative_events(self) -> List[DevelopmentEvent]:
        """Create weighted table of negative development events"""
        return [
            # MINOR NEGATIVE EVENTS (Higher frequency, small setbacks)
            DevelopmentEvent(
                name="Minor Slump",
                description="went through a brief rough patch",
                event_type=EventType.NEGATIVE,
                severity=EventSeverity.MINOR,
                weight=12.0,
                attribute_changes={"contact": (-1, -3), "discipline": (-1, -2)}
            ),
            DevelopmentEvent(
                name="Mechanics Drift",
                description="developed some bad habits in their technique",
                event_type=EventType.NEGATIVE,
                severity=EventSeverity.MINOR,
                weight=10.0,
                attribute_changes={"control": (-1, -3), "accuracy": (-1, -2)}
            ),
            DevelopmentEvent(
                name="Minor Fatigue",
                description="felt the effects of accumulated wear and tear",
                event_type=EventType.NEGATIVE,
                severity=EventSeverity.MINOR,
                weight=14.0,
                attribute_changes={"stamina": (-1, -2), "velocity": (-1, -2)}
            ),
            DevelopmentEvent(
                name="Confidence Dip",
                description="lost some confidence after a series of poor performances",
                event_type=EventType.NEGATIVE,
                severity=EventSeverity.MINOR,
                weight=11.0,
                attribute_changes={"discipline": (-1, -2), "leadership": (-1, -2)}
            ),
            DevelopmentEvent(
                name="Equipment Issues",
                description="struggled with equipment problems",
                event_type=EventType.NEGATIVE,
                severity=EventSeverity.MINOR,
                weight=8.0,
                attribute_changes={"power": (-1, -2), "control": (-1, -2)}
            ),
            
            # MODERATE NEGATIVE EVENTS (Medium frequency, noticeable setbacks)
            DevelopmentEvent(
                name="Minor Injury",
                description="suffered a minor injury that affected their performance",
                event_type=EventType.NEGATIVE,
                severity=EventSeverity.MODERATE,
                weight=6.0,
                attribute_changes={"stamina": (-2, -4), "velocity": (-1, -3), "durability": (-1, -2)},
                duration=3  # Effects last for 3 events/checks
            ),
            DevelopmentEvent(
                name="Mechanics Breakdown",
                description="experienced a significant breakdown in their fundamentals",
                event_type=EventType.NEGATIVE,
                severity=EventSeverity.MODERATE,
                weight=5.0,
                attribute_changes={"control": (-2, -4), "contact": (-2, -3), "accuracy": (-2, -3)}
            ),
            DevelopmentEvent(
                name="Pressure Struggles",
                description="struggled under pressure in key situations",
                event_type=EventType.NEGATIVE,
                severity=EventSeverity.MODERATE,
                weight=4.0,
                attribute_changes={"discipline": (-2, -4), "leadership": (-1, -3)}
            ),
            DevelopmentEvent(
                name="Conditioning Lapse",
                description="let their physical conditioning slip",
                event_type=EventType.NEGATIVE,
                severity=EventSeverity.MODERATE,
                weight=7.0,
                attribute_changes={"stamina": (-2, -4), "speed": (-1, -3), "durability": (-1, -2)}
            ),
            DevelopmentEvent(
                name="Focus Issues",
                description="developed concentration problems during games",
                event_type=EventType.NEGATIVE,
                severity=EventSeverity.MODERATE,
                weight=5.0,
                attribute_changes={"discipline": (-2, -3), "reaction": (-1, -3), "hands": (-1, -2)}
            ),
            
            # MAJOR NEGATIVE EVENTS (Low frequency, significant setbacks)
            DevelopmentEvent(
                name="Serious Injury",
                description="suffered a serious injury requiring extended recovery",
                event_type=EventType.NEGATIVE,
                severity=EventSeverity.MAJOR,
                weight=2.0,
                attribute_changes={"stamina": (-3, -6), "velocity": (-2, -4), "power": (-2, -4), "durability": (-3, -5)},
                duration=10  # Long-lasting effects
            ),
            DevelopmentEvent(
                name="Complete Mechanics Loss",
                description="lost all feel for their mechanics and struggled to find their form",
                event_type=EventType.NEGATIVE,
                severity=EventSeverity.MAJOR,
                weight=1.5,
                attribute_changes={"control": (-4, -6), "contact": (-3, -5), "accuracy": (-3, -5)}
            ),
            DevelopmentEvent(
                name="Personal Issues",
                description="dealt with significant personal problems affecting their game",
                event_type=EventType.NEGATIVE,
                severity=EventSeverity.MAJOR,
                weight=2.5,
                attribute_changes={"discipline": (-3, -5), "leadership": (-2, -4), "work_ethic": (-2, -4)}
            ),
            DevelopmentEvent(
                name="Career Threatening Injury",
                description="suffered an injury that threatened their career",
                event_type=EventType.NEGATIVE,
                severity=EventSeverity.MAJOR,
                weight=0.5,
                attribute_changes={"stamina": (-4, -8), "velocity": (-3, -6), "power": (-3, -6), "durability": (-4, -6)},
                duration=15,  # Very long-lasting effects
                requires_conditions={"age": (">=", 30)}
            )
        ]
    
    def check_event_conditions(self, player, event: DevelopmentEvent) -> bool:
        """Check if a player meets the conditions for an event to occur"""
        if not event.requires_conditions:
            return True
        
        for condition, (operator, value) in event.requires_conditions.items():
            # Handle nested attributes (e.g., "pitching_stats.gp")
            if "." in condition:
                obj_name, attr_name = condition.split(".", 1)
                if hasattr(player, obj_name):
                    obj = getattr(player, obj_name)
                    if hasattr(obj, attr_name):
                        player_value = getattr(obj, attr_name)
                    else:
                        continue
                else:
                    continue
            else:
                if hasattr(player, condition):
                    player_value = getattr(player, condition)
                else:
                    continue
            
            # Handle special cases
            if condition == "seasons_played":
                player_value = len(player.seasons_played)
            
            # Apply operator
            if operator == ">=":
                if not (player_value >= value):
                    return False
            elif operator == "<=":
                if not (player_value <= value):
                    return False
            elif operator == "==":
                if not (player_value == value):
                    return False
            elif operator == ">":
                if not (player_value > value):
                    return False
            elif operator == "<":
                if not (player_value < value):
                    return False
        
        return True
    
    def get_weighted_event(self, event_list: List[DevelopmentEvent], player) -> Optional[DevelopmentEvent]:
        """Select a weighted random event from a list, respecting conditions"""
        # Filter events based on conditions
        eligible_events = [event for event in event_list if self.check_event_conditions(player, event)]
        
        if not eligible_events:
            return None
        
        # Create weighted selection
        weights = [event.weight for event in eligible_events]
        return random.choices(eligible_events, weights=weights, k=1)[0]
    
    def process_player_events(self, player, season_diary=None, positive_chance=0.12, negative_chance=0.08) -> List[DevelopmentEvent]:
        """Process potential development events for a player"""
        events_occurred = []
        
        # Check for positive events
        if random.random() < positive_chance:
            positive_event = self.get_weighted_event(self.positive_events, player)
            if positive_event:
                positive_event.apply_to_player(player, season_diary)
                events_occurred.append(positive_event)
        
        # Check for negative events (independent of positive events)
        if random.random() < negative_chance:
            negative_event = self.get_weighted_event(self.negative_events, player)
            if negative_event:
                negative_event.apply_to_player(player, season_diary)
                events_occurred.append(negative_event)
        
        return events_occurred
    
    def get_event_summary(self, event: DevelopmentEvent, changes_made: Dict[str, int]) -> str:
        """Generate a summary string for an event"""
        change_strs = []
        for attr, change in changes_made.items():
            if change > 0:
                change_strs.append(f"+{change} {attr}")
            elif change < 0:
                change_strs.append(f"{change} {attr}")
        
        severity_str = f"[{event.severity.name}]"
        changes_str = ", ".join(change_strs) if change_strs else "no attribute changes"
        
        return f"{severity_str} {event.name}: {changes_str}"
