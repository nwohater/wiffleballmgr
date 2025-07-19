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
        
        # Calculate development based on experience and playing time
        self.calculate_experience_bonus(player)
        
        # Apply aging effects
        self.apply_aging_effects(player)
        
        # Random development events
        self.random_development_events(player)
    
    def calculate_experience_bonus(self, player: Player):
        """Calculate development bonus based on playing time and experience"""
        batting_experience = self.calculate_batting_experience(player)
        pitching_experience = self.calculate_pitching_experience(player)
        
        # Apply batting development based on experience
        if batting_experience > 0:
            self.apply_batting_development(player, batting_experience)
        
        # Apply pitching development based on experience
        if pitching_experience > 0:
            self.apply_pitching_development(player, pitching_experience)
    
    def calculate_batting_experience(self, player: Player) -> float:
        """Calculate batting experience factor (0.0 to 1.0)"""
        if not hasattr(player, 'batting_stats') or not player.batting_stats:
            return 0.0
        
        # Base experience on games played and plate appearances
        games_played = player.batting_stats.gp
        plate_appearances = player.batting_stats.pa
        
        # Experience factors
        games_factor = min(games_played / 30.0, 1.0)  # Cap at 30 games
        pa_factor = min(plate_appearances / 100.0, 1.0)  # Cap at 100 PAs
        
        # Weight plate appearances more heavily than just games
        experience = (games_factor * 0.4) + (pa_factor * 0.6)
        
        return min(experience, 1.0)
    
    def calculate_pitching_experience(self, player: Player) -> float:
        """Calculate pitching experience factor (0.0 to 1.0)"""
        if not hasattr(player, 'pitching_stats') or not player.pitching_stats:
            return 0.0
        
        # Base experience on games pitched and innings pitched
        games_pitched = player.pitching_stats.gp
        innings_pitched = player.pitching_stats.ip
        
        # Experience factors
        games_factor = min(games_pitched / 25.0, 1.0)  # Cap at 25 games
        ip_factor = min(innings_pitched / 75.0, 1.0)  # Cap at 75 innings
        
        # Weight innings pitched more heavily
        experience = (games_factor * 0.3) + (ip_factor * 0.7)
        
        return min(experience, 1.0)
    
    def apply_batting_development(self, player: Player, experience: float):
        """Apply batting development based on experience"""
        # Base chance of improvement scaled by experience
        improvement_chance = 0.15 + (experience * 0.25)  # 15% to 40% chance
        
        if random.random() < improvement_chance:
            # Modest improvements for regular players
            if experience >= 0.7:  # High experience (21+ games, 70+ PAs)
                # Better chance for larger improvements
                if random.random() < 0.3:
                    self.improve_attribute(player, 'velocity', 1, 3)
                    print(f"{player.name}: Batting power improved through experience")
                else:
                    self.improve_attribute(player, 'control', 1, 2)
                    print(f"{player.name}: Batting control improved through practice")
            
            elif experience >= 0.4:  # Moderate experience (12+ games, 40+ PAs)
                # Modest improvements
                attr = random.choice(['velocity', 'control'])
                self.improve_attribute(player, attr, 0, 2)
                print(f"{player.name}: Modest batting improvement from regular play")
            
            else:  # Low experience
                # Small improvements
                attr = random.choice(['velocity', 'control'])
                self.improve_attribute(player, attr, 0, 1)
                print(f"{player.name}: Minor batting development from limited play")
    
    def apply_pitching_development(self, player: Player, experience: float):
        """Apply pitching development based on experience"""
        # Base chance of improvement scaled by experience
        improvement_chance = 0.20 + (experience * 0.25)  # 20% to 45% chance
        
        if random.random() < improvement_chance:
            # Pitching tends to improve more with experience than batting
            if experience >= 0.7:  # High experience (18+ games, 50+ IP)
                # Better chance for larger improvements
                if random.random() < 0.4:
                    attrs = random.sample(['velocity', 'control', 'stamina'], 2)
                    for attr in attrs:
                        self.improve_attribute(player, attr, 1, 2)
                    print(f"{player.name}: Significant pitching improvement through experience")
                else:
                    attr = random.choice(['velocity', 'control', 'stamina'])
                    self.improve_attribute(player, attr, 1, 3)
                    print(f"{player.name}: Pitching {attr} improved through heavy use")
            
            elif experience >= 0.4:  # Moderate experience (10+ games, 30+ IP)
                # Modest improvements
                attr = random.choice(['velocity', 'control', 'stamina'])
                self.improve_attribute(player, attr, 0, 2)
                print(f"{player.name}: Modest pitching improvement from regular starts")
            
            else:  # Low experience
                # Small improvements
                attr = random.choice(['velocity', 'control'])
                self.improve_attribute(player, attr, 0, 1)
                print(f"{player.name}: Minor pitching development from limited use")
    
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
        """Random development events that can occur (reduced frequency since experience is primary)"""
        events = [
            ("Training breakthrough", 0.02, lambda p: self.improve_attribute(p, 'velocity', 2, 4)),
            ("Control workshop", 0.02, lambda p: self.improve_attribute(p, 'control', 2, 4)),
            ("Conditioning program", 0.02, lambda p: self.improve_attribute(p, 'stamina', 2, 4)),
            ("Technique refinement", 0.02, lambda p: self.improve_attribute(p, 'speed_control', 2, 4)),
            ("Minor injury", 0.015, lambda p: self.improve_attribute(p, 'velocity', -2, -1)),
            ("Mechanics issue", 0.015, lambda p: self.improve_attribute(p, 'control', -2, -1)),
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