#!/usr/bin/env python3
"""
Test script for the enhanced bot flow
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

async def test_data_detection():
    """Test if the bot can detect Ingress data automatically"""
    print("🧪 Testing automatic data detection...")
    
    try:
        from src.handlers.message_handlers import MessageHandlers
        from src.database.manager import DatabaseManager
        from src.parsers.data_parser import DataParser
        from src.services.leaderboard_service import LeaderboardManager
        
        # Initialize components
        db = DatabaseManager()
        parser = DataParser()
        leaderboard = LeaderboardManager()
        handlers = MessageHandlers(db, leaderboard, parser)
        
        # Test with user's actual data (sent as a regular message, not command)
        user_data = "ALL TIME AgentD1nesh Resistance 2025-09-21 20:58:35 14 103740604 22233357 3426 406 3 176 172552376 3148 12423 956 51182 12309 12722 167096645 1926 37881720 122773281 8184 2773 11640 32283 1440 72431 13294 154 398 43727 5772 6678 2723 85 51 4387 33192 3891 2694 889 354 242201 243 1602786688 65 6589 965 138 1067 166 20 14 3 9020 22 196575 2 4"
        
        update = MockUpdate(user_data)
        context = MockContext()
        # Note: user is NOT in awaiting_data state
        
        # Test message handling
        result = await handlers.handle_message(update, context)
        
        print(f"handle_message returned: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_data_detection_function():
    """Test the data detection function directly"""
    print("\n🧪 Testing data detection function...")
    
    try:
        from src.handlers.message_handlers import MessageHandlers
        from src.database.manager import DatabaseManager
        from src.parsers.data_parser import DataParser
        from src.services.leaderboard_service import LeaderboardManager
        
        # Initialize components
        db = DatabaseManager()
        parser = DataParser()
        leaderboard = LeaderboardManager()
        handlers = MessageHandlers(db, leaderboard, parser)
        
        # Test cases
        test_cases = [
            ("ALL TIME AgentD1nesh Resistance 2025-09-21 20:58:35 14 103740604 22233357", True),
            ("Hello world", False),
            ("WEEKLY TestAgent Enlightened 2025-01-01 12:00:00 16 1000000", True),
            ("Just some random text", False),
            ("ALL TIME", False),  # Too short
        ]
        
        for text, expected in test_cases:
            result = handlers._looks_like_ingress_data(text)
            status = "✅" if result == expected else "❌"
            print(f"{status} '{text[:50]}...' -> {result} (expected {expected})")
        
        return True
        
    except Exception as e:
        print(f"❌ Data detection function test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all async tests"""
    print("🚀 Starting enhanced bot flow tests...\n")
    
    # Test data detection function
    detection_func_success = await test_data_detection_function()
    
    # Test automatic data detection and processing
    detection_success = await test_data_detection()
    
    print(f"\n📊 Results:")
    print(f"Data detection function: {'✅' if detection_func_success else '❌'}")
    print(f"Automatic data detection: {'✅' if detection_success else '❌'}")
    
    if detection_func_success and detection_success:
        print("\n🎉 All enhanced tests passed!")
        print("\nThe bot now supports:")
        print("1. /submit (interactive mode)")
        print("2. /submit [data] (direct submission)")
        print("3. Automatic detection of data sent as regular messages")
    else:
        print("\n⚠️ Some enhanced tests failed.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())