#!/usr/bin/env python3

import sys
import os
sys.path.append('/home/codesagepath/Documents/TGBot/ingress-leaderboard')

import asyncio
from unittest.mock import Mock
from src.handlers.message_handlers import MessageHandlers
from src.database.db_manager import DatabaseManager
from src.services.leaderboard_manager import LeaderboardManager
from src.parsers.data_parser import DataParser
from config.settings import BOT_USERNAME

class MockMessage:
    def __init__(self, text, entities=None, reply_to_message=None):
        self.text = text
        self.entities = entities or []
        self.reply_to_message = reply_to_message

class MockUser:
    def __init__(self, username=None, is_bot=False, id=12345):
        self.username = username
        self.is_bot = is_bot
        self.id = id

class MockUpdate:
    def __init__(self, message):
        self.message = message
        self.effective_user = message.from_user if hasattr(message, 'from_user') else MockUser()

class MockContext:
    def __init__(self):
        self.user_data = {}

async def test_message_flow():
    print("Testing message flow with debug logging...")
    
    # Initialize components
    db = DatabaseManager()
    leaderboard = LeaderboardManager(db)
    parser = DataParser()
    handlers = MessageHandlers(db, leaderboard, parser)
    
    # Test case: Regular message that should be ignored
    message = MockMessage("Hello world")
    message.from_user = MockUser(id=12345)
    update = MockUpdate(message)
    context = MockContext()
    
    print(f"\nTesting message: '{message.text}'")
    print(f"Bot username: {BOT_USERNAME}")
    
    # Test _should_respond_to_message directly
    should_respond = handlers._should_respond_to_message(update, context)
    print(f"_should_respond_to_message returned: {should_respond}")
    
    # Test handle_message
    print("\nCalling handle_message...")
    try:
        result = await handlers.handle_message(update, context)
        print(f"handle_message completed without error")
    except Exception as e:
        print(f"handle_message raised exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_message_flow())