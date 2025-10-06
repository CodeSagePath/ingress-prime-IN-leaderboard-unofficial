#!/usr/bin/env python3
"""
Script to check if the bot is already running and prevent multiple instances
"""

import os
import sys
import psutil
import logging
from pathlib import Path

def check_bot_running():
    """Check if bot is already running"""
    current_pid = os.getpid()
    bot_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['pid'] == current_pid:
                continue
                
            cmdline = proc.info['cmdline']
            if cmdline and any('main.py' in arg for arg in cmdline):
                if any('python' in arg for arg in cmdline):
                    bot_processes.append({
                        'pid': proc.info['pid'],
                        'cmdline': ' '.join(cmdline)
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return bot_processes

def create_lock_file():
    """Create a lock file to prevent multiple instances"""
    lock_file = Path(__file__).parent / '.bot_running.lock'
    
    if lock_file.exists():
        try:
            with open(lock_file, 'r') as f:
                old_pid = int(f.read().strip())
            
            # Check if the process is still running
            if psutil.pid_exists(old_pid):
                return False, f"Bot is already running with PID {old_pid}"
            else:
                # Stale lock file, remove it
                lock_file.unlink()
        except (ValueError, FileNotFoundError):
            # Invalid lock file, remove it
            lock_file.unlink()
    
    # Create new lock file
    with open(lock_file, 'w') as f:
        f.write(str(os.getpid()))
    
    return True, "Lock file created successfully"

def remove_lock_file():
    """Remove the lock file when bot stops"""
    lock_file = Path(__file__).parent / '.bot_running.lock'
    if lock_file.exists():
        lock_file.unlink()

if __name__ == "__main__":
    print("🔍 Checking for running bot instances...")
    
    # Check for running processes
    running_bots = check_bot_running()
    
    if running_bots:
        print("⚠️  Found running bot instances:")
        for bot in running_bots:
            print(f"   PID {bot['pid']}: {bot['cmdline']}")
        print("\n❌ Please stop other instances before starting a new one!")
        sys.exit(1)
    else:
        print("✅ No other bot instances found")
    
    # Check lock file
    can_run, message = create_lock_file()
    if not can_run:
        print(f"❌ {message}")
        sys.exit(1)
    else:
        print(f"✅ {message}")
        print("🚀 Bot can start safely!")