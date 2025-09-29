"""
Configuration file for the Ingress Leaderboard Bot
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Load environment variables from .env file
load_dotenv(PROJECT_ROOT / ".env")

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Use environment variable or default
BOT_USERNAME = "IngressIN_leaderboard_bot"  # Bot username for mention detection

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