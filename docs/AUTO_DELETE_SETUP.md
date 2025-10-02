# 🧹 Auto-Delete Feature - Quick Setup Guide

## ✅ What Was Implemented

Your bot now has the ability to **automatically delete user stats messages** after they've been processed successfully. This keeps your chat clean and prevents users from copying each other's statistics.

## 🚀 Quick Setup (3 Steps)

### Step 1: Make Bot an Admin

1. Open your Telegram group
2. Go to **Group Info** → **Administrators**
3. Add your bot as administrator
4. Grant permission: ✅ **Delete Messages**
5. Save

### Step 2: Configure (Optional)

The feature is **enabled by default**. Your `.env` file now has:

```bash
# Auto-delete is ON by default
AUTO_DELETE_USER_STATS=true

# Wait 2 seconds before deleting (gives user confirmation)
AUTO_DELETE_DELAY_SECONDS=2
```

To disable, change to:
```bash
AUTO_DELETE_USER_STATS=false
```

### Step 3: Restart Bot

```bash
# Stop the bot (Ctrl+C)
# Start it again
python main.py
```

## 📋 How It Works

```
User sends stats → Bot processes → Bot confirms → ⏱️ 2 seconds → 🗑️ Message deleted
```

**Result:** Only the bot's confirmation message remains visible!

## 🎯 Benefits

✅ **Clean chat** - No clutter from long stats messages  
✅ **Prevent copying** - Users can't copy others' stats  
✅ **Privacy** - Stats data isn't permanently visible  
✅ **Professional** - Chat looks organized  

## 🔧 Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `AUTO_DELETE_USER_STATS` | `true` | Enable/disable auto-delete |
| `AUTO_DELETE_DELAY_SECONDS` | `2` | Seconds to wait before deletion |

### Recommended Settings

**For public groups:**
```bash
AUTO_DELETE_USER_STATS=true
AUTO_DELETE_DELAY_SECONDS=2
```

**For private testing:**
```bash
AUTO_DELETE_USER_STATS=false
```

## ⚠️ Troubleshooting

### Messages NOT Deleting?

**Check:**
1. ✅ Is bot an admin?
2. ✅ Does bot have "Delete Messages" permission?
3. ✅ Is `AUTO_DELETE_USER_STATS=true` in `.env`?
4. ✅ Did you restart the bot after changing `.env`?

### Messages Delete Too Fast?

Increase the delay:
```bash
AUTO_DELETE_DELAY_SECONDS=5
```

### Want to See Logs?

Check bot logs for messages like:
- `Successfully deleted stats message from user 123456789` ✅
- `Cannot delete message - bot needs admin privileges` ⚠️

## 📚 Full Documentation

For complete details, see: [docs/AUTO_DELETE_FEATURE.md](docs/AUTO_DELETE_FEATURE.md)

## 🧪 Testing

1. Make bot an admin with delete permission
2. Send test stats to the bot
3. Watch for:
   - Bot confirms receipt ✅
   - Wait 2 seconds ⏱️
   - Your message disappears 🗑️
   - Bot's confirmation stays ✅

## 🔐 Security Notes

- ✅ Only successful submissions are deleted
- ✅ Failed submissions remain (so user can fix them)
- ✅ Works gracefully even without admin rights (just doesn't delete)
- ✅ No data is lost (everything is saved before deletion)

## 📝 Changes Made

### Files Modified:
1. `config/settings.py` - Added configuration variables
2. `src/handlers/message_handlers.py` - Added auto-delete logic
3. `.env` - Added configuration options
4. `docs/README.md` - Updated documentation

### Files Created:
1. `docs/AUTO_DELETE_FEATURE.md` - Comprehensive documentation
2. `AUTO_DELETE_SETUP.md` - This quick guide

---

**That's it!** Make your bot an admin and enjoy a cleaner chat! 🎉