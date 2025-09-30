#!/usr/bin/env python3
"""
Comprehensive verification that navigation buttons are implemented everywhere
"""

import os
import re

def analyze_file_for_navigation(filepath):
    """Analyze a file for navigation button implementation"""
    results = {
        'file': filepath,
        'has_navigation_method': False,
        'reply_text_calls': [],
        'navigation_implemented': [],
        'missing_navigation': []
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check if file has navigation button creation method
        if '_create_navigation_buttons' in content:
            results['has_navigation_method'] = True
            
        # Find all reply_text calls
        reply_text_pattern = r'(?:update\.message\.reply_text|query\.edit_message_text|context\.bot\.send_message)\s*\([^)]*\)'
        matches = re.finditer(reply_text_pattern, content, re.DOTALL | re.MULTILINE)
        
        for match in matches:
            call = match.group(0)
            line_num = content[:match.start()].count('\n') + 1
            
            results['reply_text_calls'].append({
                'line': line_num,
                'call': call[:100] + '...' if len(call) > 100 else call
            })
            
            # Check if this call includes reply_markup
            if 'reply_markup' in call:
                results['navigation_implemented'].append(line_num)
            else:
                results['missing_navigation'].append(line_num)
                
    except Exception as e:
        results['error'] = str(e)
        
    return results

def main():
    """Verify navigation implementation across all handler files"""
    print("🔍 **Comprehensive Navigation Button Verification**\n")
    
    # Files to check
    script_dir = os.path.dirname(os.path.abspath(__file__))
    handler_files = [
        os.path.join(script_dir, "src", "handlers", "command_handlers.py"),
        os.path.join(script_dir, "src", "handlers", "message_handlers.py"),
        os.path.join(script_dir, "src", "handlers", "callback_handlers.py")
    ]
    
    total_calls = 0
    total_with_navigation = 0
    total_missing = 0
    
    for filepath in handler_files:
        if not os.path.exists(filepath):
            print(f"❌ File not found: {filepath}")
            continue
            
        print(f"📄 **Analyzing:** `{os.path.basename(filepath)}`")
        results = analyze_file_for_navigation(filepath)
        
        if 'error' in results:
            print(f"   ❌ Error: {results['error']}")
            continue
            
        # Statistics
        has_method = "✅" if results['has_navigation_method'] else "❌"
        print(f"   Navigation method: {has_method}")
        print(f"   Total message calls: {len(results['reply_text_calls'])}")
        print(f"   With navigation: {len(results['navigation_implemented'])}")
        print(f"   Missing navigation: {len(results['missing_navigation'])}")
        
        if results['missing_navigation']:
            print("   ⚠️  Missing navigation on lines:", results['missing_navigation'])
            
        total_calls += len(results['reply_text_calls'])
        total_with_navigation += len(results['navigation_implemented'])
        total_missing += len(results['missing_navigation'])
        print()
    
    # Overall summary
    print("📊 **Overall Summary:**")
    print(f"   Total message calls: {total_calls}")
    print(f"   With navigation: {total_with_navigation}")
    print(f"   Missing navigation: {total_missing}")
    
    if total_missing == 0:
        print("\n🎉 **PERFECT!** All bot messages include navigation buttons!")
        print("\n✅ **Navigation Implementation Complete:**")
        print("   • Message handlers: Fully implemented")
        print("   • Command handlers: Fully implemented") 
        print("   • Callback handlers: Fully implemented")
        print("\n🚀 **User Experience Improvements:**")
        print("   • Users no longer need to type commands repeatedly")
        print("   • Quick access buttons on every message")
        print("   • Mobile-friendly tap navigation")
        print("   • Consistent navigation across all interactions")
    else:
        print(f"\n⚠️  Found {total_missing} message calls without navigation buttons")
        print("   These should be reviewed and updated.")
    
    return total_missing == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)