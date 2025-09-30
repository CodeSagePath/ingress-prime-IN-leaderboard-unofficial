#!/usr/bin/env python3
"""
Script to easily switch between prefix detection modes
"""

import os
import sys
from pathlib import Path

def update_env_file(mode):
    """Update the .env file with the new prefix detection mode"""
    env_file = Path(__file__).parent / ".env"
    
    if not env_file.exists():
        print(f"❌ .env file not found at {env_file}")
        return False
    
    # Read current content
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update or add the PREFIX_DETECTION_MODE line
    updated = False
    new_lines = []
    
    for line in lines:
        if line.startswith('PREFIX_DETECTION_MODE='):
            new_lines.append(f'PREFIX_DETECTION_MODE={mode}\n')
            updated = True
        else:
            new_lines.append(line)
    
    # If not found, add it
    if not updated:
        new_lines.append(f'\nPREFIX_DETECTION_MODE={mode}\n')
    
    # Write back to file
    with open(env_file, 'w') as f:
        f.writelines(new_lines)
    
    return True

def main():
    """Main function to handle mode switching"""
    print("🔧 Ingress Bot Prefix Detection Mode Switcher")
    print("=" * 50)
    
    if len(sys.argv) != 2 or sys.argv[1] not in ['strict', 'flexible']:
        print("Usage: python switch_prefix_mode.py <mode>")
        print()
        print("Available modes:")
        print("  strict   - Only process messages with 'Time Span Agent Name' prefix")
        print("  flexible - Process all messages, prefer those with prefix (default)")
        print()
        print("Examples:")
        print("  python switch_prefix_mode.py strict")
        print("  python switch_prefix_mode.py flexible")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    print(f"🎯 Switching to {mode} mode...")
    
    if update_env_file(mode):
        print(f"✅ Successfully updated .env file")
        print(f"📝 PREFIX_DETECTION_MODE={mode}")
        print()
        
        if mode == 'strict':
            print("🔴 STRICT MODE ENABLED")
            print("   • Bot will ONLY process messages containing 'Time Span Agent Name'")
            print("   • All other messages will be ignored")
            print("   • Users will receive guidance about required prefix")
        else:
            print("🟢 FLEXIBLE MODE ENABLED")
            print("   • Bot will process ALL messages")
            print("   • Messages with 'Time Span Agent Name' get priority/enhanced processing")
            print("   • Maintains backward compatibility")
        
        print()
        print("🔄 Restart the bot for changes to take effect")
        print("🧪 Test with: python test_prefix_detection.py")
        
    else:
        print("❌ Failed to update .env file")
        sys.exit(1)

if __name__ == "__main__":
    main()