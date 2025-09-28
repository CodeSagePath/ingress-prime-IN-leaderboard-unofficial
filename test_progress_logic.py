#!/usr/bin/env python3
"""
Test the progress command logic directly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.manager import DatabaseManager
from services.leaderboard_service import LeaderboardManager

def test_progress_logic():
    """Test the progress command logic"""
    print("🧪 Testing Progress Command Logic")
    print("=" * 50)
    
    # Initialize components
    db = DatabaseManager()
    leaderboard = LeaderboardManager(db)
    
    # Test user ID from the conversation (HighTower)
    test_user_id = 574747247
    
    print(f"📋 Testing for user ID: {test_user_id}")
    
    # Step 1: Check if user has agents
    user_agents = db.get_agents_by_user(test_user_id)
    print(f"🔍 Found {len(user_agents)} agents:")
    
    for agent_name, faction in user_agents:
        print(f"  • {agent_name} ({faction})")
    
    if not user_agents:
        print("❌ No agents found - progress command would fail here")
        return
    
    # Step 2: Test progress generation
    agent_name = user_agents[0][0]
    stat = "Current AP"
    days = 30
    
    print(f"\n🧪 Testing progress generation:")
    print(f"  Agent: {agent_name}")
    print(f"  Stat: {stat}")
    print(f"  Days: {days}")
    
    try:
        progress_report = leaderboard.generate_agent_progress(agent_name, test_user_id, stat, days)
        
        if progress_report:
            print("✅ Progress report generated successfully!")
            print("\n📊 Progress Report:")
            print("-" * 40)
            print(progress_report)
            print("-" * 40)
        else:
            print("❌ Progress report generation returned None/empty")
            
    except Exception as e:
        print(f"❌ Error generating progress report: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_progress_logic()