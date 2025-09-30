#!/data/data/com.termux/files/usr/bin/bash

# Ingress Leaderboard Bot - Termux Boot Script
# Place this file in ~/.termux/boot/ directory
# Make it executable: chmod +x ~/.termux/boot/boot_ingress_bot.sh

# Configuration
BOT_DIR="$HOME/telegram-bots/ingress-leaderboard"
LOG_FILE="$HOME/telegram-bots/ingress-leaderboard/logs/boot.log"
PYTHON_SCRIPT="start_termux.py"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to send notification if termux-api is available
notify() {
    if command -v termux-notification >/dev/null 2>&1; then
        termux-notification --title "Ingress Bot" --content "$1"
    fi
}

# Start of boot script
log_message "🚀 Boot script started"
notify "Starting Ingress Bot..."

# Wait a bit for system to settle
log_message "⏳ Waiting 10 seconds for system to settle..."
sleep 10

# Check if bot directory exists
if [ ! -d "$BOT_DIR" ]; then
    log_message "❌ Bot directory not found: $BOT_DIR"
    notify "❌ Bot directory not found!"
    exit 1
fi

# Change to bot directory
cd "$BOT_DIR" || {
    log_message "❌ Failed to change to bot directory: $BOT_DIR"
    notify "❌ Failed to access bot directory!"
    exit 1
}

log_message "📁 Changed to directory: $(pwd)"

# Check if .env file exists
if [ ! -f ".env" ]; then
    log_message "❌ .env file not found in $(pwd)"
    notify "❌ .env file not found!"
    exit 1
fi

log_message "✅ .env file found"

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    log_message "❌ Python script not found: $PYTHON_SCRIPT"
    notify "❌ Python script not found!"
    exit 1
fi

log_message "✅ Python script found: $PYTHON_SCRIPT"

# Acquire wake lock
if command -v termux-wake-lock >/dev/null 2>&1; then
    termux-wake-lock
    log_message "🔒 Wake lock acquired"
else
    log_message "⚠️ termux-wake-lock not available"
fi

# Start the bot
log_message "🤖 Starting Ingress Leaderboard Bot..."
notify "🤖 Ingress Bot is starting..."

# Run the bot and capture output
python "$PYTHON_SCRIPT" >> "$LOG_FILE" 2>&1 &
BOT_PID=$!

log_message "🔢 Bot started with PID: $BOT_PID"

# Wait a moment to check if bot started successfully
sleep 5

if kill -0 "$BOT_PID" 2>/dev/null; then
    log_message "✅ Bot is running successfully (PID: $BOT_PID)"
    notify "✅ Ingress Bot is running!"
    
    # Create PID file for later reference
    echo "$BOT_PID" > "$BOT_DIR/bot.pid"
    
    # Wait for the bot process (this keeps the boot script alive)
    wait "$BOT_PID"
    
    log_message "⏹️ Bot process ended (PID: $BOT_PID)"
    notify "⏹️ Ingress Bot stopped"
else
    log_message "❌ Bot failed to start or crashed immediately"
    notify "❌ Bot failed to start!"
    exit 1
fi

log_message "🏁 Boot script completed"