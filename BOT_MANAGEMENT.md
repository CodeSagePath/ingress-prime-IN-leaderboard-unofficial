# Bot Management Guide

## The Problem: Multiple Bot Instances

Running multiple instances of the same bot simultaneously causes:
- **Duplicate responses** to user messages
- **Race conditions** between instances
- **Database conflicts** and inconsistencies
- **Unexpected behavior** like automatic leaderboards appearing

## Solution: Instance Management

### Quick Fix
1. **Stop your Termux bot** (go to Termux and press Ctrl+C or close terminal)
2. **Use only ONE instance** at a time
3. **Use the management tools** provided below

### Management Tools

#### 1. Check Bot Status
```bash
python manage_bot.py status
```
Shows:
- Running bot processes
- Lock file status
- Process IDs and command lines

#### 2. Stop All Bot Instances
```bash
python manage_bot.py stop
```
- Stops all running bot processes
- Cleans up lock files
- Safe shutdown

#### 3. Start Bot Safely
```bash
python manage_bot.py start
```
- Stops any existing instances first
- Starts a fresh bot instance
- Prevents conflicts

#### 4. Manual Start with Protection
```bash
python main.py
```
- Now includes automatic instance detection
- Will refuse to start if another instance is running
- Creates lock file to prevent conflicts

### Best Practices

1. **Always stop existing instances** before starting a new one
2. **Use different bot tokens** for testing vs production
3. **Check status** before starting: `python manage_bot.py status`
4. **Use the management script** for safe operations

### For Termux Users

When running on Termux (Android):
1. **Stop the Termux instance** before testing on desktop
2. **Use the management tools** to check for conflicts
3. **Consider using different tokens** for mobile vs desktop testing

### Troubleshooting

**Problem**: Bot still misbehaves after stopping instances
**Solution**: 
```bash
python manage_bot.py stop
# Wait a few seconds
python manage_bot.py status
# Verify no processes are running
python manage_bot.py start
```

**Problem**: "Permission denied" when stopping processes
**Solution**: The process might be owned by a different user or running on another system (like Termux)

**Problem**: Lock file exists but no process running
**Solution**: The management tools will automatically clean up stale lock files

### Files Added
- `check_bot_status.py` - Instance detection and lock file management
- `manage_bot.py` - Bot management commands
- `main.py` - Updated with instance protection
- `.bot_running.lock` - Lock file (created automatically)