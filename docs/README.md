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

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create your Telegram bot**:
   - Go to [@BotFather](https://t.me/BotFather) on Telegram
   - Create a new bot with `/newbot`
   - Copy the bot token

4. **Configure the bot**:
   - Open `config.py`
   - Replace `YOUR_BOT_TOKEN_HERE` with your actual bot token

5. **Setup the database**:
   ```bash
   python setup.py
   ```

6. **Start the bot**:
   ```bash
   python bot.py
   ```

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

1. Use `/submit` command
2. Paste your Ingress statistics in the format:
   ```
   ALL TIME YourAgentName Enlightened 2025-01-15 12:30:45 16 50000000 25000000 3000 500 5 150 200000000 5000 1200 800 50000 10000 8000 5000000 200 500000 150000000 8000 2500 7000 20000 1200 40000 15 180 20000 4000 3500 1800 20 5 200 1000 120 70 220 135 2500 90 1500000 35 2500 240 300 100 20 3 1 18 6 3000 150 3500 0 1 0
   ```

### Example Commands

- `/leaderboard "Current AP" weekly` - Weekly AP leaderboard
- `/leaderboard "Portals Captured" all_time Enlightened` - All-time Enlightened portals
- `/factions monthly` - Monthly faction comparison
- `/progress "Lifetime AP" 14` - Your AP progress over 14 days

## Data Format

The bot expects Ingress statistics in a specific space-separated format. Each line should contain:

1. Time Span (e.g., "ALL TIME")
2. Agent Name
3. Faction (Enlightened/Resistance)
4. Date (YYYY-MM-DD)
5. Time (HH:MM:SS)
6. Level
7. Lifetime AP
8. Current AP
9. ... (and many more statistics)

See the sample data in `data-format.txt` for reference.

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