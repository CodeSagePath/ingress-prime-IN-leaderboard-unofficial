"""
Main bot service for the Ingress Leaderboard Bot
"""

import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram import Update

from config.settings import BOT_TOKEN
from ..database import DatabaseManager
from ..parsers import DataParser
from .leaderboard_service import LeaderboardManager
from ..handlers import CommandHandlers, MessageHandlers, CallbackHandlers

logger = logging.getLogger(__name__)

class IngressLeaderboardBot:
    def __init__(self):
        self.db = DatabaseManager()
        self.parser = DataParser()
        self.leaderboard = LeaderboardManager()
        
        # Initialize handlers
        self.command_handlers = CommandHandlers(self.db, self.leaderboard, self.parser)
        self.message_handlers = MessageHandlers(self.db, self.leaderboard, self.parser)
        self.callback_handlers = CallbackHandlers(self.db, self.leaderboard, self.parser)
    
    def run(self):
        """Run the bot"""
        if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            logger.error("Please set your bot token in config/settings.py or environment variable BOT_TOKEN")
            return
        
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", self.command_handlers.start_command))
        application.add_handler(CommandHandler("help", self.command_handlers.help_command))
        application.add_handler(CommandHandler("help_detailed", self.command_handlers.help_detailed_command))
        application.add_handler(CommandHandler("submit", self.command_handlers.submit_command))
        application.add_handler(CommandHandler("leaderboard", self.command_handlers.leaderboard_command))
        application.add_handler(CommandHandler("progress", self.command_handlers.progress_command))
        application.add_handler(CommandHandler("factions", self.command_handlers.factions_command))
        application.add_handler(CommandHandler("stats", self.command_handlers.stats_command))
        application.add_handler(CommandHandler("create_stickers", self.command_handlers.create_stickers_command))
        application.add_handler(CommandHandler("prepare_emoji", self.command_handlers.prepare_emoji_command))
        application.add_handler(CommandHandler("cancel", self.command_handlers.cancel_command))
        
        # Add message and callback handlers
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handlers.handle_message))
        application.add_handler(CallbackQueryHandler(self.callback_handlers.handle_callback_query))
        
        # Start the bot
        logger.info("Starting Ingress Leaderboard Bot...")
        application.run_polling()