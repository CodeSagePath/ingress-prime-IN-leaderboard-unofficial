#!/usr/bin/env python3
"""
Test script to verify strict mode behavior fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.ingress_prefix_detector import IngressPrefixDetector

def test_strict_mode_behavior():
    """Test that strict mode only responds to appropriate messages"""
    
    print("🧪 Testing Strict Mode Behavior Fix")
    print("=" * 50)
    
    # Initialize components
    detector = IngressPrefixDetector()
    
    print(f"📋 Current mode: {detector.get_mode_info()['mode']}")
    print(f"📋 Required pattern: '{detector.required_pattern}'")
    print()
    
    # Test cases
    test_messages = [
        "Hello world",  # Should be ignored in strict mode
        "How are you?",  # Should be ignored in strict mode
        "Time Span Agent Name TestAgent Enlightened 2024-01-01 12:00:00 Level 16",  # Should be processed
        "@IngressIN_leaderboard_bot hello",  # Should be processed (mention)
        "STATS: some data here",  # Should be ignored (no required prefix)
        "Time Span Agent Name",  # Should be processed but might fail validation
    ]
    
    print("🔍 Testing message processing decisions:")
    print()
    
    for i, message in enumerate(test_messages, 1):
        should_process, reason, info = detector.should_process_message(message)
        
        print(f"Test {i}: '{message[:50]}{'...' if len(message) > 50 else ''}'")
        print(f"  ✅ Should process: {should_process}")
        print(f"  📝 Reason: {reason}")
        print(f"  🔍 Has prefix: {info.get('pattern_found', False)}")
        print()
    
    print("✅ Test completed!")
    print()
    print("📊 Expected behavior in strict mode:")
    print("  • Messages without 'Time Span Agent Name' should be ignored")
    print("  • Messages with the prefix should be processed")
    print("  • Bot mentions should always be processed")
    print("  • Replies to bot should always be processed")

if __name__ == "__main__":
    test_strict_mode_behavior()