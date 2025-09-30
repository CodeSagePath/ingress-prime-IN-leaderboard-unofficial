#!/usr/bin/env python3
"""
Test script to verify current bot behavior with direct paste
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.handlers.message_handlers import MessageHandlers
from src.database import DatabaseManager
from src.services.leaderboard_service import LeaderboardManager
from src.parsers import DataParser
from unittest.mock import Mock, AsyncMock
import asyncio

async def test_current_behavior():
    """Test current bot behavior"""
    print("🔍 Testing Current Bot Behavior")
    print("=" * 50)
    
    # Create real instances
    db = DatabaseManager()
    leaderboard = LeaderboardManager()
    parser = DataParser()
    handler = MessageHandlers(db, leaderboard, parser)
    
    # Test data - realistic Ingress stats
    test_data = """ALL TIME
Agent Name: TestAgent
Faction: Enlightened
Level: 16
Lifetime AP: 50000000
Current AP: 45000000
Distance Walked: 1000 km
Resonators Deployed: 100000
Links Created: 50000
Control Fields Created: 25000
Mind Units Captured: 1000000
Longest Link Ever Created: 100 km
Largest Control Field: 50000 MUs
XM Collected: 200000000
Portals Discovered: 5000
Seer Points: 2500
Portals Captured: 15000
Unique Portals Visited: 8000
Unique Portals Drone Visited: 500
Furthest Drone Distance: 1000 km
Mods Deployed: 30000
Resonators Destroyed: 80000
Portals Neutralized: 12000
Enemy Links Destroyed: 40000
Enemy Fields Destroyed: 20000
Max Time Portal Held: 150 days
Max Time Link Maintained: 100 days
Max Link Length x Days: 50000 km×days
Max Time Field Maintained: 80 days
Largest Field MUs x Days: 1000000 MU×days
Unique Missions Completed: 200
Hacks: 500000
Glyph Hack Points: 150000
Longest Hacking Streak: 365 days
Agents Successfully Recruited: 50
Mission Day(s) Attended: 10
NL-1331 Meetup(s) Attended: 5
First Saturday Events: 20
Recursions: 2
Spec Ops Completed: 15
Stealth Ops Completed: 8
Intel Ops Completed: 12
FS Ops Completed: 25
Clear Ops Completed: 18
Complex Ops Completed: 6
Operation Days Attended: 30
Kinetic Capsules Completed: 100
Overclock Portal Attacks: 5000
Overclock Portal Defenses: 3000
Overclock Portal Neutralizations: 2000
Overclock Links Created: 1500
Overclock Fields Created: 800
Overclock MUs Captured: 50000
Drone Hacks: 10000
Drone Portals Visited: 2000
Machina Links Destroyed: 1000
Machina Resonators Destroyed: 5000
Machina Portals Neutralized: 800
Machina Portals Reclaimed: 600
Machina Clusters Neutralized: 50
Machina Clusters Reclaimed: 30"""
    
    # Mock update and context
    update = Mock()
    update.effective_user.id = 12345
    update.message.text = test_data
    update.message.reply_to_message = None
    update.message.entities = None
    update.message.reply_text = AsyncMock()
    
    context = Mock()
    context.user_data = {}
    
    print("📊 Testing with realistic Ingress statistics data...")
    print(f"Data length: {len(test_data.split())} words")
    
    # Test the _should_respond_to_message method
    should_respond = handler._should_respond_to_message(update, context)
    print(f"Should respond: {should_respond}")
    
    # Test the _analyze_message method
    analysis = handler._analyze_message(test_data)
    print(f"Message analysis: {analysis}")
    
    # Mock the process_data_submission method to track calls
    original_process = handler.process_data_submission
    handler.process_data_submission = AsyncMock()
    
    try:
        # Test the full handle_message flow
        await handler.handle_message(update, context)
        
        print(f"Process data submission called: {handler.process_data_submission.called}")
        print(f"Reply text called: {update.message.reply_text.called}")
        
        if update.message.reply_text.called:
            call_args = update.message.reply_text.call_args[0][0]
            print(f"Response message: {call_args[:100]}...")
            
            if "Processing your stats data" in call_args:
                print("✅ SUCCESS: Direct paste is working correctly!")
            else:
                print("❌ ISSUE: Unexpected response message")
        else:
            print("❌ ISSUE: No response message sent")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Restore original method
    handler.process_data_submission = original_process
    
    print("\n" + "=" * 50)
    print("🎯 Current Status:")
    print("Direct copy-paste functionality should be working!")
    print("If users are reporting issues, it might be:")
    print("1. Bot not running the latest version")
    print("2. Data format issues")
    print("3. Bot configuration problems")

if __name__ == "__main__":
    asyncio.run(test_current_behavior())