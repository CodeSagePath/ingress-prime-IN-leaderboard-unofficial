"""
Configuration file for the Ingress Leaderboard Bot
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Robust .env file loading with multiple fallback locations
def load_env_file():
    """Load .env file with fallback locations for different environments"""
    env_locations = [
        PROJECT_ROOT / ".env",  # Standard location
        Path.cwd() / ".env",    # Current working directory
        Path(os.path.expanduser("~")) / "ingress-bot" / ".env",  # Home directory
    ]
    
    # Add Termux-specific locations
    if os.environ.get('PREFIX', '').endswith('com.termux'):
        termux_locations = [
            Path("/data/data/com.termux/files/home/ingress-bot/.env"),
            Path(os.path.expanduser("~")) / ".env",
        ]
        env_locations.extend(termux_locations)
    
    for env_path in env_locations:
        try:
            if env_path.exists():
                result = load_dotenv(env_path, override=True)
                if result:
                    # Verify that BOT_TOKEN was actually loaded
                    test_token = os.getenv("BOT_TOKEN")
                    if test_token and test_token.strip() and test_token != "YOUR_BOT_TOKEN_HERE":
                        print(f"✅ Loaded .env from: {env_path}")
                        return True
        except Exception as e:
            print(f"Warning: Could not load {env_path}: {e}")
            continue
    
    print("⚠️ Warning: Could not find or load .env file")
    return False

# Load environment variables
load_env_file()

# Bot configuration with additional validation
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
    # Try to load .env again as a fallback
    load_dotenv(PROJECT_ROOT / ".env", override=True)
    BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = "ingressIN_leaderboard_bot"  # Bot username for mention detection

# Central command metadata
BOT_COMMANDS = [
    {
        "command": "start",
        "label": "🚀 Start",
        "description": "Welcome message & quick start guide",
        "callback": "nav_main_menu",
        "show_in_menu": False
    },
    {
        "command": "commands",
        "label": "🛠 Commands",
        "description": "Show every available bot command",
        "callback": "nav_commands",
        "show_in_menu": True
    },
    {
        "command": "submit",
        "label": "📊 Submit Stats",
        "description": "Submit Ingress statistics",
        "callback": "nav_submit",
        "show_in_menu": True
    },
    {
        "command": "leaderboard",
        "label": "🏆 Leaderboard",
        "description": "View key element leaderboards",
        "callback": "nav_leaderboard",
        "show_in_menu": True
    },
    {
        "command": "progress",
        "label": "📈 Progress",
        "description": "Track agent progress",
        "callback": "nav_progress",
        "show_in_menu": True
    },
    {
        "command": "factions",
        "label": "⚔️ Factions",
        "description": "Compare factions by time frame",
        "callback": "nav_factions",
        "show_in_menu": True
    },
    {
        "command": "stats",
        "label": "📋 Stats",
        "description": "List supported statistics",
        "callback": "nav_stats",
        "show_in_menu": True
    },
    {
        "command": "help",
        "label": "❓ Help",
        "description": "Quick help & tips",
        "callback": "nav_help",
        "show_in_menu": True
    },
    {
        "command": "help_detailed",
        "label": "📚 Help (Detailed)",
        "description": "Comprehensive help guide",
        "callback": "nav_help_detailed",
        "show_in_menu": False
    },
    {
        "command": "health",
        "label": "💚 Health Check",
        "description": "Check if server is up and running",
        "callback": "nav_health",
        "show_in_menu": True
    },
    {
        "command": "cancel",
        "label": "❌ Cancel",
        "description": "Cancel current operation",
        "show_in_menu": False
    },
    {
        "command": "create_stickers",
        "label": "🎨 Stickers",
        "description": "Create faction sticker set",
        "show_in_menu": False
    },
    {
        "command": "prepare_emoji",
        "label": "🧪 Prepare Emoji",
        "description": "Prepare faction emoji assets",
        "show_in_menu": False
    }
]

# Database configuration
DATABASE_PATH = PROJECT_ROOT / "data" / "ingress_leaderboard.db"

# Faction colors
FACTION_COLORS = {
    "Enlightened": "💚",
    "Resistance": "💙"
}

# Time slots for leaderboards
TIME_SLOTS = {
    "daily": 1,
    "weekly": 7,
    "monthly": 30,
    "all_time": None
}

# Key statistics to track for leaderboards
LEADERBOARD_STATS = [
    "Level",
    "Lifetime AP",
    "Current AP",
    "Unique Portals Visited",
    "Portals Discovered",
    "XM Collected",
    "Resonators Deployed",
    "Links Created",
    "Control Fields Created",
    "Mind Units Captured",
    "Portals Captured",
    "Distance Walked",
    "Mods Deployed",
    "Hacks",
    "Kinetic Capsules Completed",
    "Drone Hacks",
    "Glyph Hack Points",
    "Resonators Destroyed",
    "XM Recharged",
    "Machina Portals Reclaimed",
    "OPR Agreements",
    "Recursions",
    "Portal Scans Uploaded",
    "Uniques Scout Controlled",
    "Unique Missions Completed"
]

# Key elements mapping for enhanced leaderboard UI
KEY_ELEMENTS = {
    "🔸AP": {
        "display_name": "AP",
        "stat_name": "Current AP",
        "description": "Agent Points"
    },
    "🔸Builder": {
        "display_name": "Builder",
        "stat_name": "Resonators Deployed",
        "description": "Resonator Deploy"
    },
    "🔸Connector": {
        "display_name": "Connector", 
        "stat_name": "Links Created",
        "description": "Link Create"
    },
    "🔸Engineer": {
        "display_name": "Engineer",
        "stat_name": "Mods Deployed", 
        "description": "Mod Deploy"
    },
    "🔸Explorer": {
        "display_name": "Explorer",
        "stat_name": "Unique Portals Visited",
        "description": "Unique Portal Visit"
    },
    "🔸Hacker": {
        "display_name": "Hacker",
        "stat_name": "Hacks",
        "description": "Portal Hack"
    },
    "🔸Illuminator": {
        "display_name": "Illuminator",
        "stat_name": "Mind Units Captured",
        "description": "MU"
    },
    "🔸Kinetic Capsules": {
        "display_name": "Kinetic Capsules",
        "stat_name": "Kinetic Capsules Completed",
        "description": "Kinetic Capsules Completed"
    },
    "🔸Liberator": {
        "display_name": "Liberator",
        "stat_name": "Portals Captured",
        "description": "Portal Capture"
    },
    "🔸Maverick": {
        "display_name": "Maverick",
        "stat_name": "Drone Hacks",
        "description": "Drone Hack"
    },
    "🔸Mind Controller": {
        "display_name": "Mind Controller",
        "stat_name": "Control Fields Created",
        "description": "Field Create"
    },
    "🔸Overclock": {
        "display_name": "Overclock",
        "stat_name": "Glyph Hack Points",
        "description": "Overclock Hack"
    },
    "🔸Pioneer": {
        "display_name": "Pioneer",
        "stat_name": "Portals Discovered",
        "description": "Portal Discovery"
    },
    "🔸Purifier": {
        "display_name": "Purifier",
        "stat_name": "Resonators Destroyed",
        "description": "Resonator Destroy"
    },
    "🔸Recharger": {
        "display_name": "Recharger",
        "stat_name": "XM Recharged",
        "description": "Resonator Recharge"
    },
    "🔸Reclaimer": {
        "display_name": "Reclaimer",
        "stat_name": "Machina Portals Reclaimed",
        "description": "Machina Destroy and Capture"
    },
    "🔸Recon": {
        "display_name": "Recon",
        "stat_name": "OPR Agreements",
        "description": "Nomination Review"
    },
    "🔸Recursions": {
        "display_name": "Recursions",
        "stat_name": "Recursions",
        "description": "Recurse"
    },
    "🔸Scout": {
        "display_name": "Scout",
        "stat_name": "Portal Scans Uploaded",
        "description": "Portal Scan Upload"
    },
    "🔸Scout Controller": {
        "display_name": "Scout Controller",
        "stat_name": "Uniques Scout Controlled",
        "description": "Unique Portal Scan"
    },
    "🔸Specops": {
        "display_name": "Specops",
        "stat_name": "Unique Missions Completed",
        "description": "Mission Completion"
    },
    "🔸Translator": {
        "display_name": "Translator",
        "stat_name": "Glyph Hack Points",
        "description": "Glyph Hack"
    },
    "🔸Trekker": {
        "display_name": "Trekker",
        "stat_name": "Distance Walked",
        "description": "Distance Walk"
    }
}

# Prefix Detection Configuration
PREFIX_DETECTION_MODE = os.getenv("PREFIX_DETECTION_MODE", "flexible").lower()  # "strict" or "flexible"
REQUIRED_PREFIX_PATTERN = "Time Span Agent Name"  # The required prefix pattern for strict mode

# Prefix Detection Settings
PREFIX_SETTINGS = {
    "strict_mode": PREFIX_DETECTION_MODE == "strict",
    "required_pattern": REQUIRED_PREFIX_PATTERN,
    "case_sensitive": False,  # Whether pattern matching is case-sensitive
    "pattern_anywhere": True,  # Whether pattern can be anywhere in message (True) or must be at start (False)
    "ignore_without_prefix": PREFIX_DETECTION_MODE == "strict",  # In strict mode, ignore messages without prefix
}

# Auto-delete settings for stats messages
AUTO_DELETE_USER_STATS = os.getenv("AUTO_DELETE_USER_STATS", "true").lower() == "true"  # Auto-delete user's stats message after processing
AUTO_DELETE_DELAY_SECONDS = int(os.getenv("AUTO_DELETE_DELAY_SECONDS", "2"))  # Delay before deleting (2 seconds default)

# Data format mapping (field positions in the input data)
DATA_FIELDS = [
    "Time Span", "Agent Name", "Agent Faction", "Date", "Time", "Level",
    "Lifetime AP", "Current AP", "Unique Portals Visited", "Unique Portals Drone Visited",
    "Furthest Drone Distance", "Portals Discovered", "XM Collected", "OPR Agreements",
    "Portal Scans Uploaded", "Uniques Scout Controlled", "Resonators Deployed",
    "Links Created", "Control Fields Created", "Mind Units Captured",
    "Longest Link Ever Created", "Largest Control Field", "XM Recharged",
    "Portals Captured", "Unique Portals Captured", "Mods Deployed", "Hacks",
    "Drone Hacks", "Glyph Hack Points", "Completed Hackstreaks", "Longest Sojourner Streak",
    "Resonators Destroyed", "Portals Neutralized", "Enemy Links Destroyed",
    "Enemy Fields Destroyed", "Battle Beacon Combatant", "Drones Returned",
    "Machina Links Destroyed", "Machina Resonators Destroyed", "Machina Portals Neutralized",
    "Machina Portals Reclaimed", "Max Time Portal Held", "Max Time Link Maintained",
    "Max Link Length x Days", "Max Time Field Held", "Largest Field MUs x Days",
    "Forced Drone Recalls", "Distance Walked", "Kinetic Capsules Completed",
    "Unique Missions Completed", "Research Bounties Completed", "Research Days Completed",
    "Mission Day(s) Attended", "NL-1331 Meetup(s) Attended", "First Saturday Events",
    "Second Sunday Events", "+Delta Tokens", "+Delta Reso Points", "+Delta Field Points",
    "Agents Recruited", "Recursions", "Months Subscribed"
]