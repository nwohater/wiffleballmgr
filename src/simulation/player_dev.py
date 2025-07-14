"""
Player development and aging system for Wiffle Ball Manager
"""
import random
from typing import List
from models.player import Player, BattingStats, PitchingStats

class PlayerDevelopment:
    """Handles player development, aging, and skill progression"""
    
    def __init__(self):
        self.peak_age = 25  # Peak performance age
        self.decline_start = 30  # Age when decline begins
        self.retirement_age = 40  # Age when players retire
        
    def develop_players(self, players: List[Player]):
        """Develop all players in a list (called at end of season)"""
        for player in players:
            self.develop_player(player)
    
    def develop_player(self, player: Player):
        """Develop a single player based on performance and age"""
        # Add age if not present
        if not hasattr(player, 'age'):
            player.age = random.randint(18, 35)  # Random age for existing players
        
        # Age the player
        player.age += 1
        
        # Check for retirement
        if player.age >= self.retirement_age:
            if random.random() < 0.3:  # 30% chance to retire
                player.retired = True
                return
        
        # Calculate development based on performance
        self.calculate_performance_bonus(player)
        
        # Apply aging effects
        self.apply_aging_effects(player)
        
        # Random development events
        self.random_development_events(player)
    
    def calculate_performance_bonus(self, player: Player):
        """Calculate development bonus based on season performance"""
        # Batting performance bonus
        if player.batting_stats.ab > 0:
            avg = player.batting_stats.avg
            if avg > 0.300:  # Good hitter
                self.improve_attribute(player, 'velocity', 1, 3)
                self.improve_attribute(player, 'control', 1, 2)
            elif avg < 0.200:  # Poor hitter
                self.improve_attribute(player, 'velocity', -2, -1)
                self.improve_attribute(player, 'control', -1, 0)
        
        # Pitching performance bonus
        if player.pitching_stats.ip > 0:
            era = player.pitching_stats.era
            if era < 2.0:  # Excellent pitcher
                self.improve_attribute(player, 'velocity', 1, 3)
                self.improve_attribute(player, 'control', 2, 4)
                self.improve_attribute(player, 'stamina', 1, 2)
            elif era > 5.0:  # Poor pitcher
                self.improve_attribute(player, 'velocity', -1, 0)
                self.improve_attribute(player, 'control', -2, -1)
                self.improve_attribute(player, 'stamina', -1, 0)
    
    def apply_aging_effects(self, player: Player):
        """Apply aging effects to player attributes"""
        if player.age < self.peak_age:
            # Young player - potential for growth
            if random.random() < 0.3:  # 30% chance for growth
                self.improve_attribute(player, 'velocity', 0, 2)
                self.improve_attribute(player, 'control', 0, 2)
                self.improve_attribute(player, 'stamina', 0, 2)
                self.improve_attribute(player, 'speed_control', 0, 2)
        
        elif player.age >= self.decline_start:
            # Aging player - decline
            decline_chance = (player.age - self.decline_start) / (self.retirement_age - self.decline_start)
            if random.random() < decline_chance:
                self.improve_attribute(player, 'velocity', -2, 0)
                self.improve_attribute(player, 'control', -1, 0)
                self.improve_attribute(player, 'stamina', -2, 0)
                self.improve_attribute(player, 'speed_control', -1, 0)
    
    def random_development_events(self, player: Player):
        """Random development events that can occur"""
        events = [
            ("Training breakthrough", 0.05, lambda p: self.improve_attribute(p, 'velocity', 2, 5)),
            ("Control improvement", 0.05, lambda p: self.improve_attribute(p, 'control', 2, 5)),
            ("Stamina boost", 0.05, lambda p: self.improve_attribute(p, 'stamina', 2, 5)),
            ("Speed control mastery", 0.05, lambda p: self.improve_attribute(p, 'speed_control', 2, 5)),
            ("Injury setback", 0.03, lambda p: self.improve_attribute(p, 'velocity', -3, -1)),
            ("Control issues", 0.03, lambda p: self.improve_attribute(p, 'control', -3, -1)),
        ]
        
        for event_name, chance, effect in events:
            if random.random() < chance:
                effect(player)
                print(f"{player.name}: {event_name}")
    
    def improve_attribute(self, player: Player, attr: str, min_change: int, max_change: int):
        """Improve a player attribute within bounds"""
        current_value = getattr(player, attr, 50)
        change = random.randint(min_change, max_change)
        new_value = max(1, min(100, current_value + change))
        setattr(player, attr, new_value)
    
    def generate_rookie_attributes(self, player: Player, player_type: str):
        """Generate appropriate attributes for a rookie based on type"""
        if player_type == "Hitter-only":
            player.velocity = random.randint(60, 85)
            player.control = random.randint(60, 85)
            player.stamina = random.randint(40, 60)
            player.speed_control = random.randint(40, 60)
        elif player_type == "Pitcher-only":
            player.velocity = random.randint(70, 90)
            player.control = random.randint(70, 90)
            player.stamina = random.randint(60, 80)
            player.speed_control = random.randint(60, 80)
        else:  # Two-way
            player.velocity = random.randint(50, 75)
            player.control = random.randint(50, 75)
            player.stamina = random.randint(50, 70)
            player.speed_control = random.randint(50, 70)
        
        player.age = random.randint(18, 22)  # Rookies are young 