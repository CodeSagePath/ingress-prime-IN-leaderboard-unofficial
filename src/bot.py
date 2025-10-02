"""
Main Telegram Bot for Ingress Leaderboards
"""

import logging
import asyncio
from datetime import datetime
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

from config import BOT_TOKEN, LEADERBOARD_STATS, TIME_SLOTS
from database import DatabaseManager
from data_parser import DataParser
from leaderboard import LeaderboardManager

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class IngressLeaderboardBot:
    def __init__(self):
        self.db = DatabaseManager()
        self.parser = DataParser()
        self.leaderboard = LeaderboardManager()
        self.user_states = {}  # Track user interaction states
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        welcome_text = f"""
🎮 Welcome to the Ingress Leaderboard Bot, {user.first_name}!

This bot helps you track and compare Ingress statistics with other agents.

💚 **Enlightened** vs 💙 **Resistance**

Use /help to see all available commands.
Use /submit to submit your first statistics.

Let's see who dominates the leaderboards! 🏆
        """
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = self.leaderboard.generate_help_text()
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def submit_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /submit command"""
        user_id = update.effective_user.id
        self.user_states[user_id] = 'awaiting_data'
        
        submit_text = f"""
📊 **Data Submission**

Please paste your Ingress statistics data in the following format:

{self.parser.extract_sample_data()}

Just copy your stats line and paste it here. The bot will automatically parse and store your data.

❌ Send /cancel to cancel submission.
        """
        await update.message.reply_text(submit_text, parse_mode='Markdown')
    
    async def leaderboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /leaderboard command"""
        args = context.args
        
        # Default values
        stat = "Current AP"
        time_slot = "all_time"
        faction = None
        
        # Parse arguments
        if len(args) >= 1:
            stat = " ".join(args[0].split("_")).title()
        if len(args) >= 2:
            time_slot = args[1].lower()
        if len(args) >= 3:
            faction = args[2].title()
        
        # Validate inputs
        if stat not in LEADERBOARD_STATS:
            keyboard = []
            for i in range(0, len(LEADERBOARD_STATS), 2):
                row = []
                for j in range(2):
                    if i + j < len(LEADERBOARD_STATS):
                        stat_name = LEADERBOARD_STATS[i + j]
                        callback_data = f"lb_{stat_name.replace(' ', '_')}_{time_slot}_{faction or 'all'}"
                        row.append(InlineKeyboardButton(stat_name, callback_data=callback_data))
                keyboard.append(row)
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "Please select a statistic for the leaderboard:",
                reply_markup=reply_markup
            )
            return
        
        if time_slot not in TIME_SLOTS:
            time_slot = "all_time"
        
        if faction and faction not in ["Enlightened", "Resistance"]:
            faction = None
        
        # Generate leaderboard
        user_id = update.effective_user.id
        leaderboard_text = self.leaderboard.generate_leaderboard(stat, time_slot, faction, requestor_user_id=user_id)
        await update.message.reply_text(leaderboard_text, parse_mode='Markdown')
    
    async def progress_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /progress command"""
        user_id = update.effective_user.id
        args = context.args
        
        # Get user's agent name from database
        # For now, we'll ask them to specify or use a default
        stat = "Current AP"
        days = 30
        
        if len(args) >= 1:
            stat = " ".join(args[0].split("_")).title()
        if len(args) >= 2:
            try:
                days = int(args[1])
            except ValueError:
                days = 30
        
        # This would need the agent name - for now we'll show an error
        await update.message.reply_text(
            "Progress tracking requires your agent name to be registered. "
            "Please submit data first using /submit, then try /progress again."
        )
    
    async def factions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /factions command"""
        args = context.args
        time_slot = "all_time"
        
        if len(args) >= 1:
            time_slot = args[0].lower()
        
        if time_slot not in TIME_SLOTS:
            time_slot = "all_time"
        
        comparison_text = self.leaderboard.generate_faction_comparison(time_slot)
        await update.message.reply_text(comparison_text, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command - show available statistics"""
        stats_text = "📊 **Available Statistics for Leaderboards:**\n\n"
        for i, stat in enumerate(LEADERBOARD_STATS, 1):
            stats_text += f"{i}. {stat}\n"
        
        stats_text += "\n🕐 **Available Time Frames:**\n"
        for slot, days in TIME_SLOTS.items():
            if days:
                stats_text += f"• {slot.replace('_', ' ').title()} ({days} days)\n"
            else:
                stats_text += f"• {slot.replace('_', ' ').title()}\n"
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cancel command"""
        user_id = update.effective_user.id
        if user_id in self.user_states:
            del self.user_states[user_id]
        await update.message.reply_text("❌ **Operation cancelled.**", parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user_id = update.effective_user.id
        
        # Check if user is in data submission mode
        if user_id in self.user_states and self.user_states[user_id] == 'awaiting_data':
            await self.process_data_submission(update, context)
        else:
            await update.message.reply_text(
                "🤔 **I don't understand that command.**\n\n"
                "_Use_ `/help` _to see available commands._",
                parse_mode='Markdown'
            )
    
    async def process_data_submission(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process submitted Ingress data"""
        user_id = update.effective_user.id
        data_text = update.message.text.strip()
        
        try:
            # Parse the data
            parsed_data = self.parser.parse_data_line(data_text)
            
            if not parsed_data:
                await update.message.reply_text(
                    "❌ **Error parsing your data.**\n\n"
                    "_Please check the format and try again._\n\n"
                    "Use `/submit` to see the expected format.",
                    parse_mode='Markdown'
                )
                return
            
            # Validate faction
            if not self.parser.validate_faction(parsed_data['faction']):
                await update.message.reply_text(
                    "❌ **Invalid faction.**\n\n"
                    "_Please use_ '__Enlightened__' _or_ '__Resistance__'_._",
                    parse_mode='Markdown'
                )
                return
            
            # Add agent to database
            agent_id = self.db.add_agent(
                parsed_data['agent_name'],
                parsed_data['faction'],
                user_id
            )
            
            # Add submission
            success = self.db.add_submission(agent_id, parsed_data)
            
            if success:
                faction_emoji = "💚" if parsed_data['faction'].lower() == 'enlightened' else "💙"
                success_text = f"""
✅ **Data submitted successfully!**

{faction_emoji} **Agent:** __{parsed_data['agent_name']}__
📅 **Data Date:** _{parsed_data['data_date']}_
📊 **Level:** __{parsed_data['level']}__
⚡ **Current AP:** __{self.parser.format_number(parsed_data['current_ap'])}__

_Your data has been added to the leaderboards!_
Use `/leaderboard` to see __current rankings__.
                """
                await update.message.reply_text(success_text, parse_mode='Markdown')
            else:
                await update.message.reply_text(
                    "❌ **Error saving your data.**\n\n"
                    "_Please try again later._",
                    parse_mode='Markdown'
                )
            
            # Clear user state
            if user_id in self.user_states:
                del self.user_states[user_id]
                
        except Exception as e:
            logger.error(f"Error processing data submission: {e}")
            await update.message.reply_text(
                "❌ **An error occurred while processing your data.**\n\n"
                "_Please try again._",
                parse_mode='Markdown'
            )
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith('lb_'):
            # Leaderboard callback
            parts = data.split('_')
            if len(parts) >= 4:
                stat = parts[1].replace('_', ' ').title()
                time_slot = parts[2]
                faction = parts[3] if parts[3] != 'all' else None
                
                user_id = query.from_user.id
                leaderboard_text = self.leaderboard.generate_leaderboard(stat, time_slot, faction, requestor_user_id=user_id)
                await query.edit_message_text(leaderboard_text, parse_mode='Markdown')
    
    def run(self):
        """Run the bot"""
        if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            logger.error("Please set your bot token in config.py")
            return
        
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("submit", self.submit_command))
        application.add_handler(CommandHandler("leaderboard", self.leaderboard_command))
        application.add_handler(CommandHandler("progress", self.progress_command))
        application.add_handler(CommandHandler("factions", self.factions_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(CommandHandler("cancel", self.cancel_command))
        
        # NOTE: Message handler removed - using enhanced handler from bot_service.py instead
        # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        application.add_handler(CallbackQueryHandler(self.handle_callback_query))
        
        # Start the bot
        logger.info("Starting Ingress Leaderboard Bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    bot = IngressLeaderboardBot()
    bot.run()