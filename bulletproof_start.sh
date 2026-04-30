#!/data/data/com.termux/files/usr/bin/bash
# LILJR BULLETPROOF LAUNCHER
# Makes the server survive Android's process killer
# Usage: bash bulletproof_start.sh

LOG="$HOME/liljr_bulletproof.log"
PIDFILE="$HOME/liljr_server.pid"
SERVER="$HOME/liljr-autonomous/server_v8.py"

echo "[BULLETPROOF] $(date) Starting..." >> "$LOG"

# 1. Kill any old servers (nuclear)
pkill -9 -f "python.*server" 2>/dev/null
pkill -9 -f "server_v[0-9]" 2>/dev/null
pkill -9 -f "liljr_os" 2>/dev/null
pkill -9 -f "watchdog" 2>/dev/null
sleep 2

# 2. Acquire wake lock (keeps CPU alive)
termux-wake-lock 2>/dev/null || echo "[BULLETPROOF] wake-lock not available" >> "$LOG"

# 3. Start server with FULL isolation from terminal
# nohup = immune to hangup
# & = background
# >/dev/null 2>&1 = no output that could block
if [ -f "$SERVER" ]; then
    nohup python3 "$SERVER" > /dev/null 2>&1 &
    PID=$!
    echo $PID > "$PIDFILE"
    echo "[BULLETPROOF] Server PID: $PID" >> "$LOG"
else
    echo "[BULLETPROOF] ERROR: $SERVER not found" >> "$LOG"
    exit 1
fi

# 4. Wait for it to be ready
sleep 3

# 5. Verify
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "[BULLETPROOF] Server alive on port 8000" >> "$LOG"
    echo "✅ LilJR Empire is running. PID: $PID"
else
    echo "[BULLETPROOF] WARNING: Server not responding" >> "$LOG"
    echo "⚠️ Server started but not responding yet. Wait 5s and check."
fi

# 6. Start watchdog (separate process, also bulletproof)
watchdog_script="$HOME/liljr-autonomous/scripts/watchdog.sh"
if [ -f "$watchdog_script" ]; then
    nohup bash "$watchdog_script" > /dev/null 2>&1 &
    echo "[BULLETPROOF] Watchdog started" >> "$LOG"
fi

echo "[BULLETPROOF] Launch complete $(date)" >> "$LOG"
