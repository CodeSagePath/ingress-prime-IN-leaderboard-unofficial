#!/usr/bin/env python3
"""
Test script for the fixed bot flow
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

class MockUpdate:
    """Mock Telegram Update object"""
    def __init__(self, text, user_id=12345):
        self.message = MockMessage(text)
        self.effective_user = MockUser(user_id)

class MockMessage:
    """Mock Telegram Message object"""
    def __init__(self, text):
        self.text = text
        self.reply_text_calls = []
    
    async def reply_text(self, text, parse_mode=None):
        self.reply_text_calls.append((text, parse_mode))
        print(f"Bot would reply: \n{text}")

class MockUser:
    """Mock Telegram User object"""
    def __init__(self, user_id):
        self.id = user_id
        self.first_name = "TestUser"

class MockContext:
    """Mock Telegram CallbackContext object"""
    def __init__(self, args=None):
        self.user_data = {}
        self.args = args or []

async def test_submit_with_data():
    """Test submit command with data provided directly"""
    print("🧪 Testing /submit with data provided directly...")
    
    try:
        from src.handlers.command_handlers import CommandHandlers
        from src.database.manager import DatabaseManager
        from src.parsers.data_parser import DataParser
        from src.services.leaderboard_service import LeaderboardManager
        
        # Initialize components
        db = DatabaseManager()
        parser = DataParser()
        leaderboard = LeaderboardManager()
        handlers = CommandHandlers(db, leaderboard, parser)
        
        # Simulate the user's actual command with data
        user_data = "ALL TIME AgentD1nesh Resistance 2025-09-21 20:58:35 14 103740604 22233357 3426 406 3 176 172552376 3148 12423 956 51182 12309 12722 167096645 1926 37881720 122773281 8184 2773 11640 32283 1440 72431 13294 154 398 43727 5772 6678 2723 85 51 4387 33192 3891 2694 889 354 242201 243 1602786688 65 6589 965 138 1067 166 20 14 3 9020 22 196575 2 4"
        
        # Split the data into args as Telegram would do
        args = user_data.split()
        
        update = MockUpdate("/submit")
        context = MockContext(args=args)
        
        # Test submit command with data
        result = await handlers.submit_command(update, context)
        
        print(f"submit_command returned: {result}")
        print(f"User state: {context.user_data.get('state')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Submit with data test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_submit_without_data():
    """Test submit command without data (original flow)"""
    print("\n🧪 Testing /submit without data (original flow)...")
    
    try:
        from src.handlers.command_handlers import CommandHandlers
        from src.database.manager import DatabaseManager
        from src.parsers.data_parser import DataParser
        from src.services.leaderboard_service import LeaderboardManager
        
        # Initialize components
        db = DatabaseManager()
        parser = DataParser()
        leaderboard = LeaderboardManager()
        handlers = CommandHandlers(db, leaderboard, parser)
        
        # Create mock objects (no args)
        update = MockUpdate("/submit")
        context = MockContext()  # No args
        
        # Test submit command without data
        result = await handlers.submit_command(update, context)
        
        print(f"submit_command returned: {result}")
        print(f"User state: {context.user_data.get('state')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Submit without data test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all async tests"""
    print("🚀 Starting fixed bot flow tests...\n")
    
    # Test submit with data (the problematic case)
    with_data_success = await test_submit_with_data()
    
    # Test submit without data (original flow should still work)
    without_data_success = await test_submit_without_data()
    
    print(f"\n📊 Results:")
    print(f"Submit with data: {'✅' if with_data_success else '❌'}")
    print(f"Submit without data: {'✅' if without_data_success else '❌'}")
    
    if with_data_success and without_data_success:
        print("\n🎉 All tests passed! The fix should work correctly.")
    else:
        print("\n⚠️ Some tests failed.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())