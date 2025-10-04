#!/usr/bin/env python3
"""
Test with realistic Ingress data format
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from parsers.enhanced_data_parser import EnhancedDataParser
from utils.spreadsheet_formatter import SpreadsheetFormatter

def test_with_realistic_data():
    """Test with realistic Ingress data format"""
    
    # Realistic Ingress data format (single line as expected by the parser)
    realistic_data = "ALL TIME TestAgent Enlightened 2024-01-15 14:30:00 16 12345678 8765432 1234 567 2345678 890 1456 234 123 5678 345 123 456789 123.45 234.56 3456789 45 67 12345 8901 234"
    
    print("🧪 Testing with Realistic Ingress Data")
    print("=" * 50)
    print(f"Data: {realistic_data[:100]}...")
    
    # Initialize parser
    parser = EnhancedDataParser()
    
    # Parse the data
    result = parser.parse_data_line(realistic_data)
    
    print(f"\n✅ Parse Success: {result.success}")
    print(f"📊 Confidence Score: {result.confidence_score:.1f}%")
    
    if result.data:
        print(f"🔍 Fields Detected: {len(result.data)}")
        print("\n📋 Parsed Fields:")
        for key, value in list(result.data.items())[:10]:  # Show first 10 fields
            print(f"  • {key}: {value}")
        if len(result.data) > 10:
            print(f"  ... and {len(result.data) - 10} more fields")
    
    if result.errors:
        print(f"\n⚠️  Validation Issues: {len(result.errors)}")
        for error in result.errors[:5]:  # Show first 5
            print(f"   • {error}")
    
    if result.warnings:
        print(f"\n💡 Warnings: {len(result.warnings)}")
        for warning in result.warnings[:5]:  # Show first 5
            print(f"   • {warning}")
    
    # Test spreadsheet formatter if parsing was successful
    if result.success and result.data:
        print("\n🎨 Testing Spreadsheet Formatter")
        print("=" * 50)
        
        formatter = SpreadsheetFormatter()
        
        # Test summary view
        print("\n📋 Summary View:")
        print("-" * 30)
        
        table = formatter.format_stats_table(
            result.data, 
            view_type='summary',
            confidence_score=result.confidence_score,
            validation_errors=result.errors or []
        )
        
        print(table)
        
        # Test detailed view (first 20 lines)
        print("\n📋 Detailed View (first 20 lines):")
        print("-" * 40)
        
        detailed_table = formatter.format_stats_table(
            result.data, 
            view_type='detailed',
            confidence_score=result.confidence_score,
            validation_errors=result.errors or []
        )
        
        lines = detailed_table.split('\n')
        for line in lines[:20]:
            print(line)
        if len(lines) > 20:
            print(f"... ({len(lines) - 20} more lines)")
    
    return result

if __name__ == "__main__":
    print("🚀 Realistic Ingress Data Test")
    print("=" * 60)
    
    try:
        result = test_with_realistic_data()
        
        if result.success:
            print(f"\n🎉 Test completed successfully!")
            print(f"📈 Data parsed with {result.confidence_score:.1f}% confidence!")
        else:
            print(f"\n⚠️  Test completed with issues")
            print(f"📊 Confidence: {result.confidence_score:.1f}%")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)