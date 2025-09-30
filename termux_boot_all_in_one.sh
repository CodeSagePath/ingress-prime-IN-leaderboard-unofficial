#!/data/data/com.termux/files/usr/bin/bash
#
# Termux Boot Script - Ingress Leaderboard Bot
# This script will be executed on boot by the Termux:Boot application.
# Place this file in ~/.termux/boot/ directory and make it executable.
#

# Prevent the device from sleeping, which could kill Termux and your bot.
termux-wake-lock

# Start the SSH server for remote management (optional).
# Ensure you have OpenSSH installed (`pkg install openssh`) and configured.
# Uncomment the next line if you want SSH access:
# sshd

# --- Bot Configuration ---

# IMPORTANT: Change this to your actual project directory path.
PROJECT_DIR="/data/data/com.termux/files/home/telegram-bots/ingress-leaderboard"

# Directory name for the virtual environment.
VENV_DIR="venv"

# Name for the tmux session where the bot will run.
TMUX_SESSION="ingress_bot"

# Requirements file (will try both termux-specific and regular).
REQUIREMENTS_FILES=("requirements-termux.txt" "requirements.txt")

# Log file for boot process.
BOOT_LOG="$PROJECT_DIR/logs/boot.log"

# --- Logging Setup ---

# Create logs directory and setup logging function.
mkdir -p "$PROJECT_DIR/logs" 2>/dev/null

log() {
    local message="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo "$message"
    echo "$message" >> "$BOOT_LOG" 2>/dev/null || true
}

# --- Main Boot Sequence ---

log "🚀 Starting Ingress Bot boot sequence..."

# Wait for system to stabilize after boot.
sleep 10
log "⏳ System stabilized"

# Check if project directory exists.
if [ ! -d "$PROJECT_DIR" ]; then
    log "❌ Project directory not found: $PROJECT_DIR"
    termux-notification --title "Ingress Bot Error" --content "Project directory not found" 2>/dev/null || true
    exit 1
fi

# Navigate to project directory.
cd "$PROJECT_DIR" || {
    log "❌ Failed to navigate to project directory"
    exit 1
}

log "📁 Changed to project directory: $(pwd)"

# Ensure required packages are installed.
if ! command -v python >/dev/null 2>&1; then
    log "📦 Installing Python..."
    pkg install -y python python-pip git sqlite 2>/dev/null || {
        log "❌ Failed to install Python packages"
        exit 1
    }
fi

if ! command -v tmux >/dev/null 2>&1; then
    log "📦 Installing tmux..."
    pkg install -y tmux 2>/dev/null || {
        log "❌ Failed to install tmux"
        exit 1
    }
fi

# Create virtual environment if it doesn't exist.
if [ ! -d "$VENV_DIR" ]; then
    log "🐍 Creating virtual environment..."
    python -m venv "$VENV_DIR" || {
        log "❌ Failed to create virtual environment"
        exit 1
    }
    log "✅ Virtual environment created"
else
    log "✅ Virtual environment exists"
fi

# Activate virtual environment.
log "🔄 Activating virtual environment..."
source "$VENV_DIR/bin/activate" || {
    log "❌ Failed to activate virtual environment"
    exit 1
}

# Upgrade pip.
log "⬆️ Upgrading pip..."
python -m pip install --upgrade pip --quiet 2>/dev/null || {
    log "⚠️ Pip upgrade failed, continuing"
}

# Install/update dependencies.
log "📚 Installing dependencies..."
REQUIREMENTS_INSTALLED=false

for req_file in "${REQUIREMENTS_FILES[@]}"; do
    if [ -f "$req_file" ]; then
        log "📋 Installing from $req_file..."
        if python -m pip install -r "$req_file" --quiet 2>/dev/null; then
            log "✅ Dependencies installed from $req_file"
            REQUIREMENTS_INSTALLED=true
            break
        else
            log "⚠️ Failed to install from $req_file, trying next..."
        fi
    fi
done

# Fallback to essential packages if requirements files failed.
if [ "$REQUIREMENTS_INSTALLED" = false ]; then
    log "📋 Installing essential packages..."
    python -m pip install python-telegram-bot requests python-dotenv --quiet 2>/dev/null || {
        log "❌ Failed to install essential packages"
        exit 1
    }
    log "✅ Essential packages installed"
fi

# Check configuration.
log "⚙️ Checking configuration..."
if [ ! -f "config/config.py" ]; then
    if [ -f "config/config.example.py" ]; then
        log "📝 Creating config from example..."
        cp config/config.example.py config/config.py
        log "⚠️ Please configure your bot token in config/config.py"
        termux-notification --title "Ingress Bot Setup" --content "Please configure bot token" 2>/dev/null || true
    else
        log "❌ No configuration files found"
        exit 1
    fi
fi

# Quick config validation.
if python -c "
import sys
sys.path.insert(0, '.')
try:
    from config.config import BOT_TOKEN
    if BOT_TOKEN and BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE':
        exit(0)
    else:
        exit(1)
except:
    exit(1)
" 2>/dev/null; then
    log "✅ Bot token configured"
else
    log "❌ Bot token not configured properly"
    termux-notification --title "Ingress Bot Error" --content "Bot token not configured" 2>/dev/null || true
    exit 1
fi

# Check if bot is already running in tmux.
if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
    log "⚠️ Bot session already exists: $TMUX_SESSION"
    termux-notification --title "Ingress Bot" --content "Bot already running" 2>/dev/null || true
else
    # Start the bot in a new tmux session.
    log "🤖 Starting bot in tmux session: $TMUX_SESSION"
    
    tmux new-session -d -s "$TMUX_SESSION" -c "$PROJECT_DIR" \
        "source $VENV_DIR/bin/activate && python main.py" || {
        log "❌ Failed to start bot in tmux"
        exit 1
    }
    
    # Wait a moment and verify the session started.
    sleep 5
    if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
        log "✅ Bot started successfully in tmux session: $TMUX_SESSION"
        termux-notification --title "🎮 Ingress Bot Started" \
            --content "Bot running in tmux session: $TMUX_SESSION" 2>/dev/null || true
    else
        log "❌ Bot session failed to start"
        termux-notification --title "Ingress Bot Error" --content "Failed to start bot" 2>/dev/null || true
        exit 1
    fi
fi

# Set up health monitoring in background.
{
    log "💓 Starting health monitor..."
    sleep 300  # Wait 5 minutes before first check
    
    while true; do
        if ! tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
            log "🔄 Bot session died, restarting..."
            termux-notification --title "Ingress Bot" --content "Restarting bot..." 2>/dev/null || true
            
            cd "$PROJECT_DIR"
            source "$VENV_DIR/bin/activate"
            tmux new-session -d -s "$TMUX_SESSION" -c "$PROJECT_DIR" \
                "source $VENV_DIR/bin/activate && python main.py"
            
            sleep 10
            if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
                log "✅ Bot restarted successfully"
                termux-notification --title "Ingress Bot" --content "Bot restarted" 2>/dev/null || true
            else
                log "❌ Bot restart failed"
                termux-notification --title "Ingress Bot Error" --content "Restart failed" 2>/dev/null || true
            fi
        fi
        sleep 600  # Check every 10 minutes
    done
} &

MONITOR_PID=$!
echo $MONITOR_PID > "$PROJECT_DIR/logs/monitor.pid"
log "👁️ Health monitor started (PID: $MONITOR_PID)"

# Create convenience scripts for management.
log "🔧 Creating management scripts..."

# Bot status script.
cat > "$PROJECT_DIR/bot_status.sh" << 'EOFSTATUS'
#!/data/data/com.termux/files/usr/bin/bash
TMUX_SESSION="ingress_bot"
echo "🤖 Ingress Bot Status"
echo "==================="
if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
    echo "✅ Bot is RUNNING in tmux session: $TMUX_SESSION"
    echo "📊 Session info:"
    tmux list-sessions | grep "$TMUX_SESSION"
    echo ""
    echo "🔍 To view bot console:"
    echo "   tmux attach -t $TMUX_SESSION"
    echo ""
    echo "🛑 To stop bot:"
    echo "   tmux kill-session -t $TMUX_SESSION"
else
    echo "❌ Bot is NOT RUNNING"
fi
echo ""
echo "📋 Recent boot log entries:"
tail -n 5 logs/boot.log 2>/dev/null || echo "No boot log found"
EOFSTATUS

# Bot control script.
cat > "$PROJECT_DIR/bot_control.sh" << 'EOFCONTROL'
#!/data/data/com.termux/files/usr/bin/bash
TMUX_SESSION="ingress_bot"
PROJECT_DIR="/data/data/com.termux/files/home/telegram-bots/ingress-leaderboard"

case "$1" in
    start)
        if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
            echo "⚠️ Bot is already running"
        else
            echo "🚀 Starting bot..."
            cd "$PROJECT_DIR"
            source venv/bin/activate
            tmux new-session -d -s "$TMUX_SESSION" -c "$PROJECT_DIR" \
                "source venv/bin/activate && python main.py"
            echo "✅ Bot started in tmux session: $TMUX_SESSION"
        fi
        ;;
    stop)
        if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
            echo "🛑 Stopping bot..."
            tmux kill-session -t "$TMUX_SESSION"
            echo "✅ Bot stopped"
        else
            echo "⚠️ Bot is not running"
        fi
        ;;
    restart)
        echo "🔄 Restarting bot..."
        tmux kill-session -t "$TMUX_SESSION" 2>/dev/null || true
        sleep 2
        cd "$PROJECT_DIR"
        source venv/bin/activate
        tmux new-session -d -s "$TMUX_SESSION" -c "$PROJECT_DIR" \
            "source venv/bin/activate && python main.py"
        echo "✅ Bot restarted"
        ;;
    console)
        if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
            echo "🖥️ Attaching to bot console (Ctrl+B, D to detach)..."
            tmux attach -t "$TMUX_SESSION"
        else
            echo "❌ Bot is not running"
        fi
        ;;
    *)
        echo "🤖 Ingress Bot Control"
        echo "Usage: $0 {start|stop|restart|console}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the bot"
        echo "  stop    - Stop the bot"
        echo "  restart - Restart the bot"
        echo "  console - Attach to bot console"
        ;;
esac
EOFCONTROL

chmod +x "$PROJECT_DIR/bot_status.sh" "$PROJECT_DIR/bot_control.sh"

log "🎮 Boot sequence completed successfully!"
log ""
log "📋 Management commands:"
log "   Status: $PROJECT_DIR/bot_status.sh"
log "   Control: $PROJECT_DIR/bot_control.sh {start|stop|restart|console}"
log "   View console: tmux attach -t $TMUX_SESSION"
log "   Boot logs: tail -f $PROJECT_DIR/logs/boot.log"
log ""
log "🔧 Tmux session: $TMUX_SESSION"
log "💓 Health monitor PID: $MONITOR_PID"

# Final success notification.
termux-notification \
    --title "🎮 Ingress Bot Ready!" \
    --content "Bot running in tmux session: $TMUX_SESSION" \
    --button1 "Status" \
    --button1-action "bash $PROJECT_DIR/bot_status.sh" 2>/dev/null || true

log "🚀 Ingress Bot is now running and monitored!"