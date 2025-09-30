#!/usr/bin/env python3
"""
Test script to verify bot configuration is working correctly
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config():
    """Test the configuration loading"""
    print("🧪 Testing configuration loading...\n")
    
    try:
        from config.settings import BOT_TOKEN, PREFIX_DETECTION_MODE
        
        print("✅ Configuration imported successfully")
        
        # Test BOT_TOKEN
        if BOT_TOKEN:
            if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
                print("❌ BOT_TOKEN is not configured (still has placeholder value)")
                return False
            else:
                print(f"✅ BOT_TOKEN loaded: {BOT_TOKEN[:10]}...{BOT_TOKEN[-5:]}")
        else:
            print("❌ BOT_TOKEN is None or empty")
            return False
        
        # Test other configuration
        print(f"✅ PREFIX_DETECTION_MODE: {PREFIX_DETECTION_MODE}")
        
        print("\n🎯 Testing bot service import...")
        from src.services.bot_service import IngressLeaderboardBot
        print("✅ Bot service imported successfully")
        
        print("\n🚀 Testing bot initialization...")
        bot = IngressLeaderboardBot()
        print("✅ Bot initialized successfully")
        
        print("\n✅ All configuration tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_env_file():
    """Test .env file directly"""
    print("📄 Testing .env file loading...\n")
    
    env_file = Path(__file__).parent / ".env"
    
    if not env_file.exists():
        print(f"❌ .env file not found at: {env_file}")
        return False
    
    print(f"✅ .env file found at: {env_file}")
    
    try:
        with open(env_file, 'r') as f:
            content = f.read()
        
        if "BOT_TOKEN=" in content:
            lines = content.split('\n')
            for line in lines:
                if line.startswith('BOT_TOKEN='):
                    token_value = line.split('=', 1)[1].strip()
                    if token_value and token_value != "YOUR_BOT_TOKEN_HERE":
                        print(f"✅ BOT_TOKEN found in .env file: {token_value[:10]}...{token_value[-5:]}")
                        return True
                    else:
                        print("❌ BOT_TOKEN in .env file is empty or placeholder")
                        return False
        
        print("❌ BOT_TOKEN not found in .env file")
        return False
        
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 Ingress Leaderboard Bot - Configuration Test")
    print("=" * 60)
    
    # Test .env file first
    env_test = test_env_file()
    
    print("\n" + "-" * 60)
    
    # Test configuration loading
    config_test = test_config()
    
    print("\n" + "=" * 60)
    
    if env_test and config_test:
        print("🎉 All tests passed! Bot should work correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the issues above.")
        
        print("\n🔧 Troubleshooting tips:")
        if not env_test:
            print("1. Make sure .env file exists in the project root")
            print("2. Ensure .env file contains: BOT_TOKEN=your_actual_token")
            print("3. Check file permissions: chmod 644 .env")
        
        if not config_test:
            print("4. Try running: python -c 'from config.settings import BOT_TOKEN; print(BOT_TOKEN)'")
            print("5. Make sure you're in the correct directory")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)