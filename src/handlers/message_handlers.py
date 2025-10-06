"""
Message handlers for the Ingress Leaderboard Bot
Enhanced with smart prefix detection for flexible stats parsing
"""

import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.error import BadRequest
from config.settings import BOT_USERNAME, AUTO_DELETE_USER_STATS, AUTO_DELETE_DELAY_SECONDS
from ..services.prefix_detector import PrefixDetector
from ..services.ingress_prefix_detector import IngressPrefixDetector
from .enhanced_message_handlers import EnhancedMessageHandlers

logger = logging.getLogger(__name__)

class MessageHandlers:
    def __init__(self, db_manager, leaderboard_manager, data_parser):
        self.db = db_manager
        self.leaderboard = leaderboard_manager
        self.parser = data_parser
        self.prefix_detector = PrefixDetector(db_manager)
        self.ingress_prefix_detector = IngressPrefixDetector()
        self.enhanced_handlers = EnhancedMessageHandlers(db_manager, leaderboard_manager)
    
    async def _auto_delete_user_message(self, update: Update):
        """
        Auto-delete user's stats message to keep chat clean and prevent stat copying.
        Requires bot to have admin privileges with 'delete messages' permission.
        """
        if not AUTO_DELETE_USER_STATS:
            return
        
        try:
            # Wait a bit before deleting (allows user to see their message was received)
            if AUTO_DELETE_DELAY_SECONDS > 0:
                await asyncio.sleep(AUTO_DELETE_DELAY_SECONDS)
            
            # Attempt to delete the user's message
            await update.message.delete()
            logger.info(f"Successfully deleted stats message from user {update.effective_user.id}")
            
        except BadRequest as e:
            # Bot doesn't have permission to delete messages
            if "Message can't be deleted" in str(e) or "not enough rights" in str(e):
                logger.warning(
                    f"Cannot delete message - bot needs admin privileges with 'delete messages' permission. "
                    f"Chat: {update.effective_chat.id}, User: {update.effective_user.id}"
                )
            else:
                logger.warning(f"Failed to delete user message: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while deleting user message: {e}")
    
    def _should_respond_to_message(self, update: Update, context: CallbackContext) -> bool:
        """Check if the bot should respond to this message - VERY CONSERVATIVE TO PREVENT INTERRUPTIONS"""
        message = update.message
        
        # Always respond if user is in data submission mode or broadcast mode
        if context.user_data.get('state') in ['awaiting_data', 'awaiting_broadcast']:
            return True
        
        # Check if the message is a reply to one of our messages
        if message.reply_to_message and message.reply_to_message.from_user.is_bot:
            # Check if it's replying to this bot specifically
            if message.reply_to_message.from_user.username == BOT_USERNAME:
                return True
        
        # Check if the bot is mentioned in the message
        bot_mentioned = False
        if message.entities:
            for entity in message.entities:
                if entity.type == "mention":
                    # Extract the mentioned username
                    mention_text = message.text[entity.offset:entity.offset + entity.length]
                    if mention_text == f"@{BOT_USERNAME}":
                        bot_mentioned = True
                        break
        
        # If bot is mentioned, always respond (regardless of message length)
        if bot_mentioned:
            return True
        
        # ADDITIONAL SAFEGUARD: Don't respond to very short messages (likely conversation)
        message_text = message.text.strip() if message.text else ""
        if len(message_text) < 200:  # Very short messages are almost never Ingress stats
            return False
        
        # ADDITIONAL SAFEGUARD: Don't respond to messages that look like casual conversation
        # Check for common conversation patterns that should be ignored
        casual_patterns = [
            # Emoji-heavy messages (like the example: "😴 @9saw walked 3.1k in month")
            lambda text: len([c for c in text if ord(c) > 127]) > len(text) * 0.1,  # >10% non-ASCII chars (emojis)
            # Messages with @mentions of users (not the bot)
            lambda text: '@' in text and f'@{BOT_USERNAME}' not in text,
            # Messages that are clearly conversational
            lambda text: any(phrase in text.lower() for phrase in [
                'seems like', 'i think', 'maybe', 'probably', 'lol', 'haha', 'what do you think',
                'by the way', 'btw', 'anyway', 'just saying', 'in my opinion', 'imho'
            ])
        ]
        
        # If any casual pattern matches, don't respond
        for i, pattern_check in enumerate(casual_patterns):
            if pattern_check(message_text):
                logger.info(f"Message ignored - casual conversation pattern {i+1} detected (user: {update.effective_user.id})")
                return False
        
        # Only respond to messages that VERY clearly look like Ingress statistics
        # This is now much more conservative
        if self._looks_like_ingress_stats(message_text):
            logger.info(f"Message accepted - looks like Ingress stats (user: {update.effective_user.id})")
            return True
        
        # Don't respond to regular conversation messages
        logger.info(f"Message ignored - doesn't look like Ingress stats (user: {update.effective_user.id}, length: {len(message_text)})")
        return False
    
    def _looks_like_ingress_stats(self, message_text: str) -> bool:
        """Check if message looks like actual Ingress statistics data - MUCH MORE CONSERVATIVE"""
        if not message_text or len(message_text) < 200:  # Stats are typically very long (increased from 100)
            return False
        
        # First, check for the required prefix pattern - this is the most reliable indicator
        has_prefix, _ = self.ingress_prefix_detector.has_required_prefix(message_text)
        if has_prefix:
            return True
        
        # Look for VERY specific Ingress statistics patterns that are unlikely to appear in normal conversation
        # These are complete phrases that appear in actual Ingress statistics exports
        specific_ingress_patterns = [
            'time span agent name',
            'agent faction',
            'lifetime ap',
            'current ap',
            'unique portals visited',
            'portals discovered',
            'xm collected',
            'resonators deployed',
            'links created',
            'control fields created',
            'mind units captured',
            'portals captured',
            'unique portals captured',
            'mods deployed',
            'resonators destroyed',
            'portals neutralized',
            'enemy links destroyed',
            'enemy fields destroyed',
            'kinetic capsules completed',
            'unique missions completed',
            'glyph hack points',
            'longest sojourner streak',
            'max time portal held',
            'max time link maintained',
            'max link length x days',
            'max time field held',
            'largest field mus x days',
            'opr agreements',
            'portal scans uploaded',
            'uniques scout controlled',
            'machina portals reclaimed'
        ]
        
        # Convert to lowercase for case-insensitive matching
        text_lower = message_text.lower()
        
        # Count how many SPECIFIC patterns are found (not just keywords)
        pattern_count = sum(1 for pattern in specific_ingress_patterns if pattern in text_lower)
        
        # Require a much higher threshold - at least 12 specific patterns
        if pattern_count >= 12:
            return True
        
        # Additional check: Look for structured data format typical of Ingress stats
        # Must have many lines with colons and numbers (typical stats format)
        lines = message_text.split('\n')
        stats_lines = 0
        
        for line in lines:
            line = line.strip()
            # Look for lines that have a colon and contain numbers (typical stats format)
            if ':' in line and any(char.isdigit() for char in line):
                # Check if this line contains any of our specific patterns
                if any(pattern in line.lower() for pattern in specific_ingress_patterns):
                    stats_lines += 1
        
        # Only consider it stats if we have many structured lines AND some specific patterns
        if stats_lines >= 15 and pattern_count >= 8:
            return True
        
        # If none of the above conditions are met, it's probably not Ingress stats
        return False
    
    async def handle_message(self, update: Update, context: CallbackContext):
        """Handle text messages with controlled submission acceptance"""
        # Check if we should respond to this message
        should_respond = self._should_respond_to_message(update, context)
        
        if not should_respond:
            # In strict mode, silently ignore messages without required conditions
            return
        
        user_id = update.effective_user.id
        message_text = update.message.text.strip()
        
        # Remove bot mention from message text if present
        message_text = message_text.replace(f"@{BOT_USERNAME}", "").strip()
        
        # Check if user is in broadcast mode (after /broadcast command)
        if context.user_data.get('state') == 'awaiting_broadcast':
            from config.settings import ADMIN_USER_IDS
            # Verify user is still admin
            if user_id in ADMIN_USER_IDS:
                # Get command handlers instance to call broadcast method
                from ..handlers import CommandHandlers
                command_handler = CommandHandlers(self.db, self.leaderboard, self.parser)
                await command_handler._send_broadcast(update, context, message_text)
            else:
                await update.message.reply_text(
                    "❌ **Access Denied**\n\n"
                    "_This command is only available to administrators._",
                    parse_mode='Markdown'
                )
                context.user_data.pop('state', None)
            return
        
        # Check if user is in data submission mode (after /submit command or Submit button)
        if context.user_data.get('state') == 'awaiting_data':
            # Use enhanced handlers for better parsing and spreadsheet layout
            await self.enhanced_handlers.handle_stats_message(update, context)
            return
        
        # Check if this is a reply to a bot message (Submit button flow)
        message = update.message
        if message.reply_to_message and message.reply_to_message.from_user.is_bot:
            if message.reply_to_message.from_user.username == BOT_USERNAME:
                # This is a reply to our bot message
                # In strict mode, only process if it has the required prefix or valid Ingress data
                should_process_reply, reply_reason, reply_prefix_info = self.ingress_prefix_detector.should_process_message(message_text)
                
                if should_process_reply:
                    # Has required prefix - process it
                    detection_result = self._analyze_message(message_text, user_id)
                    if detection_result['type'] == 'ingress_data':
                        # Valid stats data in reply to bot message - use enhanced processing
                        await self.enhanced_handlers.handle_stats_message(update, context)
                        return
                    else:
                        # Has prefix but not valid stats data
                        reply_markup = self._create_navigation_buttons(context_type="data_help")
                        await update.message.reply_text(
                            "🤔 **I found the required prefix but don't recognize this as complete Ingress statistics**\n\n"
                            "💡 **To submit your stats:**\n"
                            "1. Go to Ingress → Agent → Statistics\n"
                            "2. Copy ALL your statistics data\n"
                            "3. Reply to this message with the complete data\n\n"
                            "Or use the **Submit** button below for guided submission.",
                            reply_markup=reply_markup,
                            parse_mode='Markdown'
                        )
                        return
                else:
                    # Reply to bot but no required prefix - in strict mode, ignore silently
                    if self.ingress_prefix_detector.strict_mode:
                        logger.info(f"Reply to bot message ignored in strict mode - no required prefix: {reply_reason}")
                        return
                    else:
                        # In flexible mode, still try to help
                        detection_result = self._analyze_message(message_text, user_id)
                        if detection_result['type'] == 'ingress_data':
                            # Valid stats data in reply to bot message - use enhanced processing
                            await self.enhanced_handlers.handle_stats_message(update, context)
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
        
        # Check if bot is mentioned - always respond to mentions
        is_mentioned = False
        original_message_text = update.message.text.strip()  # Keep original text for mention detection
        if message.entities:
            for entity in message.entities:
                if entity.type == "mention":
                    mention_text = original_message_text[entity.offset:entity.offset + entity.length]
                    if mention_text == f"@{BOT_USERNAME}":
                        is_mentioned = True
                        break
        
        # NEW: Check if message should be processed based on "Time Span Agent Name" prefix requirements
        should_process, reason, prefix_info = self.ingress_prefix_detector.should_process_message(message_text)
        
        # In strict mode, only respond if:
        # 1. Message has required prefix, OR
        # 2. Bot is mentioned, OR  
        # 3. User is in submission state (already handled above), OR
        # 4. Message is reply to bot (already handled above)
        if not should_process and not is_mentioned:
            # In strict mode, silently ignore messages without required prefix unless mentioned
            logger.info(f"Message ignored due to strict mode - no required prefix found and bot not mentioned: {reason}")
            return
        
        # If bot is mentioned but no stats data, provide simple guidance
        if is_mentioned and not should_process:
            reply_markup = self._create_navigation_buttons(context_type="data_help")
            await update.message.reply_text(
                "👋 Hi! To submit your Ingress stats, use the **Submit** button below or copy your complete statistics from the Ingress app.",
                reply_markup=reply_markup
            )
            return
        
        # Process the message for Ingress data
        processing_text = self.ingress_prefix_detector.get_processing_text(message_text)
        detection_result = self._analyze_message(processing_text, user_id)
        
        if detection_result['type'] == 'ingress_data':
            # Valid stats data - use enhanced processing for better parsing and layout
            await self.enhanced_handlers.handle_stats_message(update, context)
            return
        
        elif detection_result['type'] == 'partial_data':
            # Only respond if mentioned or looks like a genuine attempt
            if is_mentioned:
                reply_markup = self._create_navigation_buttons(context_type="data_help")
                await update.message.reply_text(
                    f"⚠️ {detection_result.get('issue', 'Incomplete data')} - Please copy your complete statistics from Ingress.",
                    reply_markup=reply_markup
                )
            return
        
        # For any other case, only respond if explicitly mentioned
        elif is_mentioned:
            reply_markup = self._create_navigation_buttons(context_type="data_help")
            await update.message.reply_text(
                "🤔 I don't see Ingress statistics in your message. Use the **Submit** button below for help.",
                reply_markup=reply_markup
            )
    
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
            if len(parts) >= 50:  # Sufficient fields
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
                    'issue': f"only {len(parts)} fields found, need 50+ complete statistics.",
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
            if len(parts) >= 50:  # Sufficient fields
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
                    'issue': f"only {len(parts)} fields found, need 50+ complete statistics.",
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
                        'issue': f"only {len(parts)} fields found, need 50+ complete statistics.",
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
        
        # ENHANCED: Check for "Time Span Agent Name" prefix first
        should_process, reason, ingress_prefix_info = self.ingress_prefix_detector.should_process_message(data_text)
        
        if not should_process:
            # In strict mode, don't process without required prefix
            guidance_message = self.ingress_prefix_detector.create_user_guidance_message(False, ingress_prefix_info)
            reply_markup = self._create_navigation_buttons(context_type="data_help")
            
            await update.message.reply_text(
                guidance_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
        
        # Use clean text from Ingress prefix detector (removes "Time Span Agent Name" if found)
        data_text = self.ingress_prefix_detector.get_processing_text(data_text)
        
        # Also check for legacy prefixes and clean further if needed
        prefix_result = self.prefix_detector.detect_prefix(data_text, user_id)
        if prefix_result['has_prefix']:
            # Use the clean text (legacy prefix removed) for data processing
            data_text = prefix_result['clean_text']
            logger.info(f"Processing data with legacy prefix '{prefix_result['prefix_text']}' removed")
        
        if ingress_prefix_info.get('pattern_found'):
            logger.info(f"Processing data with 'Time Span Agent Name' prefix detected at {ingress_prefix_info.get('pattern_location', 'unknown location')}")
        
        # Process submission directly instead of creating temporary handler instances
        await self._process_submission_data_internal(update, context, data_text)
        return
    
    async def _process_submission_data_internal(self, update: Update, context: CallbackContext, data_text: str):
        """Internal method to process submitted Ingress data efficiently for concurrent users"""
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
                
                reply_markup = self._create_navigation_buttons(context_type="error")
                await update.message.reply_text(error_message, reply_markup=reply_markup, parse_mode='Markdown')
                return
            
            # If some lines had errors but we got some valid data, show warnings
            if parse_errors and parsed_data_list:
                warning_msg = f"⚠️ **Processed {len(parsed_data_list)} submissions, but found issues:**\n\n"
                for error in parse_errors[:2]:  # Show first 2 errors
                    warning_msg += f"• {error.user_message}\n"
                if len(parse_errors) > 2:
                    warning_msg += f"• _...and {len(parse_errors)-2} more issues_\n"
                
                reply_markup = self._create_navigation_buttons(context_type="error")
                await update.message.reply_text(warning_msg, reply_markup=reply_markup, parse_mode='Markdown')
            
            if not parsed_data_list:
                reply_markup = self._create_navigation_buttons(context_type="error")
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
                try:
                    # Add agent to database (concurrent-safe)
                    agent_id = self.db.add_agent(
                        parsed_data['agent_name'],
                        parsed_data['faction'],
                        user_id
                    )

                    # Add submission (concurrent-safe)
                    success = self.db.add_submission(agent_id, parsed_data)

                    if success:
                        success_count += 1
                        faction_emoji = "💚" if parsed_data['faction'].lower() == 'enlightened' else "💙"
                        success_text = f"""🎉 **Stats submitted!**

{faction_emoji} **{parsed_data['agent_name']}** _({parsed_data['faction']})_
📅 {parsed_data['data_date']} at {parsed_data['data_time']}
📊 Level **{parsed_data['level']}** • ⚡ **{self.parser.format_number(parsed_data['current_ap'])}** AP

__Great work, Agent!__ 💪"""
                        
                        reply_markup = self._create_navigation_buttons(context_type="success")
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
                
                reply_markup = self._create_navigation_buttons(context_type="success")
                await update.message.reply_text(summary_msg, reply_markup=reply_markup, parse_mode='Markdown')

            # Auto-delete user's stats message if enabled and at least one submission was successful
            if success_count > 0:
                # Run delete in background to not block the response
                asyncio.create_task(self._auto_delete_user_message(update))

            # Clear user state if it was set (user-specific, concurrent-safe)
            context.user_data.pop('state', None)
                
        except Exception as e:
            logger.error(f"Unexpected error processing data submission for user {user_id}: {e}")
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
                ("📊 Submit Stats", "nav_submit"),
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