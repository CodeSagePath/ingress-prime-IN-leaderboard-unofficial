"""
Message handlers for the Ingress Leaderboard Bot
Enhanced with smart prefix detection for flexible stats parsing
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from config.settings import BOT_USERNAME
from ..services.prefix_detector import PrefixDetector
from ..services.ingress_prefix_detector import IngressPrefixDetector

logger = logging.getLogger(__name__)

class MessageHandlers:
    def __init__(self, db_manager, leaderboard_manager, data_parser):
        self.db = db_manager
        self.leaderboard = leaderboard_manager
        self.parser = data_parser
        self.prefix_detector = PrefixDetector(db_manager)
        self.ingress_prefix_detector = IngressPrefixDetector()
    
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
                # In strict mode, only respond to replies that have the required prefix
                if self.ingress_prefix_detector.strict_mode:
                    message_text = message.text.strip() if message.text else ""
                    should_process, reason, prefix_info = self.ingress_prefix_detector.should_process_message(message_text)
                    return should_process
                else:
                    # In flexible mode, respond to all replies to bot messages
                    return True
        
        # Check if the bot is mentioned in the message
        if message.entities:
            for entity in message.entities:
                if entity.type == "mention":
                    # Extract the mentioned username
                    mention_text = message.text[entity.offset:entity.offset + entity.length]
                    if mention_text == f"@{BOT_USERNAME}":
                        return True
        
        # Check if message has the required prefix for Ingress data
        message_text = message.text.strip() if message.text else ""
        should_process, reason, prefix_info = self.ingress_prefix_detector.should_process_message(message_text)
        
        if should_process:
            return True
        
        # In strict mode, don't respond to messages without required conditions
        if self.ingress_prefix_detector.strict_mode:
            return False
        
        # In flexible mode, respond to all messages
        return True
    
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
        
        # Check if user is in data submission mode (after /submit command or Submit button)
        if context.user_data.get('state') == 'awaiting_data':
            await self.process_data_submission(update, context)
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
        
        # If bot is mentioned but no prefix, provide guidance
        if is_mentioned and not should_process:
            guidance_message = self.ingress_prefix_detector.create_user_guidance_message(False, prefix_info)
            reply_markup = self._create_navigation_buttons(context_type="data_help")
            
            await update.message.reply_text(
                guidance_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
        
        # For all other messages (not in awaiting_data state, not replying to bot):
        # ENHANCED: Auto-process valid Ingress data with smart prefix detection
        # Use clean text (with "Time Span Agent Name" prefix removed if found)
        processing_text = self.ingress_prefix_detector.get_processing_text(message_text)
        detection_result = self._analyze_message(processing_text, user_id)
        
        # Add prefix information to detection result
        detection_result['ingress_prefix_info'] = prefix_info
        
        if detection_result['type'] == 'ingress_data':
            # Valid stats data - process it directly (ENHANCED WITH PREFIX SUPPORT)
            reply_markup = self._create_navigation_buttons(context_type="data_processing")
            
            # Enhanced response with "Time Span Agent Name" prefix acknowledgment
            ingress_prefix_info = detection_result.get('ingress_prefix_info', {})
            
            if ingress_prefix_info.get('pattern_found'):
                response_text = self.ingress_prefix_detector.create_user_guidance_message(True, ingress_prefix_info)
            else:
                response_text = "🎯 **Processing your stats data...**\n\n"
                response_text += "Thanks for submitting your statistics! ⚡"
            
            # Also check for legacy prefix detection
            if detection_result.get('prefix_info', {}).get('has_prefix'):
                legacy_prefix_info = detection_result['prefix_info']
                response_text += f"\n\n✨ **Additional prefix detected:** `{legacy_prefix_info['prefix_text']}` ({legacy_prefix_info['prefix_type']})"
            
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
            response_text += f"`{prefix_info.get('prefix_text', 'STATS:')} ALL TIME YourName Enlightened 2025-01-01 12:00:00 [your stats...]`"
            
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