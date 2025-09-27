# 🎮 Ingress Leaderboard Telegram Bot

A comprehensive Telegram bot for tracking and comparing Ingress game statistics with faction-based leaderboards, progress tracking, and local data storage.

## 🏗️ Project Structure

```
ingress-leaderboard/
├── venv/                    # Virtual environment (created by setup)
├── src/                     # Source code
│   ├── handlers/           # Telegram bot handlers
│   │   ├── command_handlers.py
│   │   ├── message_handlers.py
│   │   └── callback_handlers.py
│   ├── database/           # Database management
│   │   └── manager.py
│   ├── parsers/            # Data parsing logic
│   │   └── data_parser.py
│   ├── services/           # Business logic services
│   │   ├── bot_service.py
│   │   └── leaderboard_service.py
│   └── utils/              # Utility functions
│       ├── formatters.py
│       └── validators.py
├── config/                 # Configuration files
│   ├── settings.py
│   └── local_settings.py   # Created by setup
├── tests/                  # Test files
│   └── test_bot.py
├── docs/                   # Documentation
├── scripts/                # Setup and utility scripts
│   ├── setup.py
│   └── run_bot.sh
├── data/                   # Database and data files
├── main.py                 # Main entry point
└── requirements.txt        # Python dependencies
```

## ✨ Features

- **🏆 Dynamic Leaderboards**: Daily, weekly, monthly, and all-time rankings
- **⚔️ Faction Competition**: Enlightened vs Resistance comparisons
- **📈 Progress Tracking**: Individual agent progress over time
- **💾 Local Storage**: SQLite database for data persistence
- **🔒 Data Validation**: Robust parsing and validation of Ingress data
- **🎯 Interactive Commands**: Easy-to-use Telegram interface

## 🚀 Quick Start

### 1. Setup

```bash
# Clone or navigate to the project directory
cd ingress-leaderboard

# Run the setup script
python scripts/setup.py
```

### 2. Configure

Edit `config/local_settings.py` and add your Telegram bot token:

```python
BOT_TOKEN = "your_actual_bot_token_here"
```

### 3. Run

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Start the bot
python main.py

# Or use the convenience script (Linux/Mac)
./scripts/run_bot.sh
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

# Run tests
python tests/test_bot.py
```

## 🔧 Development

### Virtual Environment

The project uses a virtual environment to isolate dependencies:

```bash
# Create virtual environment (done by setup script)
python -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Project Structure

- **Handlers**: Separate files for different types of Telegram handlers
- **Services**: Business logic and core functionality
- **Database**: Data persistence and queries
- **Parsers**: Data parsing and validation
- **Utils**: Utility functions and helpers
- **Config**: Configuration management

### Adding New Features

1. Add handlers in `src/handlers/`
2. Implement business logic in `src/services/`
3. Add database operations in `src/database/`
4. Update tests in `tests/`

## 📝 Configuration

### Environment Variables

- `BOT_TOKEN`: Your Telegram bot token

### Config Files

- `config/settings.py`: Main configuration
- `config/local_settings.py`: Local overrides (created by setup)

## 🗄️ Database

The bot uses SQLite for local data storage:

- **Location**: `data/ingress_leaderboard.db`
- **Tables**: `agents`, `submissions`
- **Automatic**: Database is created automatically on first run

## 🔒 Security

- Bot token stored in local config file (not in version control)
- Input validation for all user data
- SQL injection protection with parameterized queries
- Error handling to prevent crashes

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure virtual environment is activated
2. **Bot Token**: Verify token is set in `config/local_settings.py`
3. **Database**: Check that `data/` directory exists and is writable
4. **Dependencies**: Run `pip install -r requirements.txt`

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