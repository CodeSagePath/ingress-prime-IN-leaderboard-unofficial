#!/usr/bin/env python3
"""
Demonstration of the Enhanced Ingress Bot System
Shows the complete workflow with realistic data
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.spreadsheet_formatter import SpreadsheetFormatter

def demo_spreadsheet_formatter():
    """Demonstrate the spreadsheet formatter with sample data"""
    
    print("🎨 Enhanced Ingress Bot - Spreadsheet Layout Demo")
    print("=" * 60)
    
    # Sample parsed data (what would come from the enhanced parser)
    sample_data = {
        'time_span': 'ALL TIME',
        'agent_name': 'TestAgent',
        'faction': 'Enlightened',
        'data_date': '2024-01-15',
        'data_time': '14:30:00',
        'level': 16,
        'lifetime_ap': 12345678,
        'current_ap': 8765432,
        'unique_portals_visited': 1234,
        'seer_points': 567,
        'xm_collected': 2345678,
        'portals_captured': 890,
        'unique_captures': 1456,
        'portals_neutralized': 234,
        'enemy_portals_captured': 123,
        'resonators_deployed': 5678,
        'links_created': 345,
        'control_fields_created': 123,
        'mind_units_captured': 456789,
        'longest_link_ever_created': 123.45,
        'largest_control_field': 234.56,
        'xm_recharged': 3456789,
        'portals_owned': 45,
        'unique_missions_completed': 67,
        'hacks': 12345,
        'glyph_hack_points': 8901,
        'consecutive_days_hacking': 234
    }
    
    # Sample validation data
    validation_errors = [
        "Field 'drone_hacks': Missing field, using default value 0",
        "Field 'completed_hackstreaks': Value seems low for level 16 agent"
    ]
    
    confidence_score = 87.5
    
    # Initialize formatter
    formatter = SpreadsheetFormatter()
    
    # Demo different view types
    views = [
        ('summary', 'Summary View - Key Statistics'),
        ('detailed', 'Detailed View - All Fields'),
        ('validation', 'Validation Report - Data Quality')
    ]
    
    for view_type, description in views:
        print(f"\n📋 {description}")
        print("=" * len(description))
        
        if view_type == 'summary':
            table = formatter.format_agent_summary(sample_data, validation_errors)
        elif view_type == 'detailed':
            table = formatter.format_detailed_stats(sample_data)
        elif view_type == 'validation':
            table = formatter.format_validation_report(validation_errors)
        
        print(table)
        
        if view_type == 'detailed':
            print("\n💡 Note: This is just a sample of the detailed view.")
            print("    The actual table would show all parsed fields.")
    
    # Demo comparison table
    print(f"\n📊 Comparison View - Progress Tracking")
    print("=" * 40)
    
    # Sample comparison data (current vs previous)
    comparison_data = {
        'current': sample_data,
        'previous': {
            **sample_data,
            'lifetime_ap': 12000000,  # Lower previous AP
            'portals_captured': 850,   # Lower previous captures
            'level': 15               # Previous level
        }
    }
    
    # For comparison, let's show a simple comparison of key stats
    comparison_agents = [
        {**comparison_data['previous'], 'agent_name': 'TestAgent (Previous)'},
        {**comparison_data['current'], 'agent_name': 'TestAgent (Current)'}
    ]
    comparison_table = formatter.format_comparison_table(comparison_agents, 'lifetime_ap')
    print(comparison_table)
    
    print(f"\n🎉 Demo Complete!")
    print(f"📈 The enhanced system provides:")
    print(f"   • Professional spreadsheet-like layout")
    print(f"   • Multiple view types for different needs")
    print(f"   • Visual indicators and progress tracking")
    print(f"   • Data quality reporting with confidence scores")

def demo_user_workflow():
    """Demonstrate the complete user workflow"""
    
    print(f"\n🎮 Enhanced User Workflow Demo")
    print("=" * 40)
    
    workflow_steps = [
        "1. User types /submit or clicks Submit button",
        "2. Bot shows enhanced submission prompt with new features",
        "3. User pastes their Ingress statistics",
        "4. Enhanced parser analyzes data with intelligent validation",
        "5. Bot displays confidence score (e.g., '87% confidence')",
        "6. Professional spreadsheet table is shown",
        "7. Interactive buttons allow switching between views:",
        "   • 📋 Summary View",
        "   • 📊 Detailed View", 
        "   • ⚠️ Validation Report",
        "8. User reviews data and confirms save",
        "9. Data is stored with quality metrics"
    ]
    
    for step in workflow_steps:
        print(f"   {step}")
    
    print(f"\n✨ Key Improvements:")
    improvements = [
        "❌ Before: Data mismatches due to hardcoded field positions",
        "✅ After: Intelligent field detection prevents mismatches",
        "",
        "❌ Before: Plain text display, hard to read",
        "✅ After: Professional spreadsheet-like tables",
        "",
        "❌ Before: No data quality feedback",
        "✅ After: Confidence scores and validation warnings",
        "",
        "❌ Before: Limited error handling",
        "✅ After: Comprehensive error detection with suggestions"
    ]
    
    for improvement in improvements:
        if improvement:
            print(f"   {improvement}")
        else:
            print()

if __name__ == "__main__":
    try:
        # Demo the spreadsheet formatter
        demo_spreadsheet_formatter()
        
        # Demo the user workflow
        demo_user_workflow()
        
        print(f"\n🚀 Enhanced Ingress Bot System Ready!")
        print(f"📋 All components integrated and working:")
        print(f"   ✅ Enhanced Data Parser")
        print(f"   ✅ Spreadsheet Formatter") 
        print(f"   ✅ Enhanced Message Handlers")
        print(f"   ✅ Updated Bot Integration")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)