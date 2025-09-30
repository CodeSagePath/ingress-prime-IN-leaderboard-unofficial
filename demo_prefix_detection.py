#!/usr/bin/env python3
"""
Demo script showing the "Time Span Agent Name" prefix detection system in action
"""

from src.services.ingress_prefix_detector import IngressPrefixDetector

def demo_prefix_detection():
    """Demonstrate the prefix detection system with real examples"""
    
    print("🚀 Ingress Bot Prefix Detection Demo")
    print("=" * 50)
    
    detector = IngressPrefixDetector()
    mode_info = detector.get_mode_info()
    
    print(f"🔧 Current Mode: {mode_info['mode']}")
    print(f"📝 Description: {mode_info['description']}")
    print(f"🎯 Required Pattern: '{mode_info['required_pattern']}'")
    print()
    
    # Test cases
    test_cases = [
        {
            "name": "✅ Perfect Ingress Header",
            "text": "Time Span Agent Name Agent Faction Date (yyyy-mm-dd) Time (hh:mm:ss) Level Lifetime AP Current AP ALL TIME TestAgent Enlightened 2025-01-15 12:30:45 16 50000000 25000000"
        },
        {
            "name": "✅ Header with Custom Message",
            "text": "Time Span Agent Name Here are my latest stats: ALL TIME TestAgent Enlightened 2025-01-15 12:30:45 16 50000000 25000000"
        },
        {
            "name": "✅ Case Insensitive",
            "text": "time span agent name ALL TIME TestAgent Enlightened 2025-01-15 12:30:45 16 50000000 25000000"
        },
        {
            "name": "❌ Missing Header",
            "text": "ALL TIME TestAgent Enlightened 2025-01-15 12:30:45 16 50000000 25000000"
        },
        {
            "name": "❌ Random Message",
            "text": "Hello, how is the bot working today?"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🧪 Test {i}: {test_case['name']}")
        print(f"📝 Input: {test_case['text'][:80]}{'...' if len(test_case['text']) > 80 else ''}")
        
        # Check prefix detection
        has_prefix, info = detector.has_required_prefix(test_case['text'])
        should_process, reason, _ = detector.should_process_message(test_case['text'])
        
        print(f"✅ Has Prefix: {has_prefix}")
        if has_prefix:
            print(f"📍 Location: {info.get('pattern_location', 'unknown')}")
        print(f"⚙️  Should Process: {should_process} ({reason})")
        
        # Show user guidance
        guidance = detector.create_user_guidance_message(has_prefix, info)
        print(f"💬 User Guidance: {guidance[:100]}{'...' if len(guidance) > 100 else ''}")
        print("-" * 60)
        print()
    
    print("🎯 Summary:")
    print(f"• In '{mode_info['mode']}' mode")
    if mode_info['mode'] == 'strict':
        print("• Only messages with 'Time Span Agent Name' are processed")
        print("• All other messages are ignored with helpful guidance")
    else:
        print("• All messages are processed")
        print("• Messages with 'Time Span Agent Name' get enhanced processing")
    print("• Pattern detection is case-insensitive")
    print("• Pattern can appear anywhere in the message")
    print()
    print("🔄 To switch modes:")
    print("   python switch_prefix_mode.py strict")
    print("   python switch_prefix_mode.py flexible")

if __name__ == "__main__":
    demo_prefix_detection()