#!/usr/bin/env python3
"""
Script to ensure direct paste functionality is working
This will verify and potentially fix any issues with direct paste
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_message_handlers():
    """Check if message handlers have direct paste functionality"""
    print("🔍 Checking message handlers implementation...")
    
    try:
        with open('/home/codesagepath/Documents/TGBot/ingress-leaderboard/src/handlers/message_handlers.py', 'r') as f:
            content = f.read()
        
        # Check for key indicators of direct paste functionality
        checks = {
            "Always respond enabled": "return True" in content and "RESTORED" in content,
            "Direct paste processing": "Valid stats data - process it directly" in content,
            "RESTORED FUNCTIONALITY": "RESTORED FUNCTIONALITY" in content,
            "Auto-process valid data": "Auto-process valid Ingress data" in content
        }
        
        print("\n📋 Direct Paste Functionality Checks:")
        all_good = True
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"{status} {check}: {'PRESENT' if result else 'MISSING'}")
            if not result:
                all_good = False
        
        if all_good:
            print("\n✅ All direct paste functionality is present in the code!")
        else:
            print("\n❌ Some direct paste functionality is missing!")
            
        return all_good
        
    except Exception as e:
        print(f"❌ Error checking message handlers: {e}")
        return False

def check_bot_service():
    """Check if bot service is using the correct message handlers"""
    print("\n🔍 Checking bot service configuration...")
    
    try:
        with open('/home/codesagepath/Documents/TGBot/ingress-leaderboard/src/services/bot_service.py', 'r') as f:
            content = f.read()
        
        # Check if bot service is using MessageHandlers
        checks = {
            "MessageHandlers imported": "MessageHandlers" in content,
            "MessageHandlers initialized": "self.message_handlers = MessageHandlers" in content,
            "Message handler registered": "self.message_handlers.handle_message" in content
        }
        
        print("\n📋 Bot Service Configuration Checks:")
        all_good = True
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"{status} {check}: {'PRESENT' if result else 'MISSING'}")
            if not result:
                all_good = False
        
        if all_good:
            print("\n✅ Bot service is configured correctly!")
        else:
            print("\n❌ Bot service configuration has issues!")
            
        return all_good
        
    except Exception as e:
        print(f"❌ Error checking bot service: {e}")
        return False

def verify_data_analysis():
    """Verify the data analysis function works correctly"""
    print("\n🔍 Verifying data analysis functionality...")
    
    try:
        from src.handlers.message_handlers import MessageHandlers
        from src.database import DatabaseManager
        from src.services.leaderboard_service import LeaderboardManager
        from src.parsers import DataParser
        
        # Create handler instance
        db = DatabaseManager()
        leaderboard = LeaderboardManager()
        parser = DataParser()
        handler = MessageHandlers(db, leaderboard, parser)
        
        # Test data
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
        
        # Test analysis
        result = handler._analyze_message(test_data)
        print(f"\n📊 Analysis result: {result}")
        
        if result['type'] == 'ingress_data':
            print("✅ Data analysis is working correctly!")
            return True
        else:
            print("❌ Data analysis is not working correctly!")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying data analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main verification function"""
    print("🚀 DIRECT PASTE FUNCTIONALITY VERIFICATION")
    print("=" * 60)
    
    # Run all checks
    checks = [
        ("Message Handlers", check_message_handlers),
        ("Bot Service", check_bot_service),
        ("Data Analysis", verify_data_analysis)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{'='*20} {name} {'='*20}")
        result = check_func()
        results.append((name, result))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
        if not result:
            all_passed = False
    
    print(f"\n🎯 Overall Status: {'✅ ALL CHECKS PASSED' if all_passed else '❌ SOME CHECKS FAILED'}")
    
    if all_passed:
        print("\n🎉 DIRECT PASTE FUNCTIONALITY IS WORKING!")
        print("\n📋 The bot should accept stats data through:")
        print("1. ✅ Direct copy-paste of valid stats data")
        print("2. ✅ /submit <stats data> command")
        print("3. ✅ Submit button → reply to bot message")
        print("4. ✅ Submit button → awaiting data state")
        print("\n💡 If users are still experiencing issues, it might be:")
        print("   • Bot not running the latest version")
        print("   • Bot needs to be restarted")
        print("   • Data format issues from users")
        print("   • Network/deployment issues")
    else:
        print("\n⚠️ ISSUES DETECTED!")
        print("Direct paste functionality may not be working correctly.")
        print("Please check the failed components above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)