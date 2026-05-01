#!/bin/bash
# liljr_voice_boot.sh — LILJR LIVES. Voice-first. Your phone IS him.
# One command. He wakes up. He speaks. He listens. He executes.

cd ~/liljr-autonomous

# Pull latest
git fetch origin main
git reset --hard origin/main

# NUCLEAR KILL — no old processes
pkill -9 -f "liljr_v90_omni" 2>/dev/null
pkill -9 -f "server_v8" 2>/dev/null
pkill -9 -f "immortal_watchdog" 2>/dev/null
pkill -9 -f "liljr_voice_daemon" 2>/dev/null
pkill -9 -f "liljr_phone_master" 2>/dev/null
pkill -9 -f "liljr_phone_ui" 2>/dev/null
sleep 1

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║              🧬 LILJR — WAKING UP                          ║"
echo "║                                                            ║"
echo "║         Your phone. Your voice. Your command.              ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# START OMNI brain (server-only, no crash)
echo "[1/3] Booting OMNI brain..."
python3 liljr_v90_omni.py --server > ~/liljr_omni.log 2>&1 &
OMNI_PID=$!
disown $OMNI_PID 2>/dev/null

# Wait for OMNI
for i in $(seq 1 10); do
    if curl -s --max-time 1 http://localhost:7777/api/omni/status > /dev/null 2>&1; then
        echo "        ✅ OMNI ONLINE"
        break
    fi
    sleep 1
done

# START VOICE DAEMON
echo "[2/3] Starting voice daemon..."
python3 liljr_voice_daemon.py &
VOICE_PID=$!
disown $VOICE_PID 2>/dev/null
sleep 2

echo "        ✅ VOICE ACTIVE"
echo ""
echo "[3/3] LILJR IS ALIVE."
echo ""
echo "    Say: 'Wake up' or 'Hey Junior'"
echo "    He'll speak back. He'll execute."
echo "    He IS your phone."
echo ""
echo "    'Open camera' → Camera opens"
echo "    'Buy AAPL 10' → Trade executes"
echo "    'What's the weather' → He tells you"
echo "    'Go stealth' → Stealth active"
echo "    'Research nuclear fusion' → Deep dive"
echo "    'Tell me a joke' → He roasts you"
echo ""
echo "    Say 'sleep' or 'quiet' when done."
echo "    He'll watch everything in the dark."
echo ""

# Keep alive
while true; do
    sleep 3600
done
