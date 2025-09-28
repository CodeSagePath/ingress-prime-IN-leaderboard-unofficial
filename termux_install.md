# Termux Installation Guide

This guide will help you set up the Ingress Leaderboard Bot on Termux (Android).

## Prerequisites

1. **Install Termux** from F-Droid (recommended) or Google Play Store
2. **Enable storage access** in Termux:
   ```bash
   termux-setup-storage
   ```

## Quick Setup

1. **Clone or download** this project to your Termux environment
2. **Navigate** to the project directory:
   ```bash
   cd ingress-leaderboard
   ```
3. **Run the setup script**:
   ```bash
   chmod +x setup_termux.sh
   ./setup_termux.sh
   ```

## Manual Setup (Alternative)

If the automatic setup doesn't work, follow these steps:

### 1. Update Termux
```bash
pkg update && pkg upgrade
```

### 2. Install Dependencies
```bash
pkg install python python-pip git sqlite
```

### 3. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate
```

### 4. Install Python Packages
```bash
pip install --upgrade pip
pip install -r requirements-termux.txt
```

### 5. Configure the Bot
```bash
cp config/config.example.py config/config.py
nano config/config.py  # Edit and add your bot token
```

### 6. Initialize Database
```bash
python setup.py
```

## Running the Bot

### Foreground (Interactive)
```bash
./start_bot_termux.sh
```

### Background (Daemon)
```bash
./run_bot_background.sh
```

### Stop Background Bot
```bash
./stop_bot.sh
```

## Termux-Specific Features

### 1. Wake Lock (Prevent Android Sleep)
```bash
termux-wake-lock
```
Run this before starting the bot to prevent Android from killing it.

### 2. Notifications
The bot can send Android notifications:
```bash
pkg install termux-api
```

### 3. Auto-start on Boot
Create a script in `~/.termux/boot/`:
```bash
mkdir -p ~/.termux/boot
cat > ~/.termux/boot/start-bot.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd /path/to/your/ingress-leaderboard
./run_bot_background.sh
EOF
chmod +x ~/.termux/boot/start-bot.sh
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   chmod +x *.sh
   ```

2. **Python Module Not Found**
   ```bash
   source venv/bin/activate
   pip install -r requirements-termux.txt
   ```

3. **Database Locked**
   ```bash
   rm data/ingress_leaderboard.db
   python setup.py
   ```

4. **Bot Token Error**
   - Edit `config/config.py`
   - Make sure your bot token is correct
   - Check internet connection

### Performance Tips

1. **Use wake lock** to prevent Android from killing the process
2. **Monitor memory usage** with `top` or `htop`
3. **Check logs** regularly: `tail -f logs/bot.log`
4. **Restart periodically** to free up memory

### Storage Management

- Bot database: `data/ingress_leaderboard.db`
- Logs: `logs/bot.log`
- Config: `config/config.py`

## Security Notes

1. **Keep your bot token secure**
2. **Don't share your config files**
3. **Use strong passwords** if exposing to network
4. **Regular backups** of your database

## Advanced Configuration

### Environment Variables
Create a `.env` file:
```bash
BOT_TOKEN=your_bot_token_here
DATABASE_PATH=data/ingress_leaderboard.db
LOG_LEVEL=INFO
```

### Custom Logging
Edit `config/settings.py` to customize logging levels and formats.

### Database Backup
```bash
# Backup
cp data/ingress_leaderboard.db data/backup_$(date +%Y%m%d).db

# Restore
cp data/backup_YYYYMMDD.db data/ingress_leaderboard.db
```

## Support

If you encounter issues:

1. Check the logs: `tail -f logs/bot.log`
2. Verify your configuration
3. Ensure all dependencies are installed
4. Check Termux permissions
5. Restart Termux if needed

## Updates

To update the bot:
```bash
git pull  # If using git
source venv/bin/activate
pip install -r requirements-termux.txt --upgrade
```

---

**Happy hunting, Agent!** 🎮⚡