"""
Test script for the Ingress Leaderboard Bot
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    """Test if all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from config.config import BOT_TOKEN, DATABASE_PATH, FACTION_COLORS
        print("✅ Config imported successfully")
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        assert False
    
    try:
        from src.database.manager import DatabaseManager
        print("✅ Database module imported successfully")
    except ImportError as e:
        print(f"❌ Database import failed: {e}")
        assert False
    
    try:
        from src.parsers.data_parser import DataParser
        print("✅ Data parser imported successfully")
    except ImportError as e:
        print(f"❌ Data parser import failed: {e}")
        assert False
    
    try:
        from src.services.leaderboard import LeaderboardManager
        print("✅ Leaderboard manager imported successfully")
    except ImportError as e:
        print(f"❌ Leaderboard manager import failed: {e}")
        assert False
    
    assert True

def test_database():
    """Test database functionality"""
    print("\n🗄️ Testing database...")
    
    try:
        from src.database.manager import DatabaseManager
        db = DatabaseManager()
        print("✅ Database initialized successfully")
        
        # Test adding an agent
        agent_id = db.add_agent("TestAgent", "Enlightened", 12345)
        print(f"✅ Test agent added with ID: {agent_id}")
        
        assert True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        assert False

def test_data_parser():
    """Test data parsing functionality"""
    print("\n📊 Testing data parser...")
    
    try:
        from src.parsers.data_parser import DataParser
        parser = DataParser()
        
        # Test with sample data
        sample_data = "ALL TIME TestAgent Enlightened 2025-01-15 12:30:45 16 50000000 25000000 3000 500 5 150 200000000 5000 1200 800 50000 10000 8000 5000000 200 500000 150000000 8000 2500 7000 20000 1200 40000 15 180 20000 4000 3500 1800 20 5 200 1000 120 70 220 135 2500 90 1500000 35 2500 240 300 100 20 3 1 18 6 3000 150 3500 0 1 0"
        
        result = parser.parse_data_line(sample_data)
        if isinstance(result, tuple):
            parsed, error = result
        else:
            parsed = result
            error = None
            
        if parsed:
            print("✅ Sample data parsed successfully")
            print(f"   Agent: {parsed['agent_name']}")
            print(f"   Faction: {parsed['faction']}")
            print(f"   Level: {parsed['level']}")
            print(f"   Current AP: {parser.format_number(parsed['current_ap'])}")
        else:
            print("❌ Failed to parse sample data")
            if error:
                print(f"   Error: {error.user_message}")
            assert False
        
        assert True
    except Exception as e:
        print(f"❌ Data parser test failed: {e}")
        assert False

def test_leaderboard():
    """Test leaderboard functionality"""
    print("\n🏆 Testing leaderboard...")
    
    try:
        from src.services.leaderboard import LeaderboardManager
        leaderboard = LeaderboardManager()
        
        # Test help text generation
        help_text = leaderboard.generate_help_text()
        if help_text and len(help_text) > 100:
            print("✅ Help text generated successfully")
        else:
            print("❌ Help text generation failed")
            assert False
        
        # Test available stats
        stats = leaderboard.get_available_stats()
        if stats and len(stats) > 0:
            print(f"✅ Available stats: {len(stats)} statistics")
        else:
            print("❌ No available stats found")
            assert False
        
        assert True
    except Exception as e:
        print(f"❌ Leaderboard test failed: {e}")
        assert False

def test_bot_token():
    """Test bot token configuration"""
    print("\n🤖 Testing bot configuration...")
    
    try:
        from config.config import BOT_TOKEN
        if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            print("⚠️  Bot token not configured - this is expected for initial setup")
            print("   Please update BOT_TOKEN in config.py with your actual token")
            assert True
        elif BOT_TOKEN and len(BOT_TOKEN) > 20:
            print("✅ Bot token appears to be configured")
            assert True
        else:
            print("❌ Bot token appears to be invalid")
            assert False
    except Exception as e:
        print(f"❌ Bot token test failed: {e}")
        assert False

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Ingress Leaderboard Bot Tests\n")
    
    tests = [
        ("Imports", test_imports),
        ("Database", test_database),
        ("Data Parser", test_data_parser),
        ("Leaderboard", test_leaderboard),
        ("Bot Token", test_bot_token)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The bot is ready to use.")
        print("\n🚀 Next steps:")
        print("1. Update your bot token in config.py")
        print("2. Run: python bot.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()