"""
Enhanced Message handlers with improved data parsing and spreadsheet-like display
"""

import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.error import BadRequest
from config.settings import BOT_USERNAME, AUTO_DELETE_USER_STATS, AUTO_DELETE_DELAY_SECONDS
from ..parsers.enhanced_data_parser import EnhancedDataParser
from ..utils.spreadsheet_formatter import SpreadsheetFormatter
from ..services.prefix_detector import PrefixDetector
from ..services.ingress_prefix_detector import IngressPrefixDetector

logger = logging.getLogger(__name__)

class EnhancedMessageHandlers:
    def __init__(self, db_manager, leaderboard_manager):
        self.db = db_manager
        self.leaderboard = leaderboard_manager
        self.enhanced_parser = EnhancedDataParser()
        self.formatter = SpreadsheetFormatter()
        self.prefix_detector = PrefixDetector(db_manager)
        self.ingress_prefix_detector = IngressPrefixDetector()
    
    async def handle_enhanced_data_submission(self, update: Update, context: CallbackContext):
        """Handle data submission with enhanced parsing and validation"""
        user_id = update.effective_user.id
        message_text = update.message.text.strip()
        
        # Remove bot mention if present
        message_text = message_text.replace(f"@{BOT_USERNAME}", "").strip()
        
        try:
            # Parse the data with enhanced parser
            parse_result = self.enhanced_parser.parse_data_line(message_text)
            
            if not parse_result.success:
                # Show parsing errors with helpful suggestions
                error_message = "❌ **Data Parsing Failed**\n\n"
                error_message += "**Issues found:**\n"
                for error in parse_result.errors[:3]:  # Show first 3 errors
                    error_message += f"• {error}\n"
                
                if parse_result.warnings:
                    error_message += "\n**Suggestions:**\n"
                    for warning in parse_result.warnings[:3]:  # Show first 3 warnings
                        error_message += f"• {warning}\n"
                
                error_message += "\n💡 **Need help?** Use `/help` for data format examples."
                
                await update.message.reply_text(error_message, parse_mode='Markdown')
                return
            
            # Show parsing results with validation
            await self._show_parsing_results(update, context, parse_result)
            
        except Exception as e:
            logger.error(f"Error in enhanced data submission: {e}")
            await update.message.reply_text(
                "❌ **Unexpected Error**\n\n"
                "Something went wrong while processing your data. Please try again or contact support.",
                parse_mode='Markdown'
            )
    
    async def _show_parsing_results(self, update: Update, context: CallbackContext, parse_result):
        """Show parsing results with spreadsheet-like formatting"""
        try:
            # Store the parse result for later use
            context.user_data['parse_result'] = parse_result
            context.user_data['state'] = 'reviewing_data'
            
            # Create the formatted display
            summary, keyboard = self.formatter.create_interactive_menu(
                parse_result.data, 
                parse_result.field_validations
            )
            
            # Add confidence score info
            confidence_emoji = "✅" if parse_result.confidence_score > 0.9 else "⚠️" if parse_result.confidence_score > 0.7 else "❌"
            confidence_info = f"\n{confidence_emoji} **Confidence Score:** {parse_result.confidence_score:.1%}"
            
            # Create inline keyboard
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(btn['text'], callback_data=btn['callback_data']) for btn in row]
                for row in keyboard
            ])
            
            # Send the formatted message
            full_message = summary + confidence_info
            await update.message.reply_text(
                full_message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
            # Auto-delete user message if enabled
            if AUTO_DELETE_USER_STATS:
                await self._auto_delete_user_message(update)
                
        except Exception as e:
            logger.error(f"Error showing parsing results: {e}")
            await update.message.reply_text(
                "❌ Error displaying results. Please try again.",
                parse_mode='Markdown'
            )
    
    async def handle_view_callback(self, update: Update, context: CallbackContext):
        """Handle callback queries for different view types"""
        query = update.callback_query
        await query.answer()
        
        if 'parse_result' not in context.user_data:
            await query.edit_message_text("❌ No data available. Please submit your statistics again.")
            return
        
        parse_result = context.user_data['parse_result']
        callback_data = query.data
        
        try:
            if callback_data == 'view_summary':
                content = self.formatter.format_agent_summary(
                    parse_result.data, 
                    parse_result.field_validations
                )
            elif callback_data == 'view_detailed':
                content = self.formatter.format_detailed_stats(parse_result.data)
            elif callback_data == 'view_validation':
                content = self.formatter.format_validation_report(parse_result.field_validations)
            elif callback_data == 'view_compare':
                # For now, show a placeholder - would need leaderboard data
                content = "🏆 **Comparison View**\n\nThis feature will show how you rank against other agents. Coming soon!"
            elif callback_data == 'save_data':
                await self._save_data_to_database(update, context, parse_result)
                return
            elif callback_data == 'cancel':
                await query.edit_message_text("❌ **Cancelled**\n\nData submission cancelled.")
                context.user_data.clear()
                return
            else:
                content = "❓ Unknown view type"
            
            # Create back button
            back_keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu"),
                    InlineKeyboardButton("💾 Save Data", callback_data="save_data")
                ],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
            ])
            
            await query.edit_message_text(
                content,
                parse_mode='Markdown',
                reply_markup=back_keyboard
            )
            
        except Exception as e:
            logger.error(f"Error handling view callback: {e}")
            await query.edit_message_text("❌ Error loading view. Please try again.")
    
    async def handle_back_to_menu(self, update: Update, context: CallbackContext):
        """Handle back to menu callback"""
        query = update.callback_query
        await query.answer()
        
        if 'parse_result' not in context.user_data:
            await query.edit_message_text("❌ No data available. Please submit your statistics again.")
            return
        
        parse_result = context.user_data['parse_result']
        
        try:
            # Recreate the main menu
            summary, keyboard = self.formatter.create_interactive_menu(
                parse_result.data, 
                parse_result.field_validations
            )
            
            confidence_emoji = "✅" if parse_result.confidence_score > 0.9 else "⚠️" if parse_result.confidence_score > 0.7 else "❌"
            confidence_info = f"\n{confidence_emoji} **Confidence Score:** {parse_result.confidence_score:.1%}"
            
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(btn['text'], callback_data=btn['callback_data']) for btn in row]
                for row in keyboard
            ])
            
            full_message = summary + confidence_info
            await query.edit_message_text(
                full_message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error returning to menu: {e}")
            await query.edit_message_text("❌ Error loading menu. Please try again.")
    
    async def _save_data_to_database(self, update: Update, context: CallbackContext, parse_result):
        """Save the parsed data to database"""
        query = update.callback_query if hasattr(update, 'callback_query') and update.callback_query else None
        user_id = update.effective_user.id
        
        try:
            # Check confidence score
            if parse_result.confidence_score < 0.7:
                warning_message = (
                    f"⚠️ **Low Confidence Warning**\n\n"
                    f"The data confidence score is {parse_result.confidence_score:.1%}, which is below the recommended 70%.\n\n"
                    f"**Do you want to proceed anyway?**"
                )
                
                confirm_keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✅ Save Anyway", callback_data="force_save"),
                        InlineKeyboardButton("🔙 Review Data", callback_data="back_to_menu")
                    ],
                    [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
                ])
                
                if query:
                    await query.edit_message_text(
                        warning_message,
                        parse_mode='Markdown',
                        reply_markup=confirm_keyboard
                    )
                else:
                    await update.message.reply_text(
                        warning_message,
                        parse_mode='Markdown',
                        reply_markup=confirm_keyboard
                    )
                
                context.user_data['pending_save'] = True
                return
            
            # Proceed with saving
            await self._perform_database_save(update, context, parse_result)
            
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            error_message = "❌ **Save Failed**\n\nThere was an error saving your data. Please try again."
            
            if query:
                await query.edit_message_text(error_message, parse_mode='Markdown')
            else:
                await update.message.reply_text(error_message, parse_mode='Markdown')
    
    async def handle_force_save(self, update: Update, context: CallbackContext):
        """Handle forced save with low confidence"""
        query = update.callback_query
        await query.answer()
        
        if 'parse_result' not in context.user_data:
            await query.edit_message_text("❌ No data available. Please submit your statistics again.")
            return
        
        parse_result = context.user_data['parse_result']
        await self._perform_database_save(update, context, parse_result)
    
    async def _perform_database_save(self, update: Update, context: CallbackContext, parse_result):
        """Actually save the data to the database"""
        query = update.callback_query if hasattr(update, 'callback_query') and update.callback_query else None
        user_id = update.effective_user.id
        
        try:
            # Add agent to database
            agent_id = self.db.add_agent(
                parse_result.data['agent_name'],
                parse_result.data['faction'],
                user_id
            )
            
            # Add submission
            success = self.db.add_submission(agent_id, parse_result.data)
            
            if success:
                success_message = (
                    f"✅ **Data Saved Successfully!**\n\n"
                    f"**Agent:** {parse_result.data['agent_name']}\n"
                    f"**Faction:** {parse_result.data['faction']}\n"
                    f"**Level:** {parse_result.data['level']}\n"
                    f"**Current AP:** {self.enhanced_parser.format_number(parse_result.data['current_ap'])}\n\n"
                    f"Your statistics have been added to the leaderboard! 🎉"
                )
                
                # Create navigation buttons
                nav_keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("🏆 View Leaderboard", callback_data="nav_leaderboard"),
                        InlineKeyboardButton("📈 My Progress", callback_data="nav_progress")
                    ],
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="nav_main_menu")]
                ])
                
                if query:
                    await query.edit_message_text(
                        success_message,
                        parse_mode='Markdown',
                        reply_markup=nav_keyboard
                    )
                else:
                    await update.message.reply_text(
                        success_message,
                        parse_mode='Markdown',
                        reply_markup=nav_keyboard
                    )
                
                # Clear user data
                context.user_data.clear()
                
            else:
                error_message = "❌ **Database Error**\n\nFailed to save your data. Please try again later."
                
                if query:
                    await query.edit_message_text(error_message, parse_mode='Markdown')
                else:
                    await update.message.reply_text(error_message, parse_mode='Markdown')
                    
        except Exception as e:
            logger.error(f"Error performing database save: {e}")
            error_message = f"❌ **Save Error**\n\nDatabase error: {str(e)}"
            
            if query:
                await query.edit_message_text(error_message, parse_mode='Markdown')
            else:
                await update.message.reply_text(error_message, parse_mode='Markdown')
    
    async def _auto_delete_user_message(self, update: Update):
        """Auto-delete user's stats message to keep chat clean"""
        if not AUTO_DELETE_USER_STATS:
            return
        
        try:
            if AUTO_DELETE_DELAY_SECONDS > 0:
                await asyncio.sleep(AUTO_DELETE_DELAY_SECONDS)
            
            await update.message.delete()
            logger.info(f"Successfully deleted stats message from user {update.effective_user.id}")
            
        except BadRequest as e:
            if "Message can't be deleted" in str(e) or "not enough rights" in str(e):
                logger.warning(
                    f"Cannot delete message - bot needs admin privileges with 'delete messages' permission. "
                    f"Chat: {update.effective_chat.id}, User: {update.effective_user.id}"
                )
            else:
                logger.warning(f"Failed to delete user message: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while deleting user message: {e}")
    
    def create_enhanced_help_message(self) -> str:
        """Create enhanced help message with examples"""
        help_message = """
🎯 **Enhanced Data Submission Guide**

**New Features:**
✅ **Automatic field detection** - No more data mismatches!
✅ **Spreadsheet-like display** - Clear, organized view of your stats
✅ **Data validation** - Automatic error detection and suggestions
✅ **Confidence scoring** - Know how reliable your data parsing is

**How to Submit:**
1. Copy your statistics from Ingress → Agent → Statistics
2. Send `/submit` followed by your data, or just paste your stats
3. Review the formatted display with validation results
4. Choose different views: Summary, Detailed, or Validation Report
5. Save when you're satisfied with the results

**Example Format:**
```
ALL TIME YourAgent Enlightened 2025-01-15 12:30:45 16 50000000 25000000 ...
```

**What's New:**
• **Smart parsing** - Handles variations in data format
• **Visual tables** - Easy-to-read spreadsheet-like layout
• **Error detection** - Spots when data might be in wrong fields
• **Confidence scores** - Shows how reliable the parsing is
• **Interactive menus** - Switch between different views easily

**Need Help?**
If you see low confidence scores or validation errors, the bot will suggest corrections automatically!
        """
        return help_message.strip()