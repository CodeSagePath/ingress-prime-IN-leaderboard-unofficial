#!/usr/bin/env python3
"""
Verify navigation buttons are properly implemented in all handlers
"""

import sys
import os
import re

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_file_for_navigation_buttons(filepath):
    """Check if a handler file properly implements navigation buttons"""
    results = {
        'has_navigation_method': False,
        'reply_text_calls': [],
        'navigation_button_calls': 0,
        'missing_navigation': []
    }
    
    with open(filepath, 'r') as f:
        content = f.read()
        
        # Check if it has navigation button method
        if '_create_navigation_buttons' in content:
            results['has_navigation_method'] = True
        
        # Find all reply_text calls
        reply_text_pattern = r'await.*\.reply_text\((.*?)\)'
        matches = re.finditer(reply_text_pattern, content, re.DOTALL)
        
        for match in matches:
            call_content = match.group(1)
            results['reply_text_calls'].append(call_content[:100] + "..." if len(call_content) > 100 else call_content)
            
            # Check if this call includes reply_markup
            if 'reply_markup' in call_content:
                results['navigation_button_calls'] += 1
            else:
                # Skip very brief status messages that don't need navigation
                if not any(brief in call_content for brief in ['[result removed]', '_This message will self-delete']):
                    results['missing_navigation'].append(call_content[:50] + "...")
    
    return results

def main():
    print("🔍 **Verifying Navigation Button Implementation**\n")
    
    handler_files = [
        'src/handlers/command_handlers.py',
        'src/handlers/callback_handlers.py', 
        'src/handlers/message_handlers.py'
    ]
    
    total_calls = 0
    total_with_navigation = 0
    
    for filepath in handler_files:
        full_path = os.path.join(os.path.dirname(__file__), filepath)
        if os.path.exists(full_path):
            print(f"📁 **{filepath}**")
            results = check_file_for_navigation_buttons(full_path)
            
            print(f"   ✅ Has navigation method: {results['has_navigation_method']}")
            print(f"   📊 Total reply_text calls: {len(results['reply_text_calls'])}")
            print(f"   🎯 Calls with navigation: {results['navigation_button_calls']}")
            
            total_calls += len(results['reply_text_calls'])
            total_with_navigation += results['navigation_button_calls']
            
            if results['missing_navigation']:
                print(f"   ⚠️  Missing navigation: {len(results['missing_navigation'])}")
                for missing in results['missing_navigation'][:3]:  # Show first 3
                    print(f"      - {missing}")
                if len(results['missing_navigation']) > 3:
                    print(f"      - ...and {len(results['missing_navigation']) - 3} more")
            else:
                print("   ✅ All important messages have navigation buttons")
            
            print()
        else:
            print(f"❌ File not found: {filepath}\n")
    
    print("📊 **Summary:**")
    print(f"   Total reply_text calls: {total_calls}")
    print(f"   Calls with navigation: {total_with_navigation}")
    
    coverage = (total_with_navigation / total_calls * 100) if total_calls > 0 else 0
    print(f"   Navigation coverage: {coverage:.1f}%")
    
    if coverage > 85:
        print("\n🎉 **Excellent!** Navigation buttons are well implemented!")
        print("\n📱 **Benefits for users:**")
        print("   • No need to type commands repeatedly")
        print("   • Quick access to all bot features")
        print("   • Better mobile user experience")
        print("   • Seamless navigation between functions")
    elif coverage > 70:
        print("\n✅ **Good!** Most messages have navigation buttons.")
    else:
        print("\n⚠️ **Needs improvement!** Many messages missing navigation.")

if __name__ == "__main__":
    main()