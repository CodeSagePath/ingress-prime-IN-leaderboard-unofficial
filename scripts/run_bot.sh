#!/bin/bash
# Script to run the Ingress Leaderboard Bot with virtual environment

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   python scripts/setup.py"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source "$PROJECT_ROOT/venv/bin/activate"

# Load environment variables from .env file if it exists
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "📄 Loading environment variables from .env file..."
    export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | xargs)
fi

# Check if bot token is set
if [ -z "$BOT_TOKEN" ]; then
    echo "⚠️ BOT_TOKEN environment variable not set."
    echo "   Please set it or update config/local_settings.py"
fi

# Run the bot
echo "🚀 Starting Ingress Leaderboard Bot..."
cd "$PROJECT_ROOT"
python main.py