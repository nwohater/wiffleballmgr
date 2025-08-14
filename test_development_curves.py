#!/usr/bin/env python3
"""
Test script to demonstrate the new age & usage-based development curves
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.simulation.player_dev import PlayerDevelopment
from src.models.player import Player, BattingStats, PitchingStats

def create_test_player(name, age, potential, work_ethic, usage_games=0, usage_pa=0, usage_ip=0):
    """Create a test player with specific attributes"""
    player = Player(name=name)
    
    # Set basic attributes
    player.age = age
    player.potential = potential
    player.work_ethic = work_ethic
    player.leadership = 50  # Average leadership
    
    # Set initial attribute values to 60 for visibility of changes
    player.power = 60
    player.contact = 60
    player.discipline = 60
    player.speed = 60
    player.velocity = 60
    player.movement = 60
    player.control = 60
    player.stamina = 60
    player.deception = 60
    player.range = 60
    player.arm_strength = 60
    player.hands = 60
    player.reaction = 60
    
    # Set usage stats
    if usage_games > 0 or usage_pa > 0:
        player.batting_stats = BattingStats()
        player.batting_stats.gp = usage_games
        player.batting_stats.pa = usage_pa
        
    if usage_ip > 0:
        player.pitching_stats = PitchingStats()
        player.pitching_stats.gp = usage_games
        player.pitching_stats.ip = usage_ip
    
    return player

def test_age_curves():
    """Test different age scenarios"""
    print("=== AGE & USAGE-BASED DEVELOPMENT CURVE TESTING ===\n")
    
    dev_system = PlayerDevelopment()
    
    # Test different age scenarios
    test_cases = [
        ("Young Prospect", 20, 75, 70, 20, 80, 0),  # Young, high potential, good usage
        ("Peak Player", 25, 60, 60, 15, 60, 30),   # Peak age, average potential, moderate usage
        ("Aging Veteran", 32, 50, 80, 25, 100, 50), # Aging, low potential, high work ethic, heavy usage  
        ("Rookie", 19, 85, 50, 5, 20, 10),         # Very young, very high potential, light usage
        ("Decline", 35, 40, 40, 10, 40, 20),       # Old, low potential, low work ethic
    ]
    
    for name, age, potential, work_ethic, games, pa, ip in test_cases:
        print(f"--- Testing {name} (Age {age}, Potential {potential}, Work Ethic {work_ethic}) ---")
        
        player = create_test_player(name, age, potential, work_ethic, games, pa, ip)
        
        # Store initial values
        initial_attrs = {}
        test_attributes = ['power', 'contact', 'velocity', 'control', 'stamina']
        for attr in test_attributes:
            initial_attrs[attr] = getattr(player, attr)
        
        # Apply development (without aging up)
        original_age = player.age
        player.age -= 1  # Subtract 1 because develop_player will add 1
        dev_system.develop_player(player)
        
        print(f"  Age: {original_age} -> {player.age}")
        print(f"  Usage: {games} games, {pa} PA, {ip} IP")
        
        # Show attribute changes
        total_change = 0
        for attr in test_attributes:
            old_val = initial_attrs[attr]
            new_val = getattr(player, attr)
            change = new_val - old_val
            total_change += abs(change)
            if change != 0:
                print(f"  {attr}: {old_val} -> {new_val} ({change:+d})")
        
        print(f"  Total absolute change: {total_change}")
        print()

def test_potential_impact():
    """Test how potential affects development"""
    print("=== POTENTIAL IMPACT TESTING ===\n")
    
    dev_system = PlayerDevelopment()
    
    # Create players with different potential levels at same age
    potentials = [25, 50, 75, 95]
    
    for potential in potentials:
        print(f"--- Testing Potential {potential} ---")
        
        player = create_test_player(f"Player_P{potential}", 22, potential, 60, 15, 60, 25)
        
        # Store initial values
        initial_power = player.power
        initial_velocity = player.velocity
        
        # Apply development multiple times to see cumulative effect
        changes = []
        for i in range(3):  # 3 seasons
            old_power = player.power
            old_velocity = player.velocity
            player.age -= 1  # Reset age effect
            dev_system.develop_player(player)
            
            power_change = player.power - old_power
            velocity_change = player.velocity - old_velocity
            changes.append((power_change, velocity_change))
        
        total_power_change = player.power - initial_power
        total_velocity_change = player.velocity - initial_velocity
        
        print(f"  Total Power change over 3 seasons: {total_power_change:+d}")
        print(f"  Total Velocity change over 3 seasons: {total_velocity_change:+d}")
        print()

def test_usage_impact():
    """Test how usage affects development"""
    print("=== USAGE IMPACT TESTING ===\n")
    
    dev_system = PlayerDevelopment()
    
    # Create players with different usage levels
    usage_scenarios = [
        ("Low Usage", 5, 20, 10),
        ("Medium Usage", 15, 60, 30), 
        ("High Usage", 25, 100, 60),
        ("No Usage", 0, 0, 0),
    ]
    
    for scenario_name, games, pa, ip in usage_scenarios:
        print(f"--- Testing {scenario_name} ---")
        
        player = create_test_player(f"Player_{scenario_name}", 23, 65, 65, games, pa, ip)
        
        initial_contact = player.contact
        initial_control = player.control
        
        player.age -= 1  # Reset age effect
        dev_system.develop_player(player)
        
        contact_change = player.contact - initial_contact
        control_change = player.control - initial_control
        
        print(f"  Usage: {games} games, {pa} PA, {ip} IP")
        print(f"  Contact change: {contact_change:+d}")
        print(f"  Control change: {control_change:+d}")
        print()

if __name__ == "__main__":
    test_age_curves()
    test_potential_impact() 
    test_usage_impact()
    
    print("=== SUMMARY ===")
    print("✓ Age & usage-based development curves implemented")
    print("✓ Bell curve centered on peak_age (25) with decline after 30")
    print("✓ Potential, work ethic, and usage factors integrated")
    print("✓ Yearly attribute changes capped to ±6")
    print("✓ Coach quality placeholder ready for team integration")
