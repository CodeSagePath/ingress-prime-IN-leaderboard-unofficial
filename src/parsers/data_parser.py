"""
Data parser for Ingress statistics with improved user experience
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from config.settings import DATA_FIELDS

class ParseError:
    """Represents a specific parsing error with user-friendly message"""
    def __init__(self, error_type: str, user_message: str, technical_details: str = ""):
        self.error_type = error_type
        self.user_message = user_message
        self.technical_details = technical_details

class DataParser:
    def __init__(self):
        self.field_mapping = {field.lower().replace(' ', '_'): i for i, field in enumerate(DATA_FIELDS)}
    
    def parse_data_line(self, data_line: str) -> Tuple[Optional[Dict], Optional[ParseError]]:
        """Parse a single line of Ingress data with detailed error reporting"""
        try:
            # Clean the data line - remove any bot commands or headers
            cleaned_line = self._clean_data_line(data_line.strip())
            if not cleaned_line:
                return None, None  # Empty lines (like /submit commands) are OK to skip, not an error
                
            # Split the data by spaces/tabs
            parts = cleaned_line.split()
            
            # Skip header lines, but check if there's data mixed in
            if self._is_header_line(parts):
                # Try to extract data from mixed header/data line
                extracted_data = self._extract_data_from_mixed_line(parts)
                if extracted_data:
                    # Use the extracted data instead
                    parts = extracted_data
                else:
                    return None, None  # Pure header line, OK to skip, not an error
            
            # Check minimum field count
            if len(parts) < 10:
                return None, ParseError(
                    "too_few_fields", 
                    f"❌ **Not enough data fields**\n\n"
                    f"I found only **{len(parts)} fields**, but need at least **50 fields** for a basic Ingress statistics submission.\n\n"
                    f"🤔 **Did you copy the complete statistics?**\n"
                    f"Make sure to copy __ALL__ your statistics from Ingress, _not just the first few columns._"
                )
            
            if len(parts) < 50:
                return None, ParseError(
                    "insufficient_fields",
                    f"❌ **Incomplete statistics data**\n\n"
                    f"I found **{len(parts)} fields**, but need **50+ fields** for complete statistics.\n\n"
                    f"💡 **How to fix:**\n"
                    f"• Copy your __ENTIRE__ statistics table from Ingress\n"
                    f"• Make sure you **scroll right** to see all columns\n"
                    f"• Include _all statistics_, not just the visible ones"
                )
            
            # Validate basic structure
            error = self._validate_basic_structure(parts)
            if error:
                return None, error
            
            # Create data dictionary
            data = {}
            
            # Handle "ALL TIME" or other multi-word time spans
            if len(parts) > 1 and parts[0] == "ALL" and parts[1] == "TIME":
                data['time_span'] = "ALL TIME"
                data['agent_name'] = parts[2]
                data['faction'] = parts[3]
                try:
                    data['data_date'] = datetime.strptime(parts[4], '%Y-%m-%d').date()
                    data['data_time'] = datetime.strptime(parts[5], '%H:%M:%S').time()
                except (ValueError, IndexError):
                    return None, ParseError(
                        "date_format", 
                        f"❌ **Invalid date/time format**\n\n"
                        f"Expected: `YYYY-MM-DD HH:MM:SS`\n"
                        f"Got: `{' '.join(parts[4:6]) if len(parts) > 5 else 'missing'}`\n\n"
                        f"💡 Make sure your date is in `YYYY-MM-DD` format and time in `HH:MM:SS`"
                    )
                offset = 6  # Start of numeric data
            else:
                # Single word time span
                data['time_span'] = parts[0]
                data['agent_name'] = parts[1]
                data['faction'] = parts[2]
                try:
                    data['data_date'] = datetime.strptime(parts[3], '%Y-%m-%d').date()
                    data['data_time'] = datetime.strptime(parts[4], '%H:%M:%S').time()
                except (ValueError, IndexError):
                    return None, ParseError(
                        "date_format",
                        f"❌ **Invalid date/time format**\n\n"
                        f"Expected: `YYYY-MM-DD HH:MM:SS`\n"
                        f"Got: `{' '.join(parts[3:5]) if len(parts) > 4 else 'missing'}`\n\n"
                        f"💡 Make sure your date is in `YYYY-MM-DD` format and time in `HH:MM:SS`"
                    )
                offset = 5  # Start of numeric data
            
            # Parse numeric fields
            numeric_fields = [
                ('level', 0), ('lifetime_ap', 1), ('current_ap', 2),
                ('unique_portals_visited', 3), ('unique_portals_drone_visited', 4),
                ('furthest_drone_distance', 5), ('portals_discovered', 6),
                ('xm_collected', 7), ('opr_agreements', 8), ('portal_scans_uploaded', 9),
                ('uniques_scout_controlled', 10), ('resonators_deployed', 11),
                ('links_created', 12), ('control_fields_created', 13),
                ('mind_units_captured', 14), ('longest_link_ever_created', 15),
                ('largest_control_field', 16), ('xm_recharged', 17),
                ('portals_captured', 18), ('unique_portals_captured', 19),
                ('mods_deployed', 20), ('hacks', 21), ('drone_hacks', 22),
                ('glyph_hack_points', 23), ('completed_hackstreaks', 24),
                ('longest_sojourner_streak', 25), ('resonators_destroyed', 26),
                ('portals_neutralized', 27), ('enemy_links_destroyed', 28),
                ('enemy_fields_destroyed', 29), ('battle_beacon_combatant', 30),
                ('drones_returned', 31), ('machina_links_destroyed', 32),
                ('machina_resonators_destroyed', 33), ('machina_portals_neutralized', 34),
                ('machina_portals_reclaimed', 35), ('max_time_portal_held', 36),
                ('max_time_link_maintained', 37), ('max_link_length_x_days', 38),
                ('max_time_field_held', 39), ('largest_field_mus_x_days', 40),
                ('forced_drone_recalls', 41), ('distance_walked', 42),
                ('kinetic_capsules_completed', 43), ('unique_missions_completed', 44),
                ('research_bounties_completed', 45), ('research_days_completed', 46),
                ('mission_days_attended', 47), ('nl1331_meetups_attended', 48),
                ('first_saturday_events', 49), ('second_sunday_events', 50),
                ('delta_tokens', 51), ('delta_reso_points', 52),
                ('delta_field_points', 53), ('agents_recruited', 54),
                ('recursions', 55), ('months_subscribed', 56)
            ]
            
            for field_name, relative_index in numeric_fields:
                try:
                    actual_index = offset + relative_index
                    if actual_index < len(parts):
                        value = parts[actual_index]
                        data[field_name] = int(value) if value.isdigit() or (value.startswith('-') and value[1:].isdigit()) else 0
                    else:
                        data[field_name] = 0
                except (IndexError, ValueError):
                    data[field_name] = 0
            
            return data, None
            
        except Exception as e:
            logging.error(f"Error parsing data line: {e}")
            return None, ParseError(
                "unexpected_error", 
                f"❌ **Unexpected error while parsing**\n\n"
                f"_Something went wrong:_ `{str(e)}`\n\n"
                f"💡 **Try this:**\n"
                f"• Use `/help` to see data format examples\n"
                f"• Make sure you copied __complete statistics__ from Ingress"
            )
    
    def _validate_basic_structure(self, parts: List[str]) -> Optional[ParseError]:
        """Validate basic structure of data line"""
        
        # Check if we have basic required parts
        if len(parts) < 6:
            return ParseError(
                "basic_structure",
                f"❌ **Missing basic information**\n\n"
                f"I need at least: _Time Span_, _Agent Name_, _Faction_, _Date_, _Time_, and statistics.\n\n"
                f"💡 **Make sure you have:**\n"
                f"• **Agent name**\n"
                f"• **Faction** _(Enlightened/Resistance)_\n"  
                f"• **Date and time**\n"
                f"• Your __complete statistics__"
            )
        
        # Validate faction (allowing for offset if "ALL TIME")
        faction_index = 3 if parts[0] == "ALL" and len(parts) > 1 and parts[1] == "TIME" else 2
        if faction_index < len(parts):
            faction = parts[faction_index].lower()
            if faction not in ['enlightened', 'resistance']:
                return ParseError(
                    "invalid_faction",
                    f"❌ **Invalid faction: `{parts[faction_index]}`**\n\n"
                    f"Faction must be either:\n"
                    f"• **Enlightened** _(green team)_ 💚\n" 
                    f"• **Resistance** _(blue team)_ 💙\n\n"
                    f"💡 Make sure you copied the faction name __correctly__ from Ingress"
                )
        
        return None
    
    def validate_faction(self, faction: str) -> bool:
        """Validate faction name"""
        return faction.lower() in ['enlightened', 'resistance']
    
    def format_number(self, number: int) -> str:
        """Format large numbers with appropriate suffixes"""
        if number >= 1_000_000_000:
            return f"{number / 1_000_000_000:.1f}B"
        elif number >= 1_000_000:
            return f"{number / 1_000_000:.1f}M"
        elif number >= 1_000:
            return f"{number / 1_000:.1f}K"
        else:
            return str(number)
    
    def calculate_delta(self, current_data: Dict, previous_data: Dict, field: str) -> int:
        """Calculate the difference between current and previous submission"""
        current_value = current_data.get(field, 0)
        previous_value = previous_data.get(field, 0)
        return current_value - previous_value
    
    def get_display_name(self, field_name: str) -> str:
        """Get human-readable display name for a field"""
        display_names = {
            'level': 'Level',
            'lifetime_ap': 'Lifetime AP',
            'current_ap': 'Current AP',
            'unique_portals_visited': 'Unique Portals Visited',
            'portals_discovered': 'Portals Discovered',
            'xm_collected': 'XM Collected',
            'resonators_deployed': 'Resonators Deployed',
            'links_created': 'Links Created',
            'control_fields_created': 'Control Fields Created',
            'mind_units_captured': 'Mind Units Captured',
            'portals_captured': 'Portals Captured',
            'distance_walked': 'Distance Walked',
            'resonators_destroyed': 'Resonators Destroyed',
            'portals_neutralized': 'Portals Neutralized',
            'enemy_links_destroyed': 'Enemy Links Destroyed',
            'enemy_fields_destroyed': 'Enemy Fields Destroyed',
            'mods_deployed': 'Mods Deployed',
            'hacks': 'Hacks',
            'kinetic_capsules_completed': 'Kinetic Capsules Completed',
            'drone_hacks': 'Drone Hacks',
            'glyph_hack_points': 'Glyph Hack Points',
            'xm_recharged': 'XM Recharged',
            'machina_portals_reclaimed': 'Machina Portals Reclaimed',
            'opr_agreements': 'OPR Agreements',
            'recursions': 'Recursions',
            'portal_scans_uploaded': 'Portal Scans Uploaded',
            'uniques_scout_controlled': 'Uniques Scout Controlled',
            'unique_missions_completed': 'Unique Missions Completed'
        }
        return display_names.get(field_name, field_name.replace('_', ' ').title())
    
    def get_database_field_name(self, display_name: str) -> str:
        """Convert display name to database field name"""
        # Create reverse mapping from display names to database field names
        display_to_field = {
            'Level': 'level',
            'Lifetime AP': 'lifetime_ap',
            'Current AP': 'current_ap',
            'Unique Portals Visited': 'unique_portals_visited',
            'Portals Discovered': 'portals_discovered', 
            'XM Collected': 'xm_collected',
            'Resonators Deployed': 'resonators_deployed',
            'Links Created': 'links_created',
            'Control Fields Created': 'control_fields_created',
            'Mind Units Captured': 'mind_units_captured',
            'Portals Captured': 'portals_captured',
            'Distance Walked': 'distance_walked',
            'Resonators Destroyed': 'resonators_destroyed',
            'Portals Neutralized': 'portals_neutralized',
            'Enemy Links Destroyed': 'enemy_links_destroyed',
            'Enemy Fields Destroyed': 'enemy_fields_destroyed',
            'Mods Deployed': 'mods_deployed',
            'Hacks': 'hacks',
            'Kinetic Capsules Completed': 'kinetic_capsules_completed',
            'Drone Hacks': 'drone_hacks',
            'Glyph Hack Points': 'glyph_hack_points',
            'XM Recharged': 'xm_recharged',
            'Machina Portals Reclaimed': 'machina_portals_reclaimed',
            'OPR Agreements': 'opr_agreements',
            'Recursions': 'recursions',
            'Portal Scans Uploaded': 'portal_scans_uploaded',
            'Uniques Scout Controlled': 'uniques_scout_controlled',
            'Unique Missions Completed': 'unique_missions_completed'
        }
        
        # Try exact match first
        if display_name in display_to_field:
            return display_to_field[display_name]
        
        # Fallback to simple conversion
        return display_name.lower().replace(' ', '_')
    
    def get_quick_help(self) -> str:
        """Return simple, quick help for data submission"""
        return """
🎯 **Quick Guide: Submit Your Ingress Stats**

**Step 1:** Open Ingress → Agent → Statistics
**Step 2:** Copy your statistics
**Step 3:** Send it here with `/submit`

**That's it!** ✨ _The bot handles the rest automatically._

🔗 Need detailed help? Use `/help_detailed`
        """
    
    def get_detailed_help(self) -> str:
        """Return detailed help with examples"""
        return """
📋 **Complete Data Submission Guide**

🚀 **Easiest Method:**
1. Open Ingress app → Agent tab → Statistics  
2. Select and copy **ALL** your statistics
3. Send: `/submit` followed by your copied data

💎 **Perfect Examples:**
```
/submit
ALL TIME YourAgent Enlightened 2025-01-15 12:30:45 16 50000000 25000000 ...
```

```  
/submit YourAgent Resistance 2025-01-15 12:30:45 16 50000000 25000000 ...
```

📝 **What you need:**
• **Agent name** _(your Ingress username)_
• **Faction**: __Enlightened__ or __Resistance__  
• **Date**: `YYYY-MM-DD` format
• **Time**: `HH:MM:SS` format
• **All 60+ statistics** from Ingress

💡 **Pro Tips:**
• Copy with headers - _I'll skip them automatically_
• Make sure to **scroll right** in Ingress to get **ALL** stats
• You can submit **multiple time periods** at once

🆘 **Still stuck?** Copy your stats exactly as they appear in Ingress and send them!
        """
    
    def _clean_data_line(self, line: str) -> str:
        """Clean data line by removing bot commands and unnecessary text"""
        # Remove common bot command patterns
        if line.startswith('/submit'):
            line = line[7:].strip()  # Remove '/submit' and leading whitespace
        
        # Look for actual data patterns in the line
        parts = line.split()
        if not parts:
            return ""
        
        # Look for data patterns that indicate start of actual statistics
        for i, part in enumerate(parts):
            # Look for "ALL TIME" pattern followed by agent name and faction
            if (i < len(parts) - 4 and 
                part == "ALL" and 
                parts[i+1] == "TIME" and
                i+3 < len(parts) and
                parts[i+3].lower() in ['enlightened', 'resistance']):
                return " ".join(parts[i:])
            
            # Look for single word time span patterns followed by agent name and faction
            elif (part in ["DAILY", "WEEKLY", "MONTHLY", "YEARLY"] and
                  i < len(parts) - 3 and 
                  parts[i+2].lower() in ['enlightened', 'resistance']):
                return " ".join(parts[i:])
            
            # Look for pattern: [timespan] [agent_name] [faction] [date] [time] [level] [numbers...]
            # This handles cases where timespan is not in our predefined list
            elif (i < len(parts) - 5 and
                  parts[i+1].lower() in ['enlightened', 'resistance'] and
                  self._looks_like_date(parts[i+2]) and
                  self._looks_like_time(parts[i+3]) and
                  parts[i+4].isdigit()):  # Level should be a number
                return " ".join(parts[i:])
        
        # If no clear data pattern found, return the original line
        # The header detection will handle filtering out pure header lines
        return line
    
    def _looks_like_date(self, text: str) -> bool:
        """Check if text looks like a date in YYYY-MM-DD format"""
        try:
            datetime.strptime(text, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def _looks_like_time(self, text: str) -> bool:
        """Check if text looks like a time in HH:MM:SS format"""
        try:
            datetime.strptime(text, '%H:%M:%S')
            return True
        except ValueError:
            return False
    
    def _is_header_line(self, parts: List[str]) -> bool:
        """Check if this is a header line that should be skipped"""
        if not parts:
            return True
            
        # Check if line starts with /submit or bot commands
        if parts[0].startswith('/') or parts[0].startswith('@'):
            return True
        
        # Check for exact header patterns (more precise detection)
        header_patterns = [
            ["Time", "Span", "Agent", "Name"],  # Start of typical header
            ["Agent", "Name", "Agent", "Faction"],  # Another common header pattern
            ["Date", "(yyyy-mm-dd)", "Time", "(hh:mm:ss)"],  # Date/time header pattern
        ]
        
        # Check if this matches any known header pattern
        for pattern in header_patterns:
            if len(parts) >= len(pattern):
                if all(parts[i] == pattern[i] for i in range(len(pattern))):
                    return True
        
        # Check for obvious header indicators (but be more specific)
        # A real header line will have many descriptive words, not data values
        if len(parts) > 10:  # Headers are usually long
            descriptive_words = [
                "Time", "Span", "Agent", "Name", "Faction", "Date", "Level", 
                "Lifetime", "Current", "Unique", "Portals", "Visited", "XM",
                "Collected", "Deployed", "Created", "Captured", "Distance",
                "(yyyy-mm-dd)", "(hh:mm:ss)", "Agreements", "Uploaded"
            ]
            
            # Count how many parts are descriptive words vs potential data
            descriptive_count = sum(1 for part in parts if part in descriptive_words)
            numeric_count = sum(1 for part in parts if part.replace('-', '').replace(':', '').isdigit())
            
            # If more than 50% are descriptive words and less than 20% are numeric, it's likely a header
            if len(parts) > 0 and descriptive_count > len(parts) * 0.5 and numeric_count < len(parts) * 0.2:
                return True
        
        # Additional check: if it starts with "ALL TIME" followed by what looks like data, it's NOT a header
        if len(parts) >= 6 and parts[0] == "ALL" and parts[1] == "TIME":
            # Check if positions 4 and 5 look like date and time
            try:
                datetime.strptime(parts[4], '%Y-%m-%d')
                datetime.strptime(parts[5], '%H:%M:%S')
                return False  # This is data, not a header
            except (ValueError, IndexError):
                pass
            
        return False

    def _extract_data_from_mixed_line(self, parts: List[str]) -> Optional[List[str]]:
        """Extract data from a line that contains both header and data"""
        # Look for "ALL TIME" pattern which indicates start of data
        for i in range(len(parts) - 1):
            if parts[i] == "ALL" and parts[i + 1] == "TIME":
                # Check if this looks like the start of actual data
                # We need at least agent_name, faction, date, time after "ALL TIME"
                if i + 6 < len(parts):
                    try:
                        # Try to parse date and time at expected positions
                        datetime.strptime(parts[i + 4], '%Y-%m-%d')
                        datetime.strptime(parts[i + 5], '%H:%M:%S')
                        # Extract from "ALL TIME" onwards
                        return parts[i:]
                    except (ValueError, IndexError):
                        continue
        
        # Look for other time span patterns (single word followed by agent name, faction, date, time)
        for i in range(len(parts) - 5):
            # Check if this position could be start of data
            if i + 4 < len(parts):
                try:
                    # Check if positions i+2, i+3 could be date and time
                    datetime.strptime(parts[i + 2], '%Y-%m-%d')
                    datetime.strptime(parts[i + 3], '%H:%M:%S')
                    # Check if position i+1 looks like a faction
                    if parts[i + 1].lower() in ['enlightened', 'resistance']:
                        return parts[i:]
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def parse_multiline_data(self, data_text: str) -> Tuple[List[Dict], List[ParseError]]:
        """Parse multiple lines of data with detailed error reporting"""
        results = []
        errors = []
        lines = data_text.strip().split('\n')
        
        if not lines or all(not line.strip() for line in lines):
            return [], [ParseError(
                "no_data",
                "❌ **No data provided**\n\n"
                "_I didn't receive any statistics data to process._\n\n"
                "💡 **How to submit:**\n"
                "1. Copy your statistics from Ingress\n"
                "2. Send `/submit` followed by your data"
            )]
        
        data_lines_found = 0
        header_lines_skipped = 0
        
        for line_num, line in enumerate(lines, 1):
            if line.strip():  # Skip empty lines
                parsed_data, error = self.parse_data_line(line)
                
                if parsed_data:  # Successfully parsed data
                    results.append(parsed_data)
                    data_lines_found += 1
                elif error:  # Parse error occurred
                    # Add line number context to error
                    error.user_message = f"**Line {line_num}:** {error.user_message}"
                    errors.append(error)
                else:  # Header line (skipped, not an error)
                    header_lines_skipped += 1
        
        # If no data was found, provide helpful feedback
        if not results and not errors:
            errors.append(ParseError(
                "only_headers",
                f"❌ **Only found headers, no data**\n\n"
                f"I skipped **{header_lines_skipped}** header lines but found no actual statistics data.\n\n"
                f"💡 **Make sure to include:**\n"
                f"• Your **agent name** and **faction**\n"
                f"• The __complete statistics row__ from Ingress\n"
                f"• _Not just the column headers_"
            ))
        
        return results, errors