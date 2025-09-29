"""
Main bot service for the Ingress Leaderboard Bot
"""

import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext
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
        
        # Add error handler
        application.add_error_handler(self._error_handler)
        
        # Start the bot
        logger.info("Starting Ingress Leaderboard Bot...")
        application.run_polling()
    
    async def _error_handler(self, update: Update, context: CallbackContext):
        """Handle errors in bot operations"""
        try:
            error_msg = str(context.error)
            
            # Log different types of errors with appropriate levels
            if "Message is not modified" in error_msg:
                # This is expected when users click buttons rapidly
                logger.debug(f"Message not modified error: {error_msg}")
                return
            elif "Bad Request" in error_msg:
                logger.warning(f"Bad request error: {error_msg}")
            elif "Forbidden" in error_msg:
                logger.warning(f"Forbidden error (user may have blocked bot): {error_msg}")
            else:
                logger.error(f"Unhandled error: {error_msg}", exc_info=context.error)
            
            # Try to inform the user if possible
            if update and update.callback_query:
                try:
                    await update.callback_query.answer(
                        "⚠️ Something went wrong. Please try again.",
                        show_alert=False
                    )
                except:
                    pass
        except Exception as e:
            logger.error(f"Error in error handler: {e}")