#!/data/data/com.termux/files/usr/bin/bash
# LILJR IMMORTAL WATCHDOG
# If the server dies for ANY reason, restart it instantly
# Run this in background: nohup bash immortal_watchdog.sh &

LOG="$HOME/liljr_immortal.log"
SERVER="$HOME/liljr-autonomous/server_v8.py"
CHECK_INTERVAL=5

echo "[IMMORTAL] $(date) Watchdog started" >> "$LOG"

while true; do
    # Check if server is responding
    if ! curl -s --max-time 3 http://localhost:8000/api/health > /dev/null 2>&1; then
        echo "[IMMORTAL] $(date) Server dead. Restarting..." >> "$LOG"
        
        # Kill any zombies
        pkill -9 -f "python.*8000" 2>/dev/null
        pkill -9 -f "server_v[0-9]" 2>/dev/null
        sleep 1
        
        # Start fresh
        if [ -f "$SERVER" ]; then
            termux-wake-lock 2>/dev/null
            nohup python3 "$SERVER" > /dev/null 2>&1 &
echo "[IMMORTAL] $(date) Server restarted" >> "$LOG"
        else
            echo "[IMMORTAL] $(date) ERROR: $SERVER missing" >> "$LOG"
        fi
    fi
    
    sleep $CHECK_INTERVAL
done
