#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.ingress_prefix_detector import IngressPrefixDetector
from config.settings import BOT_USERNAME

class MockMessage:
    def __init__(self, text, entities=None, reply_to_message=None):
        self.text = text
        self.entities = entities or []
        self.reply_to_message = reply_to_message

class MockUser:
    def __init__(self, username=None, is_bot=False):
        self.username = username
        self.is_bot = is_bot

class MockUpdate:
    def __init__(self, message):
        self.message = message

class MockContext:
    def __init__(self):
        self.user_data = {}

def simulate_should_respond_to_message(update, context):
    """Simulate the updated _should_respond_to_message method"""
    message = update.message
    detector = IngressPrefixDetector()
    
    # Always respond if user is in data submission mode
    if context.user_data.get('state') == 'awaiting_data':
        return True, "awaiting_data"
    
    # Check if the message is a reply to one of our messages
    if message.reply_to_message and message.reply_to_message.from_user.is_bot:
        # Check if it's replying to this bot specifically
        if message.reply_to_message.from_user.username == BOT_USERNAME:
            # In strict mode, only respond to replies that have the required prefix
            if detector.strict_mode:
                message_text = message.text.strip() if message.text else ""
                should_process, reason, prefix_info = detector.should_process_message(message_text)
                return should_process, f"reply_to_bot_strict: {reason}"
            else:
                # In flexible mode, respond to all replies to bot messages
                return True, "reply_to_bot_flexible"
    
    # Check if the bot is mentioned in the message
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                # Extract the mentioned username
                mention_text = message.text[entity.offset:entity.offset + entity.length]
                if mention_text == f"@{BOT_USERNAME}":
                    return True, "bot_mentioned"
    
    # Check if message has the required prefix for Ingress data
    message_text = message.text.strip() if message.text else ""
    should_process, reason, prefix_info = detector.should_process_message(message_text)
    
    if should_process:
        return True, f"prefix_found: {reason}"
    
    # In strict mode, don't respond to messages without required conditions
    if detector.strict_mode:
        return False, f"strict_mode_ignore: {reason}"
    
    # In flexible mode, respond to all messages
    return True, "flexible_mode"

def test_fixed_logic():
    print(f"Bot username: {BOT_USERNAME}")
    print(f"Mode: strict")
    print()
    
    # Create a mock bot message (like a guidance message)
    bot_message = MockMessage("🚫 Prefix Required\n\nTo submit Ingress statistics...")
    bot_message.from_user = MockUser(username=BOT_USERNAME, is_bot=True)
    
    test_cases = [
        {
            "name": "Regular message (not reply)",
            "message": MockMessage("Hello world"),
            "context": MockContext(),
            "expected": False
        },
        {
            "name": "Reply to bot message without prefix",
            "message": MockMessage("Hello world", reply_to_message=bot_message),
            "context": MockContext(),
            "expected": False  # Should be False in strict mode now
        },
        {
            "name": "Reply to bot message with prefix",
            "message": MockMessage("Time Span Agent Name ALL TIME TestAgent Enlightened 2025-01-01 12:00:00 16 123456", reply_to_message=bot_message),
            "context": MockContext(),
            "expected": True
        },
        {
            "name": "Message with bot mention",
            "message": MockMessage(f"Hello @{BOT_USERNAME}"),
            "context": MockContext(),
            "expected": True
        },
        {
            "name": "Message with prefix (not reply)",
            "message": MockMessage("Time Span Agent Name ALL TIME TestAgent Enlightened 2025-01-01 12:00:00 16 123456"),
            "context": MockContext(),
            "expected": True
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        update = MockUpdate(test_case["message"])
        context = test_case["context"]
        
        should_respond, reason = simulate_should_respond_to_message(update, context)
        expected = test_case["expected"]
        
        status = "✅ PASS" if should_respond == expected else "❌ FAIL"
        if should_respond != expected:
            all_passed = False
        
        print(f"{status} {test_case['name']}")
        print(f"  Message: '{test_case['message'].text[:50]}{'...' if len(test_case['message'].text) > 50 else ''}'")
        print(f"  Expected: {expected}, Got: {should_respond}")
        print(f"  Reason: {reason}")
        print()
    
    print(f"Overall result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")

if __name__ == "__main__":
    test_fixed_logic()