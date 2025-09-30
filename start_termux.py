#!/usr/bin/env python3
"""
Termux-Optimized Startup Script for Ingress Leaderboard Bot
===========================================================

This script provides comprehensive startup management specifically designed for Termux environments.
It handles environment loading, dependency checking, and provides detailed feedback during startup.

Key Features:
- Multiple .env file location fallback
- Termux-specific path handling
- Enhanced error reporting
- Wake lock management
- Step-by-step startup feedback

Author: HighTower
Created: 2025
"""

import os
import sys
import logging
import subprocess
import time
from pathlib import Path

def setup_logging():
    """Setup logging with both file and console output."""
    # Ensure logs directory exists
    logs_dir = Path(__file__).parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    log_file = logs_dir / "termux_startup.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def print_banner():
    """Print startup banner."""
    banner = """
╔══════════════════════════════════════════════════════════╗
║              🤖 INGRESS LEADERBOARD BOT 🤖              ║
║                   Termux Startup Manager                 ║
╚══════════════════════════════════════════════════════════╝
"""
    print(banner)

def check_termux_environment():
    """Check if we're running in Termux and perform environment checks."""
    logger = logging.getLogger(__name__)
    
    # Check if we're in Termux
    if 'com.termux' not in os.environ.get('PREFIX', ''):
        logger.warning("⚠️  Not running in Termux environment")
        return False
    
    logger.info("✅ Termux environment detected")
    
    # Check for wake lock
    try:
        result = subprocess.run(['termux-wake-lock'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            logger.info("✅ Wake lock acquired")
        else:
            logger.warning("⚠️  Wake lock failed, but continuing...")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        logger.warning("⚠️  termux-wake-lock not available, but continuing...")
    
    return True

def find_env_file():
    """Find .env file with multiple fallback locations."""
    logger = logging.getLogger(__name__)
    
    # Get current script directory
    script_dir = Path(__file__).parent.absolute()
    
    # Potential .env file locations (in order of preference)
    env_locations = [
        script_dir / '.env',  # Same directory as script
        Path.cwd() / '.env',  # Current working directory
        Path.home() / 'telegram-bots' / 'ingress-leaderboard' / '.env',  # Termux typical location
        Path('/data/data/com.termux/files/home/telegram-bots/ingress-leaderboard/.env'),  # Termux absolute path
    ]
    
    logger.info(f"🔍 Searching for .env file...")
    logger.info(f"   Script directory: {script_dir}")
    logger.info(f"   Working directory: {Path.cwd()}")
    
    for env_path in env_locations:
        logger.info(f"   Checking: {env_path}")
        if env_path.exists():
            logger.info(f"✅ Found .env file at: {env_path}")
            return env_path
    
    logger.error("❌ .env file not found in any of the expected locations:")
    for env_path in env_locations:
        logger.error(f"   ❌ {env_path}")
    
    return None

def load_environment():
    """Load environment variables from .env file."""
    logger = logging.getLogger(__name__)
    
    # Find .env file
    env_file = find_env_file()
    if not env_file:
        logger.error("❌ Cannot proceed without .env file")
        return False
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        logger.info(f"📂 Loading environment from: {env_file}")
        
        # Load the .env file
        success = load_dotenv(env_file, override=True)
        if not success:
            logger.error(f"❌ Failed to load .env file: {env_file}")
            return False
        
        logger.info("✅ Environment file loaded successfully")
        
        # Verify BOT_TOKEN is loaded
        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token:
            logger.error("❌ BOT_TOKEN not found in environment variables")
            logger.error("   Please check your .env file contains: BOT_TOKEN=your_token_here")
            return False
        
        # Don't log the actual token, just confirm it exists and has reasonable length
        if len(bot_token) < 40:
            logger.warning("⚠️  BOT_TOKEN seems too short (expected ~46 characters)")
        else:
            logger.info(f"✅ BOT_TOKEN loaded (length: {len(bot_token)} characters)")
        
        return True
        
    except ImportError:
        logger.error("❌ python-dotenv not installed")
        logger.error("   Please install with: pip install python-dotenv")
        return False
    except Exception as e:
        logger.error(f"❌ Error loading environment: {str(e)}")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    logger = logging.getLogger(__name__)
    
    logger.info("🔍 Checking dependencies...")
    
    required_packages = [
        'telebot',
        'python-dotenv',
        'requests',
        'sqlite3',  # Usually built-in
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
            elif package == 'telebot':
                import telebot
            elif package == 'python-dotenv':
                import dotenv
            elif package == 'requests':
                import requests
            
            logger.info(f"   ✅ {package}")
        except ImportError:
            logger.warning(f"   ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        logger.error("❌ Missing dependencies:")
        for package in missing_packages:
            logger.error(f"   - {package}")
        logger.error("   Please install with: pip install -r requirements.txt")
        return False
    
    logger.info("✅ All dependencies are installed")
    return True

def start_bot():
    """Start the main bot application."""
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Starting Ingress Leaderboard Bot...")
    
    try:
        # Import and start the main application
        sys.path.insert(0, str(Path(__file__).parent))
        
        # Import main application
        import main
        
        logger.info("✅ Bot started successfully!")
        logger.info("🔄 Bot is now running... (Press Ctrl+C to stop)")
        
        # The main.py should handle the bot execution
        # If it doesn't start properly, we'll catch it here
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Error starting bot: {str(e)}")
        logger.error(f"   Exception type: {type(e).__name__}")
        logger.error(f"   Exception details: {e}")
        return False
    
    return True

def main():
    """Main startup routine."""
    # Setup logging first
    logger = setup_logging()
    
    # Print startup banner
    print_banner()
    
    logger.info("🚀 Termux startup sequence initiated")
    
    # Step 1: Check Termux environment
    logger.info("📋 Step 1: Checking Termux environment...")
    check_termux_environment()
    time.sleep(1)
    
    # Step 2: Load environment variables
    logger.info("📋 Step 2: Loading environment variables...")
    if not load_environment():
        logger.error("❌ Environment loading failed. Cannot continue.")
        logger.error("💡 Troubleshooting tips:")
        logger.error("   1. Ensure .env file exists in the project directory")
        logger.error("   2. Check .env file contains: BOT_TOKEN=your_bot_token")
        logger.error("   3. Verify file permissions are readable")
        sys.exit(1)
    time.sleep(1)
    
    # Step 3: Check dependencies
    logger.info("📋 Step 3: Checking dependencies...")
    if not check_dependencies():
        logger.error("❌ Dependency check failed. Cannot continue.")
        logger.error("💡 Please run: pip install -r requirements.txt")
        sys.exit(1)
    time.sleep(1)
    
    # Step 4: Start the bot
    logger.info("📋 Step 4: Starting bot application...")
    if not start_bot():
        logger.error("❌ Bot startup failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()