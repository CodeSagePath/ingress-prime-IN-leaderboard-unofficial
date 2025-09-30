# Termux Troubleshooting Guide - "Bot token not configured" Error

This guide helps resolve the "Bot token not configured" error in Termux environments.

## 🚀 Quick Fix (Recommended)

1. **Use the new Termux startup script:**
   ```bash
   cd /path/to/your/ingress-leaderboard
   python start_termux.py
   ```

2. **Or test your configuration first:**
   ```bash
   python test_config.py
   ```

## 🔧 Manual Troubleshooting Steps

### Step 1: Verify .env File Location and Content

1. **Check if .env file exists:**
   ```bash
   ls -la .env
   ```

2. **View .env file content:**
   ```bash
   cat .env
   ```

   Should contain:
   ```
   BOT_TOKEN=your_actual_bot_token_here
   PREFIX_DETECTION_MODE=strict
   ```

3. **Check file permissions:**
   ```bash
   chmod 644 .env
   ```

### Step 2: Verify You're in the Correct Directory

```bash
pwd
# Should show: /data/data/com.termux/files/home/your-project-path
ls -la
# Should show main.py, src/, config/, etc.
```

### Step 3: Test Environment Loading

Run the environment debug script:
```bash
python debug_env_loading.py
```

### Step 4: Alternative .env Locations for Termux

If the .env file isn't being found, try copying it to these locations:

1. **Home directory:**
   ```bash
   cp .env ~/
   ```

2. **Create ingress-bot directory:**
   ```bash
   mkdir -p ~/ingress-bot
   cp .env ~/ingress-bot/
   ```

### Step 5: Manual Environment Variable

As a last resort, set the environment variable directly:
```bash
export BOT_TOKEN="your_actual_bot_token_here"
python main.py
```

## 🔍 Diagnostic Commands

### Check Python Path
```bash
python -c "import sys; print('\n'.join(sys.path))"
```

### Check Current Directory
```bash
python -c "import os; print('CWD:', os.getcwd())"
```

### Test Direct Import
```bash
python -c "from config.settings import BOT_TOKEN; print('Token loaded:', bool(BOT_TOKEN))"
```

### Check Termux Environment
```bash
echo "PREFIX: $PREFIX"
echo "HOME: $HOME"
python -c "import os; print('Is Termux:', os.environ.get('PREFIX', '').endswith('com.termux'))"
```

## 📝 Common Issues and Solutions

### Issue 1: "No module named 'config'"
**Solution:** Make sure you're in the project root directory and run:
```bash
export PYTHONPATH="$PWD:$PYTHONPATH"
python main.py
```

### Issue 2: ".env file exists but BOT_TOKEN is empty"
**Solution:** 
1. Check .env file content: `cat .env`
2. Ensure no extra spaces: `BOT_TOKEN=token` (not `BOT_TOKEN = token`)
3. Remove any quotes if present: `BOT_TOKEN=123456:ABC` (not `BOT_TOKEN="123456:ABC"`)

### Issue 3: "Permission denied" errors
**Solution:**
```bash
chmod 755 .
chmod 644 .env
chmod +x main.py
```

### Issue 4: Working directory issues
**Solution:** Use absolute paths:
```bash
cd /data/data/com.termux/files/home/ingress-leaderboard
python main.py
```

## 🛠️ Termux-Specific Setup

### Install Required Packages
```bash
# Update packages
pkg update && pkg upgrade

# Install Python and dependencies
pkg install python python-pip

# Install Termux API (optional but recommended)
pkg install termux-api

# Install project dependencies
pip install -r requirements.txt
```

### Grant Storage Permissions (Optional)
```bash
termux-setup-storage
```

### Keep Bot Running
```bash
# Acquire wake lock to prevent Android from killing the process
termux-wake-lock

# Run bot (it will auto-acquire wake lock)
python start_termux.py

# Release wake lock when done (automatically done by the script)
```

## 📋 Verification Checklist

- [ ] .env file exists in project root
- [ ] .env file contains valid BOT_TOKEN
- [ ] File permissions are correct (644 for .env)
- [ ] You're in the correct project directory
- [ ] Python can import config.settings without errors
- [ ] test_config.py shows all tests passed

## 🆘 If Nothing Works

1. **Create a fresh .env file:**
   ```bash
   echo "BOT_TOKEN=your_actual_token_here" > .env
   echo "PREFIX_DETECTION_MODE=strict" >> .env
   ```

2. **Use the environment fix utility:**
   ```bash
   python fix_termux_env.py
   ```

3. **Run with debug output:**
   ```bash
   python -v main.py 2>&1 | grep -E "(env|config|token)"
   ```

## 📞 Getting Help

If you're still having issues, please provide:

1. Output of `python test_config.py`
2. Output of `python debug_env_loading.py`
3. Content of `.env` file (with token censored)
4. Your current directory: `pwd`
5. Termux environment info: `echo $PREFIX`

---

**Note:** The improved configuration system now checks multiple locations for the .env file and provides better error messages. Use `start_termux.py` for the most reliable startup experience in Termux.