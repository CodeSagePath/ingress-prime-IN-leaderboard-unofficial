#!/usr/bin/env python3
"""
Simple test to check if the progress command should work
"""

import sqlite3
import os
from pathlib import Path

# Get database path
PROJECT_ROOT = Path(__file__).parent
DATABASE_PATH = PROJECT_ROOT / "data" / "ingress_leaderboard.db"

def test_database_directly():
    """Test database directly without imports"""
    print("🧪 Testing Database Directly")
    print("=" * 50)
    
    if not DATABASE_PATH.exists():
        print(f"❌ Database not found at: {DATABASE_PATH}")
        return
    
    print(f"✅ Database found at: {DATABASE_PATH}")
    
    # Test user ID from the conversation (HighTower)
    test_user_id = 574747247
    
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            # Check agents for this user
            cursor.execute('''
                SELECT agent_name, faction
                FROM agents
                WHERE telegram_user_id = ?
                ORDER BY agent_name
            ''', (test_user_id,))
            
            user_agents = cursor.fetchall()
            
            print(f"📋 Agents for user ID {test_user_id}:")
            print(f"🔍 Found {len(user_agents)} agents:")
            
            for agent_name, faction in user_agents:
                print(f"  • {agent_name} ({faction})")
            
            if user_agents:
                print("\n✅ User has agents - progress command should work!")
                
                # Check if there are any submissions for this agent
                agent_name = user_agents[0][0]
                cursor.execute('''
                    SELECT COUNT(*) 
                    FROM submissions s
                    JOIN agents a ON s.agent_id = a.id
                    WHERE a.agent_name = ? AND a.telegram_user_id = ?
                ''', (agent_name, test_user_id))
                
                submission_count = cursor.fetchone()[0]
                print(f"📊 Submissions for {agent_name}: {submission_count}")
                
                if submission_count > 0:
                    print("✅ Agent has submissions - progress reports should be available!")
                else:
                    print("⚠️  Agent has no submissions - progress reports will be empty")
                    
            else:
                print("❌ No agents found - this explains why progress command fails!")
                
                # Let's check all agents in the database
                cursor.execute('SELECT agent_name, faction, telegram_user_id FROM agents')
                all_agents = cursor.fetchall()
                
                print(f"\n🔍 All agents in database ({len(all_agents)} total):")
                for agent_name, faction, user_id in all_agents:
                    print(f"  • {agent_name} ({faction}) - User ID: {user_id}")
                    
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    test_database_directly()