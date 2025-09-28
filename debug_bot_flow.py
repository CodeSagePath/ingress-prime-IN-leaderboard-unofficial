#!/usr/bin/env python3
"""
Debug script to test the bot flow
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
    def __init__(self):
        self.user_data = {}
        self.args = []

async def test_submit_command():
    """Test the submit command"""
    print("🧪 Testing submit command...")
    
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
        
        # Create mock objects
        update = MockUpdate("/submit")
        context = MockContext()
        
        # Test submit command
        result = await handlers.submit_command(update, context)
        
        print(f"submit_command returned: {result}")
        print(f"User state: {context.user_data.get('state')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Submit command test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_message_handling():
    """Test message handling with data submission"""
    print("\n📨 Testing message handling...")
    
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
        
        # Create mock objects
        user_data = "ALL TIME AgentD1nesh Resistance 2025-09-21 20:58:35 14 103740604 22233357 3426 406 3 176 172552376 3148 12423 956 51182 12309 12722 167096645 1926 37881720 122773281 8184 2773 11640 32283 1440 72431 13294 154 398 43727 5772 6678 2723 85 51 4387 33192 3891 2694 889 354 242201 243 1602786688 65 6589 965 138 1067 166 20 14 3 9020 22 196575 2 4"
        
        update = MockUpdate(user_data)
        context = MockContext()
        context.user_data['state'] = 'awaiting_data'  # Simulate user in submission mode
        
        # Test message handling
        result = await handlers.handle_message(update, context)
        
        print(f"handle_message returned: {result}")
        print(f"User state after: {context.user_data.get('state')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Message handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_full_flow():
    """Test the complete submission flow"""
    print("\n🔄 Testing full submission flow...")
    
    try:
        from src.handlers.command_handlers import CommandHandlers
        from src.handlers.message_handlers import MessageHandlers
        from src.database.manager import DatabaseManager
        from src.parsers.data_parser import DataParser
        from src.services.leaderboard_service import LeaderboardManager
        
        # Initialize components
        db = DatabaseManager()
        parser = DataParser()
        leaderboard = LeaderboardManager()
        cmd_handlers = CommandHandlers(db, leaderboard, parser)
        msg_handlers = MessageHandlers(db, leaderboard, parser)
        
        # Step 1: User sends /submit
        print("Step 1: User sends /submit")
        update1 = MockUpdate("/submit")
        context1 = MockContext()
        
        await cmd_handlers.submit_command(update1, context1)
        print(f"State after /submit: {context1.user_data.get('state')}")
        
        # Step 2: User sends data
        print("\nStep 2: User sends data")
        user_data = "ALL TIME AgentD1nesh Resistance 2025-09-21 20:58:35 14 103740604 22233357 3426 406 3 176 172552376 3148 12423 956 51182 12309 12722 167096645 1926 37881720 122773281 8184 2773 11640 32283 1440 72431 13294 154 398 43727 5772 6678 2723 85 51 4387 33192 3891 2694 889 354 242201 243 1602786688 65 6589 965 138 1067 166 20 14 3 9020 22 196575 2 4"
        
        update2 = MockUpdate(user_data)
        context2 = MockContext()
        context2.user_data['state'] = 'awaiting_data'  # Copy state from step 1
        
        await msg_handlers.handle_message(update2, context2)
        print(f"State after data submission: {context2.user_data.get('state')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Full flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all async tests"""
    print("🚀 Starting bot flow debug tests...\n")
    
    # Test submit command
    submit_success = await test_submit_command()
    
    # Test message handling
    message_success = await test_message_handling()
    
    # Test full flow
    flow_success = await test_full_flow()
    
    print(f"\n📊 Results:")
    print(f"Submit Command: {'✅' if submit_success else '❌'}")
    print(f"Message Handling: {'✅' if message_success else '❌'}")
    print(f"Full Flow: {'✅' if flow_success else '❌'}")
    
    if submit_success and message_success and flow_success:
        print("\n🎉 All bot flow tests passed!")
    else:
        print("\n⚠️ Some bot flow tests failed.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())