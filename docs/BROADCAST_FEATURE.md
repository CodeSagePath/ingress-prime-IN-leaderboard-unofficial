# Broadcast Feature

## Overview
The broadcast feature allows administrators to send messages to all users who have interacted with the bot via DM (Direct Message).

## Setup

### 1. Find Your Telegram User ID
To use the broadcast feature, you need to find your Telegram user ID:
1. Open Telegram
2. Search for and message `@userinfobot`
3. The bot will reply with your user ID (a numeric value like `123456789`)

### 2. Configure Admin Users
Edit the `.env` file in the project root and add your user ID to the `ADMIN_USER_IDS` configuration:

```env
# Single admin
ADMIN_USER_IDS=123456789

# Multiple admins (comma-separated)
ADMIN_USER_IDS=123456789,987654321
```

### 3. Restart the Bot
After updating the `.env` file, restart the bot for the changes to take effect:

```bash
# If running manually
python main.py

# If running with script
./scripts/run_bot.sh
```

## Usage

### Method 1: Direct Broadcast
Send a message directly with the `/broadcast` command:

```
/broadcast Your message here
```

**Example:**
```
/broadcast 🎉 New feature released! Check out the updated leaderboards!
```

### Method 2: Interactive Broadcast
Use the command without a message to enter interactive mode:

1. Send `/broadcast`
2. The bot will ask you to send the message you want to broadcast
3. Send your message
4. The bot will broadcast it to all users

**Example:**
```
You: /broadcast
Bot: 📢 Broadcast Message

Please send the message you want to broadcast to all users.
This message will be sent to all users who have interacted with the bot.

Send /cancel to cancel.

You: Hello everyone! Important update coming soon!
Bot: [Broadcasting...]
```

## Features

### Real-time Progress
The broadcast feature shows real-time progress:
- Total number of users
- Current progress (X/Y users)
- Success count
- Failed count

### Error Handling
- Users who have blocked the bot will be skipped (counted as failed)
- The broadcast will continue even if some messages fail
- A final summary will be shown with success/failure counts

### Message Formatting
All broadcast messages:
- Are automatically prefixed with "📢 **Broadcast Message**"
- Support Markdown formatting
- Can include emojis and special characters

## Example Output

```
✅ Broadcast Complete!

📊 Results:
• Total users: 50
• Successfully sent: 48
• Failed: 2

📝 Message:
🎉 New feature released! Check out the updated leaderboards!
```

## Security

- Only users listed in `ADMIN_USER_IDS` can use the `/broadcast` command
- Non-admin users will receive an "Access Denied" message
- The broadcast state is tracked per user to prevent conflicts

## Limitations

- Only sends to users who have submitted data (i.e., users in the database)
- Cannot send to users who have blocked the bot
- Message length is limited by Telegram's API (4096 characters for text messages)

## Troubleshooting

### "Access Denied" Error
**Problem:** You receive an access denied message when using `/broadcast`

**Solution:** 
1. Verify your user ID is correct (message @userinfobot)
2. Check that your ID is added to `ADMIN_USER_IDS` in `.env`
3. Make sure there are no spaces around the commas in the `.env` file
4. Restart the bot after updating the `.env` file

### "No users found" Message
**Problem:** The bot says there are no users to broadcast to

**Solution:**
- This means no users have submitted data yet
- Users need to interact with the bot and submit stats before they can receive broadcasts
- Check the database to verify users exist: `SELECT COUNT(DISTINCT telegram_user_id) FROM agents;`

### Some Messages Fail
**Problem:** Some messages show as "failed" in the summary

**Common Causes:**
- Users have blocked the bot
- Users have deleted their Telegram account
- Telegram API temporary issues

**Note:** This is normal and expected. The broadcast will continue for all other users.

## Best Practices

1. **Test First**: Test your broadcast with a small test message to ensure formatting looks good
2. **Keep It Short**: Shorter messages are more likely to be read
3. **Use Formatting**: Use Markdown to make important parts **bold** or _italic_
4. **Add Emojis**: Emojis make messages more engaging 🎉
5. **Be Respectful**: Don't spam users with too many broadcasts
6. **Time It Right**: Consider time zones when sending broadcasts

## Examples

### Announcement
```
/broadcast 📣 Announcement: Server maintenance scheduled for tomorrow at 2 PM UTC. Bot will be offline for 30 minutes.
```

### Update Notification
```
/broadcast 🚀 New features added! Now you can track your progress over time. Use /progress to try it out!
```

### Community Message
```
/broadcast 🎉 Congratulations to all agents! We've reached 100 users on the leaderboard! Keep up the great work! 💪
```

### Reminder
```
/broadcast ⏰ Reminder: Don't forget to submit your monthly stats! Use /submit to update your leaderboard position.
```