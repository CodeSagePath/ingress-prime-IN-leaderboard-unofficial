#!/usr/bin/env python3
"""
Main entry point for the Ingress Leaderboard Telegram Bot
Optimized for both standard systems and Termux (Android)
"""

import sys
import os
import logging
import logging.config
import signal
import atexit

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.bot_service import IngressLeaderboardBot

# Import Termux-specific settings
try:
    from config.termux_settings import (
        IS_TERMUX, LOGGING_CONFIG, get_termux_info, 
        send_termux_notification, acquire_wake_lock, release_wake_lock
    )
except ImportError:
    IS_TERMUX = False
    LOGGING_CONFIG = None

def setup_logging():
    """Setup logging configuration"""
    if LOGGING_CONFIG:
        logging.config.dictConfig(LOGGING_CONFIG)
    else:
        # Fallback logging configuration
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

def setup_termux():
    """Setup Termux-specific configurations"""
    if not IS_TERMUX:
        return
    
    # Get Termux info
    termux_info = get_termux_info()
    if termux_info:
        logger = logging.getLogger(__name__)
        logger.info(f"Running in Termux environment")
        logger.info(f"Storage available: {termux_info['storage_available']}")
        logger.info(f"Termux API available: {termux_info['termux_api_available']}")
    
    # Acquire wake lock to prevent Android from killing the process
    if acquire_wake_lock():
        logger.info("Wake lock acquired - bot will stay active")
        # Register cleanup function
        atexit.register(release_wake_lock)
    else:
        logger.warning("Could not acquire wake lock - bot may be killed by Android")
    
    # Send startup notification
    send_termux_notification("Ingress Bot", "Bot is starting up...")

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger = logging.getLogger(__name__)
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    
    # Clean up lock file
    try:
        from check_bot_status import remove_lock_file
        remove_lock_file()
    except ImportError:
        pass
    
    if IS_TERMUX:
        send_termux_notification("Ingress Bot", "Bot is shutting down...")
        release_wake_lock()
    
    sys.exit(0)

def main():
    """Main function to start the bot"""
    # Setup logging first
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Check for multiple instances before starting
    try:
        from check_bot_status import check_bot_running, create_lock_file, remove_lock_file
        
        # Check for running processes
        running_bots = check_bot_running()
        if running_bots:
            error_msg = "⚠️  Multiple bot instances detected!\n"
            error_msg += "Found running bot instances:\n"
            for bot in running_bots:
                error_msg += f"   PID {bot['pid']}: {bot['cmdline']}\n"
            error_msg += "\n❌ Please stop other instances before starting a new one!"
            logger.error(error_msg)
            print(error_msg)
            return
        
        # Create lock file
        can_run, message = create_lock_file()
        if not can_run:
            logger.error(f"Cannot start bot: {message}")
            print(f"❌ {message}")
            return
        
        # Register cleanup function for lock file
        atexit.register(remove_lock_file)
        
    except ImportError:
        logger.warning("Bot status check not available, proceeding without instance check")
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Setup Termux-specific configurations
    setup_termux()
    
    try:
        # Create and run the bot
        logger.info("Initializing Ingress Leaderboard Bot...")
        bot = IngressLeaderboardBot()
        
        logger.info("Starting Ingress Leaderboard Bot...")
        if IS_TERMUX:
            send_termux_notification("Ingress Bot", "Bot is now running!")
        
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
        if IS_TERMUX:
            send_termux_notification("Ingress Bot", "Bot stopped by user")
    except Exception as e:
        logger.error(f"Error starting bot: {e}", exc_info=True)
        if IS_TERMUX:
            send_termux_notification("Ingress Bot Error", f"Bot crashed: {str(e)[:50]}...")
        sys.exit(1)
    finally:
        # Cleanup
        if IS_TERMUX:
            release_wake_lock()
            logger.info("Cleanup completed")

if __name__ == "__main__":
    main()