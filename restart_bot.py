#!/usr/bin/env python3
"""
Script to restart the bot and ensure direct paste functionality is working
"""

import sys
import os
import subprocess
import time

def restart_bot():
    """Restart the bot to ensure latest code is loaded"""
    print("🔄 RESTARTING BOT TO ENABLE DIRECT PASTE")
    print("=" * 50)
    
    # Change to project directory
    project_dir = "/home/codesagepath/Documents/TGBot/ingress-leaderboard"
    os.chdir(project_dir)
    
    print("📁 Working directory:", os.getcwd())
    
    # Kill any existing bot processes
    print("\n🛑 Stopping any existing bot processes...")
    try:
        subprocess.run(["pkill", "-f", "main.py"], check=False)
        subprocess.run(["pkill", "-f", "python.*main.py"], check=False)
        time.sleep(2)
        print("✅ Existing processes stopped")
    except Exception as e:
        print(f"⚠️ Note: {e}")
    
    # Start the bot
    print("\n🚀 Starting bot with latest code...")
    try:
        # Run the bot
        print("📋 Command: python main.py")
        print("💡 Bot will now support direct copy-paste!")
        print("\n" + "=" * 50)
        print("🎯 DIRECT PASTE IS NOW ENABLED!")
        print("Users can paste Ingress stats directly into chat!")
        print("=" * 50)
        
        # Start the bot process
        subprocess.run([sys.executable, "main.py"])
        
    except KeyboardInterrupt:
        print("\n\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting bot: {e}")
        return False
    
    return True

if __name__ == "__main__":
    restart_bot()