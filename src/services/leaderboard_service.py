"""
Leaderboard generation and formatting
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import io
from ..database import DatabaseManager
from ..parsers import DataParser
from .image_service import ImageGenerator
from .sticker_service import StickerManager
from config.settings import TIME_SLOTS, LEADERBOARD_STATS

class LeaderboardManager:
    def __init__(self):
        self.db = DatabaseManager()
        self.parser = DataParser()
        self.image_generator = ImageGenerator()
        self.sticker_manager = StickerManager()
    
    def generate_leaderboard(self, stat: str, time_slot: str = "all_time", 
                           faction: Optional[str] = None, limit: int = 10) -> str:
        """Generate formatted leaderboard text"""
        try:
            days = TIME_SLOTS.get(time_slot)
            results = self.db.get_leaderboard(stat, faction, days, limit)
            
            if not results:
                return f"No data available for {stat} leaderboard."
            
            # Format header
            time_desc = time_slot.replace('_', ' ').title()
            faction_desc = f" - {faction}" if faction else ""
            header = f"🏆 {self.parser.get_display_name(stat)} Leaderboard ({time_desc}){faction_desc}\n\n"
            
            # Format entries
            leaderboard_text = header
            for i, (agent_name, agent_faction, value, submission_date) in enumerate(results, 1):
                faction_emoji = self.sticker_manager.get_faction_sticker_emoji(agent_faction)
                formatted_value = self.parser.format_number(int(value)) if value else "0"
                
                medal = ""
                if i == 1:
                    medal = "🥇"
                elif i == 2:
                    medal = "🥈"
                elif i == 3:
                    medal = "🥉"
                else:
                    if i <= 9:
                        medal = f"  {i}. "
                    else:
                        medal = f" {i}. "
                
                leaderboard_text += f"{medal} {faction_emoji} {formatted_value} @{agent_name}\n"
            
            leaderboard_text += f"\n📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            return leaderboard_text
            
        except Exception as e:
            logging.error(f"Error generating leaderboard: {e}")
            return "Error generating leaderboard. Please try again."
    
    def generate_faction_comparison(self, time_slot: str = "all_time") -> str:
        """Generate faction vs faction comparison"""
        try:
            days = TIME_SLOTS.get(time_slot)
            faction_stats = self.db.get_faction_stats(days)
            
            if not faction_stats:
                return "No faction data available."
            
            time_desc = time_slot.replace('_', ' ').title()
            header = f"⚔️ Faction Comparison ({time_desc})\n\n"
            
            comparison_text = header
            
            for faction, stats in faction_stats.items():
                faction_emoji = self.sticker_manager.get_faction_sticker_emoji(faction)
                comparison_text += f"{faction_emoji} **{faction}**\n"
                comparison_text += f"   👥 Agents: {stats['agent_count']}\n"
                comparison_text += f"   📊 Avg Level: {stats['avg_level']}\n"
                comparison_text += f"   ⚡ Total AP: {self.parser.format_number(stats['total_ap'])}\n"
                comparison_text += f"   🏰 Portals Captured: {self.parser.format_number(stats['total_portals_captured'])}\n\n"
            
            return comparison_text
            
        except Exception as e:
            logging.error(f"Error generating faction comparison: {e}")
            return "Error generating faction comparison. Please try again."
    
    def generate_agent_progress(self, agent_name: str, telegram_user_id: int, 
                              stat: str, days: int = 30) -> str:
        """Generate agent progress report"""
        try:
            progress_data = self.db.get_agent_progress(agent_name, telegram_user_id, stat, days)
            
            if not progress_data:
                return f"No progress data available for {agent_name} in the last {days} days."
            
            if len(progress_data) < 2:
                return f"Need at least 2 data points to show progress for {agent_name}."
            
            # Calculate progress
            first_value = progress_data[0][1]
            last_value = progress_data[-1][1]
            delta = last_value - first_value
            
            # Format progress report
            stat_display = self.parser.get_display_name(stat)
            header = f"📈 {agent_name}'s {stat_display} Progress ({days} days)\n\n"
            
            progress_text = header
            progress_text += f"Starting Value: {self.parser.format_number(first_value)}\n"
            progress_text += f"Current Value: {self.parser.format_number(last_value)}\n"
            
            if delta > 0:
                progress_text += f"📈 Gain: +{self.parser.format_number(delta)}\n"
            elif delta < 0:
                progress_text += f"📉 Loss: {self.parser.format_number(delta)}\n"
            else:
                progress_text += f"➡️ No change\n"
            
            # Add recent submissions
            progress_text += f"\n📊 Recent submissions:\n"
            for date, value in progress_data[-5:]:  # Last 5 submissions
                progress_text += f"   {date}: {self.parser.format_number(value)}\n"
            
            return progress_text
            
        except Exception as e:
            logging.error(f"Error generating agent progress: {e}")
            return "Error generating progress report. Please try again."
    
    def get_available_stats(self) -> List[str]:
        """Get list of available statistics for leaderboards"""
        return LEADERBOARD_STATS
    
    def get_time_slots(self) -> List[str]:
        """Get available time slots"""
        return list(TIME_SLOTS.keys())
    
    def generate_help_text(self) -> str:
        """Generate help text for the bot"""
        help_text = """
🤖 **Ingress Leaderboard Bot Help**

**Commands:**
/start - Start using the bot
/help - Show this help message
/submit - Submit your Ingress statistics (interactive mode)
/submit [data] - Submit data directly in one command
/leaderboard [stat] [timeframe] [faction] - View leaderboards
/progress [stat] [days] - View your progress
/factions [timeframe] - Compare factions
/stats - List available statistics
/prepare_emoji - Convert faction images to emoji format
/create_stickers - Create custom faction sticker set

**Data Submission:**
You can submit data in two ways:
1. Use `/submit` and follow the prompts
2. Use `/submit ALL TIME YourName Faction...` with your full data line

**Available Statistics:**
"""
        for stat in LEADERBOARD_STATS:
            help_text += f"• {stat}\n"
        
        help_text += """
**Time Frames:**
• daily - Last 24 hours
• weekly - Last 7 days  
• monthly - Last 30 days
• all_time - All time records

**Factions:**
🟢 Enlightened
🔵 Resistance

**Examples:**
/leaderboard "Lifetime AP" weekly
/leaderboard "Portals Captured" all_time Enlightened
/progress "Current AP" 14
/factions monthly

**Data Submission:**
Use /submit and paste your Ingress statistics data in the specified format.
"""
        return help_text
    
    def generate_leaderboard_image(self, stat: str, time_slot: str = "all_time", 
                                 faction: Optional[str] = None, limit: int = 10) -> io.BytesIO:
        """Generate a text-based leaderboard image with inline faction icons"""
        try:
            # Get leaderboard data
            days = TIME_SLOTS.get(time_slot)
            results = self.db.get_leaderboard(stat, days, faction, limit)
            
            if not results:
                return self.image_generator._generate_no_data_image(f"{stat} leaderboard")
            
            # Generate time description
            time_desc = time_slot.replace('_', ' ').title()
            
            # Generate title
            title = self.parser.get_display_name(stat)
            if faction:
                title += f" - {faction}"
            
            # Generate the text-based leaderboard image with faction icons
            return self.image_generator.generate_text_leaderboard_with_faction_icons(
                results, title, time_desc
            )
            
        except Exception as e:
            logging.error(f"Error generating leaderboard image: {e}")
            return self.image_generator._generate_error_image()
    
    def generate_faction_comparison_image(self, time_slot: str = "all_time") -> io.BytesIO:
        """Generate faction comparison as an image"""
        try:
            days = TIME_SLOTS.get(time_slot)
            faction_stats = self.db.get_faction_stats(days)
            
            return self.image_generator.generate_faction_comparison_image(faction_stats, time_slot)
            
        except Exception as e:
            logging.error(f"Error generating faction comparison image: {e}")
            return self.image_generator._generate_error_image()