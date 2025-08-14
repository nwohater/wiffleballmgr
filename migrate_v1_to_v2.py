"""
Migration script for Wiffle Ball Manager save files from v1.0 to v2.0
"""
import os
import json
from typing import Dict, Any

# Define the directories
OLD_SAVE_DIR = "data/saves/v1.0"
NEW_SAVE_DIR = "data/saves/v2.0"

# Ensure new save directory exists
os.makedirs(NEW_SAVE_DIR, exist_ok=True)

# Default new attributes for players
DEFAULT_ATTRIBUTES = {
    "clutch": 50,
    "composure": 50,
    "height": 70,     # inches
    "weight": 180,    # pounds
}

# Migration function
def migrate_save_file(old_file_path: str, new_file_path: str) -> None:
    with open(old_file_path, 'r') as old_file:
        data = json.load(old_file)

    # Update each player with new attributes
    for player in data.get('players', []):
        for key, value in DEFAULT_ATTRIBUTES.items():
            player.setdefault(key, value)

    # Save the updated data to a new file
    with open(new_file_path, 'w') as new_file:
        json.dump(data, new_file, indent=4)

# Perform the migration
for filename in os.listdir(OLD_SAVE_DIR):
    if filename.endswith('.json'):
        old_file_path = os.path.join(OLD_SAVE_DIR, filename)
        new_file_path = os.path.join(NEW_SAVE_DIR, filename)
        migrate_save_file(old_file_path, new_file_path)

print("Migration complete!")
