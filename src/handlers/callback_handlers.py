"""
Callback handlers for the Ingress Leaderboard Bot
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from config.settings import KEY_ELEMENTS, TIME_SLOTS

logger = logging.getLogger(__name__)

class CallbackHandlers:
    def __init__(self, db_manager, leaderboard_manager, data_parser):
        self.db = db_manager
        self.leaderboard = leaderboard_manager
        self.parser = data_parser
        self.user_selections = {}  # Store user selections temporarily
    
    async def handle_callback_query(self, update: Update, context: CallbackContext):
        """Handle inline keyboard callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        
        # Initialize user selection if not exists
        if user_id not in self.user_selections:
            self.user_selections[user_id] = {'time_slot': 'all_time', 'faction': None}
        
        if data.startswith('key_element_'):
            # Key element selection
            element_key = data.replace('key_element_', '').replace('_', ' ')
            
            # Find the matching key element
            selected_element = None
            for key, element_info in KEY_ELEMENTS.items():
                if key.replace('🔸', '').strip() == element_key:
                    selected_element = element_info
                    break
            
            if selected_element:
                # Get user's current time selection
                time_slot = self.user_selections[user_id].get('time_slot', 'all_time')
                faction = self.user_selections[user_id].get('faction', None)
                
                # Generate leaderboard text and image with faction icons
                leaderboard_text = self.leaderboard.generate_leaderboard(
                    selected_element['stat_name'], time_slot, faction
                )
                
                # Create back button
                back_keyboard = [[
                    InlineKeyboardButton("🔙 Back to Selection", callback_data="back_to_selection")
                ]]
                reply_markup = InlineKeyboardMarkup(back_keyboard)
                
                # Send as image with faction icons inline
                try:
                    leaderboard_image = self.leaderboard.generate_leaderboard_image(
                        selected_element['stat_name'], time_slot, faction
                    )
                    
                    # Delete the original message and send new photo message
                    await query.delete_message()
                    await context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=leaderboard_image,
                        caption="🏆 Leaderboard with Faction Icons",
                        reply_markup=reply_markup
                    )
                except Exception as e:
                    logger.error(f"Error sending leaderboard image: {e}")
                    # Fallback to text-only
                    await query.edit_message_text(
                        leaderboard_text, 
                        parse_mode='Markdown',
                        reply_markup=reply_markup
                    )
        
        elif data.startswith('time_'):
            # Time slot selection
            time_slot = data.replace('time_', '')
            self.user_selections[user_id]['time_slot'] = time_slot
            
            # Update the message to show time selection feedback
            time_display = time_slot.replace('_', ' ').title()
            await query.edit_message_text(
                f"⏰ **Time frame selected: {time_display}**\n\n"
                "Now select a key element to view the leaderboard:",
                reply_markup=self._create_key_element_keyboard(),
                parse_mode='Markdown'
            )
        
        elif data == 'back_to_selection':
            # Back to key element selection
            await query.edit_message_text(
                """🏆 **Ingress Leaderboard**

Select a key element to view the leaderboard:""",
                reply_markup=self._create_key_element_keyboard(),
                parse_mode='Markdown'
            )
        
        elif data.startswith('lb_'):
            # Legacy leaderboard callback (for backward compatibility)
            parts = data.split('_')
            if len(parts) >= 4:
                stat = parts[1].replace('_', ' ').title()
                time_slot = parts[2]
                faction = parts[3] if parts[3] != 'all' else None
                
                # Generate leaderboard text with custom faction stickers
                leaderboard_text = self.leaderboard.generate_leaderboard(stat, time_slot, faction)
                await query.edit_message_text(leaderboard_text, parse_mode='Markdown')
        
        return
    
    def _create_key_element_keyboard(self):
        """Create keyboard with key elements"""
        keyboard = []
        key_elements = list(KEY_ELEMENTS.keys())
        
        for i in range(0, len(key_elements), 3):
            row = []
            for j in range(3):
                if i + j < len(key_elements):
                    key = key_elements[i + j]
                    element_info = KEY_ELEMENTS[key]
                    button_text = element_info['display_name']
                    callback_data = f"key_element_{key.replace('🔸', '').replace(' ', '_')}"
                    row.append(InlineKeyboardButton(button_text, callback_data=callback_data))
            keyboard.append(row)
        
        # Add time frame selection row
        time_row = [
            InlineKeyboardButton("📅 All Time", callback_data="time_all_time"),
            InlineKeyboardButton("📅 Monthly", callback_data="time_monthly"),
            InlineKeyboardButton("📅 Weekly", callback_data="time_weekly")
        ]
        keyboard.append(time_row)
        
        return InlineKeyboardMarkup(keyboard)