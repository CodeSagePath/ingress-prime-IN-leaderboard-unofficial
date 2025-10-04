#!/usr/bin/env python3
"""
Test the parser fix for mixed header/data lines
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.parsers.data_parser import DataParser
from src.parsers.enhanced_data_parser import EnhancedDataParser

def test_mixed_header_data():
    """Test parsing mixed header/data line like the user provided"""
    
    # The user's data (mixed header and data on same line)
    test_data = """Time Span Agent Name Agent Faction Date (yyyy-mm-dd) Time (hh:mm:ss) Level Lifetime AP Current AP Unique Portals Visited Unique Portals Drone Visited Furthest Drone Distance Portals Discovered XM Collected OPR Agreements Portal Scans Uploaded Uniques Scout Controlled Resonators Deployed Links Created Control Fields Created Mind Units Captured Longest Link Ever Created Largest Control Field XM Recharged Portals Captured Unique Portals Captured Mods Deployed Hacks Drone Hacks Glyph Hack Points Completed Hackstreaks Longest Sojourner Streak Resonators Destroyed Portals Neutralized Enemy Links Destroyed Enemy Fields Destroyed Drones Returned Machina Links Destroyed Machina Resonators Destroyed Machina Portals Neutralized Machina Portals Reclaimed Max Time Portal Held Max Time Link Maintained Max Link Length x Days Max Time Field Held Largest Field MUs x Days Forced Drone Recalls Distance Walked Kinetic Capsules Completed Unique Missions Completed Research Bounties Completed Research Days Completed NL-1331 Meetup(s) Attended First Saturday Events Second Sunday Events +Delta Tokens +Beta Tokens Agents Recruited ALL TIME rmv96hg Enlightened 2025-10-04 06:57:58 13 12588332 12588332 2033 196 5 35 71226529 1068 77 24 14865 2815 1911 31000068 124 2836821 55393800 2893 1292 2034 10151 844 11468 33 104 3428 604 599 276 7 81 541 63 74 206 148 10475 68 22874940 40 3049 174 11 809 106 1 23 2 8040 150 1"""
    
    print("Testing DataParser...")
    parser = DataParser()
    
    try:
        data, error = parser.parse_data_line(test_data)
        
        if error:
            print(f"❌ DataParser failed: {error.user_message}")
            return False
        
        if not data:
            print("❌ DataParser returned no data")
            return False
            
        # Check key fields
        print(f"✅ DataParser successful!")
        print(f"   Agent: {data.get('agent_name')}")
        print(f"   Faction: {data.get('faction')}")
        print(f"   Level: {data.get('level')}")
        print(f"   Lifetime AP: {data.get('lifetime_ap'):,}")
        print(f"   Portals Visited: {data.get('unique_portals_visited'):,}")
        
    except Exception as e:
        print(f"❌ DataParser crashed: {e}")
        return False
    
    print("\nTesting EnhancedDataParser...")
    enhanced_parser = EnhancedDataParser()
    
    try:
        result = enhanced_parser.parse_data_line(test_data)
        
        if not result.success:
            print(f"❌ EnhancedDataParser failed: {result.errors}")
            return False
        
        if not result.data:
            print("❌ EnhancedDataParser returned no data")
            return False
            
        # Check key fields
        data = result.data
        print(f"✅ EnhancedDataParser successful!")
        print(f"   Agent: {data.get('agent_name')}")
        print(f"   Faction: {data.get('faction')}")
        print(f"   Level: {data.get('level')}")
        print(f"   Lifetime AP: {data.get('lifetime_ap'):,}")
        print(f"   Portals Visited: {data.get('unique_portals_visited'):,}")
        print(f"   Confidence: {result.confidence_score:.2f}")
        
        if result.warnings:
            print(f"   Warnings: {result.warnings}")
        
    except Exception as e:
        print(f"❌ EnhancedDataParser crashed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🧪 Testing parser fix for mixed header/data lines...\n")
    
    success = test_mixed_header_data()
    
    if success:
        print("\n🎉 Parser fix successful! The bot should now handle your data correctly.")
        print("\n💡 The issue was that your data contained both headers and data on the same line.")
        print("   The parser now detects this case and extracts the actual data part.")
    else:
        print("\n❌ Parser fix failed. There might be additional issues to resolve.")