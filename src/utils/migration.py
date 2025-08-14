"""
Migration utilities for Wiffle Ball Manager save files
Handles migration from v1.0 to v2.0 format with new attributes and advanced stats
"""
import os
import json
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import random

class SaveFileMigrator:
    """Handles migration of save files between versions"""
    
    def __init__(self, save_dir: str = "data/saves"):
        self.save_dir = Path(save_dir)
        self.backup_dir = self.save_dir / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def migrate_v1_to_v2(self, save_file_path: str) -> Dict[str, Any]:
        """
        Migrate a v1.0 save file to v2.0 format
        
        Args:
            save_file_path: Path to the v1.0 save file
            
        Returns:
            Dictionary containing the migrated save data
        """
        # Create backup first
        self._create_backup(save_file_path)
        
        with open(save_file_path, 'r') as f:
            data = json.load(f)
        
        # Update version info
        data['game_version'] = '2.0'
        data['migration_date'] = datetime.now().isoformat()
        data['migrated_from'] = data.get('game_version', '1.0')
        
        # Migrate players
        if 'teams' in data:
            for team in data['teams']:
                if 'players' in team:
                    for player in team['players']:
                        self._migrate_player_v1_to_v2(player)
        
        # Migrate standalone players list if it exists
        if 'players' in data:
            for player in data['players']:
                self._migrate_player_v1_to_v2(player)
                
        return data
    
    def _migrate_player_v1_to_v2(self, player: Dict[str, Any]) -> None:
        """
        Migrate a single player from v1.0 to v2.0 format
        
        Args:
            player: Player dictionary to migrate (modified in place)
        """
        # Add new mental attributes with sensible defaults based on existing attributes
        player.setdefault('clutch', self._calculate_clutch_default(player))
        player.setdefault('composure', self._calculate_composure_default(player))
        
        # Add physical attributes with realistic variation
        player.setdefault('height', self._generate_height())
        player.setdefault('weight', self._generate_weight(player.get('height', 70)))
        
        # Ensure all existing attributes have reasonable bounds
        self._normalize_attributes(player)
        
        # Add career stats structure if not present
        if 'career_stats' not in player:
            player['career_stats'] = {
                'season_batting': {},
                'season_pitching': {},
                'season_fielding': {},
                'career_batting': self._empty_batting_stats(),
                'career_pitching': self._empty_pitching_stats(),
                'career_fielding': self._empty_fielding_stats()
            }
        
        # Add seasons_played list if not present
        player.setdefault('seasons_played', [])
        
        # Update batting stats to include new fields
        self._update_batting_stats(player.get('batting_stats', {}))
        
        # Update pitching stats to include new fields  
        self._update_pitching_stats(player.get('pitching_stats', {}))
        
        # Update fielding stats to include new fields
        self._update_fielding_stats(player.get('fielding_stats', {}))
    
    def _calculate_clutch_default(self, player: Dict[str, Any]) -> int:
        """Calculate a reasonable clutch rating based on existing attributes"""
        # Base clutch on mental attributes if they exist
        leadership = player.get('leadership', 50)
        work_ethic = player.get('work_ethic', 50)
        
        # Players with higher leadership and work ethic tend to be more clutch
        base_clutch = (leadership + work_ethic) // 2
        
        # Add some random variation (-10 to +10)
        variation = random.randint(-10, 10)
        
        return max(1, min(100, base_clutch + variation))
    
    def _calculate_composure_default(self, player: Dict[str, Any]) -> int:
        """Calculate a reasonable composure rating based on existing attributes"""
        # Base composure on control and discipline if they exist
        control = player.get('control', 50)
        discipline = player.get('discipline', 50)
        
        # Players with better control and discipline tend to have better composure
        base_composure = (control + discipline) // 2
        
        # Add some random variation (-8 to +8)
        variation = random.randint(-8, 8)
        
        return max(1, min(100, base_composure + variation))
    
    def _generate_height(self) -> int:
        """Generate a realistic height in inches (5'6" to 6'6")"""
        return random.randint(66, 78)  # 66-78 inches
    
    def _generate_weight(self, height: int) -> int:
        """Generate a realistic weight based on height"""
        # Basic BMI-based weight calculation
        # Target BMI between 20-28 for athletes
        height_meters = height * 0.0254
        target_bmi = random.uniform(20, 28)
        weight_kg = target_bmi * (height_meters ** 2)
        weight_lbs = int(weight_kg * 2.20462)
        
        return max(140, min(280, weight_lbs))  # Reasonable bounds
    
    def _normalize_attributes(self, player: Dict[str, Any]) -> None:
        """Ensure all attributes are within valid ranges (1-100)"""
        attributes = [
            'power', 'contact', 'discipline', 'speed',
            'velocity', 'movement', 'control', 'stamina', 'deception',
            'range', 'arm_strength', 'hands', 'reaction', 'accuracy',
            'potential', 'leadership', 'work_ethic', 'durability',
            'clutch', 'composure'
        ]
        
        for attr in attributes:
            if attr in player:
                player[attr] = max(1, min(100, player[attr]))
    
    def _empty_batting_stats(self) -> Dict[str, Any]:
        """Return empty batting stats structure"""
        return {
            'gp': 0, 'gs': 0, 'pa': 0, 'ab': 0, 'r': 0, 'h': 0,
            'doubles': 0, 'triples': 0, 'hr': 0, 'rbi': 0, 'bb': 0,
            'k': 0, 'hbp': 0, 'ibb': 0, 'lob': 0, 'tb': 0,
            'obp': 0.0, 'slg': 0.0, 'ops': 0.0
        }
    
    def _empty_pitching_stats(self) -> Dict[str, Any]:
        """Return empty pitching stats structure"""
        return {
            'gp': 0, 'gs': 0, 'ip': 0.0, 'r': 0, 'er': 0, 'h': 0,
            'bb': 0, 'hbp': 0, 'ibb': 0, 'k': 0, 'cg': 0, 'w': 0,
            'l': 0, 's': 0, 'hld': 0, 'bs': 0, 'pt': 0, 'b': 0,
            'st': 0, 'wp': 0
        }
    
    def _empty_fielding_stats(self) -> Dict[str, Any]:
        """Return empty fielding stats structure"""
        return {
            'po': 0, 'a': 0, 'e': 0, 'dp': 0, 'fpct': 1.0
        }
    
    def _update_batting_stats(self, batting_stats: Dict[str, Any]) -> None:
        """Update batting stats to include all v2.0 fields"""
        defaults = self._empty_batting_stats()
        for key, default_value in defaults.items():
            batting_stats.setdefault(key, default_value)
    
    def _update_pitching_stats(self, pitching_stats: Dict[str, Any]) -> None:
        """Update pitching stats to include all v2.0 fields"""
        defaults = self._empty_pitching_stats()
        for key, default_value in defaults.items():
            pitching_stats.setdefault(key, default_value)
    
    def _update_fielding_stats(self, fielding_stats: Dict[str, Any]) -> None:
        """Update fielding stats to include all v2.0 fields"""
        defaults = self._empty_fielding_stats()
        for key, default_value in defaults.items():
            fielding_stats.setdefault(key, default_value)
    
    def _create_backup(self, save_file_path: str) -> str:
        """Create a backup of the original save file"""
        save_path = Path(save_file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{save_path.stem}_backup_{timestamp}{save_path.suffix}"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(save_file_path, backup_path)
        return str(backup_path)
    
    def migrate_directory(self, input_dir: str, output_dir: str) -> List[str]:
        """
        Migrate all save files in a directory
        
        Args:
            input_dir: Directory containing v1.0 save files
            output_dir: Directory to save v2.0 files
            
        Returns:
            List of successfully migrated file paths
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        migrated_files = []
        
        if not input_path.exists():
            print(f"Input directory {input_dir} does not exist")
            return migrated_files
        
        for save_file in input_path.glob("*.json"):
            try:
                # Migrate the file
                migrated_data = self.migrate_v1_to_v2(str(save_file))
                
                # Save to output directory
                output_file = output_path / save_file.name
                with open(output_file, 'w') as f:
                    json.dump(migrated_data, f, indent=2)
                
                migrated_files.append(str(output_file))
                print(f"Successfully migrated {save_file.name}")
                
            except Exception as e:
                print(f"Error migrating {save_file.name}: {str(e)}")
        
        return migrated_files
    
    def validate_v2_save(self, save_file_path: str) -> bool:
        """
        Validate that a save file is in proper v2.0 format
        
        Args:
            save_file_path: Path to the save file to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            with open(save_file_path, 'r') as f:
                data = json.load(f)
            
            # Check version
            if data.get('game_version') != '2.0':
                return False
            
            # Check that teams exist and have players with new attributes
            if 'teams' in data:
                for team in data['teams']:
                    if 'players' in team:
                        for player in team['players']:
                            if not self._validate_player_v2(player):
                                return False
            
            return True
            
        except Exception:
            return False
    
    def _validate_player_v2(self, player: Dict[str, Any]) -> bool:
        """Validate that a player has all required v2.0 fields"""
        required_fields = [
            'name', 'clutch', 'composure', 'height', 'weight',
            'career_stats', 'seasons_played'
        ]
        
        for field in required_fields:
            if field not in player:
                return False
        
        # Validate career_stats structure
        career_stats = player.get('career_stats', {})
        required_career_fields = [
            'season_batting', 'season_pitching', 'season_fielding',
            'career_batting', 'career_pitching', 'career_fielding'
        ]
        
        for field in required_career_fields:
            if field not in career_stats:
                return False
        
        return True


def main():
    """Command-line interface for migration"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate Wiffle Ball Manager save files')
    parser.add_argument('--input', '-i', required=True, help='Input directory containing v1.0 saves')
    parser.add_argument('--output', '-o', required=True, help='Output directory for v2.0 saves')
    parser.add_argument('--validate', '-v', action='store_true', help='Validate migrated files')
    
    args = parser.parse_args()
    
    migrator = SaveFileMigrator()
    
    # Perform migration
    print(f"Migrating saves from {args.input} to {args.output}")
    migrated_files = migrator.migrate_directory(args.input, args.output)
    
    print(f"\nMigration complete! {len(migrated_files)} files migrated.")
    
    # Validate if requested
    if args.validate:
        print("\nValidating migrated files...")
        valid_count = 0
        for file_path in migrated_files:
            if migrator.validate_v2_save(file_path):
                valid_count += 1
                print(f"✓ {Path(file_path).name} is valid")
            else:
                print(f"✗ {Path(file_path).name} failed validation")
        
        print(f"\nValidation complete: {valid_count}/{len(migrated_files)} files are valid")


if __name__ == "__main__":
    main()
