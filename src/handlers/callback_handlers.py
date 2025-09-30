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
                    [InlineKeyboardButton("📊 Submit Stats", callback_data="nav_submit"),
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
            else:
                # Handle case when no matching key element is found
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="❌ **Unknown key element selected**\n\n_Please try selecting a different option._",
                    reply_markup=self._create_key_element_keyboard(),
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
                reply_markup = self._create_navigation_buttons(context_type="leaderboard")
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
    
    def _create_navigation_buttons(self, context_type="minimal"):
        """Create contextual navigation buttons for callback handlers"""
        buttons = []
        
        # Define context-specific button sets
        context_buttons = {
            "welcome": [
                ("📊 Submit Stats", "nav_submit"),
                ("🏆 Leaderboard", "nav_leaderboard"),
                ("❓ Help", "nav_help")
            ],
            "success": [
                ("🏆 View Leaderboard", "nav_leaderboard"),
                ("⚔️ Faction Stats", "nav_factions"),
                ("📊 Submit More", "nav_submit")
            ],
            "error": [
                ("🔄 Try Again", "nav_submit"),
                ("❓ Help", "nav_help")
            ],
            "leaderboard": [
                ("⚔️ Faction Comparison", "nav_factions"),
                ("📈 Progress", "nav_progress"),
                ("📊 Submit Stats", "nav_submit")
            ],
            "help": [
                ("📊 Submit Stats", "nav_submit"),
                ("🏆 Leaderboard", "nav_leaderboard"),
                ("🛠 All Commands", "nav_commands")
            ],
            "minimal": [
                ("📊 Submit Stats", "nav_submit"),
                ("🏆 Leaderboard", "nav_leaderboard")
            ],
            "data_processing": [
                ("🏆 View Results", "nav_leaderboard"),
                ("❓ Help", "nav_help")
            ],
            "data_help": [
                ("📊 Try Submit", "nav_submit"),
                ("❓ More Help", "nav_help")
            ]
        }
        
        # Get buttons for the specified context, fallback to minimal
        nav_buttons = context_buttons.get(context_type, context_buttons["minimal"])
        
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
        """Auto-delete the previous menu message for cleaner UX"""
        try:
            # Delete the previous menu message instead of editing it
            await query.delete_message()
        except Exception as e:
            # Silently handle cases where message can't be deleted (e.g., too old, already deleted)
            logger.debug(f"Could not delete previous menu: {e}")
    
    async def _handle_navigation_callback(self, query, data, context):
        """Handle navigation button callbacks"""
        user_id = query.from_user.id
        
        try:
            if data == 'nav_submit':
                # Set user state for data submission and show detailed instructions
                context.user_data['state'] = 'awaiting_data'
                
                submit_text = """📊 **Ready to submit your stats!**

🎯 **Quick Guide:**
**Step 1:** Open Ingress → Agent → Statistics
**Step 2:** Copy ALL your statistics and paste them here
**Step 3:** I'll automatically process and add them to leaderboards

**That's it!** ✨ _The bot handles the rest automatically._

⚠️ **In groups: REPLY to this message when pasting your stats!**

❌ Send `/cancel` to cancel anytime."""

                # Create action buttons for submission
                submit_keyboard = [
                    [InlineKeyboardButton("❓ Need Help?", callback_data="nav_help"),
                     InlineKeyboardButton("❌ Cancel", callback_data="nav_cancel_submit")],
                    [InlineKeyboardButton("🏘 HOME", callback_data="nav_main_menu")]
                ]
                submit_reply_markup = InlineKeyboardMarkup(submit_keyboard)
                
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=submit_text,
                    reply_markup=submit_reply_markup,
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
                user_id = query.from_user.id
                
                # Check if user has any agents registered
                user_agents = self.db.get_agents_by_user_id(user_id)
                
                if not user_agents:
                    # No agents found - guide user to submit data first
                    progress_keyboard = [
                        [InlineKeyboardButton("📊 Submit Data First", callback_data="nav_submit"),
                         InlineKeyboardButton("❓ Help", callback_data="nav_help")],
                        [InlineKeyboardButton("🏘 HOME", callback_data="nav_main_menu")]
                    ]
                    progress_reply_markup = InlineKeyboardMarkup(progress_keyboard)
                    
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text="""📈 **Progress Tracking**

⚠️ **No agents found!** You need to submit your statistics first.

**Quick Start:**
1. Click "📊 Submit Data First" below
2. Copy your stats from Ingress
3. Paste them here
4. Then you can track your progress!""",
                        reply_markup=progress_reply_markup,
                        parse_mode='Markdown'
                    )
                else:
                    # User has agents - show their progress for Current AP
                    agent_name = user_agents[0][0]
                    stat = "Current AP"
                    days = 30
                    
                    progress_text = self.leaderboard.generate_agent_progress(agent_name, user_id, stat, days)
                    
                    # Add additional info if user has multiple agents
                    if len(user_agents) > 1:
                        other_agents = [agent for agent, faction in user_agents if agent != agent_name]
                        progress_text += f"\n\n💡 **Other agents:** _{', '.join(other_agents)}_"
                    
                    progress_text += f"\n\n⏰ **_This message will self-delete in 30 seconds_**"
                    
                    progress_keyboard = [
                        [InlineKeyboardButton("📊 Submit New Data", callback_data="nav_submit"),
                         InlineKeyboardButton("🏆 View Leaderboard", callback_data="nav_leaderboard")],
                        [InlineKeyboardButton("🏘 HOME", callback_data="nav_main_menu")]
                    ]
                    progress_reply_markup = InlineKeyboardMarkup(progress_keyboard)
                    
                    # Send progress message
                    sent_message = await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text=progress_text,
                        parse_mode='Markdown'
                    )
                    
                    # Schedule auto-deletion after 30 seconds
                    import asyncio
                    asyncio.create_task(self._auto_delete_progress_message(context, query.message.chat_id, sent_message, progress_reply_markup))
            
            elif data == 'nav_factions':
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="""⚔️ **Faction Comparison**

Compare Enlightened vs Resistance performance across all statistics.

**Time Frames:** All Time, Monthly, Weekly""",
                    reply_markup=self._create_navigation_buttons(context_type="leaderboard"),
                    parse_mode='Markdown'
                )
            
            elif data == 'nav_commands':
                # Show all available bot commands
                from config.settings import BOT_COMMANDS
                
                # Escape underscores in command names to prevent Markdown parsing issues
                command_lines = [
                    f"/{cmd['command'].replace('_', '\\_')} - {cmd['description']}"
                    for cmd in BOT_COMMANDS
                ]

                commands_text = """🛠 **Bot Commands Overview**

""" + "\n".join(command_lines)

                try:
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text=commands_text,
                        reply_markup=self._create_navigation_buttons(context_type="help"),
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Error sending commands list with Markdown: {e}")
                    # Fallback: send without Markdown parsing
                    try:
                        # Remove markdown formatting for fallback
                        fallback_text = commands_text.replace('**', '').replace('\\_', '_')
                        await context.bot.send_message(
                            chat_id=query.message.chat_id,
                            text=fallback_text,
                            reply_markup=self._create_navigation_buttons(context_type="help")
                        )
                    except Exception as fallback_error:
                        logger.error(f"Error sending commands list fallback: {fallback_error}")
                        await context.bot.send_message(
                            chat_id=query.message.chat_id,
                            text="❌ Error displaying commands list. Please try again.",
                            reply_markup=self._create_navigation_buttons(context_type="error")
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
                    reply_markup=self._create_navigation_buttons(context_type="help"),
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
                    reply_markup=self._create_navigation_buttons(context_type="help"),
                    parse_mode='Markdown'
                )
            
            elif data == 'nav_help_detailed':
                # Show the comprehensive detailed help from parser
                detailed_help_text = self.parser.get_detailed_help()
                
                help_keyboard = [
                    [InlineKeyboardButton("📊 Submit Now", callback_data="nav_submit"),
                     InlineKeyboardButton("🏆 Leaderboard", callback_data="nav_leaderboard")],
                    [InlineKeyboardButton("🔙 Back to Simple Help", callback_data="nav_help")]
                ]
                help_reply_markup = InlineKeyboardMarkup(help_keyboard)
                
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=detailed_help_text,
                    reply_markup=help_reply_markup,
                    parse_mode='Markdown'
                )
            
            elif data == 'nav_cancel_submit':
                # Cancel submission state
                context.user_data.pop('state', None)
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="❌ **Submission cancelled.**",
                    reply_markup=self._create_navigation_buttons(),
                    parse_mode='Markdown'
                )
            
            elif data == 'nav_main_menu':
                # Show main menu
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="""🏠 **Main Menu**

**Choose an option:**""",
                    reply_markup=self._create_navigation_buttons(),
                    parse_mode='Markdown'
                )
            
            elif data.startswith('factions_'):
                # Handle faction time frame selection
                time_slot = data.replace('factions_', '')
                comparison_text = self.leaderboard.generate_faction_comparison(time_slot)
                
                faction_keyboard = [
                    [InlineKeyboardButton("🔄 Change Time Frame", callback_data="nav_factions"),
                     InlineKeyboardButton("🏆 View Leaderboard", callback_data="nav_leaderboard")],
                    [InlineKeyboardButton("🏘 HOME", callback_data="nav_main_menu")]
                ]
                faction_reply_markup = InlineKeyboardMarkup(faction_keyboard)
                
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=comparison_text,
                    reply_markup=faction_reply_markup,
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