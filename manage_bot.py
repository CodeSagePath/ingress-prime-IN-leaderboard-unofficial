#!/usr/bin/env python3
"""
Bot management script to help with starting/stopping the Ingress Leaderboard Bot
"""

import os
import sys
import psutil
import signal
from pathlib import Path

def find_bot_processes():
    """Find all running bot processes"""
    bot_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any('main.py' in arg or 'ingress' in arg.lower() for arg in cmdline):
                if any('python' in arg for arg in cmdline):
                    bot_processes.append({
                        'pid': proc.info['pid'],
                        'cmdline': ' '.join(cmdline),
                        'create_time': proc.info['create_time']
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return bot_processes

def stop_bot_processes():
    """Stop all running bot processes"""
    processes = find_bot_processes()
    
    if not processes:
        print("✅ No running bot processes found")
        return
    
    print(f"🛑 Found {len(processes)} running bot process(es):")
    
    for proc in processes:
        print(f"   PID {proc['pid']}: {proc['cmdline']}")
        try:
            os.kill(proc['pid'], signal.SIGTERM)
            print(f"   ✅ Sent SIGTERM to PID {proc['pid']}")
        except ProcessLookupError:
            print(f"   ⚠️  Process {proc['pid']} already stopped")
        except PermissionError:
            print(f"   ❌ Permission denied to stop PID {proc['pid']}")
    
    # Clean up lock file
    lock_file = Path(__file__).parent / '.bot_running.lock'
    if lock_file.exists():
        lock_file.unlink()
        print("🧹 Cleaned up lock file")

def show_status():
    """Show current bot status"""
    processes = find_bot_processes()
    lock_file = Path(__file__).parent / '.bot_running.lock'
    
    print("🤖 Ingress Leaderboard Bot Status")
    print("=" * 40)
    
    if processes:
        print(f"🟢 Running processes: {len(processes)}")
        for proc in processes:
            print(f"   PID {proc['pid']}: {proc['cmdline']}")
    else:
        print("🔴 No running processes found")
    
    if lock_file.exists():
        try:
            with open(lock_file, 'r') as f:
                lock_pid = f.read().strip()
            print(f"🔒 Lock file exists (PID: {lock_pid})")
        except:
            print("🔒 Lock file exists (invalid content)")
    else:
        print("🔓 No lock file found")

def main():
    if len(sys.argv) < 2:
        print("🤖 Ingress Leaderboard Bot Manager")
        print("Usage:")
        print("  python manage_bot.py status   - Show bot status")
        print("  python manage_bot.py stop     - Stop all bot instances")
        print("  python manage_bot.py start    - Start the bot (after stopping others)")
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        show_status()
    elif command == "stop":
        stop_bot_processes()
    elif command == "start":
        print("🛑 Stopping any existing instances first...")
        stop_bot_processes()
        print("\n🚀 Starting bot...")
        os.system("python main.py")
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: status, stop, start")

if __name__ == "__main__":
    main()