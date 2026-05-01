#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# LILJR HARD RESET — Nuclear option. Fresh start.
# Kills everything, wipes logs, restarts clean.
# ═══════════════════════════════════════════════════════════════

echo "☢️ LILJR HARD RESET — Starting..."

# 1. KILL EVERYTHING
pkill -9 -f "python.*server" 2>/dev/null
pkill -9 -f "server_v[0-9]" 2>/dev/null
pkill -9 -f "liljr_os" 2>/dev/null
pkill -9 -f "watchdog" 2>/dev/null
pkill -9 -f "immortal" 2>/dev/null
pkill -9 -f "nohup" 2>/dev/null
pkill -9 -f "python.*natural" 2>/dev/null
pkill -9 python3 2>/dev/null
sleep 2

# 2. Clear ALL logs
rm -f ~/liljr*.log
rm -f ~/liljr_startup.log
rm -f ~/server_test.log
rm -f ~/liljr_bulletproof.log
rm -f ~/liljr_immortal.log
rm -f ~/liljr_watchdog.log

# 3. Remove old state files that might be corrupted
rm -f ~/liljr_state.json.bak
rm -f ~/liljr_memory.json.bak
rm -f ~/liljr_empire.db.bak

# 4. Clear any stuck PID files
rm -f ~/liljr_server.pid

# 5. Reset Termux wake lock (release it)
termux-wake-unlock 2>/dev/null
sleep 1

# 6. Pull latest code
cd ~/liljr-autonomous 2>/dev/null && git pull origin main 2>/dev/null

# 7. Copy fresh CLI
cp ~/liljr-autonomous/lj_empire.py ~/lj_empire.py 2>/dev/null

# 8. Verify no python processes remain
COUNT=$(ps -ef | grep python | grep -v grep | wc -l)
if [ "$COUNT" -gt 0 ]; then
    echo "⚠️ $COUNT python processes still alive. Killing again..."
    killall -9 python3 2>/dev/null
    sleep 1
fi

# 9. Start fresh with minimal footprint
echo "🚀 Starting LilJR clean..."
termux-wake-lock 2>/dev/null || true
nohup python3 ~/liljr-autonomous/server_v8.py > /dev/null 2>&1 &
PID=$!
echo "PID: $PID"

sleep 3

# 10. Verify
HEALTH=$(curl -s --max-time 3 http://localhost:8000/api/health 2>/dev/null)
if echo "$HEALTH" | grep -q "liljr-empire-8.0"; then
    echo "✅ LilJR v8.0 running clean. PID: $PID"
    echo "$HEALTH"
else
    echo "⚠️ Server may need a moment..."
fi

# 11. DO NOT start autonomous loop (user wants it off)
# DO NOT start watchdog (reduces background noise)
# DO NOT start immortal watcher

echo ""
echo "═" 50
echo "HARD RESET COMPLETE"
echo "No autonomous loop running."
echo "No watchdog running."
echo "Clean start. Minimal background processes."
echo "═" 50
