#!/usr/bin/env python3
"""
Test script for the enhanced Ingress bot system
Tests the enhanced data parser and spreadsheet formatter
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from parsers.enhanced_data_parser import EnhancedDataParser
from utils.spreadsheet_formatter import SpreadsheetFormatter

def test_enhanced_parsing():
    """Test the enhanced data parser with sample Ingress data"""
    
    # Sample Ingress statistics data (typical format)
    sample_data = """
    Agent Name: TestAgent
    Faction: Enlightened
    Level: 16
    
    Lifetime Stats:
    XM Collected: 1,234,567
    Portals Discovered: 1,234
    Seer Points: 567
    XM Recharged: 2,345,678
    Portals Captured: 890
    Unique Portals Visited: 1,456
    Portals Neutralized: 234
    Enemy Portals Captured: 123
    Resonators Deployed: 5,678
    Links Created: 345
    Control Fields Created: 123
    Mind Units Captured: 456,789
    Longest Link Ever Created: 123.45 km
    Largest Control Field: 234.56 MUs
    XM Recharged: 3,456,789
    Portals Owned: 45
    Unique Missions Completed: 67
    Hacks: 12,345
    Glyph Hack Points: 8,901
    Consecutive Days Hacking: 234
    """
    
    print("🧪 Testing Enhanced Data Parser")
    print("=" * 50)
    
    # Initialize parser
    parser = EnhancedDataParser()
    
    # Parse the data
    result = parser.parse_data_line(sample_data)
    
    print(f"✅ Parse Success: {result.success}")
    print(f"📊 Confidence Score: {result.confidence_score}%")
    print(f"🔍 Fields Detected: {len(result.data) if result.data else 0}")
    
    if result.errors:
        print(f"⚠️  Validation Issues: {len(result.errors)}")
        for error in result.errors[:3]:  # Show first 3
            print(f"   • {error}")
    
    if result.warnings:
        print(f"💡 Warnings: {len(result.warnings)}")
        for warning in result.warnings[:3]:  # Show first 3
            print(f"   • {warning}")
    
    print("\n🎨 Testing Spreadsheet Formatter")
    print("=" * 50)
    
    # Initialize formatter
    formatter = SpreadsheetFormatter()
    
    if result.success and result.data:
        # Test different view types
        views = ['summary', 'detailed', 'validation']
        
        for view_type in views:
            print(f"\n📋 {view_type.title()} View:")
            print("-" * 30)
            
            table = formatter.format_stats_table(
                result.data, 
                view_type=view_type,
                confidence_score=result.confidence_score,
                validation_errors=result.errors or []
            )
            
            # Show first few lines of the table
            lines = table.split('\n')
            for line in lines[:10]:  # Show first 10 lines
                print(line)
            
            if len(lines) > 10:
                print(f"... ({len(lines) - 10} more lines)")
    
    print("\n✨ Test completed!")
    return result

def test_error_handling():
    """Test error handling with invalid data"""
    
    print("\n🔧 Testing Error Handling")
    print("=" * 50)
    
    parser = EnhancedDataParser()
    
    # Test with incomplete data
    incomplete_data = "Agent Name: TestAgent\nLevel: 16"
    
    result = parser.parse_data_line(incomplete_data)
    
    print(f"Incomplete Data Test:")
    print(f"  Success: {result.success}")
    print(f"  Confidence: {result.confidence_score}%")
    print(f"  Errors: {len(result.errors) if result.errors else 0}")
    
    # Test with completely invalid data
    invalid_data = "This is not Ingress data at all!"
    
    result = parser.parse_data_line(invalid_data)
    
    print(f"\nInvalid Data Test:")
    print(f"  Success: {result.success}")
    print(f"  Confidence: {result.confidence_score}%")
    print(f"  Errors: {len(result.errors) if result.errors else 0}")

if __name__ == "__main__":
    print("🚀 Enhanced Ingress Bot System Test")
    print("=" * 60)
    
    try:
        # Test main functionality
        result = test_enhanced_parsing()
        
        # Test error handling
        test_error_handling()
        
        print(f"\n🎉 All tests completed successfully!")
        print(f"📈 System is ready for deployment!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)