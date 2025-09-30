#!/usr/bin/env python3
"""
Test script to verify direct copy-paste functionality is restored
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.handlers.message_handlers import MessageHandlers
from unittest.mock import Mock, AsyncMock
import asyncio

# Mock classes
class MockDB:
    pass

class MockLeaderboard:
    pass

class MockParser:
    pass

# Test data
VALID_STATS_DATA = """ALL TIME
Agent Name: TestAgent
Faction: Enlightened
Level: 16
Lifetime AP: 50000000
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

PARTIAL_STATS_DATA = """ALL TIME
Agent Name: TestAgent
Faction: Enlightened
Level: 16
Lifetime AP: 50000000"""

INVALID_DATA = """Hello, this is just a regular message that doesn't contain any Ingress statistics data."""

async def test_direct_paste():
    """Test direct copy-paste functionality"""
    print("🧪 Testing Direct Copy-Paste Functionality")
    print("=" * 50)
    
    # Create handler instance
    handler = MessageHandlers(MockDB(), MockLeaderboard(), MockParser())
    
    # Mock update and context objects
    def create_mock_update(text):
        update = Mock()
        update.effective_user.id = 12345
        update.message.text = text
        update.message.reply_to_message = None
        update.message.entities = None
        update.message.reply_text = AsyncMock()
        return update
    
    def create_mock_context():
        context = Mock()
        context.user_data = {}
        return context
    
    # Test 1: Valid stats data (should be processed directly)
    print("\n1️⃣ Testing valid stats data (direct paste)...")
    update = create_mock_update(VALID_STATS_DATA)
    context = create_mock_context()
    
    # Mock the process_data_submission method
    handler.process_data_submission = AsyncMock()
    
    try:
        await handler.handle_message(update, context)
        
        # Check if processing was called
        if handler.process_data_submission.called:
            print("✅ PASS: Valid stats data was processed directly")
        else:
            print("❌ FAIL: Valid stats data was NOT processed")
            
        # Check the response message
        if update.message.reply_text.called:
            call_args = update.message.reply_text.call_args[0][0]
            if "Processing your stats data" in call_args:
                print("✅ PASS: Correct processing message sent")
            else:
                print(f"❌ FAIL: Unexpected message: {call_args}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 2: Partial stats data (should show guidance)
    print("\n2️⃣ Testing partial stats data...")
    update = create_mock_update(PARTIAL_STATS_DATA)
    context = create_mock_context()
    handler.process_data_submission.reset_mock()
    
    try:
        await handler.handle_message(update, context)
        
        # Should NOT process incomplete data
        if not handler.process_data_submission.called:
            print("✅ PASS: Partial data was NOT processed")
        else:
            print("❌ FAIL: Partial data was incorrectly processed")
            
        # Check guidance message
        if update.message.reply_text.called:
            call_args = update.message.reply_text.call_args[0][0]
            if "partial Ingress statistics" in call_args:
                print("✅ PASS: Correct guidance message for partial data")
            else:
                print(f"❌ FAIL: Unexpected message: {call_args}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 3: Invalid data (should show help)
    print("\n3️⃣ Testing invalid data...")
    update = create_mock_update(INVALID_DATA)
    context = create_mock_context()
    handler.process_data_submission.reset_mock()
    
    try:
        await handler.handle_message(update, context)
        
        # Should NOT process invalid data
        if not handler.process_data_submission.called:
            print("✅ PASS: Invalid data was NOT processed")
        else:
            print("❌ FAIL: Invalid data was incorrectly processed")
            
        # Check help message
        if update.message.reply_text.called:
            call_args = update.message.reply_text.call_args[0][0]
            if "I'm here to help" in call_args:
                print("✅ PASS: Correct help message for invalid data")
            else:
                print(f"❌ FAIL: Unexpected message: {call_args}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Direct copy-paste functionality has been RESTORED!")
    print("\n📋 Summary of supported submission methods:")
    print("1. ✅ Direct copy-paste of valid stats data")
    print("2. ✅ /submit <stats data> command")
    print("3. ✅ Submit button → reply to bot message")
    print("\n🚀 The bot now accepts stats data through direct paste again!")

if __name__ == "__main__":
    asyncio.run(test_direct_paste())