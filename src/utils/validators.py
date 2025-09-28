"""
Validation utilities for the Ingress Leaderboard Bot
"""

import re
from datetime import datetime
from typing import Optional

class DataValidator:
    @staticmethod
    def validate_faction(faction: str) -> bool:
        """Validate faction name"""
        return faction.lower() in ['enlightened', 'resistance']
    
    @staticmethod
    def validate_agent_name(agent_name: str) -> bool:
        """Validate agent name format"""
        # Agent names should be alphanumeric with possible underscores
        return bool(re.match(r'^[a-zA-Z0-9_]{3,15}$', agent_name))
    
    @staticmethod
    def validate_date_format(date_str: str) -> Optional[datetime]:
        """Validate and parse date string"""
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return None
    
    @staticmethod
    def validate_time_format(time_str: str) -> Optional[datetime]:
        """Validate and parse time string"""
        try:
            return datetime.strptime(time_str, '%H:%M:%S')
        except ValueError:
            return None
    
    @staticmethod
    def validate_numeric_field(value: str) -> bool:
        """Validate numeric field"""
        try:
            int(value)
            return True
        except ValueError:
            return False