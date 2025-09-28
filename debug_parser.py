#!/usr/bin/env python3
"""
Debug script to test data parsing
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_data_parsing():
    """Test the data parsing with the actual user data"""
    
    # The actual data from the user
    user_data = "ALL TIME AgentD1nesh Resistance 2025-09-21 20:58:35 14 103740604 22233357 3426 406 3 176 172552376 3148 12423 956 51182 12309 12722 167096645 1926 37881720 122773281 8184 2773 11640 32283 1440 72431 13294 154 398 43727 5772 6678 2723 85 51 4387 33192 3891 2694 889 354 242201 243 1602786688 65 6589 965 138 1067 166 20 14 3 9020 22 196575 2 4"
    
    print("🧪 Testing data parsing with user data...")
    print(f"Data length: {len(user_data.split())} fields")
    print(f"Data: {user_data[:100]}...")
    
    try:
        from src.parsers.data_parser import DataParser
        parser = DataParser()
        
        parsed = parser.parse_data_line(user_data)
        
        if parsed:
            print("✅ Data parsed successfully!")
            print(f"Agent: {parsed['agent_name']}")
            print(f"Faction: {parsed['faction']}")
            print(f"Level: {parsed['level']}")
            print(f"Current AP: {parsed['current_ap']}")
            print(f"Data Date: {parsed['data_date']}")
            return True
        else:
            print("❌ Failed to parse data")
            return False
            
    except Exception as e:
        print(f"❌ Error during parsing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_submission():
    """Test database submission"""
    print("\n🗄️ Testing database submission...")
    
    try:
        from src.database.manager import DatabaseManager
        from src.parsers.data_parser import DataParser
        
        db = DatabaseManager()
        parser = DataParser()
        
        # Parse the user data
        user_data = "ALL TIME AgentD1nesh Resistance 2025-09-21 20:58:35 14 103740604 22233357 3426 406 3 176 172552376 3148 12423 956 51182 12309 12722 167096645 1926 37881720 122773281 8184 2773 11640 32283 1440 72431 13294 154 398 43727 5772 6678 2723 85 51 4387 33192 3891 2694 889 354 242201 243 1602786688 65 6589 965 138 1067 166 20 14 3 9020 22 196575 2 4"
        
        parsed_data = parser.parse_data_line(user_data)
        
        if not parsed_data:
            print("❌ Could not parse data for database test")
            return False
        
        # Add agent
        agent_id = db.add_agent(
            parsed_data['agent_name'],
            parsed_data['faction'],
            12345  # Test user ID
        )
        
        print(f"✅ Agent added with ID: {agent_id}")
        
        # Add submission
        success = db.add_submission(agent_id, parsed_data)
        
        if success:
            print("✅ Data submitted to database successfully!")
            return True
        else:
            print("❌ Failed to submit data to database")
            return False
            
    except Exception as e:
        print(f"❌ Database test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting debug tests...\n")
    
    # Test parsing
    parse_success = test_data_parsing()
    
    # Test database submission
    db_success = test_database_submission()
    
    print(f"\n📊 Results:")
    print(f"Parsing: {'✅' if parse_success else '❌'}")
    print(f"Database: {'✅' if db_success else '❌'}")
    
    if parse_success and db_success:
        print("\n🎉 All tests passed! The issue might be elsewhere.")
    else:
        print("\n⚠️ Found issues that need to be fixed.")