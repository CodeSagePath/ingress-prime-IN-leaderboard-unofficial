"""
Image generation service for creating leaderboard images with faction icons
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import os
from pathlib import Path

from config.settings import FACTION_COLORS, PROJECT_ROOT

logger = logging.getLogger(__name__)

class ImageGenerator:
    def __init__(self):
        self.assets_path = PROJECT_ROOT / "assets"
        self.faction_images = {
            "Enlightened": self.assets_path / "enlightened.webp",
            "Resistance": self.assets_path / "resistance.webp"
        }
        
        # Image settings
        self.width = 800
        self.background_color = (30, 30, 30)  # Dark background
        self.text_color = (255, 255, 255)  # White text
        self.header_color = (255, 215, 0)  # Gold for header
        self.enlightened_color = (40, 167, 69)  # Green
        self.resistance_color = (0, 123, 255)  # Blue
        
        # Font settings
        self.header_font_size = 32
        self.entry_font_size = 20
        self.small_font_size = 16
        
        # Try to load fonts
        self.header_font = self._load_font(self.header_font_size)
        self.entry_font = self._load_font(self.entry_font_size)
        self.small_font = self._load_font(self.small_font_size)
        
    def _load_font(self, size: int):
        """Load font with fallback to default"""
        try:
            # Try to load a nice font (works on most systems)
            return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
        except:
            try:
                return ImageFont.truetype("arial.ttf", size)
            except:
                # Fallback to default font
                return ImageFont.load_default()
    
    def _load_faction_image(self, faction: str, size: Tuple[int, int] = (40, 40)) -> Optional[Image.Image]:
        """Load and resize faction image"""
        try:
            faction_path = self.faction_images.get(faction)
            if not faction_path or not faction_path.exists():
                logger.warning(f"Faction image not found: {faction_path}")
                return None
            
            img = Image.open(faction_path)
            img = img.convert("RGBA")
            img = img.resize(size, Image.Resampling.LANCZOS)
            return img
        except Exception as e:
            logger.error(f"Error loading faction image for {faction}: {e}")
            return None
    
    def generate_leaderboard_image(self, leaderboard_data: Dict, stat: str, 
                                 time_slot: str = "all_time", faction: Optional[str] = None) -> io.BytesIO:
        """Generate leaderboard image with faction icons"""
        try:
            # Parse leaderboard data
            results = leaderboard_data.get('results', [])
            if not results:
                return self._generate_no_data_image(stat)
            
            # Calculate image height based on content
            header_height = 80
            entry_height = 50
            footer_height = 40
            padding = 20
            
            total_height = header_height + (len(results) * entry_height) + footer_height + (padding * 2)
            
            # Create image
            img = Image.new('RGB', (self.width, total_height), self.background_color)
            draw = ImageDraw.Draw(img)
            
            # Draw header
            time_desc = time_slot.replace('_', ' ').title()
            faction_desc = f" - {faction}" if faction else ""
            header_text = f"🏆 {stat} Leaderboard ({time_desc}){faction_desc}"
            
            # Center the header text
            header_bbox = draw.textbbox((0, 0), header_text, font=self.header_font)
            header_width = header_bbox[2] - header_bbox[0]
            header_x = (self.width - header_width) // 2
            
            draw.text((header_x, padding), header_text, fill=self.header_color, font=self.header_font)
            
            # Draw entries
            y_offset = header_height + padding
            
            for i, (agent_name, agent_faction, value, submission_date) in enumerate(results, 1):
                # Get faction color and image
                faction_color = self.enlightened_color if agent_faction == "Enlightened" else self.resistance_color
                faction_img = self._load_faction_image(agent_faction, (30, 30))
                
                # Format value
                formatted_value = self._format_number(int(value)) if value else "0"
                
                # Medal/position
                medal = ""
                if i == 1:
                    medal = "🥇"
                elif i == 2:
                    medal = "🥈"
                elif i == 3:
                    medal = "🥉"
                else:
                    medal = f"{i}."
                
                # Draw faction image if available
                faction_x = 20
                if faction_img:
                    img.paste(faction_img, (faction_x, y_offset + 10), faction_img)
                    text_x = faction_x + 40
                else:
                    # Fallback to colored circle
                    draw.ellipse([faction_x, y_offset + 10, faction_x + 30, y_offset + 40], 
                               fill=faction_color)
                    text_x = faction_x + 40
                
                # Draw entry text
                entry_text = f"{medal} {formatted_value} @{agent_name}"
                draw.text((text_x, y_offset + 10), entry_text, fill=self.text_color, font=self.entry_font)
                
                y_offset += entry_height
            
            # Draw footer
            footer_text = f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            footer_bbox = draw.textbbox((0, 0), footer_text, font=self.small_font)
            footer_width = footer_bbox[2] - footer_bbox[0]
            footer_x = (self.width - footer_width) // 2
            
            draw.text((footer_x, total_height - footer_height), footer_text, 
                     fill=(150, 150, 150), font=self.small_font)
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return img_bytes
            
        except Exception as e:
            logger.error(f"Error generating leaderboard image: {e}")
            return self._generate_error_image()
    
    def generate_faction_comparison_image(self, faction_stats: Dict, time_slot: str = "all_time") -> io.BytesIO:
        """Generate faction comparison image"""
        try:
            if not faction_stats:
                return self._generate_no_data_image("Faction Comparison")
            
            # Calculate image dimensions
            header_height = 80
            faction_section_height = 200
            padding = 20
            
            total_height = header_height + (len(faction_stats) * faction_section_height) + padding * 2
            
            # Create image
            img = Image.new('RGB', (self.width, total_height), self.background_color)
            draw = ImageDraw.Draw(img)
            
            # Draw header
            time_desc = time_slot.replace('_', ' ').title()
            header_text = f"⚔️ Faction Comparison ({time_desc})"
            
            header_bbox = draw.textbbox((0, 0), header_text, font=self.header_font)
            header_width = header_bbox[2] - header_bbox[0]
            header_x = (self.width - header_width) // 2
            
            draw.text((header_x, padding), header_text, fill=self.header_color, font=self.header_font)
            
            # Draw faction sections
            y_offset = header_height + padding
            
            for faction, stats in faction_stats.items():
                faction_color = self.enlightened_color if faction == "Enlightened" else self.resistance_color
                faction_img = self._load_faction_image(faction, (50, 50))
                
                # Draw faction image and name
                faction_x = 50
                if faction_img:
                    img.paste(faction_img, (faction_x, y_offset), faction_img)
                    text_x = faction_x + 60
                else:
                    # Fallback to colored circle
                    draw.ellipse([faction_x, y_offset, faction_x + 50, y_offset + 50], 
                               fill=faction_color)
                    text_x = faction_x + 60
                
                # Draw faction name
                draw.text((text_x, y_offset + 10), f"{faction}", fill=faction_color, font=self.header_font)
                
                # Draw stats
                stats_y = y_offset + 60
                stats_text = [
                    f"👥 Agents: {stats['agent_count']}",
                    f"📊 Avg Level: {stats['avg_level']}",
                    f"⚡ Total AP: {self._format_number(stats['total_ap'])}",
                    f"🏰 Portals Captured: {self._format_number(stats['total_portals_captured'])}"
                ]
                
                for stat_line in stats_text:
                    draw.text((text_x, stats_y), stat_line, fill=self.text_color, font=self.entry_font)
                    stats_y += 25
                
                y_offset += faction_section_height
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return img_bytes
            
        except Exception as e:
            logger.error(f"Error generating faction comparison image: {e}")
            return self._generate_error_image()
    
    def generate_text_style_leaderboard_image(self, leaderboard_data: Dict, stat: str, 
                                            time_slot: str = "all_time", faction: Optional[str] = None) -> io.BytesIO:
        """Generate a text-style leaderboard image with inline faction icons (like the text output but as image)"""
        try:
            # Parse leaderboard data
            results = leaderboard_data.get('results', [])
            if not results:
                return self._generate_no_data_image(stat)
            
            # Calculate image dimensions
            line_height = 35
            padding = 30
            header_height = 60
            footer_height = 40
            
            total_height = header_height + (len(results) * line_height) + footer_height + (padding * 2)
            
            # Create image with dark background (like terminal/text style)
            img = Image.new('RGB', (self.width, total_height), (20, 20, 20))  # Dark background
            draw = ImageDraw.Draw(img)
            
            y_pos = padding
            
            # Draw header (like text format)
            time_desc = time_slot.replace('_', ' ').title()
            faction_desc = f" - {faction}" if faction else ""
            header_text = f"🏆 {stat} Leaderboard ({time_desc}){faction_desc}"
            
            draw.text((padding, y_pos), header_text, fill=self.header_color, font=self.header_font)
            y_pos += header_height
            
            # Draw each leaderboard entry with inline faction icon
            for i, (agent_name, agent_faction, value, submission_date) in enumerate(results, 1):
                # Medal emoji/number
                if i == 1:
                    medal = "🥇"
                elif i == 2:
                    medal = "🥈"
                elif i == 3:
                    medal = "🥉"
                else:
                    medal = f"  {i}. " if i <= 9 else f" {i}. "
                
                # Format value
                formatted_value = self._format_number(int(value)) if value else "0"
                
                # Draw medal/number
                draw.text((padding, y_pos), medal, fill=self.text_color, font=self.entry_font)
                
                # Load and draw faction icon (small, inline)
                faction_img = self._load_faction_image(agent_faction, (25, 25))
                faction_x = padding + 80  # After medal text
                
                if faction_img:
                    img.paste(faction_img, (faction_x, y_pos + 5), faction_img)
                else:
                    # Fallback to colored circle
                    faction_color = self.enlightened_color if agent_faction == "Enlightened" else self.resistance_color
                    draw.ellipse([faction_x, y_pos + 5, faction_x + 25, y_pos + 30], fill=faction_color)
                
                # Draw value and agent name (like text format)
                stats_text = f" {formatted_value} @{agent_name}"
                draw.text((faction_x + 35, y_pos), stats_text, fill=self.text_color, font=self.entry_font)
                
                y_pos += line_height
            
            # Draw footer (like text format)
            y_pos += 20
            footer_text = f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            draw.text((padding, y_pos), footer_text, fill=(150, 150, 150), font=self.small_font)
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return img_bytes
            
        except Exception as e:
            logger.error(f"Error generating text-style leaderboard image: {e}")
            return self._generate_error_image()

    def generate_text_style_faction_comparison_image(self, faction_stats: Dict, time_slot: str = "all_time") -> io.BytesIO:
        """Generate a text-style faction comparison image with inline faction icons"""
        try:
            if not faction_stats:
                return self._generate_no_data_image("Faction Comparison")
            
            # Calculate dimensions
            line_height = 30
            padding = 30
            header_height = 60
            faction_section_height = 150  # Space for each faction's stats
            
            total_height = header_height + (len(faction_stats) * faction_section_height) + (padding * 2)
            
            # Create image
            img = Image.new('RGB', (self.width, total_height), (20, 20, 20))
            draw = ImageDraw.Draw(img)
            
            y_pos = padding
            
            # Draw header
            time_desc = time_slot.replace('_', ' ').title()
            header_text = f"⚔️ Faction Comparison ({time_desc})"
            draw.text((padding, y_pos), header_text, fill=self.header_color, font=self.header_font)
            y_pos += header_height
            
            # Draw each faction
            for faction, stats in faction_stats.items():
                # Load and draw faction icon
                faction_img = self._load_faction_image(faction, (30, 30))
                
                if faction_img:
                    img.paste(faction_img, (padding, y_pos), faction_img)
                else:
                    # Fallback to colored circle
                    faction_color = self.enlightened_color if faction == "Enlightened" else self.resistance_color
                    draw.ellipse([padding, y_pos, padding + 30, y_pos + 30], fill=faction_color)
                
                # Draw faction name
                faction_color = self.enlightened_color if faction == "Enlightened" else self.resistance_color
                draw.text((padding + 40, y_pos), f"**{faction}**", fill=faction_color, font=self.entry_font)
                
                # Draw stats (indented like text format)
                stats_y = y_pos + 35
                stats_lines = [
                    f"   👥 Agents: {stats['agent_count']}",
                    f"   📊 Avg Level: {stats['avg_level']}",
                    f"   ⚡ Total AP: {self._format_number(stats['total_ap'])}",
                    f"   🏰 Portals Captured: {self._format_number(stats['total_portals_captured'])}"
                ]
                
                for stat_line in stats_lines:
                    draw.text((padding + 40, stats_y), stat_line, fill=self.text_color, font=self.small_font)
                    stats_y += line_height
                
                y_pos += faction_section_height
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return img_bytes
            
        except Exception as e:
            logger.error(f"Error generating text-style faction comparison image: {e}")
            return self._generate_error_image()

    def generate_faction_icons_image(self) -> io.BytesIO:
        """Generate a simple image showing faction icons for use with text captions"""
        try:
            # Create a small horizontal image with both faction icons
            img_width = 200
            img_height = 60
            img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))  # Transparent background
            
            # Load faction images
            enlightened_img = self._load_faction_image("Enlightened", (40, 40))
            resistance_img = self._load_faction_image("Resistance", (40, 40))
            
            # Position icons side by side
            if enlightened_img:
                img.paste(enlightened_img, (30, 10), enlightened_img)
            if resistance_img:
                img.paste(resistance_img, (130, 10), resistance_img)
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return img_bytes
            
        except Exception as e:
            logger.error(f"Error generating faction icons image: {e}")
            return self._generate_simple_placeholder_image()

    def _generate_simple_placeholder_image(self) -> io.BytesIO:
        """Generate a simple placeholder image"""
        img = Image.new('RGB', (200, 60), (40, 40, 40))
        draw = ImageDraw.Draw(img)
        draw.text((10, 20), "Faction Icons", fill=(255, 255, 255), font=self.small_font)
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes

    def _generate_no_data_image(self, title: str) -> io.BytesIO:
        """Generate a 'no data' image"""
        img = Image.new('RGB', (self.width, 200), self.background_color)
        draw = ImageDraw.Draw(img)
        
        text = f"No data available for {title}"
        bbox = draw.textbbox((0, 0), text, font=self.entry_font)
        text_width = bbox[2] - bbox[0]
        text_x = (self.width - text_width) // 2
        
        draw.text((text_x, 90), text, fill=self.text_color, font=self.entry_font)
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes
    
    def _generate_error_image(self) -> io.BytesIO:
        """Generate an error image"""
        img = Image.new('RGB', (self.width, 200), self.background_color)
        draw = ImageDraw.Draw(img)
        
        text = "Error generating leaderboard image"
        bbox = draw.textbbox((0, 0), text, font=self.entry_font)
        text_width = bbox[2] - bbox[0]
        text_x = (self.width - text_width) // 2
        
        draw.text((text_x, 90), text, fill=(255, 100, 100), font=self.entry_font)
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes
    
    def generate_text_leaderboard_with_faction_icons(self, leaderboard_data: list, title: str, time_desc: str) -> io.BytesIO:
        """
        Generate a text-based leaderboard image with inline faction icons
        This creates an image that looks like text but has actual faction images inline
        """
        try:
            # Calculate image dimensions based on content
            line_height = 40
            header_height = 80
            footer_height = 40
            padding = 20
            
            total_height = header_height + (len(leaderboard_data) * line_height) + footer_height + (padding * 2)
            img_width = 600
            
            # Create image
            img = Image.new('RGB', (img_width, total_height), (255, 255, 255))  # White background
            draw = ImageDraw.Draw(img)
            
            # Load faction images
            faction_images = {}
            try:
                enlightened_path = PROJECT_ROOT / "assets" / "enlightened.webp"
                resistance_path = PROJECT_ROOT / "assets" / "resistance.webp"
                
                if enlightened_path.exists():
                    enlightened_img = Image.open(enlightened_path).convert("RGBA")
                    enlightened_img = enlightened_img.resize((32, 32), Image.Resampling.LANCZOS)
                    faction_images["Enlightened"] = enlightened_img
                
                if resistance_path.exists():
                    resistance_img = Image.open(resistance_path).convert("RGBA")
                    resistance_img = resistance_img.resize((32, 32), Image.Resampling.LANCZOS)
                    faction_images["Resistance"] = resistance_img
                    
            except Exception as e:
                logger.error(f"Error loading faction images: {e}")
            
            # Draw header
            header_text = f"🏆 {title} ({time_desc})"
            draw.text((padding, padding), header_text, fill=(0, 0, 0), font=self.header_font)
            
            # Draw leaderboard entries
            y_pos = header_height + padding
            
            for i, (agent_name, agent_faction, value, submission_date) in enumerate(leaderboard_data, 1):
                # Medal emoji
                medal = ""
                if i == 1:
                    medal = "🥇"
                elif i == 2:
                    medal = "🥈"
                elif i == 3:
                    medal = "🥉"
                else:
                    medal = f"{i}."
                
                # Format value
                formatted_value = self._format_number(int(value)) if value else "0"
                
                # Draw medal
                x_pos = padding
                draw.text((x_pos, y_pos), medal, fill=(0, 0, 0), font=self.entry_font)
                x_pos += 60
                
                # Draw faction icon
                if agent_faction in faction_images:
                    faction_img = faction_images[agent_faction]
                    # Paste faction image with transparency
                    img.paste(faction_img, (x_pos, y_pos + 4), faction_img)
                    x_pos += 40
                else:
                    # Fallback to emoji
                    emoji = "🟢" if agent_faction == "Enlightened" else "🔵"
                    draw.text((x_pos, y_pos), emoji, fill=(0, 0, 0), font=self.entry_font)
                    x_pos += 40
                
                # Draw value and agent name
                entry_text = f"{formatted_value} @{agent_name}"
                draw.text((x_pos, y_pos), entry_text, fill=(0, 0, 0), font=self.entry_font)
                
                y_pos += line_height
            
            # Draw footer
            footer_text = f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            draw.text((padding, y_pos + 10), footer_text, fill=(128, 128, 128), font=self.small_font)
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return img_bytes
            
        except Exception as e:
            logger.error(f"Error generating text leaderboard with faction icons: {e}")
            return self._generate_error_image()

    def _format_number(self, num: int) -> str:
        """Format number with appropriate suffixes"""
        if num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.1f}K"
        else:
            return str(num)