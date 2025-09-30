#!/usr/bin/env python3
"""
Test script to verify Termux compatibility and setup
"""

import sys
import os
from pathlib import Path

def test_environment():
    """Test the environment setup"""
    print("🧪 Testing Termux Environment Setup")
    print("=" * 50)
    
    # Test Python version
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    # Test environment variables
    prefix = os.environ.get('PREFIX', 'Not set')
    print(f"PREFIX: {prefix}")
    
    is_termux = prefix.endswith('com.termux')
    print(f"Is Termux: {is_termux}")
    
    # Test paths
    home = Path.home()
    print(f"Home directory: {home}")
    
    # Test project structure
    base_dir = Path(__file__).parent
    print(f"Project directory: {base_dir}")
    
    required_dirs = ['src', 'config', 'data', 'logs']
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        exists = dir_path.exists()
        print(f"  {dir_name}/: {'✅' if exists else '❌'}")
    
    # Test virtual environment
    venv_path = base_dir / 'venv'
    venv_exists = venv_path.exists()
    print(f"Virtual environment: {'✅' if venv_exists else '❌'}")
    
    # Test imports
    print("\n📦 Testing imports:")
    
    try:
        from config.termux_settings import IS_TERMUX, get_termux_info
        print("  termux_settings: ✅")
        
        if IS_TERMUX:
            info = get_termux_info()
            print(f"  Termux info: {info}")
    except ImportError as e:
        print(f"  termux_settings: ❌ ({e})")
    
    try:
        import telegram
        print("  python-telegram-bot: ✅")
    except ImportError as e:
        print(f"  python-telegram-bot: ❌ ({e})")
    
    try:
        import requests
        print("  requests: ✅")
    except ImportError as e:
        print(f"  requests: ❌ ({e})")
    
    try:
        import sqlite3
        print("  sqlite3: ✅")
    except ImportError as e:
        print(f"  sqlite3: ❌ ({e})")
    
    # Test database
    print("\n🗄️  Testing database:")
    try:
        from src.database.manager import DatabaseManager
        db = DatabaseManager()
        print("  Database manager: ✅")
    except Exception as e:
        print(f"  Database manager: ❌ ({e})")
    
    # Test configuration
    print("\n⚙️  Testing configuration:")
    try:
        from config.config import BOT_TOKEN
        has_token = BOT_TOKEN and BOT_TOKEN != "YOUR_BOT_TOKEN_HERE"
        print(f"  Bot token configured: {'✅' if has_token else '❌'}")
    except ImportError:
        print("  Config file: ❌ (config.py not found)")
    
    print("\n" + "=" * 50)
    
    if is_termux:
        print("🤖 Termux-specific recommendations:")
        print("  • Run 'termux-wake-lock' before starting the bot")
        print("  • Install 'termux-api' for notifications")
        print("  • Use './run_bot_background.sh' for daemon mode")
        print("  • Monitor with 'tail -f logs/bot.log'")
    else:
        print("💻 Standard environment detected")
        print("  • Use 'python main.py' to start the bot")
        print("  • Use virtual environment: 'source venv/bin/activate'")
    
    print("\n🎮 Ready to start your Ingress Leaderboard Bot!")

if __name__ == "__main__":
    test_environment()