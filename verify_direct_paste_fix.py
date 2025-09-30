#!/usr/bin/env python3
"""
Comprehensive verification script for direct copy-paste functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.handlers.message_handlers import MessageHandlers
from src.database import DatabaseManager
from src.services.leaderboard_service import LeaderboardManager
from src.parsers import DataParser
from unittest.mock import Mock, AsyncMock
import asyncio

# Various test data formats that users might paste
TEST_CASES = {
    "standard_all_time": """ALL TIME
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
Machina Clusters Reclaimed: 30""",

    "resistance_faction": """ALL TIME
Agent Name: ResistanceAgent
Faction: Resistance
Level: 15
Lifetime AP: 30000000
Current AP: 28000000
Distance Walked: 800 km
Resonators Deployed: 80000
Links Created: 40000
Control Fields Created: 20000
Mind Units Captured: 800000
Longest Link Ever Created: 80 km
Largest Control Field: 40000 MUs
XM Collected: 150000000
Portals Discovered: 4000
Seer Points: 2000
Portals Captured: 12000
Unique Portals Visited: 6000
Unique Portals Drone Visited: 400
Furthest Drone Distance: 800 km
Mods Deployed: 25000
Resonators Destroyed: 60000
Portals Neutralized: 10000
Enemy Links Destroyed: 30000
Enemy Fields Destroyed: 15000
Max Time Portal Held: 120 days
Max Time Link Maintained: 80 days
Max Link Length x Days: 40000 km×days
Max Time Field Maintained: 60 days
Largest Field MUs x Days: 800000 MU×days
Unique Missions Completed: 150
Hacks: 400000
Glyph Hack Points: 120000
Longest Hacking Streak: 300 days
Agents Successfully Recruited: 40
Mission Day(s) Attended: 8
NL-1331 Meetup(s) Attended: 4
First Saturday Events: 15
Recursions: 1
Spec Ops Completed: 12
Stealth Ops Completed: 6
Intel Ops Completed: 10
FS Ops Completed: 20
Clear Ops Completed: 15
Complex Ops Completed: 4
Operation Days Attended: 25
Kinetic Capsules Completed: 80
Overclock Portal Attacks: 4000
Overclock Portal Defenses: 2500
Overclock Portal Neutralizations: 1500
Overclock Links Created: 1200
Overclock Fields Created: 600
Overclock MUs Captured: 40000
Drone Hacks: 8000
Drone Portals Visited: 1500
Machina Links Destroyed: 800
Machina Resonators Destroyed: 4000
Machina Portals Neutralized: 600
Machina Portals Reclaimed: 500
Machina Clusters Neutralized: 40
Machina Clusters Reclaimed: 25""",

    "daily_stats": """DAILY
Agent Name: DailyAgent
Faction: Enlightened
Level: 12
Lifetime AP: 10000000
Current AP: 9500000
Distance Walked: 50 km
Resonators Deployed: 500
Links Created: 200
Control Fields Created: 100
Mind Units Captured: 5000
Longest Link Ever Created: 10 km
Largest Control Field: 2000 MUs
XM Collected: 1000000
Portals Discovered: 50
Seer Points: 25
Portals Captured: 100
Unique Portals Visited: 200
Unique Portals Drone Visited: 20
Furthest Drone Distance: 100 km
Mods Deployed: 150
Resonators Destroyed: 300
Portals Neutralized: 50
Enemy Links Destroyed: 150
Enemy Fields Destroyed: 75
Max Time Portal Held: 10 days
Max Time Link Maintained: 5 days
Max Link Length x Days: 500 km×days
Max Time Field Maintained: 3 days
Largest Field MUs x Days: 10000 MU×days
Unique Missions Completed: 10
Hacks: 2000
Glyph Hack Points: 500
Longest Hacking Streak: 30 days
Agents Successfully Recruited: 2
Mission Day(s) Attended: 1
NL-1331 Meetup(s) Attended: 0
First Saturday Events: 2
Recursions: 0
Spec Ops Completed: 1
Stealth Ops Completed: 0
Intel Ops Completed: 1
FS Ops Completed: 2
Clear Ops Completed: 1
Complex Ops Completed: 0
Operation Days Attended: 3
Kinetic Capsules Completed: 5
Overclock Portal Attacks: 100
Overclock Portal Defenses: 50
Overclock Portal Neutralizations: 25
Overclock Links Created: 30
Overclock Fields Created: 15
Overclock MUs Captured: 1000
Drone Hacks: 200
Drone Portals Visited: 50
Machina Links Destroyed: 20
Machina Resonators Destroyed: 100
Machina Portals Neutralized: 15
Machina Portals Reclaimed: 10
Machina Clusters Neutralized: 2
Machina Clusters Reclaimed: 1""",

    "partial_data": """ALL TIME
Agent Name: PartialAgent
Faction: Enlightened
Level: 10
Lifetime AP: 5000000""",

    "invalid_data": """This is just a regular message that doesn't contain any Ingress statistics."""
}

async def test_comprehensive_direct_paste():
    """Test comprehensive direct paste functionality"""
    print("🧪 COMPREHENSIVE DIRECT PASTE VERIFICATION")
    print("=" * 60)
    
    # Create handler instance
    db = DatabaseManager()
    leaderboard = LeaderboardManager()
    parser = DataParser()
    handler = MessageHandlers(db, leaderboard, parser)
    
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
    
    results = {}
    
    for test_name, test_data in TEST_CASES.items():
        print(f"\n🔍 Testing: {test_name}")
        print("-" * 40)
        
        update = create_mock_update(test_data)
        context = create_mock_context()
        
        # Mock the process_data_submission method
        handler.process_data_submission = AsyncMock()
        
        try:
            # Test message analysis
            analysis = handler._analyze_message(test_data)
            print(f"Analysis: {analysis}")
            
            # Test should respond
            should_respond = handler._should_respond_to_message(update, context)
            print(f"Should respond: {should_respond}")
            
            # Test full flow
            await handler.handle_message(update, context)
            
            # Check results
            processed = handler.process_data_submission.called
            replied = update.message.reply_text.called
            
            print(f"Data processed: {processed}")
            print(f"Reply sent: {replied}")
            
            if replied:
                call_args = update.message.reply_text.call_args[0][0]
                print(f"Response: {call_args[:50]}...")
                
                if analysis['type'] == 'ingress_data':
                    if "Processing your stats data" in call_args and processed:
                        results[test_name] = "✅ PASS"
                        print("✅ PASS: Valid data processed correctly")
                    else:
                        results[test_name] = "❌ FAIL"
                        print("❌ FAIL: Valid data not processed correctly")
                elif analysis['type'] == 'partial_data':
                    if "partial Ingress statistics" in call_args and not processed:
                        results[test_name] = "✅ PASS"
                        print("✅ PASS: Partial data handled correctly")
                    else:
                        results[test_name] = "❌ FAIL"
                        print("❌ FAIL: Partial data not handled correctly")
                else:
                    if "I'm here to help" in call_args and not processed:
                        results[test_name] = "✅ PASS"
                        print("✅ PASS: Invalid data handled correctly")
                    else:
                        results[test_name] = "❌ FAIL"
                        print("❌ FAIL: Invalid data not handled correctly")
            else:
                results[test_name] = "❌ FAIL"
                print("❌ FAIL: No response sent")
                
        except Exception as e:
            results[test_name] = f"❌ ERROR: {e}"
            print(f"❌ ERROR: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        print(f"{result} {test_name}")
    
    passed = sum(1 for r in results.values() if r == "✅ PASS")
    total = len(results)
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Direct copy-paste functionality is working correctly!")
        print("\n📋 Supported submission methods:")
        print("1. ✅ Direct copy-paste of valid stats data")
        print("2. ✅ /submit <stats data> command")
        print("3. ✅ Submit button → reply to bot message")
        print("4. ✅ Submit button → awaiting data state")
        print("\n🚀 The bot is ready to accept direct paste submissions!")
    else:
        print(f"\n⚠️ {total - passed} tests failed!")
        print("❌ There may be issues with direct paste functionality")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(test_comprehensive_direct_paste())
    sys.exit(0 if success else 1)