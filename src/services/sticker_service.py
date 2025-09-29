"""
Sticker management service for creating and managing faction stickers
"""

import logging
from typing import Optional, Dict
from pathlib import Path
from PIL import Image
import io
import asyncio

from config.settings import PROJECT_ROOT

logger = logging.getLogger(__name__)

class StickerManager:
    def __init__(self):
        self.sticker_set_name = "ingress_factions_by_h1ght0wer_bot"  # Must end with _by_<bot_username>
        self.sticker_set_title = "Ingress Factions by H1GHT0WER"
        
        # Faction emoji mapping (no longer using assets)
        self.faction_emojis = {
            "Enlightened": "💚",
            "Resistance": "💙"
        }
    
    def prepare_emoji_image(self, image_path: Path, output_path: Path, size: tuple = (100, 100)) -> bool:
        """
        Prepare an image for use as a custom emoji
        Requirements:
        - Format: PNG with transparency
        - Size: 100x100 pixels (optimal for emoji)
        - File size: max 256KB
        """
        try:
            if not image_path.exists():
                logger.error(f"Source image not found: {image_path}")
                return False
            
            # Open and process image
            with Image.open(image_path) as img:
                # Convert to RGBA for transparency support
                img = img.convert("RGBA")
                
                # Resize to emoji size while maintaining aspect ratio
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Create a new image with the exact size and transparent background
                emoji_img = Image.new("RGBA", size, (0, 0, 0, 0))
                
                # Center the resized image
                x = (size[0] - img.width) // 2
                y = (size[1] - img.height) // 2
                emoji_img.paste(img, (x, y), img if img.mode == 'RGBA' else None)
                
                # Save as PNG
                emoji_img.save(output_path, "PNG", optimize=True)
                
                # Check file size
                file_size = output_path.stat().st_size
                if file_size > 256 * 1024:  # 256KB limit for emoji
                    logger.warning(f"Emoji image {output_path} is {file_size} bytes (over 256KB limit)")
                    return False
                
                logger.info(f"Prepared emoji image: {output_path} ({file_size} bytes)")
                return True
                
        except Exception as e:
            logger.error(f"Error preparing emoji image {image_path}: {e}")
            return False

    def prepare_sticker_image(self, image_path: Path, output_path: Path) -> bool:
        """
        Prepare an image for use as a Telegram sticker
        Requirements:
        - Format: PNG or WEBP
        - Size: 512x512 pixels max, one side must be exactly 512px
        - File size: max 500KB
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGBA if not already
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Calculate new size (one side must be 512px, maintain aspect ratio)
                width, height = img.size
                if width > height:
                    new_width = 512
                    new_height = int((height * 512) / width)
                else:
                    new_height = 512
                    new_width = int((width * 512) / height)
                
                # Resize image
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Save as PNG for stickers
                img.save(output_path, 'PNG', optimize=True)
                
                # Check file size
                if output_path.stat().st_size > 500 * 1024:  # 500KB
                    logger.warning(f"Sticker file {output_path} is larger than 500KB")
                    return False
                
                logger.info(f"Prepared sticker: {output_path} ({new_width}x{new_height})")
                return True
                
        except Exception as e:
            logger.error(f"Error preparing sticker image {image_path}: {e}")
            return False
    
    def prepare_all_faction_stickers(self) -> Dict[str, Path]:
        """
        No longer preparing faction stickers from assets.
        Returns empty dict since we now use heart emojis directly.
        """
        logger.info("Faction stickers no longer needed - using heart emojis (💚💙)")
        return {}
    
    def prepare_all_faction_emoji(self) -> Dict[str, Path]:
        """
        No longer preparing faction emoji from assets.
        Returns empty dict since we now use heart emojis directly.
        """
        logger.info("Faction emoji no longer needed - using heart emojis (💚💙)")
        return {}
    
    async def create_custom_emoji_set(self, bot, user_id: int) -> bool:
        """
        Create custom emoji from faction images
        Custom emoji can be used inline in text messages
        """
        try:
            # Prepare emoji images (custom emoji requirements are similar to stickers)
            prepared_emojis = self.prepare_all_faction_stickers()
            
            if not prepared_emojis:
                logger.error("No emoji images prepared, cannot create custom emoji set")
                return False
            
            # Upload custom emoji (this requires bot to be admin in a chat/channel)
            # Note: Custom emoji creation requires special permissions
            for faction, image_path in prepared_emojis.items():
                try:
                    with open(image_path, 'rb') as emoji_file:
                        # Upload as custom emoji
                        # This is a placeholder - actual implementation depends on bot permissions
                        logger.info(f"Would upload {faction} custom emoji from {image_path}")
                        
                except Exception as e:
                    logger.error(f"Error uploading {faction} custom emoji: {e}")
            
            logger.info("Custom emoji set creation completed")
            return True
            
        except Exception as e:
            logger.error(f"Error creating custom emoji set: {e}")
            return False

    async def create_sticker_set(self, bot, user_id: int) -> bool:
        """
        Create a sticker set with faction stickers
        Note: This requires the bot to have the user_id of an admin/creator
        """
        try:
            # Prepare sticker images
            prepared_stickers = self.prepare_all_faction_stickers()
            
            if not prepared_stickers:
                logger.error("No stickers prepared, cannot create sticker set")
                return False
            
            # Check if sticker set already exists
            try:
                existing_set = await bot.get_sticker_set(self.sticker_set_name)
                logger.info(f"Sticker set {self.sticker_set_name} already exists")
                return True
            except Exception:
                # Sticker set doesn't exist, we'll create it
                pass
            
            # Create sticker set with first sticker
            first_faction = list(prepared_stickers.keys())[0]
            first_sticker_path = prepared_stickers[first_faction]
            first_sticker_name = self.faction_stickers[first_faction]
            
            with open(first_sticker_path, 'rb') as sticker_file:
                success = await bot.create_new_sticker_set(
                    user_id=user_id,
                    name=self.sticker_set_name,
                    title=self.sticker_set_title,
                    png_sticker=sticker_file,
                    emojis="💚" if first_faction == "Enlightened" else "💙"
                )
            
            if not success:
                logger.error("Failed to create sticker set")
                return False
            
            # Add remaining stickers to the set
            for faction, sticker_path in prepared_stickers.items():
                if faction == first_faction:
                    continue  # Already added
                
                sticker_name = self.faction_stickers[faction]
                emoji = "💚" if faction == "Enlightened" else "💙"
                
                with open(sticker_path, 'rb') as sticker_file:
                    await bot.add_sticker_to_set(
                        user_id=user_id,
                        name=self.sticker_set_name,
                        png_sticker=sticker_file,
                        emojis=emoji
                    )
                
                logger.info(f"Added {faction} sticker to set")
            
            logger.info(f"Successfully created sticker set: {self.sticker_set_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating sticker set: {e}")
            return False
    
    def get_faction_sticker_emoji(self, faction: str) -> str:
        """
        Get the faction representation for text
        Returns heart emoji for the faction
        """
        return self.faction_emojis.get(faction, "⚪")
    
    def get_faction_emoji_fallback(self, faction: str) -> str:
        """
        Get emoji fallback for factions
        """
        return self.faction_emojis.get(faction, "⚪")
    
    def get_sticker_set_link(self) -> str:
        """Get the link to the sticker set"""
        return f"https://t.me/addstickers/{self.sticker_set_name}"
    
    async def send_faction_sticker(self, bot, chat_id: int, faction: str) -> bool:
        """Send a faction sticker to a chat"""
        try:
            # Try to get the sticker from our set
            sticker_set = await bot.get_sticker_set(self.sticker_set_name)
            
            # Find the appropriate sticker
            for sticker in sticker_set.stickers:
                # Match by emoji or position
                if faction == "Enlightened" and "💚" in sticker.emoji:
                    await bot.send_sticker(chat_id=chat_id, sticker=sticker.file_id)
                    return True
                elif faction == "Resistance" and "💙" in sticker.emoji:
                    await bot.send_sticker(chat_id=chat_id, sticker=sticker.file_id)
                    return True
            
            logger.warning(f"No sticker found for faction: {faction}")
            return False
            
        except Exception as e:
            logger.error(f"Error sending faction sticker: {e}")
            return False