#!/data/data/com.termux/files/usr/bin/bash

# Termux Setup Script for Ingress Leaderboard Bot
# This script sets up the bot environment in Termux

echo "🚀 Setting up Ingress Leaderboard Bot for Termux..."

# Check if we're running in Termux
if [[ ! "$PREFIX" == *"com.termux"* ]]; then
    echo "⚠️  Warning: This script is designed for Termux. Some features may not work on other systems."
fi

# Update packages
echo "📦 Updating Termux packages..."
pkg update -y

# Install required system packages
echo "🔧 Installing system dependencies..."
pkg install -y python python-pip git sqlite

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data logs config

# Set up configuration if it doesn't exist
if [ ! -f "config/config.py" ]; then
    if [ -f "config/config.example.py" ]; then
        echo "⚙️  Creating configuration file..."
        cp config/config.example.py config/config.py
        echo "📝 Please edit config/config.py and add your bot token"
    fi
fi

# Set up database
echo "🗄️  Setting up database..."
python setup.py

# Create startup script for Termux
echo "📜 Creating Termux startup script..."
cat > start_bot_termux.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash

# Termux Bot Startup Script
echo "🤖 Starting Ingress Leaderboard Bot..."

# Navigate to bot directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Start the bot
python main.py
EOF

chmod +x start_bot_termux.sh

# Create service script for background running
echo "🔧 Creating background service script..."
cat > run_bot_background.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash

# Run bot in background with logging
cd "$(dirname "$0")"
source venv/bin/activate

# Create logs directory if it doesn't exist
mkdir -p logs

# Run bot in background with output logging
nohup python main.py > logs/bot.log 2>&1 &

# Save PID for stopping later
echo $! > logs/bot.pid

echo "🤖 Bot started in background. PID: $(cat logs/bot.pid)"
echo "📋 View logs: tail -f logs/bot.log"
echo "🛑 Stop bot: kill $(cat logs/bot.pid)"
EOF

chmod +x run_bot_background.sh

# Create stop script
echo "🛑 Creating stop script..."
cat > stop_bot.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash

if [ -f "logs/bot.pid" ]; then
    PID=$(cat logs/bot.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo "🛑 Bot stopped (PID: $PID)"
        rm logs/bot.pid
    else
        echo "❌ Bot is not running"
        rm logs/bot.pid
    fi
else
    echo "❌ No PID file found. Bot may not be running."
fi
EOF

chmod +x stop_bot.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit config/config.py and add your Telegram bot token"
echo "2. Run the bot:"
echo "   • Foreground: ./start_bot_termux.sh"
echo "   • Background: ./run_bot_background.sh"
echo "3. Stop background bot: ./stop_bot.sh"
echo ""
echo "📱 Termux-specific tips:"
echo "• Use 'termux-wake-lock' to prevent Android from killing the bot"
echo "• Consider using 'termux-notification' for status updates"
echo "• The bot will auto-restart if you use the background script"
echo ""
echo "🎮 Happy hunting, Agent!"