#!/data/data/com.termux/files/usr/bin/bash
#
# This script will be executed on boot by the Termux:Boot application.
#

# Prevent the device from sleeping, which could kill Termux and your bot.
termux-wake-lock

# Start the SSH server for remote management.
# Ensure you have OpenSSH installed (`pkg install openssh`) and configured.
sshd

# --- Your Bot Configuration ---

# IMPORTANT: Change 'your-project-name' to your actual project directory name.
PROJECT_DIR="/data/data/com.termux/files/home/telegram-bots/ingress-leaderboard"

# Directory name for the virtual environment.
VENV_DIR="venv"

# Name for the tmux session where the bot will run.
TMUX_SESSION="bot_session"

# Log file for debugging
LOG_FILE="$PROJECT_DIR/logs/boot_debug.log"

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"

# Function to log with timestamp
log_msg() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log_msg "🚀 Boot script started"

# Navigate to your project directory.
cd "$PROJECT_DIR" || {
    log_msg "❌ Failed to change to directory: $PROJECT_DIR"
    exit 1
}

log_msg "📁 Changed to directory: $(pwd)"

# Check if .env file exists
if [ ! -f ".env" ]; then
    log_msg "❌ .env file not found in $(pwd)"
    exit 1
fi

log_msg "✅ .env file found"

# Create virtual environment if it doesn't exist.
if [ ! -d "$VENV_DIR" ]; then
    log_msg "📦 Creating virtual environment..."
    python -m venv "$VENV_DIR"
fi

# Activate venv, install/update dependencies, and start the bot in a tmux session.
source "$VENV_DIR/bin/activate" && \
log_msg "✅ Virtual environment activated" && \
pip install -r requirements.txt >> "$LOG_FILE" 2>&1 && \
log_msg "✅ Dependencies installed/updated" && \

# Kill existing session if it exists
if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
    log_msg "🔄 Killing existing tmux session"
    tmux kill-session -t "$TMUX_SESSION"
fi

# Start the bot using the enhanced startup script instead of run_bot.sh
log_msg "🤖 Starting bot in tmux session: $TMUX_SESSION" && \
tmux new-session -d -s "$TMUX_SESSION" -c "$PROJECT_DIR" "source $VENV_DIR/bin/activate && python start_termux.py 2>&1 | tee -a logs/bot_session.log"

# Check if tmux session started successfully
if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
    log_msg "✅ Bot started successfully in tmux session"
    
    # Send notification
    if command -v termux-notification >/dev/null 2>&1; then
        termux-notification --title "Ingress Bot" --content "✅ Bot started successfully on boot"
    fi
else
    log_msg "❌ Failed to start tmux session"
    
    # Send error notification
    if command -v termux-notification >/dev/null 2>&1; then
        termux-notification --title "Ingress Bot Error" --content "❌ Failed to start on boot"
    fi
fi

log_msg "🏁 Boot script completed"