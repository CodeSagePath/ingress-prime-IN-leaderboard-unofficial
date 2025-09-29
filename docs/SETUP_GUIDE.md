# Ingress Leaderboard Bot - Setup Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get Your Bot Token
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 3. Configure the Bot
1. Open `config.py`
2. Replace `YOUR_BOT_TOKEN_HERE` with your actual bot token:
   ```python
   BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
   ```

### 4. Test the Setup
```bash
python test_bot.py
```
You should see "🎉 All tests passed!"

### 5. Start the Bot
```bash
python bot.py
```
Or use the quick start script:
```bash
python start_bot.py
```

## 📊 How to Use

### For Users (in Telegram):

1. **Start the bot**: Send `/start`
2. **Submit data**: Send `/submit` and paste your Ingress statistics
3. **View leaderboards**: Send `/leaderboard Current AP weekly`
4. **Compare factions**: Send `/factions monthly`
5. **Get help**: Send `/help`

### Data Format:
```
ALL TIME YourAgentName Enlightened 2025-01-15 12:30:45 16 50000000 25000000 3000 500 5 150 200000000 5000 1200 800 50000 10000 8000 5000000 200 500000 150000000 8000 2500 7000 20000 1200 40000 15 180 20000 4000 3500 1800 20 5 200 1000 120 70 220 135 2500 90 1500000 35 2500 240 300 100 20 3 1 18 6 3000 150 3500 0 1 0
```

## 🎯 Features

✅ **Dynamic Time Slots**: Daily, weekly, monthly, all-time leaderboards  
✅ **Faction Support**: Separate tracking for Enlightened (💚) and Resistance (💙)  
✅ **Progress Tracking**: Monitor individual agent progress over time  
✅ **Multiple Statistics**: 12+ different Ingress statistics tracked  
✅ **Local Storage**: SQLite database for reliable data persistence  
✅ **Faction Comparison**: Compare faction performance  
✅ **User-Friendly**: Intuitive commands and formatted output  

## 🔧 Available Commands

- `/start` - Welcome message
- `/help` - Show help and usage
- `/submit` - Submit your Ingress statistics
- `/leaderboard [stat] [timeframe] [faction]` - View leaderboards
- `/progress [stat] [days]` - View your progress
- `/factions [timeframe]` - Compare factions
- `/stats` - List available statistics
- `/cancel` - Cancel current operation

## 📈 Example Commands

```
/leaderboard "Current AP" weekly
/leaderboard "Portals Captured" all_time Enlightened
/factions monthly
/progress "Lifetime AP" 14
```

## 🛠️ Troubleshooting

### Bot not responding?
- Check if BOT_TOKEN is correctly set in config.py
- Make sure the bot is running (`python bot.py`)
- Verify your internet connection

### Database errors?
- Run `python setup.py` to reinitialize the database
- Check file permissions in the project directory

### Data parsing errors?
- Ensure your data format matches the expected structure
- Check that all required fields are present
- Use the sample data format as reference

## 📁 Project Structure

```
ingress-leaderboard/
├── bot.py                 # Main bot application
├── config.py             # Configuration settings
├── database.py           # Database management
├── data_parser.py        # Data parsing utilities
├── leaderboard.py        # Leaderboard generation
├── start_bot.py          # Quick start script
├── test_bot.py           # Test suite
├── example_usage.py      # Usage examples
├── setup.py              # Setup script
├── requirements.txt      # Dependencies
├── README.md             # Documentation
└── SETUP_GUIDE.md        # This file
```

## 🔒 Security Notes

- Keep your bot token secure and never share it
- The bot stores data locally in SQLite
- User data is associated with Telegram user IDs
- All input data is validated before processing

## 🎮 Ready to Go!

Your Ingress Leaderboard Bot is now ready! Start the bot and begin tracking agent statistics across factions and time periods.

**Happy hunting, Agents!** ⚡🏆