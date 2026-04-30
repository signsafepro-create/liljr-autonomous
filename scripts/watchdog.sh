#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# LILJR WATCHDOG v8 — Auto-restart if server dies
# NEVER starts old v6 servers. Only v8.
# Run: nohup bash ~/liljr-autonomous/scripts/watchdog.sh > /dev/null 2>&1 &
# ═══════════════════════════════════════════════════════════════

REPO="$HOME/liljr-autonomous"
LOG="$HOME/liljr_watchdog.log"
SERVER="$REPO/server_v8.py"

echo "[$(date)] Watchdog v8 started" >> "$LOG"

while true; do
    # Check if v8 server is healthy
    HEALTH=$(curl -s --max-time 3 http://localhost:8000/api/health 2>/dev/null)
    if echo "$HEALTH" | grep -q "liljr-empire-8.0"; then
        # v8 is alive and healthy — do nothing
        :
    else
        echo "[$(date)] Server DOWN or wrong version. Restarting v8..." >> "$LOG"
        
        # NUCLEAR KILL — destroy ALL Python servers, old watchdogs, everything
        pkill -9 -f "python.*server" 2>/dev/null || true
        pkill -9 -f "server_v[0-9]" 2>/dev/null || true
        pkill -9 -f "liljr_os" 2>/dev/null || true
        pkill -9 -f "watchdog" 2>/dev/null || true
        sleep 2
        
        # Start v8 ONLY
        if [ -f "$SERVER" ]; then
            termux-wake-lock 2>/dev/null || true
            nohup python3 "$SERVER" > /dev/null 2>&1 &
            echo "[$(date)] v8 restarted (PID: $!)" >> "$LOG"
        else
            echo "[$(date)] ERROR: $SERVER not found" >> "$LOG"
        fi
        
        sleep 5
    fi
    
    # Check every 30 seconds
    sleep 30
done
