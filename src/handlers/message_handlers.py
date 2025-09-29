"""
Message handlers for the Ingress Leaderboard Bot
"""

import logging
from telegram import Update
from telegram.ext import CallbackContext
from config.settings import BOT_USERNAME

logger = logging.getLogger(__name__)

class MessageHandlers:
    def __init__(self, db_manager, leaderboard_manager, data_parser):
        self.db = db_manager
        self.leaderboard = leaderboard_manager
        self.parser = data_parser
    
    def _should_respond_to_message(self, update: Update, context: CallbackContext) -> bool:
        """Check if the bot should respond to this message"""
        message = update.message
        
        # Always respond if user is in data submission mode
        if context.user_data.get('state') == 'awaiting_data':
            return True
        
        # Check if the message is a reply to one of our messages
        if message.reply_to_message and message.reply_to_message.from_user.is_bot:
            # Check if it's replying to this bot specifically
            if message.reply_to_message.from_user.username == BOT_USERNAME:
                return True
        
        # Check if the bot is mentioned in the message
        if message.entities:
            for entity in message.entities:
                if entity.type == "mention":
                    # Extract the mentioned username
                    mention_text = message.text[entity.offset:entity.offset + entity.length]
                    if mention_text == f"@{BOT_USERNAME}":
                        return True
        
        # Don't respond to other messages
        return False
    
    async def handle_message(self, update: Update, context: CallbackContext):
        """Handle text messages with smart detection"""
        # Check if we should respond to this message
        if not self._should_respond_to_message(update, context):
            return
        
        user_id = update.effective_user.id
        message_text = update.message.text.strip()
        
        # Remove bot mention from message text if present
        message_text = message_text.replace(f"@{BOT_USERNAME}", "").strip()
        
        # Check if user is in data submission mode
        if context.user_data.get('state') == 'awaiting_data':
            await self.process_data_submission(update, context)
            return
        
        # Smart detection of different message types
        detection_result = self._analyze_message(message_text)
        
        if detection_result['type'] == 'ingress_data':
            # Looks like valid Ingress data
            reply_markup = self._create_navigation_buttons(exclude_current="nav_submit")
            await update.message.reply_text(
                "🎯 **Detected Ingress statistics!**\n\n"
                "Processing your data automatically... ⚡",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            await self.process_data_submission(update, context)
        
        elif detection_result['type'] == 'partial_data':
            # Looks like incomplete Ingress data
            reply_markup = self._create_navigation_buttons()
            await update.message.reply_text(
                "🤔 **This looks like partial Ingress data**\n\n"
                f"I can see some statistics, but {detection_result['issue']}\n\n"
                "💡 **To fix this:**\n"
                "1. Go to Ingress → Agent → Statistics\n"
                "2. Copy ALL your statistics (scroll right to see everything)\n"
                "3. Send the complete data here\n\n"
                "Or tap **Help** below for detailed instructions.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        elif detection_result['type'] == 'possible_data':
            # Might be data, offer to help
            reply_markup = self._create_navigation_buttons()
            await update.message.reply_text(
                "🤔 **Are you trying to submit Ingress statistics?**\n\n"
                "If yes:\n"
                "• Tap **Submit** below and follow the guide\n"
                "• Or just send your complete stats data\n\n"
                "Tap **Help** for detailed instructions.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        else:
            # Generic help for unrecognized messages
            reply_markup = self._create_navigation_buttons()
            await update.message.reply_text(
                "👋 **I'm here to help with Ingress leaderboards!**\n\n"
                "🔥 **Quick Access:**\n"
                "• **Submit** - Add your Ingress statistics\n"
                "• **Leaderboard** - View current rankings\n"
                "• **Help** - Quick help guide\n\n"
                "💡 Just copy your stats from Ingress and send them to me!\n"
                "_Use the buttons below for easy navigation._",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        return
    
    def _analyze_message(self, text: str) -> dict:
        """Analyze message and determine what type of content it is"""
        parts = text.split()
        
        if len(parts) < 3:
            return {'type': 'unrecognized'}
        
        # Check for valid faction keywords
        factions = ["Enlightened", "Resistance", "enlightened", "resistance"]
        has_faction = any(part in factions for part in parts[:6])  # Check first few parts
        
        # Look for "ALL TIME" pattern
        if len(parts) >= 2 and parts[0] == "ALL" and parts[1] == "TIME":
            if len(parts) >= 60:  # Sufficient fields
                if has_faction:
                    return {'type': 'ingress_data'}
                else:
                    return {'type': 'partial_data', 'issue': "I can't find your faction (Enlightened/Resistance)."}
            elif len(parts) >= 10:
                return {'type': 'partial_data', 'issue': f"only {len(parts)} fields found, need 60+ complete statistics."}
            else:
                return {'type': 'partial_data', 'issue': "this looks too short to be complete statistics."}
        
        # Check for single word time periods
        time_periods = ["DAILY", "WEEKLY", "MONTHLY", "ALL"]
        if parts[0] in time_periods:
            if len(parts) >= 60:  # Sufficient fields
                if has_faction:
                    return {'type': 'ingress_data'}
                else:
                    return {'type': 'partial_data', 'issue': "I can't find your faction (Enlightened/Resistance)."}
            elif len(parts) >= 10:
                return {'type': 'partial_data', 'issue': f"only {len(parts)} fields found, need 60+ complete statistics."}
        
        # Check if it has some numbers and might be partial data
        number_count = sum(1 for part in parts[:20] if part.isdigit())
        if number_count >= 3 and len(parts) >= 5:
            if has_faction:
                return {'type': 'partial_data', 'issue': f"only {len(parts)} fields found, need 60+ complete statistics."}
            else:
                return {'type': 'possible_data'}
        
        # Check if it contains Ingress-related keywords
        ingress_keywords = ["agent", "enlightened", "resistance", "level", "ap", "portals", "links", "fields", "xm"]
        has_ingress_words = any(word.lower() in [p.lower() for p in parts] for word in ingress_keywords)
        
        if has_ingress_words:
            return {'type': 'possible_data'}
        
        return {'type': 'unrecognized'}
        
    def _looks_like_ingress_data(self, text: str) -> bool:
        """Check if text looks like Ingress statistics data (legacy method)"""
        result = self._analyze_message(text)
        return result['type'] == 'ingress_data'
    
    async def process_data_submission(self, update: Update, context: CallbackContext):
        """Process submitted Ingress data"""
        data_text = update.message.text.strip()
        
        # Remove bot mention from data text if present
        data_text = data_text.replace(f"@{BOT_USERNAME}", "").strip()
        
        # Import here to avoid circular imports
        from .command_handlers import CommandHandlers
        
        # Create a temporary command handler instance to use the shared processing method
        temp_handler = CommandHandlers(self.db, self.leaderboard, self.parser)
        await temp_handler._process_submission_data(update, context, data_text)
        return