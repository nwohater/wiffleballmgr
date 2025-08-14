"""
Configuration loader for skill model parameters
"""
import os
import yaml
from typing import Dict, Any

class SkillModelConfig:
    """Loads and provides access to skill model configuration"""
    
    def __init__(self, config_path: str = "data/config/skill_model.yml"):
        self.config_path = config_path
        self._config = None
        self.load_config()
    
    def load_config(self):
        """Load configuration from YAML file"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as file:
            self._config = yaml.safe_load(file)
    
    def reload_config(self):
        """Reload configuration from file (useful for runtime changes)"""
        self.load_config()
    
    @property
    def probability_factors(self) -> Dict[str, float]:
        """Get probability factors"""
        return self._config.get('probability_factors', {})
    
    @property
    def hit_type_weights(self) -> Dict[str, float]:
        """Get hit type weights"""
        return self._config.get('hit_type_weights', {})
    
    @property
    def player_development(self) -> Dict[str, Any]:
        """Get player development parameters"""
        return self._config.get('player_development', {})
    
    @property
    def fatigue(self) -> Dict[str, float]:
        """Get fatigue parameters"""
        return self._config.get('fatigue', {})
    
    @property
    def positive_event_chance(self) -> float:
        """Get positive event chance"""
        return self._config.get('positive_event_chance', 0.12)
    
    @property
    def negative_event_chance(self) -> float:
        """Get negative event chance"""
        return self._config.get('negative_event_chance', 0.08)
    
    @property
    def game_balance(self) -> Dict[str, Any]:
        """Get game balance parameters"""
        return self._config.get('game_balance', {})
    
    @property
    def development_curves(self) -> Dict[str, Any]:
        """Get development curve parameters"""
        return self._config.get('development_curves', {})
    
    @property
    def experience_thresholds(self) -> Dict[str, Any]:
        """Get experience threshold parameters"""
        return self._config.get('experience_thresholds', {})

# Global config instance
_config_instance = None

def get_skill_config() -> SkillModelConfig:
    """Get the global skill model configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = SkillModelConfig()
    return _config_instance

def reload_skill_config():
    """Reload the global configuration"""
    global _config_instance
    if _config_instance is not None:
        _config_instance.reload_config()
