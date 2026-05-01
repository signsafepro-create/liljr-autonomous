#!/bin/bash
# liljr_start.sh — THE ONE COMMAND. Your phone IS LilJR.
# Kill everything old. Start OMNI. Start Phone Master. No limitations.

cd ~/liljr-autonomous

# Pull latest (ignore local changes — we are the source of truth)
git fetch origin main
git reset --hard origin/main

# KILL ALL OLD PROCESSES — no mercy
pkill -9 -f "liljr_v90_omni" 2>/dev/null
pkill -9 -f "server_v8" 2>/dev/null
pkill -9 -f "immortal_watchdog" 2>/dev/null
pkill -9 -f "liljr_phone_master" 2>/dev/null
pkill -9 -f "liljr_phone_ui" 2>/dev/null
sleep 1

echo "🧬 LILJR — NO LIMITATIONS. EVERYTHING."
echo ""

# START OMNI in server-only mode (no input loop, no crash)
echo "[1/3] Starting OMNI brain..."
python3 liljr_v90_omni.py --server > ~/liljr_omni.log 2>&1 &
OMNI_PID=$!
disown $OMNI_PID 2>/dev/null

# Wait for port 7777
echo "[2/3] Waiting for OMNI to come online..."
for i in $(seq 1 10); do
    if curl -s --max-time 1 http://localhost:7777/api/omni/status > /dev/null 2>&1; then
        echo "        ✅ OMNI ONLINE"
        break
    fi
    sleep 1
done

# START PHONE MASTER
echo "[3/3] Starting PHONE MASTER..."
echo ""
echo "Your phone is LilJR. No app. No limits. Just power."
echo ""
python3 liljr_phone_master.py
