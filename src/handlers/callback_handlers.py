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
        
        # Disable the previous menu first
        await self._disable_previous_menu(query)
        
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
                
                # Create back button with navigation
                keyboard = [
                    [InlineKeyboardButton("🔙 Back to Selection", callback_data="back_to_selection")],
                    [InlineKeyboardButton("📊 Submit", callback_data="nav_submit"),
                     InlineKeyboardButton("📈 Progress", callback_data="nav_progress"),
                     InlineKeyboardButton("⚔️ Factions", callback_data="nav_factions")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                # Send as new text-based message
                try:
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text=leaderboard_text,
                        parse_mode='Markdown',
                        reply_markup=reply_markup
                    )
                except Exception as e:
                    logger.error(f"Error sending leaderboard text: {e}")
                    # Fallback message if sending fails
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text="❌ Error displaying leaderboard. Please try again.",
                        parse_mode='Markdown'
                    )
        
        elif data.startswith('time_'):
            # Time slot selection
            time_slot = data.replace('time_', '')
            self.user_selections[user_id]['time_slot'] = time_slot
            
            # Send new message to show time selection feedback
            time_display = time_slot.replace('_', ' ').title()
            try:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=f"⏰ **Time frame selected:** __{time_display}__\n\n"
                         "_Now select a key element to view the leaderboard:_",
                    reply_markup=self._create_key_element_keyboard(),
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Error sending time selection: {e}")
        
        elif data == 'back_to_selection':
            # Back to key element selection - send new message
            try:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="""🏆 **Ingress Leaderboard**

_Select a key element to view the leaderboard:_""",
                    reply_markup=self._create_key_element_keyboard(),
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Error sending back to selection: {e}")
        
        elif data.startswith('nav_'):
            # Handle navigation buttons - pass context for new messages
            await self._handle_navigation_callback(query, data, context)
        
        elif data.startswith('lb_'):
            # Legacy leaderboard callback (for backward compatibility)
            parts = data.split('_')
            if len(parts) >= 4:
                stat = parts[1].replace('_', ' ').title()
                time_slot = parts[2]
                faction = parts[3] if parts[3] != 'all' else None
                
                # Generate leaderboard text with custom faction stickers - send new message
                leaderboard_text = self.leaderboard.generate_leaderboard(stat, time_slot, faction)
                reply_markup = self._create_navigation_buttons()
                try:
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text=leaderboard_text, 
                        reply_markup=reply_markup, 
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Error sending legacy leaderboard: {e}")
        
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
    
    def _create_navigation_buttons(self):
        """Create navigation buttons for callback handlers"""
        buttons = []
        
        # Main navigation buttons
        nav_buttons = [
            ("📊 Submit", "nav_submit"),
            ("🏆 Leaderboard", "nav_leaderboard"), 
            ("📈 Progress", "nav_progress"),
            ("⚔️ Factions", "nav_factions"),
            ("❓ Help", "nav_help")
        ]
        
        # Create rows of 2-3 buttons each for better mobile display
        row = []
        for text, callback_data in nav_buttons:
            row.append(InlineKeyboardButton(text, callback_data=callback_data))
            if len(row) == 2:
                buttons.append(row)
                row = []
        
        # Add remaining buttons if any
        if row:
            buttons.append(row)
        
        return InlineKeyboardMarkup(buttons)
    
    async def _disable_previous_menu(self, query):
        """Disable the previous menu by editing it to show 'send a new request'"""
        try:
            disabled_text = "🔒 **Menu disabled** - _Send a new request_"
            await query.edit_message_text(
                text=disabled_text,
                reply_markup=None,  # Remove the keyboard
                parse_mode='Markdown'
            )
        except Exception as e:
            # Silently handle cases where message can't be edited (e.g., too old)
            logger.debug(f"Could not disable previous menu: {e}")
    
    async def _handle_navigation_callback(self, query, data, context):
        """Handle navigation button callbacks"""
        user_id = query.from_user.id
        
        try:
            if data == 'nav_submit':
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="""📊 **Ready to submit your stats!**

Copy your statistics from Ingress _(Agent → Statistics)_ and paste them as a message.

**Next:** Send your copied statistics data.""",
                    reply_markup=self._create_navigation_buttons(),
                    parse_mode='Markdown'
                )
            
            elif data == 'nav_leaderboard':
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="""🏆 **Ingress Leaderboard**

_Select a key element to view the leaderboard:_""",
                    reply_markup=self._create_key_element_keyboard(),
                    parse_mode='Markdown'
                )
            
            elif data == 'nav_progress':
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="""📈 **Progress Tracking**

Track your improvement over time! If you have submitted stats before, you can see your progress.

**Usage:** Send your latest stats to see progress.""",
                    reply_markup=self._create_navigation_buttons(),
                    parse_mode='Markdown'
                )
            
            elif data == 'nav_factions':
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="""⚔️ **Faction Comparison**

Compare Enlightened vs Resistance performance across all statistics.

**Time Frames:** All Time, Monthly, Weekly""",
                    reply_markup=self._create_navigation_buttons(),
                    parse_mode='Markdown'
                )
            
            elif data == 'nav_help':
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="""❓ **Quick Help**

📊 **Data Format:**
Copy exactly from Ingress → Agent → Statistics

**Example:**
```
Agent Name: YourAgentName
Faction: Enlightened/Resistance
Current AP: 12,345,678
```

**Supported:** All Ingress statistics are supported!""",
                    reply_markup=self._create_navigation_buttons(),
                    parse_mode='Markdown'
                )
            
            elif data == 'nav_stats':
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="""📊 **Available Statistics**

All Ingress statistics are supported including:
• Current AP
• Distance Walked
• Portals Discovered
• And many more!

**Time Frames:** All Time, Monthly (30 days), Weekly (7 days)""",
                    reply_markup=self._create_navigation_buttons(),
                    parse_mode='Markdown'
                )
        except Exception as e:
            # Handle "Message is not modified" and other edit errors gracefully
            if "Message is not modified" in str(e):
                logger.debug(f"Message not modified for user {user_id}: {data}")
                # Silently ignore - user clicked the same button they're already viewing
                pass
            else:
                logger.error(f"Error handling navigation callback {data}: {e}")
                # Try to answer the callback to prevent the loading animation
                try:
                    await query.answer("⚠️ Something went wrong. Please try again.")
                except:
                    pass