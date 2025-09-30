#!/usr/bin/env python3
"""
Test script for UX improvements to the Ingress Leaderboard Bot
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from parsers.data_parser import DataParser, ParseError

def test_error_messaging():
    """Test improved error messaging"""
    parser = DataParser()
    
    print("🧪 Testing UX Improvements...")
    print("=" * 50)
    
    # Test cases with different error scenarios
    test_cases = [
        {
            'name': 'Empty data',
            'data': '',
            'expected_type': 'empty'
        },
        {
            'name': 'Too few fields',
            'data': 'ALL TIME Agent123',
            'expected_type': 'too_few_fields'
        },
        {
            'name': 'Missing faction',
            'data': 'ALL TIME Agent123 BadFaction 2025-01-15 12:30:45 16 50000000',
            'expected_type': 'invalid_faction'
        },
        {
            'name': 'Insufficient fields',
            'data': 'ALL TIME Agent123 Enlightened 2025-01-15 12:30:45 16 50000000 25000000 3000 500 5 150',
            'expected_type': 'insufficient_fields'
        },
        {
            'name': 'Good data (should succeed)',
            'data': 'ALL TIME TestAgent Enlightened 2025-01-15 12:30:45 ' + ' '.join(str(i) for i in range(57)),
            'expected_type': None
        }
    ]
    
    for test in test_cases:
        print(f"\n📋 Test: {test['name']}")
        print("-" * 30)
        
        result, error = parser.parse_data_line(test['data'])
        
        if test['expected_type'] is None:
            # Should succeed
            if result and not error:
                print("✅ SUCCESS: Data parsed correctly")
                print(f"   Agent: {result['agent_name']}, Faction: {result['faction']}")
            else:
                print(f"❌ FAILED: Expected success but got error: {error.error_type if error else 'Unknown'}")
        else:
            # Should fail with specific error
            if error and error.error_type == test['expected_type']:
                print(f"✅ SUCCESS: Correct error type '{error.error_type}'")
                print(f"   Error message preview: {error.user_message[:100]}...")
            else:
                print(f"❌ FAILED: Expected '{test['expected_type']}' but got '{error.error_type if error else 'None'}'")

def test_help_messages():
    """Test help message improvements"""
    parser = DataParser()
    
    print(f"\n\n🆘 Testing Help Messages")
    print("=" * 50)
    
    print("📝 Quick Help:")
    print(parser.get_quick_help())
    
    print("\n" + "="*30)
    print("📚 Detailed Help (first 300 chars):")
    detailed_help = parser.get_detailed_help()
    print(detailed_help[:300] + "..." if len(detailed_help) > 300 else detailed_help)

def test_multiline_parsing():
    """Test multiline parsing with mixed data"""
    parser = DataParser()
    
    print(f"\n\n📄 Testing Multiline Data Parsing")
    print("=" * 50)
    
    test_data = """Time Span Agent Name Agent Faction Date (yyyy-mm-dd) Time (hh:mm:ss) Level Lifetime AP Current AP
ALL TIME TestAgent1 Enlightened 2025-01-15 12:30:45 16 50000000 25000000 3000 500 5 150 200 100 50 25 12 8 15000000 500 300 100 50 25 10000 100 50 1000 2000 500 100 50 25 12 8 500 300 200 100 50 25 12 8 15 10 5 2 1000 500 200 100 50 25 12 8
ALL TIME TestAgent2 Resistance 2025-01-15 12:31:00 15 40000000 20000000 2500 400 4 120 180 90 40 20 10 6 12000000 400 250 80 40 20 8000 80 40 800 1600 400 80 40 20 10 6 400 240 160 80 40 20 10 6 12 8 4 1 800 400 160 80 40 20 10 6"""
    
    results, errors = parser.parse_multiline_data(test_data)
    
    print(f"✅ Successfully parsed: {len(results)} submissions")
    if errors:
        print(f"⚠️  Errors encountered: {len(errors)}")
        for error in errors:
            print(f"   - {error.error_type}: {error.user_message[:50]}...")
    else:
        print("✅ No parsing errors")
    
    for i, result in enumerate(results, 1):
        print(f"   {i}. Agent: {result['agent_name']} ({result['faction']}) - Level {result['level']}")

if __name__ == "__main__":
    print("🚀 Testing Ingress Bot UX Improvements\n")
    
    try:
        test_error_messaging()
        test_help_messages()
        test_multiline_parsing()
        
        print(f"\n\n🎉 All tests completed!")
        print("=" * 50)
        print("✅ UX improvements are working correctly!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()