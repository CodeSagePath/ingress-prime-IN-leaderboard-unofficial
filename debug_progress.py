#!/usr/bin/env python3
"""
Debug script to check progress command issue
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from database.manager import DatabaseManager
from config.settings import DATABASE_PATH

def debug_progress_issue():
    """Debug the progress command issue"""
    print("🔍 Debugging Progress Command Issue")
    print("=" * 50)
    
    # Initialize database
    db = DatabaseManager()
    
    # Test user ID from the conversation (HighTower)
    test_user_id = 574747247  # This should be the actual user ID
    
    print(f"📋 Checking agents for user ID: {test_user_id}")
    
    # Get agents for this user
    user_agents = db.get_agents_by_user(test_user_id)
    print(f"🔍 Found {len(user_agents)} agents:")
    
    for agent_name, faction in user_agents:
        print(f"  • {agent_name} ({faction})")
    
    if not user_agents:
        print("❌ No agents found for this user!")
        print("\n🔍 Let's check all agents in the database:")
        
        # Check all agents
        try:
            import sqlite3
            with sqlite3.connect(DATABASE_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT agent_name, faction, telegram_user_id FROM agents ORDER BY agent_name')
                all_agents = cursor.fetchall()
                
                print(f"📊 Total agents in database: {len(all_agents)}")
                for agent_name, faction, user_id in all_agents:
                    print(f"  • {agent_name} ({faction}) - User ID: {user_id}")
                    
        except Exception as e:
            print(f"❌ Error checking database: {e}")
    else:
        print("✅ Agents found! Progress command should work.")
        
        # Test progress generation for the first agent
        agent_name = user_agents[0][0]
        print(f"\n🧪 Testing progress generation for {agent_name}...")
        
        try:
            from services.leaderboard_service import LeaderboardManager
            leaderboard = LeaderboardManager(db)
            
            progress_report = leaderboard.generate_agent_progress(
                agent_name, test_user_id, "Current AP", 30
            )
            
            if progress_report:
                print("✅ Progress report generated successfully!")
                print("📊 Sample output:")
                print(progress_report[:200] + "..." if len(progress_report) > 200 else progress_report)
            else:
                print("❌ Progress report generation failed!")
                
        except Exception as e:
            print(f"❌ Error generating progress report: {e}")

if __name__ == "__main__":
    debug_progress_issue()