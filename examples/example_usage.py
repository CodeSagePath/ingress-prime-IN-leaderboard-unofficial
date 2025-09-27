"""
Example usage of the Ingress Leaderboard Bot components
This script demonstrates how the bot components work together
"""

from datetime import datetime
from database import DatabaseManager
from data_parser import DataParser
from leaderboard import LeaderboardManager

def example_usage():
    """Demonstrate bot functionality"""
    print("🎮 Ingress Leaderboard Bot - Example Usage")
    print("=" * 50)
    
    # Initialize components
    db = DatabaseManager()
    parser = DataParser()
    leaderboard = LeaderboardManager()
    
    # Example data (from the provided sample)
    sample_data = "ALL TIME rmkyjv Enlightened 2025-09-21 20:48:36 12 91769368 11769368 6490 908 6 254 308305720 10207 2546 1705 116660 22070 14377 9871129 290 1146680 221029999 16778 5252 14735 45372 2481 81710 31 360 44066 7844 6969 3529 42 10 398 1970 236 142 445 270 4765 177 3249101 71 5120 478 618 206 39 7 2 36 13 5780 305 7261 1 2 1"
    
    print("\n📊 Parsing sample data...")
    parsed_data = parser.parse_data_line(sample_data)
    
    if parsed_data:
        print(f"✅ Agent: {parsed_data['agent_name']}")
        print(f"✅ Faction: {parsed_data['faction']}")
        print(f"✅ Level: {parsed_data['level']}")
        print(f"✅ Current AP: {parser.format_number(parsed_data['current_ap'])}")
        print(f"✅ Portals Captured: {parser.format_number(parsed_data['portals_captured'])}")
        
        # Add to database
        print("\n💾 Adding to database...")
        agent_id = db.add_agent(parsed_data['agent_name'], parsed_data['faction'], 12345)
        success = db.add_submission(agent_id, parsed_data)
        
        if success:
            print("✅ Data added successfully!")
            
            # Generate some example leaderboards
            print("\n🏆 Generating leaderboards...")
            
            # Current AP leaderboard
            ap_leaderboard = leaderboard.generate_leaderboard("Current AP", "all_time")
            print("\n" + ap_leaderboard)
            
            # Faction comparison
            faction_comparison = leaderboard.generate_faction_comparison("all_time")
            print("\n" + faction_comparison)
            
        else:
            print("❌ Failed to add data to database")
    else:
        print("❌ Failed to parse sample data")
    
    # Show available statistics
    print("\n📈 Available Statistics:")
    stats = leaderboard.get_available_stats()
    for i, stat in enumerate(stats, 1):
        print(f"  {i}. {stat}")
    
    # Show time slots
    print("\n🕐 Available Time Slots:")
    time_slots = leaderboard.get_time_slots()
    for slot in time_slots:
        print(f"  • {slot.replace('_', ' ').title()}")
    
    print("\n✨ Example completed!")

def show_bot_commands():
    """Show example bot commands"""
    print("\n🤖 Example Bot Commands:")
    print("=" * 30)
    
    commands = [
        "/start - Welcome message",
        "/help - Show help text",
        "/submit - Submit your statistics",
        "/leaderboard Current AP weekly - Weekly AP leaderboard",
        "/leaderboard Portals Captured all_time Enlightened - Enlightened portals all-time",
        "/factions monthly - Monthly faction comparison",
        "/stats - List available statistics",
        "/progress Current AP 30 - Your AP progress over 30 days"
    ]
    
    for cmd in commands:
        print(f"  {cmd}")

if __name__ == "__main__":
    try:
        example_usage()
        show_bot_commands()
    except Exception as e:
        print(f"❌ Error running example: {e}")
        print("Make sure all dependencies are installed and the database is set up.")