#!/usr/bin/env python3
"""
Main entry point for the Ingress Leaderboard Telegram Bot
"""

import sys
import os
import logging

from src.services.bot_service import IngressLeaderboardBot

def main():
    """Main function to start the bot"""
    # Configure logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Create and run the bot
        bot = IngressLeaderboardBot()
        logger.info("Starting Ingress Leaderboard Bot...")
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()