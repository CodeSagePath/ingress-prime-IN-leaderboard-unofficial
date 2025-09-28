#!/usr/bin/env python3
"""
Debug the data detection function
"""

def debug_detection(text):
    """Debug what the detection function sees"""
    parts = text.split()
    print(f"Text: {text[:100]}...")
    print(f"Parts count: {len(parts)}")
    print(f"First 10 parts: {parts[:10]}")
    
    if len(parts) >= 4:
        print(f"parts[0]: '{parts[0]}'")
        print(f"parts[1]: '{parts[1]}'")
        print(f"parts[2]: '{parts[2]}'")
        print(f"parts[3]: '{parts[3]}'")
    
    # Check conditions
    print(f"parts[0] == 'ALL': {parts[0] == 'ALL' if len(parts) > 0 else False}")
    print(f"parts[1] == 'TIME': {parts[1] == 'TIME' if len(parts) > 1 else False}")
    print(f"parts[3] in factions: {parts[3] in ['Enlightened', 'Resistance', 'enlightened', 'resistance'] if len(parts) > 3 else False}")

if __name__ == "__main__":
    test_cases = [
        "ALL TIME AgentD1nesh Resistance 2025-09-21 20:58:35 14 103740604 22233357",
        "WEEKLY TestAgent Enlightened 2025-01-01 12:00:00 16 1000000",
    ]
    
    for text in test_cases:
        print("=" * 50)
        debug_detection(text)
        print()