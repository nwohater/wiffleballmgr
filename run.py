#!/usr/bin/env python3
"""
Wiffle Ball Manager - Main Game Launcher
A text-driven console baseball management simulation game.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import main

if __name__ == "__main__":
    main() 