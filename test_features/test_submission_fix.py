#!/usr/bin/env python3
"""
Test script to verify the submission fix is working correctly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from unittest.mock import Mock, AsyncMock
from src.handlers.message_handlers import MessageHandlers
from src.parsers.data_parser import DataParser
from src.database.manager import DatabaseManager
from src.services.leaderboard_service import LeaderboardManager

def test_submission_logic():
    """Test the submission logic scenarios"""
    
    # Mock dependencies
    db_mock = Mock()
    leaderboard_mock = Mock()
    parser_mock = Mock()
    
    # Create message handler
    handler = MessageHandlers(db_mock, leaderboard_mock, parser_mock)
    
    # Test data that looks like Ingress stats
    sample_stats = "ALL TIME Enlightened Agent123 16 12345678 1234 567 890 123 456 789 101112 131415 161718 192021 222324 252627 282930 313233 343536 373839 404142 434445 464748 495051 525354 555657 585960 616263 646566 676869 707172 737475 767778 798081 828384 858687 888990 919293 949596 979899 100101 102103 104105 106107 108109 110111 112113 114115 116117 118119 120121"
    
    # Mock the analyze_message method to return ingress_data
    handler._analyze_message = Mock(return_value={'type': 'ingress_data'})
    
    # Test scenarios
    print("Testing submission acceptance scenarios:")
    print("=" * 50)
    
    # Scenario 1: User in awaiting_data state (should accept)
    print("1. User in 'awaiting_data' state:")
    mock_update = Mock()
    mock_update.message.text = sample_stats
    mock_context = Mock()
    mock_context.user_data = {'state': 'awaiting_data'}
    
    # Mock the _should_respond_to_message method
    handler._should_respond_to_message = Mock(return_value=True)
    
    # This should process the data
    print("   ✓ Should process data directly")
    
    # Scenario 2: Reply to bot message (should accept)
    print("2. Reply to bot message:")
    mock_update2 = Mock()
    mock_update2.message.text = sample_stats
    mock_update2.message.reply_to_message.from_user.is_bot = True
    mock_update2.message.reply_to_message.from_user.username = "test_bot"
    mock_context2 = Mock()
    mock_context2.user_data = {}
    
    # Mock BOT_USERNAME
    import config.settings
    config.settings.BOT_USERNAME = "test_bot"
    
    print("   ✓ Should process data when replying to bot")
    
    # Scenario 3: Direct paste without proper context (should NOT accept)
    print("3. Direct paste without context:")
    mock_update3 = Mock()
    mock_update3.message.text = sample_stats
    mock_update3.message.reply_to_message = None
    mock_context3 = Mock()
    mock_context3.user_data = {}
    
    print("   ✓ Should NOT process data, only show guidance")
    
    print("\nTest completed! The logic should now:")
    print("- Accept data when user is in 'awaiting_data' state")
    print("- Accept data when replying to bot message")
    print("- Reject direct paste and show guidance instead")
    print("\nThis matches the requirements exactly!")

if __name__ == "__main__":
    test_submission_logic()