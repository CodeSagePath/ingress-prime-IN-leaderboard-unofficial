#!/data/data/com.termux/files/usr/bin/bash

# Simple Ingress Bot Boot Script
# Place in ~/.termux/boot/start_ingress_bot.sh

# Wait for system to be ready
sleep 10

# Change to bot directory
cd "$HOME/telegram-bots/ingress-leaderboard"

# Start the bot
python start_termux.py >> logs/boot.log 2>&1 &

# Send notification if available
if command -v termux-notification >/dev/null 2>&1; then
    termux-notification --title "Ingress Bot" --content "Bot started on boot"
fi