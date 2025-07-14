#!/usr/bin/env python3
"""
Comprehensive test for all Wiffle Ball Manager enhancements
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.team import Team
from models.player import Player, BattingStats, PitchingStats
from simulation.season_sim import SeasonSimulator
from simulation.player_dev import PlayerDevelopment
from simulation.trading import TradingSystem, TradeOffer
from simulation.mlw_rules import MLWRules
from ui.team_management import TeamManagementUI
import random

def create_enhanced_test_teams():
    """Create test teams with realistic players for demonstration."""
    teams = []
    team_names = ["Thunder", "Lightning", "Storm", "Hurricane", "Tornado", "Cyclone"]
    
    for i, name in enumerate(team_names):
        team = Team(name=name, division="Test")
        
        # Create diverse players with different ages and abilities
        players = []
        
        # Add some veterans (older players)
        for j in range(2):
            player = Player(
                name=f"Veteran {j+1}",
                age=random.randint(28, 35),
                velocity=random.randint(60, 80),
                control=random.randint(60, 80),
                stamina=random.randint(50, 70),
                speed_control=random.randint(60, 80)
            )
            # Add some stats
            player.batting_stats.h = random.randint(15, 25)
            player.batting_stats.ab = random.randint(50, 80)
            player.pitching_stats.ip = random.randint(10, 20)
            player.pitching_stats.er = random.randint(5, 15)
            players.append(player)
        
        # Add some young players
        for j in range(2):
            player = Player(
                name=f"Young {j+1}",
                age=random.randint(19, 24),
                velocity=random.randint(50, 75),
                control=random.randint(50, 75),
                stamina=random.randint(60, 80),
                speed_control=random.randint(50, 75)
            )
            players.append(player)
        
        # Add some mid-career players
        for j in range(2):
            player = Player(
                name=f"Mid {j+1}",
                age=random.randint(25, 27),
                velocity=random.randint(55, 80),
                control=random.randint(55, 80),
                stamina=random.randint(55, 75),
                speed_control=random.randint(55, 80)
            )
            players.append(player)
        
        # Add players to team
        for j, player in enumerate(players):
            if j < 6:
                team.add_player(player, active=True)
            else:
                team.add_player(player, active=False)
        
        teams.append(team)
    
    return teams

def test_mlw_rules():
    """Test MLW rule enforcement"""
    print("=== Testing MLW Rules ===")
    rules = MLWRules()
    
    # Test speed limit
    fast_pitcher = Player(name="Speed Demon", velocity=80)
    slow_pitcher = Player(name="Control Artist", velocity=70)
    
    violation, msg = rules.check_speed_limit(fast_pitcher)
    print(f"Fast pitcher: {msg}")
    
    violation, msg = rules.check_speed_limit(slow_pitcher)
    print(f"Slow pitcher: {msg}")
    
    # Test roster validation
    team = Team(name="Test Team")
    for i in range(6):
        team.add_player(Player(name=f"Player {i+1}"), active=True)
    for i in range(2):
        team.add_player(Player(name=f"Reserve {i+1}"), active=False)
    
    valid, msg = rules.validate_roster(team)
    print(f"Roster validation: {msg}")
    
    # Test weather effects
    weather = rules.generate_weather()
    effects = rules.apply_weather_effects(weather)
    print(f"Weather: {weather}, Effects: {effects}")

def test_player_development():
    """Test player development system"""
    print("\n=== Testing Player Development ===")
    dev = PlayerDevelopment()
    
    # Create a test player
    player = Player(
        name="Test Player",
        age=22,
        velocity=60,
        control=65,
        stamina=70,
        speed_control=55
    )
    
    # Add some stats
    player.batting_stats.h = 20
    player.batting_stats.ab = 60
    player.pitching_stats.ip = 15
    player.pitching_stats.er = 8
    
    print(f"Before development: {player.name}, Age: {player.age}")
    print(f"  Velocity: {player.velocity}, Control: {player.control}")
    
    # Develop the player
    dev.develop_player(player)
    
    print(f"After development: {player.name}, Age: {player.age}")
    print(f"  Velocity: {player.velocity}, Control: {player.control}")

def test_trading_system():
    """Test trading system"""
    print("\n=== Testing Trading System ===")
    trading = TradingSystem()
    
    # Create two teams with different needs
    team_a = Team(name="Team A")
    team_b = Team(name="Team B")
    
    # Team A needs pitching
    for i in range(6):
        player = Player(name=f"Team A Player {i+1}", age=25)
        if i < 2:  # Only 2 pitchers
            player.pitching_stats.ip = 10
            player.pitching_stats.er = 15  # High ERA
        team_a.add_player(player, active=True)
    
    # Team B has good pitching
    for i in range(6):
        player = Player(name=f"Team B Player {i+1}", age=25)
        if i < 3:  # 3 good pitchers
            player.pitching_stats.ip = 15
            player.pitching_stats.er = 8  # Low ERA
        team_b.add_player(player, active=True)
    
    # AI proposes trade
    offer = trading.ai_propose_trade(team_a, [team_b])
    if offer:
        approved, reason = trading.evaluate_trade(offer)
        print(f"Trade proposed: {reason}")
        if approved:
            trading.execute_trade(offer)
    else:
        print("No suitable trade found")

def test_ui_features():
    """Test UI features"""
    print("\n=== Testing UI Features ===")
    ui = TeamManagementUI()
    
    # Create a test team
    team = Team(name="UI Test Team", division="Test")
    team.wins = 8
    team.losses = 4
    team.ties = 1
    team.runs_scored = 45
    team.runs_allowed = 32
    
    # Add some players with stats
    for i in range(6):
        player = Player(
            name=f"UI Player {i+1}",
            age=random.randint(20, 30),
            velocity=random.randint(50, 80),
            control=random.randint(50, 80),
            stamina=random.randint(50, 80),
            speed_control=random.randint(50, 80)
        )
        player.batting_stats.h = random.randint(10, 25)
        player.batting_stats.ab = random.randint(40, 70)
        player.pitching_stats.ip = random.randint(5, 20)
        player.pitching_stats.er = random.randint(3, 15)
        team.add_player(player, active=True)
    
    # Show team overview
    ui.show_team_overview(team)
    input("Press Enter to continue...")
    
    # Show roster
    ui.show_roster(team, show_reserves=True)
    input("Press Enter to continue...")

def main():
    """Run comprehensive enhancement tests"""
    print("=== Wiffle Ball Manager - Enhanced Features Test ===\n")
    
    # Test MLW rules
    test_mlw_rules()
    
    # Test player development
    test_player_development()
    
    # Test trading system
    test_trading_system()
    
    # Test UI features
    test_ui_features()
    
    # Test full season with all enhancements
    print("\n=== Testing Full Season with All Enhancements ===")
    teams = create_enhanced_test_teams()
    
    # Create season simulator
    simulator = SeasonSimulator(teams, games_per_season=15, innings_per_game=3)
    
    # Run season
    simulator.play_season()
    
    # Apply player development
    dev = PlayerDevelopment()
    for team in teams:
        dev.develop_players(team.get_all_players())
    
    # Show final standings
    print("\n=== Final Standings ===")
    teams.sort(key=lambda t: t.wins, reverse=True)
    for i, team in enumerate(teams, 1):
        print(f"{i}. {team.name}: {team.wins}-{team.losses}-{team.ties}")
    
    print(f"\nAll enhancements tested successfully!")

if __name__ == "__main__":
    main() 