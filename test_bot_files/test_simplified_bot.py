#!/usr/bin/env python3
"""
Test script to verify the simplified bot behavior
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.handlers.message_handlers import MessageHandlers
from src.database.manager import DatabaseManager
from src.parsers.data_parser import DataParser
from unittest.mock import Mock, MagicMock

def test_message_filtering():
    """Test that the bot is less intrusive with message filtering"""
    
    # Mock dependencies
    db_manager = Mock()
    leaderboard_manager = Mock()
    data_parser = Mock()
    
    # Create message handler
    handler = MessageHandlers(db_manager, leaderboard_manager, data_parser)
    
    # Mock update and context
    update = Mock()
    context = Mock()
    context.user_data = {}
    
    # Test case 1: Regular conversation message (should be ignored)
    update.message.text = "Hey, how are you doing today?"
    update.message.entities = None
    update.message.reply_to_message = None
    update.effective_user.id = 12345
    
    # This should return False (don't respond)
    should_respond = handler._should_respond_to_message(update, context)
    print(f"Regular conversation message - Should respond: {should_respond}")
    assert should_respond == False, "Bot should not respond to regular conversation"
    
    # Test case 2: Message with bot mention (should respond)
    update.message.text = "@ingressIN_leaderboard_bot hello"
    entity = Mock()
    entity.type = "mention"
    entity.offset = 0
    entity.length = 26  # Length of "@ingressIN_leaderboard_bot"
    update.message.entities = [entity]
    
    should_respond = handler._should_respond_to_message(update, context)
    print(f"Message with bot mention - Should respond: {should_respond}")
    assert should_respond == True, "Bot should respond when mentioned"
    
    # Test case 3: Message that looks like Ingress stats (should respond)
    ingress_stats = """Time Span Agent Name
ALL TIME TestAgent Enlightened 2025-01-01 12:00:00
Lifetime AP: 50000000
Current Level: 16
Unique Portals Visited: 5000
Portals Discovered: 100
XM Collected: 1000000
Resonators Deployed: 10000
Links Created: 2000
Control Fields Created: 500
Mind Units Captured: 100000"""
    
    update.message.text = ingress_stats
    update.message.entities = None
    
    should_respond = handler._should_respond_to_message(update, context)
    print(f"Ingress stats message - Should respond: {should_respond}")
    assert should_respond == True, "Bot should respond to Ingress statistics"
    
    # Test case 4: Short message that doesn't look like stats (should be ignored)
    update.message.text = "lol"
    should_respond = handler._should_respond_to_message(update, context)
    print(f"Short non-stats message - Should respond: {should_respond}")
    assert should_respond == False, "Bot should not respond to short non-stats messages"
    
    print("✅ All message filtering tests passed!")

def test_ingress_stats_detection():
    """Test the new _looks_like_ingress_stats method"""
    
    db_manager = Mock()
    leaderboard_manager = Mock()
    data_parser = Mock()
    handler = MessageHandlers(db_manager, leaderboard_manager, data_parser)
    
    # Test case 1: Clear Ingress stats
    stats_text = """Time Span Agent Name
ALL TIME TestAgent Enlightened 2025-01-01 12:00:00
Lifetime AP: 50000000
Current Level: 16
Unique Portals Visited: 5000
Portals Discovered: 100
XM Collected: 1000000
Resonators Deployed: 10000
Links Created: 2000
Control Fields Created: 500
Mind Units Captured: 100000
Longest Link Ever Created: 1000 km
Largest Control Field: 50000 MUs
XM Recharged: 500000
Portals Captured: 1000
Unique Portals Captured: 800
Mods Deployed: 2000
Hacks: 20000
Drone Hacks: 500
Glyph Hack Points: 100000"""
    
    result = handler._looks_like_ingress_stats(stats_text)
    print(f"Clear Ingress stats - Detected: {result}")
    assert result == True, "Should detect clear Ingress statistics"
    
    # Test case 2: Regular conversation
    conversation = "Hey, what's up? How was your day today?"
    result = handler._looks_like_ingress_stats(conversation)
    print(f"Regular conversation - Detected: {result}")
    assert result == False, "Should not detect regular conversation as stats"
    
    # Test case 3: Short message
    short_msg = "hi"
    result = handler._looks_like_ingress_stats(short_msg)
    print(f"Short message - Detected: {result}")
    assert result == False, "Should not detect short messages as stats"
    
    print("✅ All Ingress stats detection tests passed!")

if __name__ == "__main__":
    print("Testing simplified bot behavior...")
    print("=" * 50)
    
    try:
        test_message_filtering()
        print()
        test_ingress_stats_detection()
        print()
        print("🎉 All tests passed! The bot is now much less intrusive.")
        print()
        print("Key improvements:")
        print("- Bot only responds when mentioned, replied to, or when detecting actual Ingress stats")
        print("- No more interrupting normal conversations")
        print("- Simplified error messages")
        print("- Cleaner submission process")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)