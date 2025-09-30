#!/usr/bin/env python3
"""
Termux-optimized startup script for the Ingress Leaderboard Bot
This script ensures proper environment setup before starting the bot
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

def setup_environment():
    """Setup environment variables and paths for Termux"""
    print("🔧 Setting up environment...")
    
    # Get script directory
    script_dir = Path(__file__).parent.resolve()
    
    # Add project root to Python path
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
    
    # Change to script directory to ensure relative paths work
    os.chdir(script_dir)
    print(f"📁 Working directory: {script_dir}")
    
    # Try to load .env file from multiple locations
    env_locations = [
        script_dir / ".env",
        Path.cwd() / ".env",
        Path.home() / "ingress-bot" / ".env",
        Path.home() / ".env",
    ]
    
    print("🔍 Looking for .env file...")
    env_loaded = False
    
    for env_path in env_locations:
        try:
            if env_path.exists():
                print(f"📄 Found .env at: {env_path}")
                result = load_dotenv(env_path, override=True)
                if result:
                    # Verify BOT_TOKEN is loaded
                    bot_token = os.getenv("BOT_TOKEN")
                    if bot_token and bot_token.strip() and bot_token != "YOUR_BOT_TOKEN_HERE":
                        print(f"✅ BOT_TOKEN loaded successfully")
                        env_loaded = True
                        break
                    else:
                        print(f"⚠️ BOT_TOKEN not found or invalid in {env_path}")
                else:
                    print(f"⚠️ Failed to load {env_path}")
            else:
                print(f"❌ Not found: {env_path}")
        except Exception as e:
            print(f"❌ Error loading {env_path}: {e}")
    
    if not env_loaded:
        print("\n❌ Could not load .env file!")
        print("Please ensure .env file exists with:")
        print("BOT_TOKEN=your_actual_bot_token_here")
        print("\nPossible locations:")
        for env_path in env_locations:
            print(f"  - {env_path}")
        return False
    
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    print("📦 Checking dependencies...")
    
    required_modules = [
        'telegram',
        'python_telegram_bot', 
        'dotenv',
        'sqlite3'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            if module == 'sqlite3':
                import sqlite3
            elif module == 'telegram':
                import telegram
            elif module == 'python_telegram_bot':
                from telegram.ext import Application
            elif module == 'dotenv':
                from dotenv import load_dotenv
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing modules: {', '.join(missing_modules)}")
        print("Install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies satisfied")
    return True

def setup_termux_specific():
    """Setup Termux-specific configurations"""
    is_termux = os.environ.get('PREFIX', '').endswith('com.termux')
    
    if is_termux:
        print("📱 Termux environment detected")
        
        # Try to acquire wake lock
        try:
            import subprocess
            subprocess.run(['termux-wake-lock'], check=True, capture_output=True)
            print("🔒 Wake lock acquired")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ Could not acquire wake lock (termux-api may not be installed)")
        
        # Setup storage permissions info
        storage_path = Path.home() / 'storage'
        if storage_path.exists():
            print("📂 Termux storage access available")
        else:
            print("⚠️ Termux storage access not granted (run: termux-setup-storage)")
    else:
        print("🖥️ Standard environment detected")
    
    return is_termux

def start_bot():
    """Start the Ingress Leaderboard Bot"""
    print("🚀 Starting Ingress Leaderboard Bot...")
    
    try:
        # Import and run the main bot
        from main import main
        main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the correct directory and all files are present")
        return False
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("=" * 50)
    print("🤖 Ingress Leaderboard Bot - Termux Startup")
    print("=" * 50)
    
    # Setup environment
    if not setup_environment():
        print("\n❌ Environment setup failed!")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed!")
        sys.exit(1)
    
    # Setup Termux-specific configurations
    is_termux = setup_termux_specific()
    
    print("\n✅ All checks passed!")
    print("🚀 Starting bot...\n")
    
    # Start the bot
    try:
        start_bot()
    except KeyboardInterrupt:
        print("\n⏹️ Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        if is_termux:
            # Release wake lock
            try:
                import subprocess
                subprocess.run(['termux-wake-unlock'], check=True, capture_output=True)
                print("🔓 Wake lock released")
            except:
                pass

if __name__ == "__main__":
    main()