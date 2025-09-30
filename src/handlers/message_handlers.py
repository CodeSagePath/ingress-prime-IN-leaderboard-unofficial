"""
Message handlers for the Ingress Leaderboard Bot
Enhanced with smart prefix detection for flexible stats parsing
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from config.settings import BOT_USERNAME
from ..services.prefix_detector import PrefixDetector

logger = logging.getLogger(__name__)

class MessageHandlers:
    def __init__(self, db_manager, leaderboard_manager, data_parser):
        self.db = db_manager
        self.leaderboard = leaderboard_manager
        self.parser = data_parser
        self.prefix_detector = PrefixDetector(db_manager)
    
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
        
        # RESTORED: Always respond to messages to allow direct copy-paste
        return True
    
    async def handle_message(self, update: Update, context: CallbackContext):
        """Handle text messages with controlled submission acceptance"""
        # Check if we should respond to this message
        if not self._should_respond_to_message(update, context):
            return
        
        user_id = update.effective_user.id
        message_text = update.message.text.strip()
        
        # Remove bot mention from message text if present
        message_text = message_text.replace(f"@{BOT_USERNAME}", "").strip()
        
        # Check if user is in data submission mode (after /submit command or Submit button)
        if context.user_data.get('state') == 'awaiting_data':
            await self.process_data_submission(update, context)
            return
        
        # Check if this is a reply to a bot message (Submit button flow)
        message = update.message
        if message.reply_to_message and message.reply_to_message.from_user.is_bot:
            if message.reply_to_message.from_user.username == BOT_USERNAME:
                # This is a reply to our bot message - check if it looks like stats data
                detection_result = self._analyze_message(message_text, user_id)
                if detection_result['type'] == 'ingress_data':
                    # Valid stats data in reply to bot message - process it
                    reply_markup = self._create_navigation_buttons(context_type="data_processing")
                    await update.message.reply_text(
                        "🎯 **Processing your stats data...**\n\n"
                        "Thanks for replying with your statistics! ⚡",
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                    await self.process_data_submission(update, context)
                    return
                else:
                    # Reply to bot but not valid stats data
                    reply_markup = self._create_navigation_buttons(context_type="data_help")
                    await update.message.reply_text(
                        "🤔 **I don't recognize this as Ingress statistics**\n\n"
                        "💡 **To submit your stats:**\n"
                        "1. Go to Ingress → Agent → Statistics\n"
                        "2. Copy ALL your statistics data\n"
                        "3. Reply to this message with the complete data\n\n"
                        "Or use the **Submit** button below for guided submission.",
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                    return
        
        # For all other messages (not in awaiting_data state, not replying to bot):
        # ENHANCED: Auto-process valid Ingress data with smart prefix detection
        detection_result = self._analyze_message(message_text, user_id)
        
        if detection_result['type'] == 'ingress_data':
            # Valid stats data - process it directly (ENHANCED WITH PREFIX SUPPORT)
            reply_markup = self._create_navigation_buttons(context_type="data_processing")
            
            # Enhanced response with prefix acknowledgment
            response_text = "🎯 **Processing your stats data...**\n\n"
            
            if detection_result.get('prefix_info', {}).get('has_prefix'):
                prefix_info = detection_result['prefix_info']
                response_text += f"✨ **Prefix detected:** `{prefix_info['prefix_text']}` ({prefix_info['prefix_type']})\n"
                if detection_result.get('enhanced_confidence'):
                    response_text += "🚀 **Enhanced detection** - prefix helped me identify your data faster!\n\n"
                else:
                    response_text += "\n"
            
            response_text += "Thanks for submitting your statistics! ⚡"
            
            await update.message.reply_text(
                response_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            await self.process_data_submission(update, context)
            return
        
        elif detection_result['type'] == 'partial_data':
            # Looks like incomplete stats data - provide enhanced guidance
            reply_markup = self._create_navigation_buttons(context_type="data_help")
            
            response_text = "📊 **I can see partial Ingress statistics data!**\n\n"
            response_text += f"⚠️ **Issue detected:** {detection_result.get('issue', 'Incomplete data')}\n\n"
            
            # Add prefix-specific guidance
            if detection_result.get('prefix_info', {}).get('has_prefix'):
                prefix_info = detection_result['prefix_info']
                response_text += f"✅ **Good news:** I found your prefix `{prefix_info['prefix_text']}`\n"
                response_text += "📝 **Next step:** Add your complete statistics after the prefix\n\n"
            
            response_text += "💡 **Please ensure you copy ALL statistics from:**\n"
            response_text += "Ingress → Agent → Statistics\n\n"
            
            # Add prefix suggestions if no prefix was used
            if not detection_result.get('prefix_info', {}).get('has_prefix'):
                suggestions = self.prefix_detector.suggest_prefixes_for_user(user_id)[:2]  # Top 2 suggestions
                if suggestions:
                    response_text += "🚀 **Pro tip:** Try using a prefix like:\n"
                    for suggestion in suggestions:
                        response_text += f"• {suggestion}\n"
                    response_text += "\n"
            
            response_text += "**Or use these methods:**\n"
            response_text += "• `/submit <your complete stats data>`\n"
            response_text += "• Tap **Submit** below for guided submission"
            
            await update.message.reply_text(
                response_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        elif detection_result['type'] == 'prefix_without_stats':
            # NEW: Handle prefix detected but no valid stats data
            reply_markup = self._create_navigation_buttons(context_type="data_help")
            prefix_info = detection_result.get('prefix_info', {})
            
            response_text = f"🎯 **Great! I found your prefix: `{prefix_info.get('prefix_text', '')}`**\n\n"
            response_text += f"❌ **But:** {detection_result.get('issue', 'No statistics data found after the prefix')}\n\n"
            response_text += "💡 **What to do:**\n"
            response_text += f"1. Keep your prefix: `{prefix_info.get('prefix_text', '')}`\n"
            response_text += "2. Add your complete Ingress statistics after it\n"
            response_text += "3. Copy from: Ingress → Agent → Statistics\n\n"
            response_text += "**Example format:**\n"
            response_text += f"`{prefix_info.get('prefix_text', 'STATS:')} ALL TIME YourName Enlightened 2024-01-01 12:00:00 [your stats...]`"
            
            await update.message.reply_text(
                response_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        elif detection_result['type'] == 'possible_data':
            # Might be data, offer to help with enhanced prefix suggestions
            reply_markup = self._create_navigation_buttons(context_type="data_help")
            
            response_text = "🤔 **Are you trying to submit Ingress statistics?**\n\n"
            
            # Add prefix suggestions
            if detection_result.get('prefix_info', {}).get('has_prefix'):
                prefix_info = detection_result['prefix_info']
                response_text += f"✨ **I found your prefix:** `{prefix_info['prefix_text']}`\n"
                response_text += "📝 **Tip:** This helps me identify your data faster!\n\n"
            else:
                suggestions = self.prefix_detector.suggest_prefixes_for_user(user_id)[:2]
                if suggestions:
                    response_text += "🚀 **Pro tip:** Try prefixing your data with:\n"
                    for suggestion in suggestions:
                        response_text += f"• {suggestion}\n"
                    response_text += "\n"
            
            response_text += "📋 **Proper submission methods:**\n"
            response_text += "• Use `/submit <your stats data>`\n"
            response_text += "• Or tap **Submit** below and reply with your data\n\n"
            response_text += "Tap **Help** for detailed instructions."
            
            await update.message.reply_text(
                response_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        else:
            # Generic help for unrecognized messages with smart prefix suggestions
            reply_markup = self._create_navigation_buttons(context_type="welcome")
            
            response_text = "👋 **I'm here to help with Ingress leaderboards!**\n\n"
            response_text += "🔥 **Quick Access:**\n"
            response_text += "• **Submit** - Add your Ingress statistics\n"
            response_text += "• **Leaderboard** - View current rankings\n"
            response_text += "• **Help** - Quick help guide\n\n"
            
            # Add personalized prefix suggestions
            suggestions = self.prefix_detector.suggest_prefixes_for_user(user_id)[:2]
            if suggestions:
                response_text += "🚀 **Pro tip for faster stats submission:**\n"
                for suggestion in suggestions:
                    response_text += f"• {suggestion}\n"
                response_text += "\n"
            
            response_text += "💡 **To submit stats:** Use `/submit <data>` or tap Submit button!\n"
            response_text += "_Use the buttons below for easy navigation._"
            
            await update.message.reply_text(
                response_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        return
    
    def _analyze_message(self, text: str, user_id: int = None) -> dict:
        """
        Enhanced message analysis with smart prefix detection
        Analyzes message and determines what type of content it is
        """
        if not text or not text.strip():
            return {'type': 'unrecognized'}
        
        original_text = text
        
        # 1. ENHANCED: Check for prefix detection first
        prefix_result = self.prefix_detector.detect_prefix(text, user_id)
        
        if prefix_result['has_prefix']:
            # Use the clean text (with prefix removed) for analysis
            text = prefix_result['clean_text']
            logger.info(f"Prefix detected: '{prefix_result['prefix_text']}' (type: {prefix_result['prefix_type']}, confidence: {prefix_result['confidence']})")
        
        parts = text.split()
        
        if len(parts) < 3:
            # If we had a prefix but insufficient data, provide better guidance
            if prefix_result['has_prefix']:
                return {
                    'type': 'partial_data', 
                    'issue': f"I found your prefix '{prefix_result['prefix_text']}' but need more statistics data after it.",
                    'prefix_info': prefix_result
                }
            return {'type': 'unrecognized'}
        
        # Check for valid faction keywords (search in entire text, not just first parts)
        factions = ["Enlightened", "Resistance", "enlightened", "resistance"]
        has_faction = any(faction in text for faction in factions)
        
        # Look for "ALL TIME" pattern
        if len(parts) >= 2 and parts[0] == "ALL" and parts[1] == "TIME":
            if len(parts) >= 60:  # Sufficient fields
                if has_faction:
                    result = {'type': 'ingress_data'}
                    if prefix_result['has_prefix']:
                        result['prefix_info'] = prefix_result
                        result['enhanced_confidence'] = True
                    return result
                else:
                    return {
                        'type': 'partial_data', 
                        'issue': "I can't find your faction (Enlightened/Resistance).",
                        'prefix_info': prefix_result if prefix_result['has_prefix'] else None
                    }
            elif len(parts) >= 10:
                return {
                    'type': 'partial_data', 
                    'issue': f"only {len(parts)} fields found, need 60+ complete statistics.",
                    'prefix_info': prefix_result if prefix_result['has_prefix'] else None
                }
            else:
                return {
                    'type': 'partial_data', 
                    'issue': "this looks too short to be complete statistics.",
                    'prefix_info': prefix_result if prefix_result['has_prefix'] else None
                }
        
        # Check for single word time periods
        time_periods = ["DAILY", "WEEKLY", "MONTHLY", "ALL"]
        if parts[0] in time_periods:
            if len(parts) >= 60:  # Sufficient fields
                if has_faction:
                    result = {'type': 'ingress_data'}
                    if prefix_result['has_prefix']:
                        result['prefix_info'] = prefix_result
                        result['enhanced_confidence'] = True
                    return result
                else:
                    return {
                        'type': 'partial_data', 
                        'issue': "I can't find your faction (Enlightened/Resistance).",
                        'prefix_info': prefix_result if prefix_result['has_prefix'] else None
                    }
            elif len(parts) >= 10:
                return {
                    'type': 'partial_data', 
                    'issue': f"only {len(parts)} fields found, need 60+ complete statistics.",
                    'prefix_info': prefix_result if prefix_result['has_prefix'] else None
                }
        
        # ENHANCED: If we detected a prefix, be more lenient with detection
        if prefix_result['has_prefix'] and prefix_result['confidence'] >= 0.7:
            # Check if it has some numbers and might be partial data
            number_count = sum(1 for part in parts[:20] if part.isdigit())
            if number_count >= 3 and len(parts) >= 5:
                if has_faction:
                    return {
                        'type': 'partial_data', 
                        'issue': f"only {len(parts)} fields found, need 60+ complete statistics.",
                        'prefix_info': prefix_result,
                        'enhanced_detection': True
                    }
                else:
                    return {
                        'type': 'possible_data',
                        'prefix_info': prefix_result,
                        'enhanced_detection': True
                    }
        
        # Check if it has some numbers and might be partial data (original logic)
        number_count = sum(1 for part in parts[:20] if part.isdigit())
        if number_count >= 3 and len(parts) >= 5:
            if has_faction:
                return {
                    'type': 'partial_data', 
                    'issue': f"only {len(parts)} fields found, need 60+ complete statistics.",
                    'prefix_info': prefix_result if prefix_result['has_prefix'] else None
                }
            else:
                return {'type': 'possible_data'}
        
        # Check if it contains Ingress-related keywords
        ingress_keywords = ["agent", "enlightened", "resistance", "level", "ap", "portals", "links", "fields", "xm"]
        has_ingress_words = any(word.lower() in [p.lower() for p in parts] for word in ingress_keywords)
        
        if has_ingress_words:
            result = {'type': 'possible_data'}
            if prefix_result['has_prefix']:
                result['prefix_info'] = prefix_result
            return result
        
        # ENHANCED: If we had a prefix but couldn't detect stats, provide helpful feedback
        if prefix_result['has_prefix']:
            return {
                'type': 'prefix_without_stats',
                'issue': f"I found your prefix '{prefix_result['prefix_text']}' but couldn't detect Ingress statistics after it.",
                'prefix_info': prefix_result,
                'suggestion': "Make sure to include your complete statistics data after the prefix."
            }
        
        return {'type': 'unrecognized'}
        
    def _looks_like_ingress_data(self, text: str) -> bool:
        """Check if text looks like Ingress statistics data (legacy method)"""
        result = self._analyze_message(text)
        return result['type'] == 'ingress_data'
    
    async def process_data_submission(self, update: Update, context: CallbackContext):
        """Process submitted Ingress data with enhanced prefix handling"""
        data_text = update.message.text.strip()
        user_id = update.effective_user.id
        
        # Remove bot mention from data text if present
        data_text = data_text.replace(f"@{BOT_USERNAME}", "").strip()
        
        # ENHANCED: Check for prefix and use clean data for processing
        prefix_result = self.prefix_detector.detect_prefix(data_text, user_id)
        if prefix_result['has_prefix']:
            # Use the clean text (prefix removed) for data processing
            data_text = prefix_result['clean_text']
            logger.info(f"Processing data with prefix '{prefix_result['prefix_text']}' removed")
        
        # Import here to avoid circular imports
        from .command_handlers import CommandHandlers
        
        # Create a temporary command handler instance to use the shared processing method
        temp_handler = CommandHandlers(self.db, self.leaderboard, self.parser)
        await temp_handler._process_submission_data(update, context, data_text)
        return
    
    def _create_navigation_buttons(self, exclude_current=None, context_type="default"):
        """Create contextual navigation buttons based on the situation"""
        buttons = []
        
        # Define different button sets for different contexts
        if context_type == "data_processing":
            # When processing data - show minimal options
            nav_buttons = [
                ("🏆 View Results", "nav_leaderboard"),
                ("❓ Help", "nav_help")
            ]
        elif context_type == "data_help":
            # When helping with data format - show submission focused options
            nav_buttons = [
                ("🔄 Try Submit", "nav_submit"),
                ("❓ More Help", "nav_help")
            ]
        elif context_type == "general_help":
            # General help messages - show main actions
            nav_buttons = [
                ("📊 Submit Stats", "nav_submit"),
                ("🏆 Leaderboard", "nav_leaderboard"),
                ("❓ Help", "nav_help")
            ]
        else:
            # Default - reduced set of main navigation
            nav_buttons = [
                ("📊 Submit", "nav_submit"),
                ("🏆 Leaderboard", "nav_leaderboard"), 
                ("❓ Help", "nav_help")
            ]
        
        # Filter out excluded button
        if exclude_current:
            nav_buttons = [btn for btn in nav_buttons if btn[1] != exclude_current]
        
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