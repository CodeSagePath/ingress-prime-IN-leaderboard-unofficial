#!/usr/bin/env python3
"""
Test the progress command implementation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Mock the telegram update and context
class MockUser:
    def __init__(self, user_id):
        self.id = user_id

class MockMessage:
    def __init__(self):
        self.reply_text_calls = []
    
    async def reply_text(self, text, parse_mode=None):
        self.reply_text_calls.append((text, parse_mode))
        print("📱 Bot would send:")
        print("-" * 40)
        print(text)
        print("-" * 40)

class MockUpdate:
    def __init__(self, user_id):
        self.effective_user = MockUser(user_id)
        self.message = MockMessage()

class MockContext:
    def __init__(self, args=None):
        self.args = args or []

async def test_progress_command():
    """Test the progress command implementation"""
    print("🧪 Testing Progress Command Implementation")
    print("=" * 50)
    
    # Import the required modules
    from database.manager import DatabaseManager
    from services.leaderboard_service import LeaderboardManager
    from handlers.command_handlers import CommandHandlers
    from config.settings import LEADERBOARD_STATS
    
    # Initialize components
    db = DatabaseManager()
    leaderboard = LeaderboardManager(db)
    handlers = CommandHandlers(db, None, leaderboard)  # parser not needed for this test
    
    # Test user ID from the conversation (HighTower)
    test_user_id = 574747247
    
    # Test 1: Basic progress command
    print("🧪 Test 1: Basic /progress command")
    update = MockUpdate(test_user_id)
    context = MockContext([])
    
    await handlers.progress_command(update, context)
    
    # Test 2: Progress with specific stat
    print("\n🧪 Test 2: /progress Distance_Walked")
    update = MockUpdate(test_user_id)
    context = MockContext(["Distance_Walked"])
    
    await handlers.progress_command(update, context)
    
    # Test 3: Progress with invalid stat
    print("\n🧪 Test 3: /progress Invalid_Stat")
    update = MockUpdate(test_user_id)
    context = MockContext(["Invalid_Stat"])
    
    await handlers.progress_command(update, context)
    
    # Test 4: Progress for non-existent user
    print("\n🧪 Test 4: Progress for non-existent user")
    update = MockUpdate(999999999)  # Non-existent user
    context = MockContext([])
    
    await handlers.progress_command(update, context)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_progress_command())