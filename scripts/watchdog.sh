#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# LILJR WATCHDOG — Auto-restart if server dies
# Run: nohup bash ~/liljr_watchdog.sh > /dev/null 2>&1 &
# ═══════════════════════════════════════════════════════════════

REPO="$HOME/liljr-autonomous"
LOG="$HOME/liljr_watchdog.log"

echo "[$(date)] Watchdog started" >> "$LOG"

while true; do
    # Check if server is running
    if ! curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo "[$(date)] Server DOWN. Restarting..." >> "$LOG"
        
        # Kill any stale processes
        pkill -9 -f "server_v6" 2>/dev/null || true
        sleep 2
        
        # Start server
        cd "$REPO/backend" 2>/dev/null || cd "$REPO" 2>/dev/null
        nohup python3 server_v6.2.py > "$HOME/liljr.log" 2>&1 &
        
        echo "[$(date)] Server restarted (PID: $!)" >> "$LOG"
        
        # Notify via Telegram if possible
        TOKEN=$(grep TELEGRAM_BOT_TOKEN ~/.bashrc 2>/dev/null | grep -o 'sk_[^"]*' | head -1 || echo "")
        if [ -n "$TOKEN" ]; then
            curl -s "https://api.telegram.org/bot$TOKEN/sendMessage" \
                -d "chat_id=$(grep TELEGRAM_CHAT_ID ~/.bashrc 2>/dev/null | grep -o '[0-9]*' | head -1)" \
                -d "text=🚨%20LilJR%20restarted%20after%20crash" > /dev/null 2>&1 || true
        fi
        
        sleep 5
    fi
    
    # Check every 30 seconds
    sleep 30
done
