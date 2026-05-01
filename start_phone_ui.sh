#!/bin/bash
# start_phone_ui.sh — Bulletproof launcher. Kills old OMNI, starts fresh, verifies port.

cd ~/liljr-autonomous

# Pull latest
git pull origin main 2>/dev/null

# STEP 1: Kill EVERY old OMNI (running, stopped, zombie)
echo "🧹 Cleaning up old OMNI..."
pkill -9 -f "liljr_v90_omni" 2>/dev/null
# Also kill any stopped jobs
jobs -p | xargs kill -9 2>/dev/null
sleep 1

# STEP 2: Start OMNI in server-only mode
echo "🧬 Starting OMNI brain (server-only)..."
python3 liljr_v90_omni.py --server > ~/liljr_omni.log 2>&1 &
OMNI_PID=$!
disown $OMNI_PID 2>/dev/null

# STEP 3: Wait for port 7777 to respond (max 10 seconds)
echo "⏳ Waiting for OMNI to boot..."
for i in $(seq 1 10); do
    if curl -s --max-time 1 http://localhost:7777/api/omni/status > /dev/null 2>&1; then
        echo "✅ OMNI online on port 7777"
        break
    fi
    sleep 1
done

# STEP 4: Start the phone UI
echo "📱 Starting LilJR Phone UI..."
python3 liljr_phone_ui.py
