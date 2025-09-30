#!/usr/bin/env python3
"""
Termux environment fix utility
This script ensures the .env file is loaded correctly in Termux
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def ensure_env_loaded():
    """Ensure .env file is loaded correctly, especially in Termux"""
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.resolve()
    
    # Possible .env file locations (in order of preference)
    env_locations = [
        script_dir / ".env",  # Same directory as script
        Path.cwd() / ".env",  # Current working directory
        Path(os.path.expanduser("~")) / "ingress-bot" / ".env",  # Home directory
        Path("/data/data/com.termux/files/home/ingress-bot/.env") if os.path.exists("/data/data/com.termux") else None,  # Termux home
    ]
    
    # Filter out None values
    env_locations = [loc for loc in env_locations if loc is not None]
    
    print(f"Looking for .env file in {len(env_locations)} locations...")
    
    for env_path in env_locations:
        try:
            abs_path = env_path.resolve()
            print(f"Checking: {abs_path}")
            
            if abs_path.exists():
                print(f"✅ Found .env file at: {abs_path}")
                
                # Try to load it
                result = load_dotenv(abs_path, override=True)
                if result:
                    bot_token = os.getenv("BOT_TOKEN")
                    if bot_token and bot_token.strip() and bot_token != "YOUR_BOT_TOKEN_HERE":
                        print(f"✅ Successfully loaded BOT_TOKEN: {bot_token[:10]}...{bot_token[-5:]}")
                        return True
                    else:
                        print(f"⚠️ BOT_TOKEN found but appears invalid")
                else:
                    print(f"⚠️ Failed to load .env file")
            else:
                print(f"❌ File not found")
        except Exception as e:
            print(f"❌ Error checking {env_path}: {e}")
    
    print("❌ Could not find or load .env file")
    return False

def create_env_if_missing():
    """Create a template .env file if it doesn't exist"""
    script_dir = Path(__file__).parent.resolve()
    env_file = script_dir / ".env"
    
    if not env_file.exists():
        template_content = """BOT_TOKEN=YOUR_BOT_TOKEN_HERE

# Prefix Detection Mode Configuration
# Set to "strict" to ONLY process messages with "Time Span Agent Name" prefix
# Set to "flexible" to process all messages but give priority to those with prefix
PREFIX_DETECTION_MODE=strict
"""
        
        try:
            with open(env_file, 'w') as f:
                f.write(template_content)
            print(f"✅ Created template .env file at: {env_file}")
            print("⚠️  Please edit the .env file and set your BOT_TOKEN")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    
    return True

def main():
    """Main function"""
    print("=== Termux Environment Fix Utility ===")
    
    # Check if we're in Termux
    is_termux = os.environ.get('PREFIX', '').endswith('com.termux')
    print(f"Termux detected: {is_termux}")
    
    # Try to load existing .env file
    if not ensure_env_loaded():
        print("\n=== Creating template .env file ===")
        create_env_if_missing()
        
        # Try loading again
        if not ensure_env_loaded():
            print("\n❌ Still unable to load .env file. Please check manually.")
            return False
    
    print("\n✅ Environment setup complete!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)