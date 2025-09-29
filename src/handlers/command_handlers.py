"""
Command handlers for the Ingress Leaderboard Bot
"""

import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from config.settings import LEADERBOARD_STATS, TIME_SLOTS, KEY_ELEMENTS
from ..services import LeaderboardManager
from ..parsers import DataParser

logger = logging.getLogger(__name__)

class CommandHandlers:
    def __init__(self, db_manager, leaderboard_manager, data_parser):
        self.db = db_manager
        self.leaderboard = leaderboard_manager
        self.parser = data_parser
    
    async def start_command(self, update: Update, context: CallbackContext):
        """Handle /start command"""
        user = update.effective_user
        user_first_name = user.first_name or "Agent"
        welcome_text = f"""👋 **Welcome {user_first_name}!** 

🎯 **Ingress Leaderboard Bot** - _Track & compare your Ingress stats!_

🚀 **Quick Start:**
1. Copy stats from Ingress _(Agent → Statistics)_
2. Tap "📊 Submit" below and paste
3. View rankings with "🏆 Leaderboard"

Ready to see where you rank? 🏆"""
        
        reply_markup = self._create_navigation_buttons()
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
        return
    
    async def help_command(self, update: Update, context: CallbackContext):
        """Handle /help command - show quick help"""
        help_text = self.parser.get_quick_help()
        reply_markup = self._create_navigation_buttons(exclude_current="nav_help")
        await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')
        return
    
    async def help_detailed_command(self, update: Update, context: CallbackContext):
        """Handle /help_detailed command - show comprehensive help"""
        help_text = self.parser.get_detailed_help()
        reply_markup = self._create_navigation_buttons(exclude_current="nav_help")
        await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')
        return
    
    async def submit_command(self, update: Update, context: CallbackContext):
        """Handle /submit command"""
        user_id = update.effective_user.id
        
        # Check if data was provided with the command
        if context.args:
            # Data provided with command, process it directly
            data_text = " ".join(context.args)
            await self._process_submission_data(update, context, data_text)
            return
        
        # No data provided, set state and show prompt
        context.user_data['state'] = 'awaiting_data'
        
        submit_text = f"""📊 **Ready to submit your stats!**

{self.parser.get_quick_help()}

**Next:** Paste your copied statistics data here.

❌ Send `/cancel` to cancel."""
        
        reply_markup = self._create_navigation_buttons(exclude_current="nav_submit")
        await update.message.reply_text(submit_text, reply_markup=reply_markup, parse_mode='Markdown')
        return
    
    async def _process_submission_data(self, update: Update, context: CallbackContext, data_text: str):
        """Process submitted Ingress data with improved error handling"""
        user_id = update.effective_user.id
        
        try:
            # Parse the data using the improved multiline parser
            parsed_data_list, parse_errors = self.parser.parse_multiline_data(data_text)
            
            # If there are parse errors, show them to the user
            if parse_errors and not parsed_data_list:
                # Show the first (most relevant) error with helpful guidance
                error_message = parse_errors[0].user_message
                if len(parse_errors) > 1:
                    error_message += f"\n\n📝 **Found {len(parse_errors)} issues total.** Fix this one first."
                
                error_message += f"\n\n{self.parser.get_quick_help()}"
                
                keyboard = [
                    [InlineKeyboardButton("🔄 Try Again", callback_data="nav_submit"),
                     InlineKeyboardButton("❓ Help", callback_data="nav_help")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(error_message, reply_markup=reply_markup, parse_mode='Markdown')
                return
            
            # If some lines had errors but we got some valid data, show warnings
            if parse_errors and parsed_data_list:
                warning_msg = f"⚠️ **Processed {len(parsed_data_list)} submissions, but found issues:**\n\n"
                for error in parse_errors[:2]:  # Show first 2 errors
                    warning_msg += f"• {error.user_message}\n"
                if len(parse_errors) > 2:
                    warning_msg += f"• _...and {len(parse_errors)-2} more issues_\n"
                
                keyboard = [
                    [InlineKeyboardButton("🔄 Try Again", callback_data="nav_submit"),
                     InlineKeyboardButton("❓ Help", callback_data="nav_help")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(warning_msg, reply_markup=reply_markup, parse_mode='Markdown')
            
            if not parsed_data_list:
                keyboard = [
                    [InlineKeyboardButton("🔄 Try Again", callback_data="nav_submit"),
                     InlineKeyboardButton("❓ Help", callback_data="nav_help")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    "❌ **No valid data processed**\n\n" + 
                    self.parser.get_quick_help(),
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                return
            
            # Process each valid parsed data entry
            success_count = 0
            for parsed_data in parsed_data_list:
                # Note: Faction validation is now handled in the parser with better error messages

                try:
                    # Add agent to database
                    agent_id = self.db.add_agent(
                        parsed_data['agent_name'],
                        parsed_data['faction'],
                        user_id
                    )

                    # Add submission
                    success = self.db.add_submission(agent_id, parsed_data)

                    if success:
                        success_count += 1
                        faction_emoji = "💚" if parsed_data['faction'].lower() == 'enlightened' else "💙"
                        success_text = f"""🎉 **Stats submitted!**

{faction_emoji} **{parsed_data['agent_name']}** _({parsed_data['faction']})_
📅 {parsed_data['data_date']} at {parsed_data['data_time']}
📊 Level **{parsed_data['level']}** • ⚡ **{self.parser.format_number(parsed_data['current_ap'])}** AP

__Great work, Agent!__ 💪"""
                        
                        reply_markup = self._create_navigation_buttons(exclude_current="nav_submit")
                        await update.message.reply_text(success_text, reply_markup=reply_markup, parse_mode='Markdown')
                    else:
                        keyboard = [
                            [InlineKeyboardButton("🔄 Try Again", callback_data="nav_submit"),
                             InlineKeyboardButton("❓ Help", callback_data="nav_help")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await update.message.reply_text(
                            f"❌ **Failed to save data for {parsed_data['agent_name']}**\n\n"
                            "_Temporary issue. Data was parsed correctly._",
                            reply_markup=reply_markup,
                            parse_mode='Markdown'
                        )
                
                except Exception as db_error:
                    logger.error(f"Database error for agent {parsed_data.get('agent_name', 'Unknown')}: {db_error}")
                    keyboard = [
                        [InlineKeyboardButton("🔄 Try Again", callback_data="nav_submit"),
                         InlineKeyboardButton("❓ Help", callback_data="nav_help")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text(
                        f"❌ **Database error for {parsed_data.get('agent_name', 'your agent')}**\n\n"
                        "_Could be temporary issue or duplicate data._",
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )

            # Show summary if multiple submissions were processed
            if len(parsed_data_list) > 1:
                total_processed = len(parsed_data_list)
                summary_msg = f"📊 **Submission Summary**\n\n"
                summary_msg += f"✅ Successfully processed: **{success_count}** out of **{total_processed}** submissions"
                
                if success_count == total_processed:
                    summary_msg += "\n\n🎉 _All your data has been added to the leaderboards!_"
                elif success_count > 0:
                    summary_msg += f"\n\n⚠️ **{total_processed - success_count}** submissions had issues _(see messages above)_"
                else:
                    summary_msg += "\n\n❌ _None of the submissions could be processed successfully_"
                
                reply_markup = self._create_navigation_buttons(exclude_current="nav_submit")
                await update.message.reply_text(summary_msg, reply_markup=reply_markup, parse_mode='Markdown')

            # Clear user state if it was set
            context.user_data.pop('state', None)
                
        except Exception as e:
            logger.error(f"Unexpected error processing data submission: {e}")
            keyboard = [
                [InlineKeyboardButton("🔄 Try Again", callback_data="nav_submit"),
                 InlineKeyboardButton("❓ Help", callback_data="nav_help")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "❌ **Unexpected error occurred**\n\n"
                "_Something went wrong. Check data format or try again._",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def leaderboard_command(self, update: Update, context: CallbackContext):
        """Handle /leaderboard command with enhanced UI buttons"""
        args = context.args
        
        # If no arguments provided, show key element buttons
        if not args:
            await self._show_key_element_buttons(update, context)
            return
        
        # Parse arguments for direct command usage
        stat = None
        time_slot = "all_time"
        faction = None
        
        # Check if first argument is a key element
        first_arg = " ".join(args).strip()
        key_element_found = None
        
        for key, element_info in KEY_ELEMENTS.items():
            if (first_arg.lower() == element_info['display_name'].lower() or 
                first_arg.lower() == element_info['description'].lower() or
                first_arg.lower() == key.lower().replace('🔸', '')):
                stat = element_info['stat_name']
                key_element_found = key
                break
        
        # If not a key element, try traditional parsing
        if not stat:
            if len(args) >= 1:
                stat = " ".join(args[0].split("_")).title()
            if len(args) >= 2:
                time_slot = args[1].lower()
            if len(args) >= 3:
                faction = args[2].title()
        
        # Validate stat
        if not stat or stat not in LEADERBOARD_STATS:
            # Show key element buttons if stat is invalid
            await self._show_key_element_buttons(update, context, 
                f"❌ Invalid statistic: '{first_arg}'\n\nPlease select from the available options:")
            return
        
        # Validate other inputs
        if time_slot not in TIME_SLOTS:
            time_slot = "all_time"
        
        if faction and faction not in ["Enlightened", "Resistance"]:
            faction = None
        
        # Generate leaderboard as text-based message
        try:
            leaderboard_text = self.leaderboard.generate_leaderboard(stat, time_slot, faction)
            reply_markup = self._create_navigation_buttons(exclude_current="nav_leaderboard")
            await update.message.reply_text(leaderboard_text, reply_markup=reply_markup, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error generating leaderboard: {e}")
            keyboard = [
                [InlineKeyboardButton("🔄 Try Again", callback_data="nav_leaderboard"),
                 InlineKeyboardButton("❓ Help", callback_data="nav_help")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "❌ **Error generating leaderboard**\n\n"
                "_Problem creating the leaderboard. Try again or check help._",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        return
    
    async def _show_key_element_buttons(self, update: Update, context: CallbackContext, message: str = None):
        """Show key element buttons for leaderboard selection"""
        if not message:
            message = """🏆 **Ingress Leaderboard**

_Select a key element to view the leaderboard:_"""
        
        # Create keyboard with key elements (3 buttons per row for better layout)
        keyboard = []
        key_elements = list(KEY_ELEMENTS.keys())
        
        for i in range(0, len(key_elements), 3):
            row = []
            for j in range(3):
                if i + j < len(key_elements):
                    key = key_elements[i + j]
                    element_info = KEY_ELEMENTS[key]
                    # Use shorter display name for buttons
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
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        return
    
    async def progress_command(self, update: Update, context: CallbackContext):
        """Handle /progress command"""
        user_id = update.effective_user.id
        args = context.args
        
        # Get user's agents from database
        user_agents = self.db.get_agents_by_user(user_id)
        
        if not user_agents:
            keyboard = [
                [InlineKeyboardButton("📊 Submit Stats", callback_data="nav_submit"),
                 InlineKeyboardButton("❓ Help", callback_data="nav_help")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "📈 **Progress tracking requires your agent registration.**\n\n"
                "_Please submit data first, then try progress again._",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
        
        # Parse arguments
        agent_name = None
        stat = "Current AP"
        days = 30
        
        # Check if first argument is an agent name (if user has multiple agents)
        if len(args) >= 1:
            # Check if first arg matches any of user's agents
            first_arg = args[0]
            for agent, faction in user_agents:
                if agent.lower() == first_arg.lower():
                    agent_name = agent
                    # Shift other arguments
                    if len(args) >= 2:
                        stat = " ".join(args[1].split("_")).title()
                    if len(args) >= 3:
                        try:
                            days = int(args[2])
                        except ValueError:
                            days = 30
                    break
            
            # If no agent name match, treat first arg as stat
            if not agent_name:
                stat = " ".join(args[0].split("_")).title()
                if len(args) >= 2:
                    try:
                        days = int(args[1])
                    except ValueError:
                        days = 30
        
        # If no specific agent name provided, use the first (or only) agent
        if not agent_name:
            agent_name = user_agents[0][0]
        
        # Validate stat
        if stat not in LEADERBOARD_STATS:
            keyboard = [
                [InlineKeyboardButton("📊 Available Stats", callback_data="nav_stats"),
                 InlineKeyboardButton("❓ Help", callback_data="nav_help")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"❌ **Invalid statistic:** `{stat}`\n\n"
                f"**Available:** _{', '.join(LEADERBOARD_STATS[:5])}..._",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
        
        # Generate progress report
        progress_text = self.leaderboard.generate_agent_progress(agent_name, user_id, stat, days)
        
        # If user has multiple agents, show which agent's progress is being displayed
        if len(user_agents) > 1:
            other_agents = [agent for agent, faction in user_agents if agent != agent_name]
            progress_text += f"\n\n💡 **Other agents:** _{', '.join(other_agents)}_\n"
            progress_text += f"Use `/progress {other_agents[0]} {stat}` to see __their progress__."
        
        # Add self-delete notice to the progress text
        progress_text += f"\n\n⏰ **_This message will self-delete in 30 seconds_**"
        
        # Send the progress message
        sent_message = await update.message.reply_text(progress_text, parse_mode='Markdown')
        
        # Schedule auto-deletion after 30 seconds
        asyncio.create_task(self._auto_delete_progress_message(update, sent_message))
        return
    
    async def _auto_delete_progress_message(self, update: Update, sent_message):
        """Auto-delete progress message after 30 seconds and send confirmation"""
        try:
            # Wait for 30 seconds
            await asyncio.sleep(30)
            
            # Delete the original progress message
            await sent_message.delete()
            
            # Send confirmation message with navigation
            reply_markup = self._create_navigation_buttons()
            await update.message.reply_text("_[result removed]_", reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error during auto-deletion of progress message: {e}")
            # If deletion fails, still send the confirmation message
            try:
                reply_markup = self._create_navigation_buttons()
                await update.message.reply_text("_[result removed - deletion failed]_", reply_markup=reply_markup, parse_mode='Markdown')
            except Exception as e2:
                logger.error(f"Error sending deletion confirmation: {e2}")
    
    async def factions_command(self, update: Update, context: CallbackContext):
        """Handle /factions command"""
        args = context.args
        time_slot = "all_time"
        
        if len(args) >= 1:
            time_slot = args[0].lower()
        
        if time_slot not in TIME_SLOTS:
            time_slot = "all_time"
        
        # Generate faction comparison text with custom faction stickers
        comparison_text = self.leaderboard.generate_faction_comparison(time_slot)
        reply_markup = self._create_navigation_buttons(exclude_current="nav_factions")
        await update.message.reply_text(comparison_text, reply_markup=reply_markup, parse_mode='Markdown')
        return
    
    async def stats_command(self, update: Update, context: CallbackContext):
        """Handle /stats command - show available statistics"""
        stats_text = "📊 **Available Statistics for Leaderboards:**\n\n"
        for i, stat in enumerate(LEADERBOARD_STATS, 1):
            stats_text += f"{i}. **{stat}**\n"
        
        stats_text += "\n🕐 **Available Time Frames:**\n"
        for slot, days in TIME_SLOTS.items():
            if days:
                stats_text += f"• **{slot.replace('_', ' ').title()}** _({days} days)_\n"
            else:
                stats_text += f"• **{slot.replace('_', ' ').title()}**\n"
        
        reply_markup = self._create_navigation_buttons()
        await update.message.reply_text(stats_text, reply_markup=reply_markup, parse_mode='Markdown')
        return
    
    async def create_stickers_command(self, update: Update, context: CallbackContext):
        """Handle /create_stickers command - create faction sticker set"""
        user_id = update.effective_user.id
        
        # Check if user is authorized (you might want to restrict this to admins)
        # For now, let's allow any user to trigger sticker creation
        
        reply_markup = self._create_navigation_buttons()
        await update.message.reply_text("🎨 **Creating faction sticker set...** _This may take a moment._", reply_markup=reply_markup, parse_mode='Markdown')
        
        try:
            success = await self.leaderboard.sticker_manager.create_sticker_set(context.bot, user_id)
            
            if success:
                sticker_link = self.leaderboard.sticker_manager.get_sticker_set_link()
                success_text = f"""
✅ **Faction sticker set created successfully!**

🎯 **Sticker Set:** __{self.leaderboard.sticker_manager.sticker_set_title}__
🔗 **Add to Telegram:** [Click here]({sticker_link})

_The bot will now use these custom faction stickers in leaderboards instead of emoji balls!_

**Stickers included:**
💚 __Enlightened__ faction logo
💙 __Resistance__ faction logo

_Created by:_ **H1GHT0WER**
                """
                reply_markup = self._create_navigation_buttons()
                await update.message.reply_text(success_text, reply_markup=reply_markup, parse_mode='Markdown')
            else:
                reply_markup = self._create_navigation_buttons()
                await update.message.reply_text(
                    "❌ **Failed to create sticker set**\n\n"
                    "_Could be: existing set, format issues, or API limits._",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
        
        except Exception as e:
            logger.error(f"Error in create_stickers_command: {e}")
            reply_markup = self._create_navigation_buttons()
            await update.message.reply_text(
                "❌ **Error creating sticker set**\n\n"
                "_Unexpected error. Please try again later._",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        return
    
    async def prepare_emoji_command(self, update: Update, context: CallbackContext):
        """Handle /prepare_emoji command - convert faction images to emoji format"""
        reply_markup = self._create_navigation_buttons()
        await update.message.reply_text("🎨 **Converting faction images to emoji format...**", reply_markup=reply_markup, parse_mode='Markdown')
        
        try:
            prepared_emoji = self.leaderboard.sticker_manager.prepare_all_faction_emoji()
            
            if prepared_emoji:
                success_text = f"""
✅ **Faction emoji prepared successfully!**

**Converted images:**
"""
                for faction, emoji_path in prepared_emoji.items():
                    file_size = emoji_path.stat().st_size
                    success_text += f"• __{faction}__: `{emoji_path.name}` _({file_size} bytes)_\n"
                
                success_text += f"""
📁 **Location:** `{list(prepared_emoji.values())[0].parent}`

_These emoji-format images can now be used as custom emoji in Telegram!_

**Next steps:**
1. __Download__ the emoji files from the temp/emoji directory
2. __Upload__ them as custom emoji to your Telegram server/bot
3. __Update__ the bot configuration with the custom emoji IDs
                """
                
                reply_markup = self._create_navigation_buttons()
                await update.message.reply_text(success_text, reply_markup=reply_markup, parse_mode='Markdown')
                
                # Send the emoji files to the user
                for faction, emoji_path in prepared_emoji.items():
                    with open(emoji_path, 'rb') as emoji_file:
                        await update.message.reply_document(
                            document=emoji_file,
                            filename=f"{faction.lower()}_emoji.png",
                            caption=f"__{faction}__ faction emoji _(100x100 PNG)_"
                        )
            else:
                reply_markup = self._create_navigation_buttons()
                await update.message.reply_text(
                    "❌ **Failed to prepare emoji**\n\n"
                    "_This could be due to:_\n"
                    "• __Image generation issues__\n"
                    "• __File system permissions__\n\n"
                    "_The bot now uses heart emojis (💚💙) instead of custom images._",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
        
        except Exception as e:
            logger.error(f"Error in prepare_emoji_command: {e}")
            reply_markup = self._create_navigation_buttons()
            await update.message.reply_text(
                "❌ **Error preparing emoji**\n\n"
                "_An unexpected error occurred. Please try again later._",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        return
    
    async def cancel_command(self, update: Update, context: CallbackContext):
        """Handle /cancel command"""
        current_state = context.user_data.pop('state', None)
        
        reply_markup = self._create_navigation_buttons()
        
        if current_state == 'awaiting_data':
            await update.message.reply_text(
                "✅ **Submission cancelled**\n\n"
                "_Ready when you are!_ 😊",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        elif current_state:
            await update.message.reply_text(
                "✅ **Operation cancelled**\n\n"
                "_Back to main menu._",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "🤔 **Nothing to cancel**\n\n"
                "_No active operations._",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        return
    
    def _create_navigation_buttons(self, exclude_current=None):
        """Create navigation buttons for all commands"""
        buttons = []
        
        # Main navigation buttons
        nav_buttons = [
            ("📊 Submit", "nav_submit"),
            ("🏆 Leaderboard", "nav_leaderboard"), 
            ("📈 Progress", "nav_progress"),
            ("⚔️ Factions", "nav_factions"),
            ("❓ Help", "nav_help")
        ]
        
        # Filter out current command if specified
        if exclude_current:
            nav_buttons = [(text, data) for text, data in nav_buttons if data != exclude_current]
        
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