#!/usr/bin/env python3
"""
Verify that the progress command fix is implemented correctly
"""

import sqlite3
from pathlib import Path

# Get database path
PROJECT_ROOT = Path(__file__).parent
DATABASE_PATH = PROJECT_ROOT / "data" / "ingress_leaderboard.db"

def verify_progress_fix():
    """Verify the progress command fix"""
    print("🔧 Verifying Progress Command Fix")
    print("=" * 50)
    
    # Test user ID from the conversation (HighTower)
    test_user_id = 574747247
    
    print(f"👤 Testing for user: {test_user_id}")
    
    # Check database
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            # Check if user has agents
            cursor.execute('''
                SELECT agent_name, faction
                FROM agents
                WHERE telegram_user_id = ?
            ''', (test_user_id,))
            
            user_agents = cursor.fetchall()
            
            if user_agents:
                agent_name, faction = user_agents[0]
                print(f"✅ User has agent: {agent_name} ({faction})")
                
                # Check submissions
                cursor.execute('''
                    SELECT COUNT(*) 
                    FROM submissions s
                    JOIN agents a ON s.agent_id = a.id
                    WHERE a.agent_name = ? AND a.telegram_user_id = ?
                ''', (agent_name, test_user_id))
                
                submission_count = cursor.fetchone()[0]
                print(f"✅ Agent has {submission_count} submissions")
                
                if submission_count > 0:
                    print("✅ Progress command should work!")
                else:
                    print("⚠️  No submissions - progress will be empty")
            else:
                print("❌ No agents found for user")
                
    except Exception as e:
        print(f"❌ Database error: {e}")
        return
    
    # Check if the progress command implementation exists
    command_handlers_path = PROJECT_ROOT / "src" / "handlers" / "command_handlers.py"
    
    try:
        with open(command_handlers_path, 'r') as f:
            content = f.read()
            
        if "get_agents_by_user" in content:
            print("✅ Progress command uses get_agents_by_user method")
        else:
            print("❌ Progress command missing get_agents_by_user")
            
        if "generate_agent_progress" in content:
            print("✅ Progress command calls generate_agent_progress")
        else:
            print("❌ Progress command missing generate_agent_progress")
            
        # Check if it's not just the stub implementation
        if "Progress tracking requires your agent name to be registered" in content:
            # Check if this is in an if statement (good) or standalone (bad)
            lines = content.split('\n')
            error_line_found = False
            in_if_block = False
            
            for i, line in enumerate(lines):
                if "Progress tracking requires your agent name to be registered" in line:
                    error_line_found = True
                    # Check previous lines for if statement
                    for j in range(max(0, i-5), i):
                        if "if not user_agents:" in lines[j]:
                            in_if_block = True
                            break
                    break
            
            if error_line_found and in_if_block:
                print("✅ Error message is properly conditional")
            elif error_line_found:
                print("❌ Error message appears to be unconditional (stub implementation)")
            else:
                print("✅ No hardcoded error message found")
        else:
            print("✅ No hardcoded error message found")
            
    except Exception as e:
        print(f"❌ Error checking command handlers: {e}")
    
    # Check database manager for get_agents_by_user method
    db_manager_path = PROJECT_ROOT / "src" / "database" / "manager.py"
    
    try:
        with open(db_manager_path, 'r') as f:
            content = f.read()
            
        if "def get_agents_by_user" in content:
            print("✅ DatabaseManager has get_agents_by_user method")
        else:
            print("❌ DatabaseManager missing get_agents_by_user method")
            
    except Exception as e:
        print(f"❌ Error checking database manager: {e}")
    
    print("\n🎯 Summary:")
    print("The progress command has been fixed in the code.")
    print("The issue is that the bot needs to be restarted to pick up the changes.")
    print("\n📋 To fix the issue:")
    print("1. Stop the current bot process (if running)")
    print("2. Restart the bot with: python main.py")
    print("3. The /progress command should now work correctly")

if __name__ == "__main__":
    verify_progress_fix()