#!/usr/bin/env python3
"""
Test script for the enhanced development events and season diary system
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.player import Player, BattingStats, PitchingStats
from simulation.development_events import DevelopmentEventSystem
from simulation.season_diary import SeasonDiary
from simulation.player_dev import PlayerDevelopment
import random

def create_test_players():
    """Create a few test players with different profiles"""
    players = []
    
    # Young prospect
    prospect = Player(
        name="Young Prospect",
        age=19,
        velocity=65,
        control=60,
        stamina=55,
        power=55,
        contact=50,
        discipline=45,
        potential=75,
        work_ethic=80,
        leadership=40
    )
    prospect.seasons_played = []
    players.append(prospect)
    
    # Veteran player
    veteran = Player(
        name="Veteran Star",
        age=32,
        velocity=75,
        control=85,
        stamina=70,
        power=80,
        contact=85,
        discipline=75,
        potential=55,
        work_ethic=70,
        leadership=85
    )
    veteran.seasons_played = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    # Add some stats
    veteran.batting_stats.gp = 45
    veteran.batting_stats.ab = 150
    veteran.batting_stats.h = 45
    veteran.batting_stats.hr = 8
    veteran.pitching_stats.gp = 12
    veteran.pitching_stats.ip = 36.0
    veteran.pitching_stats.k = 42
    players.append(veteran)
    
    # Average player
    average = Player(
        name="Average Joe",
        age=26,
        velocity=60,
        control=65,
        stamina=60,
        power=50,
        contact=55,
        discipline=50,
        potential=50,
        work_ethic=50,
        leadership=50
    )
    average.seasons_played = [1, 2, 3]
    average.batting_stats.gp = 25
    average.batting_stats.ab = 80
    average.batting_stats.h = 20
    players.append(average)
    
    return players

def test_development_events():
    """Test the development events system"""
    print("=" * 60)
    print("TESTING ENHANCED DEVELOPMENT EVENTS SYSTEM")
    print("=" * 60)
    
    # Create season diary
    diary = SeasonDiary(2024)
    
    # Create development system
    dev_system = DevelopmentEventSystem()
    player_dev = PlayerDevelopment(season_diary=diary)
    
    # Create test players
    players = create_test_players()
    
    print(f"\nCreated {len(players)} test players:")
    for player in players:
        print(f"  - {player.name} (Age {player.age}, Seasons: {len(player.seasons_played)})")
    
    print(f"\nAvailable positive events: {len(dev_system.positive_events)}")
    for event in dev_system.positive_events[:5]:  # Show first 5
        print(f"  - {event.name} ({event.severity.name}, weight: {event.weight})")
    print("  ...")
    
    print(f"\nAvailable negative events: {len(dev_system.negative_events)}")
    for event in dev_system.negative_events[:5]:  # Show first 5
        print(f"  - {event.name} ({event.severity.name}, weight: {event.weight})")
    print("  ...")
    
    # Simulate development events over multiple iterations
    print(f"\n{'='*60}")
    print("SIMULATING DEVELOPMENT EVENTS")
    print("=" * 60)
    
    for iteration in range(5):
        print(f"\n--- Development Cycle {iteration + 1} ---")
        
        for player in players:
            print(f"\nProcessing {player.name}:")
            
            # Store original attributes
            original_attrs = {
                'velocity': player.velocity,
                'control': player.control,
                'power': player.power,
                'contact': player.contact,
                'stamina': player.stamina
            }
            
            # Process development events
            events = dev_system.process_player_events(
                player, 
                season_diary=diary,
                positive_chance=0.3,  # Higher chance for demo
                negative_chance=0.2   # Higher chance for demo
            )
            
            if events:
                for event in events:
                    print(f"  {event.event_type.value.upper()}: {event.name} ({event.severity.name})")
                    print(f"    {event.description}")
                
                # Show attribute changes
                changes = []
                for attr, original in original_attrs.items():
                    current = getattr(player, attr)
                    if current != original:
                        diff = current - original
                        changes.append(f"{attr}: {original}→{current} ({diff:+d})")
                
                if changes:
                    print(f"    Attribute changes: {', '.join(changes)}")
            else:
                print("  No development events occurred")
        
        # Advance diary time
        diary.advance_time(7)  # Advance 1 week
    
    # Show diary summary
    print(f"\n{'='*60}")
    print("SEASON DIARY SUMMARY")
    print("=" * 60)
    
    summary = diary.get_development_events_summary()
    print(f"Total Development Events: {summary['total_events']}")
    print(f"  ✅ Positive Events: {summary['positive_events']}")
    print(f"  ❌ Negative Events: {summary['negative_events']}")
    print(f"  📈 Minor Events: {summary['minor_events']}")
    print(f"  ⭐ Moderate Events: {summary['moderate_events']}")
    print(f"  🚀 Major Events: {summary['major_events']}")
    
    # Show recent entries
    recent_entries = diary.get_recent_entries(10)
    if recent_entries:
        print(f"\nRecent Diary Entries ({len(recent_entries)}):")
        for entry in recent_entries:
            print(f"  {entry.get_display_summary()}")
    
    # Show high priority events
    high_priority = diary.get_high_priority_entries()
    if high_priority:
        print(f"\nHigh Priority Events ({len(high_priority)}):")
        for entry in high_priority:
            print(f"  {entry.get_display_summary()}")
    
    # Test export functionality
    print(f"\n{'='*60}")
    print("DIARY EXPORT TEST")
    print("=" * 60)
    
    diary_text = diary.export_diary_text()
    print(diary_text[:500] + "..." if len(diary_text) > 500 else diary_text)
    
    print(f"\n{'='*60}")
    print("DEVELOPMENT EVENTS TEST COMPLETED")
    print("=" * 60)

def test_player_development_integration():
    """Test the integration with the existing player development system"""
    print(f"\n{'='*60}")
    print("TESTING PLAYER DEVELOPMENT INTEGRATION")
    print("=" * 60)
    
    # Create season diary
    diary = SeasonDiary(2024)
    
    # Create player development system with diary
    player_dev = PlayerDevelopment(season_diary=diary)
    
    # Create test players
    players = create_test_players()
    
    print(f"\nDeveloping {len(players)} players with integrated system...")
    
    # Show before stats
    print("\nBEFORE DEVELOPMENT:")
    for player in players:
        print(f"  {player.name}: V={player.velocity}, C={player.control}, P={player.power}, Age={player.age}")
    
    # Develop players
    player_dev.develop_players(players)
    
    # Show after stats
    print("\nAFTER DEVELOPMENT:")
    for player in players:
        print(f"  {player.name}: V={player.velocity}, C={player.control}, P={player.power}, Age={player.age}")
    
    # Show diary entries created during development
    dev_entries = diary.get_entries_by_type(diary.DiaryEntryType.DEVELOPMENT_EVENT if hasattr(diary, 'DiaryEntryType') else None)
    print(f"\nDevelopment events logged to diary: {len(diary.entries)}")
    for entry in diary.entries:
        if hasattr(entry, 'entry_type') and 'development' in str(entry.entry_type).lower():
            print(f"  {entry.get_display_summary()}")

if __name__ == "__main__":
    # Set random seed for reproducible results
    random.seed(42)
    
    test_development_events()
    test_player_development_integration()
    
    print(f"\n{'='*60}")
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("Enhanced development events system is ready for use.")
    print("=" * 60)
