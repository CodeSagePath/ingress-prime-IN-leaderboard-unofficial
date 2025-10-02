# 🎮 Ingress Leaderboard Telegram Bot

A comprehensive Telegram bot for tracking and comparing Ingress game statistics with faction-based leaderboards, progress tracking, and local data storage.

## 🏗️ Project Structure

```
ingress-leaderboard/
├── venv/                    # Virtual environment
├── src/                     # Source code
│   ├── handlers/
│   ├── database/
│   ├── parsers/
│   ├── services/
│   └── utils/
├── config/                 # Configuration files
│   └── config.py
├── tests/                  # Test files
│   └── test_bot.py
├── scripts/                # Utility scripts
│   └── run_bot.sh
├── .env                     # Environment variables (for BOT_TOKEN)
├── .gitignore
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── setup.py                # Project setup script
└── setup.cfg               # Project configuration
```

## ✨ Features

- **🏆 Dynamic Leaderboards**: Daily, weekly, monthly, and all-time rankings
- **⚔️ Faction Competition**: Enlightened vs Resistance comparisons
- **📈 Progress Tracking**: Individual agent progress over time
- **💾 Local Storage**: SQLite database for data persistence
- **🔒 Data Validation**: Robust parsing and validation of Ingress data
- **🎯 Interactive Commands**: Easy-to-use Telegram interface
- **🧹 Auto-Delete Stats**: Automatically deletes user stats messages to keep chat clean and prevent copying

## 🚀 Quick Start

### 1. Setup

```bash
# Clone the repository
git clone https://github.com/your-username/ingress-leaderboard.git
cd ingress-leaderboard

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
# venv\Scripts\activate    # Windows

# Install the project in editable mode
pip install -e .
```

### 2. Configure

Create a `.env` file in the project root and add your Telegram bot token:

```
BOT_TOKEN="your_actual_bot_token_here"
```

### 3. Run

```bash
# Run the bot using the script
bash scripts/run_bot.sh
```

## 🤖 Bot Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Welcome message and introduction | `/start` |
| `/help` | Show all available commands | `/help` |
| `/submit` | Submit your Ingress statistics | `/submit` |
| `/leaderboard` | View leaderboards | `/leaderboard "Current AP" weekly` |
| `/factions` | Compare faction statistics | `/factions monthly` |
| `/progress` | View your progress | `/progress "Portals Captured" 30` |
| `/stats` | List available statistics | `/stats` |
| `/cancel` | Cancel current operation | `/cancel` |

## 📊 Supported Statistics

- Level
- Lifetime AP
- Current AP
- Unique Portals Visited
- Portals Discovered
- XM Collected
- Resonators Deployed
- Links Created
- Control Fields Created
- Mind Units Captured
- Portals Captured
- Distance Walked
- And 50+ more statistics!

## 🕐 Time Frames

- **Daily**: Last 24 hours
- **Weekly**: Last 7 days
- **Monthly**: Last 30 days
- **All Time**: Complete history

## 🎯 Data Format

The bot accepts Ingress statistics in this format:
```
ALL TIME YourAgentName Enlightened 2025-01-15 12:30:45 16 50000000 25000000 3000 500 5 150 200000000 ...
```

Use `/submit` command to see the complete format and submit your data.

## 🧪 Testing

Run tests to verify everything is working:

```bash
# Activate virtual environment first
source venv/bin/activate

# Run tests with pytest
pytest
```

## 🔧 Development

### Development Setup

The project is set up as an installable Python package. For development, it's recommended to install it in editable mode, as described in the 'Quick Start' section. This allows you to make changes to the source code and have them immediately reflected without reinstalling.

### Adding New Features

1.  Add handlers in `src/handlers/`
2.  Implement business logic in `src/services/`
3.  Add database operations in `src/database/`
4.  Update tests in `tests/`

## 📝 Configuration

### Environment Variables

- `BOT_TOKEN`: Your Telegram bot token (stored in `.env` file)
- `PREFIX_DETECTION_MODE`: Set to `strict` or `flexible` for stats parsing behavior
- `AUTO_DELETE_USER_STATS`: Set to `true` to auto-delete user stats messages (default: `true`)
- `AUTO_DELETE_DELAY_SECONDS`: Delay before deletion in seconds (default: `2`)

### Config File

- `config/config.py`: Main configuration

### Auto-Delete Feature

The bot can automatically delete user stats messages after processing to keep the chat clean and prevent stat copying.

**Requirements:** Bot must have admin privileges with "Delete Messages" permission.

See [AUTO_DELETE_FEATURE.md](AUTO_DELETE_FEATURE.md) for detailed setup instructions.

## 🗄️ Database

The bot uses SQLite for local data storage:

- **Location**: `data/ingress_leaderboard.db`
- **Tables**: `agents`, `submissions`
- **Automatic**: Database is created automatically on first run

## 🔒 Security

- Bot token stored in `.env` file (not in version control)
- Input validation for all user data
- SQL injection protection with parameterized queries
- Error handling to prevent crashes

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure the virtual environment is activated and the project is installed correctly (`pip install -e .`).
2. **Bot Token**: Verify that the `BOT_TOKEN` is set correctly in your `.env` file.
3. **Database**: Check that the `data/` directory exists and is writable.
4. **Dependencies**: Ensure all dependencies are installed by running `pip install -e .` again.

### Getting Help

1. Check the logs for error messages
2. Run tests to identify issues: `python tests/test_bot.py`
3. Verify configuration in `config/local_settings.py`

## 📄 License

This project is open source. Feel free to modify and distribute.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

**Ready to dominate the Ingress leaderboards! 🏆⚡**