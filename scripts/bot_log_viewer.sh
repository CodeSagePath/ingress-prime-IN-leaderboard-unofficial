cat bot_log_viewer.sh 
#!/bin/bash

# Boot process log
echo "Boot process log:"
cat ~/telegram-bots/ingress-leaderboard/logs/boot_debug.log
echo -e "\n\n\n\n\n\n"  # 6-line gap


# Startup process log
echo "Startup process log:"
cat ~/telegram-bots/ingress-leaderboard/logs/termux_startup.log
echo -e "\n\n\n\n\n\n"  # 6-line gap


# Bot session log
echo "Bot session log:"
cat ~/telegram-bots/ingress-leaderboard/logs/bot_session.log
echo -e "\n\n\n\n\n\n"  # 6-line gap


# Attach to running bot
echo "Attaching to bot session..."
tmux attach -t "bot_session"
