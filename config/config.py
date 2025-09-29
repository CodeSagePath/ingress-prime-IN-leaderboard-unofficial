"""
Configuration file for the Ingress Leaderboard Bot
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Database configuration
DATABASE_PATH = "ingress_leaderboard.db"

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
    "Distance Walked"
]

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