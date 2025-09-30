#!/usr/bin/env python3
"""
Debug script to test .env file loading in Termux
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def debug_env_loading():
    """Debug the .env file loading process"""
    
    print("=== Environment Debug Information ===")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script directory: {Path(__file__).parent}")
    print(f"PROJECT_ROOT calculation: {Path(__file__).parent}")
    
    # Check if we're in Termux
    is_termux = os.environ.get('PREFIX', '').endswith('com.termux')
    print(f"Is Termux: {is_termux}")
    if is_termux:
        print(f"Termux PREFIX: {os.environ.get('PREFIX', 'Not set')}")
    
    # Try different .env file locations
    possible_env_paths = [
        Path(__file__).parent / ".env",
        Path(os.getcwd()) / ".env", 
        Path("./../../.env"),
        Path(".env")
    ]
    
    print("\n=== Checking .env file locations ===")
    for env_path in possible_env_paths:
        abs_path = env_path.resolve()
        exists = abs_path.exists()
        print(f"Path: {abs_path}")
        print(f"Exists: {exists}")
        if exists:
            print(f"Size: {abs_path.stat().st_size} bytes")
            # Try to read the file
            try:
                with open(abs_path, 'r') as f:
                    content = f.read()
                    print(f"Content preview: {content[:100]}...")
            except Exception as e:
                print(f"Error reading: {e}")
        print("-" * 40)
    
    # Test loading .env with different methods
    print("\n=== Testing .env loading methods ===")
    
    # Method 1: Current method from settings.py
    project_root = Path(__file__).parent
    env_file_1 = project_root / ".env"
    print(f"Method 1 - File path: {env_file_1.resolve()}")
    print(f"File exists: {env_file_1.exists()}")
    
    if env_file_1.exists():
        result_1 = load_dotenv(env_file_1)
        print(f"load_dotenv result: {result_1}")
        token_1 = os.getenv("BOT_TOKEN")
        print(f"BOT_TOKEN from method 1: {'Found' if token_1 else 'Not found'}")
        if token_1:
            print(f"Token preview: {token_1[:10]}...{token_1[-5:]}")
    
    # Method 2: Using absolute path
    abs_env_path = os.path.abspath(".env")
    print(f"\nMethod 2 - Absolute path: {abs_env_path}")
    print(f"File exists: {os.path.exists(abs_env_path)}")
    
    if os.path.exists(abs_env_path):
        # Clear environment first
        if 'BOT_TOKEN' in os.environ:
            del os.environ['BOT_TOKEN']
        result_2 = load_dotenv(abs_env_path)
        print(f"load_dotenv result: {result_2}")
        token_2 = os.getenv("BOT_TOKEN") 
        print(f"BOT_TOKEN from method 2: {'Found' if token_2 else 'Not found'}")
        if token_2:
            print(f"Token preview: {token_2[:10]}...{token_2[-5:]}")
    
    # Method 3: Load from current directory without specifying path
    print(f"\nMethod 3 - Auto-detect .env")
    # Clear environment first
    if 'BOT_TOKEN' in os.environ:
        del os.environ['BOT_TOKEN']
    result_3 = load_dotenv()  # Should auto-detect .env in current dir
    print(f"load_dotenv result: {result_3}")
    token_3 = os.getenv("BOT_TOKEN")
    print(f"BOT_TOKEN from method 3: {'Found' if token_3 else 'Not found'}")
    if token_3:
        print(f"Token preview: {token_3[:10]}...{token_3[-5:]}")

    print("\n=== Final Environment Check ===")
    current_token = os.getenv("BOT_TOKEN")
    if current_token:
        print(f"✅ BOT_TOKEN is available: {current_token[:10]}...{current_token[-5:]}")
    else:
        print("❌ BOT_TOKEN is not available")
    
    print("\n=== All environment variables containing 'BOT' ===")
    for key, value in os.environ.items():
        if 'BOT' in key.upper():
            print(f"{key}: {value}")

if __name__ == "__main__":
    debug_env_loading()