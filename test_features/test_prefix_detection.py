#!/usr/bin/env python3
"""
Test script for the "Time Span Agent Name" prefix detection system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.ingress_prefix_detector import IngressPrefixDetector
from config.settings import PREFIX_SETTINGS

def test_prefix_detection():
    """Test the prefix detection functionality"""
    
    print("🧪 Testing 'Time Span Agent Name' Prefix Detection System")
    print("=" * 60)
    
    # Initialize detector
    detector = IngressPrefixDetector()
    
    # Display current settings
    mode_info = detector.get_mode_info()
    print(f"📋 Current Mode: {mode_info['mode']}")
    print(f"🎯 Required Pattern: '{mode_info['required_pattern']}'")
    print(f"📝 Description: {mode_info['description']}")
    print()
    
    # Test cases
    test_cases = [
        {
            "name": "Valid Ingress Header with Data",
            "text": "Time Span Agent Name Agent Faction Date (yyyy-mm-dd) Time (hh:mm:ss) Level Lifetime AP Current AP ALL TIME TestAgent Enlightened 2024-01-15 12:30:45 16 50000000 25000000 1500 200 5000 800 75000000 1200 500 300 15000 2500 3500 8500000 1200 800 5000 12000 3500 2800 45000 150 1800 2500 1200 800 500 300 200 100 50 25 15 10 5 3 2 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
        },
        {
            "name": "Data with prefix at start",
            "text": "Time Span Agent Name here is my data: ALL TIME TestAgent Enlightened 2024-01-15 12:30:45 16 50000000 25000000"
        },
        {
            "name": "Data with prefix in middle",
            "text": "Here is my stats: Time Span Agent Name Agent Faction Date ALL TIME TestAgent Enlightened 2024-01-15 12:30:45 16"
        },
        {
            "name": "Data without required prefix",
            "text": "ALL TIME TestAgent Enlightened 2024-01-15 12:30:45 16 50000000 25000000 1500 200 5000"
        },
        {
            "name": "Just the prefix without data",
            "text": "Time Span Agent Name"
        },
        {
            "name": "Random message",
            "text": "Hello, how are you today?"
        },
        {
            "name": "Case insensitive test",
            "text": "time span agent name here is my data: ALL TIME TestAgent Enlightened 2024-01-15 12:30:45"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🧪 Test {i}: {test_case['name']}")
        print(f"📝 Input: {test_case['text'][:100]}{'...' if len(test_case['text']) > 100 else ''}")
        
        # Test prefix detection
        has_prefix, info = detector.has_required_prefix(test_case['text'])
        print(f"✅ Has Prefix: {has_prefix}")
        
        if has_prefix:
            print(f"📍 Location: {info['pattern_location']}")
            print(f"🧹 Clean Text: {info['clean_text'][:80]}{'...' if len(info['clean_text']) > 80 else ''}")
        
        # Test processing decision
        should_process, reason, process_info = detector.should_process_message(test_case['text'])
        print(f"⚙️  Should Process: {should_process} ({reason})")
        
        # Test guidance message
        guidance = detector.create_user_guidance_message(has_prefix, info)
        print(f"💬 Guidance: {guidance[:100]}{'...' if len(guidance) > 100 else ''}")
        
        print("-" * 60)
        print()

def test_mode_switching():
    """Test switching between strict and flexible modes"""
    print("🔄 Testing Mode Switching")
    print("=" * 60)
    
    # Test data without prefix
    test_text = "ALL TIME TestAgent Enlightened 2024-01-15 12:30:45 16 50000000"
    
    # Test in flexible mode (should process)
    os.environ['PREFIX_DETECTION_MODE'] = 'flexible'
    # Need to reload the module to pick up new environment variable
    import importlib
    import config.settings
    importlib.reload(config.settings)
    
    detector_flexible = IngressPrefixDetector()
    should_process_flex, reason_flex, _ = detector_flexible.should_process_message(test_text)
    
    print(f"🟢 Flexible Mode:")
    print(f"   Should Process: {should_process_flex} ({reason_flex})")
    
    # Test in strict mode (should not process)
    os.environ['PREFIX_DETECTION_MODE'] = 'strict'
    # Reload settings again
    importlib.reload(config.settings)
    
    detector_strict = IngressPrefixDetector()
    should_process_strict, reason_strict, _ = detector_strict.should_process_message(test_text)
    
    print(f"🔴 Strict Mode:")
    print(f"   Should Process: {should_process_strict} ({reason_strict})")
    
    print()

if __name__ == "__main__":
    test_prefix_detection()
    test_mode_switching()
    
    print("✅ All tests completed!")
    print("\n💡 To switch modes, set environment variable:")
    print("   export PREFIX_DETECTION_MODE=strict   # Only process with prefix")
    print("   export PREFIX_DETECTION_MODE=flexible # Process all, prefer with prefix")