# 📱 Termux Setup Guide for Ingress Leaderboard Bot

This guide will help you run the Ingress Leaderboard Bot on your Android device using Termux.

## 🚀 Quick Start

1. **Install Termux** from [F-Droid](https://f-droid.org/packages/com.termux/) (recommended)
2. **Download this project** to your Termux environment
3. **Run the setup script**:
   ```bash
   chmod +x setup_termux.sh
   ./setup_termux.sh
   ```
4. **Configure your bot token** in `config/config.py`
5. **Start the bot**:
   ```bash
   ./start_bot_termux.sh
   ```

## 📋 Detailed Setup

### Step 1: Prepare Termux

```bash
# Update packages
pkg update && pkg upgrade

# Enable storage access (optional but recommended)
termux-setup-storage

# Install Termux API for notifications (optional)
pkg install termux-api
```

### Step 2: Get the Bot Code

```bash
# If using git
git clone <your-repo-url>
cd ingress-leaderboard

# Or download and extract the files manually
```

### Step 3: Run Setup

```bash
# Make setup script executable
chmod +x setup_termux.sh

# Run the setup
./setup_termux.sh
```

This will:
- Install Python and required packages
- Create a virtual environment
- Install bot dependencies
- Set up directories and configuration
- Create startup scripts

### Step 4: Configure Bot Token

1. Create a bot with [@BotFather](https://t.me/BotFather) on Telegram
2. Copy your bot token
3. Edit the configuration:
   ```bash
   nano config/config.py
   ```
4. Replace `YOUR_BOT_TOKEN_HERE` with your actual token

### Step 5: Test Setup

```bash
# Test the environment
python test_termux.py

# Test the bot (dry run)
source venv/bin/activate
python main.py --test
```

## 🎮 Running the Bot

### Foreground Mode (Interactive)
```bash
./start_bot_termux.sh
```
- Bot runs in the terminal
- You can see logs in real-time
- Press Ctrl+C to stop

### Background Mode (Daemon)
```bash
# Start in background
./run_bot_background.sh

# Check if running
ps aux | grep python

# View logs
tail -f logs/bot.log

# Stop the bot
./stop_bot.sh
```

### Auto-start on Boot

1. Create boot script directory:
   ```bash
   mkdir -p ~/.termux/boot
   ```

2. Create startup script:
   ```bash
   cat > ~/.termux/boot/start-ingress-bot.sh << 'EOF'
   #!/data/data/com.termux/files/usr/bin/bash
   cd /path/to/your/ingress-leaderboard
   ./run_bot_background.sh
   EOF
   chmod +x ~/.termux/boot/start-ingress-bot.sh
   ```

## 🔧 Termux-Specific Features

### Wake Lock (Prevent Sleep)
```bash
# Acquire wake lock before starting bot
termux-wake-lock

# The bot will automatically manage wake locks
# Or manually release when done
termux-wake-unlock
```

### Notifications
The bot can send Android notifications when:
- Bot starts/stops
- Errors occur
- New submissions received

### Storage Access
- Bot data: `data/ingress_leaderboard.db`
- Logs: `logs/bot.log`
- Backups: `data/backups/` or `~/storage/shared/IngressBot/`

### Performance Optimization
The bot automatically optimizes for Termux:
- Reduced memory usage
- Smaller log files
- Lower timeout values
- Efficient database operations

## 📊 Monitoring

### Check Bot Status
```bash
# Check if bot is running
ps aux | grep python

# Check logs
tail -f logs/bot.log

# Check last 50 log entries
tail -n 50 logs/bot.log

# Check for errors
grep -i error logs/bot.log
```

### System Resources
```bash
# Check memory usage
free -h

# Check disk space
df -h

# Check CPU usage
top
```

## 🛠️ Troubleshooting

### Common Issues

1. **Bot not starting**
   ```bash
   # Check configuration
   python test_termux.py
   
   # Check logs
   cat logs/bot.log
   
   # Verify token
   grep BOT_TOKEN config/config.py
   ```

2. **Permission denied**
   ```bash
   chmod +x *.sh
   ```

3. **Module not found**
   ```bash
   source venv/bin/activate
   pip install -r requirements-termux.txt
   ```

4. **Database locked**
   ```bash
   # Stop bot first
   ./stop_bot.sh
   
   # Remove database and recreate
   rm data/ingress_leaderboard.db
   python setup.py
   ```

5. **Android killing the bot**
   ```bash
   # Use wake lock
   termux-wake-lock
   
   # Check Android battery optimization settings
   # Disable battery optimization for Termux
   ```

### Performance Issues

1. **High memory usage**
   - Restart bot periodically
   - Clear logs: `> logs/bot.log`
   - Check for memory leaks in logs

2. **Slow responses**
   - Check internet connection
   - Reduce concurrent operations
   - Clear database cache

3. **Frequent crashes**
   - Check Android RAM availability
   - Use background mode
   - Enable wake lock

## 🔒 Security

### Best Practices
- Keep bot token secure
- Don't share config files
- Regular database backups
- Monitor logs for suspicious activity

### Backup Strategy
```bash
# Manual backup
cp data/ingress_leaderboard.db data/backup_$(date +%Y%m%d).db

# Automated backup (add to cron or script)
./backup_database.sh
```

## 📱 Android-Specific Tips

### Battery Optimization
1. Go to Android Settings → Apps → Termux
2. Disable battery optimization
3. Allow background activity
4. Set to "Don't optimize"

### Notifications
1. Install Termux:API from F-Droid
2. Grant notification permissions
3. Bot will show status notifications

### Storage Management
- Bot uses ~10-50MB storage
- Logs rotate automatically
- Database grows with submissions
- Regular cleanup recommended

## 🆘 Getting Help

### Debug Information
```bash
# Generate debug report
python test_termux.py > debug_report.txt

# Check system info
uname -a
python --version
pkg list-installed | grep python
```

### Log Analysis
```bash
# Recent errors
grep -i error logs/bot.log | tail -10

# Bot restarts
grep -i "starting\|stopping" logs/bot.log

# Performance metrics
grep -i "memory\|cpu\|timeout" logs/bot.log
```

## 🔄 Updates

### Update Bot Code
```bash
# If using git
git pull

# Reinstall dependencies
source venv/bin/activate
pip install -r requirements-termux.txt --upgrade

# Restart bot
./stop_bot.sh
./run_bot_background.sh
```

### Update Termux
```bash
pkg update && pkg upgrade
```

---

## 📞 Support

If you encounter issues:

1. **Check the logs** first: `tail -f logs/bot.log`
2. **Run the test script**: `python test_termux.py`
3. **Verify configuration**: Check `config/config.py`
4. **Restart Termux** if needed
5. **Check Android permissions** and battery settings

**Happy hunting, Agent!** 🎮⚡

---

*This bot is optimized for Termux and will automatically detect and configure itself for the Android environment.*