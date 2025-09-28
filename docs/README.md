# Ingress Leaderboard Telegram Bot

A comprehensive Telegram bot for tracking and comparing Ingress agent statistics with faction-based leaderboards and dynamic time slots.

## Features

- 📊 **Dynamic Leaderboards**: Daily, weekly, monthly, and all-time rankings
- 🟢🔵 **Faction Support**: Separate leaderboards for Enlightened (green) and Resistance (blue)
- 📈 **Progress Tracking**: Monitor individual agent progress over time
- ⚔️ **Faction Comparison**: Compare faction statistics and performance
- 💾 **Local Storage**: SQLite database for reliable data persistence
- 🎯 **Multiple Statistics**: Track 12+ different Ingress statistics

## Supported Statistics

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
- And more...

## Installation

### Standard Installation (Linux/Windows/macOS)

1. **Clone or download the project files**

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create your Telegram bot**:
   - Go to [@BotFather](https://t.me/BotFather) on Telegram
   - Create a new bot with `/newbot`
   - Copy the bot token

5. **Configure the bot**:
   - Copy `config/config.example.py` to `config/config.py`
   - Replace `YOUR_BOT_TOKEN_HERE` with your actual bot token

6. **Setup the database**:
   ```bash
   python setup.py
   ```

7. **Start the bot**:
   ```bash
   python main.py
   ```

### Termux Installation (Android)

For Android users using Termux:

1. **Quick setup**:
   ```bash
   chmod +x setup_termux.sh
   ./setup_termux.sh
   ```

2. **Configure your bot token** in `config/config.py`

3. **Start the bot**:
   ```bash
   # Foreground
   ./start_bot_termux.sh
   
   # Background (recommended)
   ./run_bot_background.sh
   ```

4. **Stop background bot**:
   ```bash
   ./stop_bot.sh
   ```

📱 **See `termux_install.md` for detailed Termux setup instructions**

## Usage

### Bot Commands

- `/start` - Welcome message and introduction
- `/help` - Show all available commands and usage
- `/submit` - Submit your Ingress statistics data
- `/leaderboard [stat] [timeframe] [faction]` - View leaderboards
- `/progress [stat] [days]` - View your progress over time
- `/factions [timeframe]` - Compare faction statistics
- `/stats` - List all available statistics
- `/cancel` - Cancel current operation

### Data Submission

**🚀 Easiest Method:**

1. **Open Ingress app** → Agent tab → Statistics
2. **Select and copy ALL your statistics** (including headers - the bot will handle them automatically)
3. **Send `/submit` command** followed by your copied data

**✅ Examples that work:**

```
/submit
Time Span	Agent Name	Faction	Date (yyyy-mm-dd)	Time (hh:mm:ss)	Level	Lifetime AP	Current AP	...
ALL TIME	YourAgent	Enlightened	2025-01-15	12:30:45	16	50000000	25000000	...
```

Or simply:
```
/submit
ALL TIME	YourAgent	Enlightened	2025-01-15	12:30:45	16	50000000	25000000	...
```

**💡 Pro Tips:**
- Copy directly from Ingress - **don't edit or remove headers**
- Make sure to scroll right in Ingress to get ALL statistics
- You can submit multiple time periods at once
- The bot automatically skips header lines and processes your data

### Example Commands

- `/leaderboard "Current AP" weekly` - Weekly AP leaderboard
- `/leaderboard "Portals Captured" all_time Enlightened` - All-time Enlightened portals
- `/factions monthly` - Monthly faction comparison
- `/progress "Lifetime AP" 14` - Your AP progress over 14 days

## Data Format

**The bot automatically handles raw Ingress statistics!** Just copy directly from your Ingress app.

**What the bot accepts:**
- ✅ Raw copy-paste from Ingress Statistics tab (with or without headers)
- ✅ Tab-separated or space-separated values
- ✅ Multiple time periods in one submission
- ✅ Headers are automatically detected and skipped

**Required fields per data line:**
1. Time Span (e.g., "ALL TIME", "CURRENT WEEK")
2. Agent Name
3. Faction (Enlightened/Resistance)
4. Date (YYYY-MM-DD)
5. Time (HH:MM:SS)
6. Level
7. Lifetime AP
8. Current AP
9. ... (50+ additional statistics)

**No manual formatting needed** - the bot handles everything automatically!

## Time Frames

- **Daily**: Last 24 hours
- **Weekly**: Last 7 days
- **Monthly**: Last 30 days
- **All Time**: Complete history

## Faction Colors

- 🟢 **Enlightened**: Green
- 🔵 **Resistance**: Blue

## Database Schema

The bot uses SQLite with two main tables:
- `agents`: Store agent information and faction
- `submissions`: Store all statistical submissions with timestamps

## File Structure

```
ingress-leaderboard/
├── bot.py              # Main bot application
├── config.py           # Configuration settings
├── database.py         # Database management
├── data_parser.py      # Data parsing utilities
├── leaderboard.py      # Leaderboard generation
├── setup.py           # Setup script
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── data-format.txt    # Sample data format
└── roadmap.txt        # Project roadmap
```

## Contributing

Feel free to contribute by:
- Adding new statistics
- Improving leaderboard formatting
- Adding new time frame options
- Enhancing the user interface
- Fixing bugs or improving performance

## Security Notes

- Keep your bot token secure and never commit it to version control
- The bot stores data locally in SQLite
- User data is associated with Telegram user IDs
- Validate all input data before processing

## Troubleshooting

1. **Bot not responding**: Check if the bot token is correct in `config.py`
2. **Database errors**: Run `python setup.py` to reinitialize the database
3. **Data parsing errors**: Ensure data format matches the expected structure
4. **Permission errors**: Make sure the bot has write permissions for the database file

## License

This project is open source. Feel free to modify and distribute as needed.

---

**Happy hunting, Agents!** 🎮⚡