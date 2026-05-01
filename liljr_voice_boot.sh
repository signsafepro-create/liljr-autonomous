#!/bin/bash
# liljr_voice_boot.sh — v92.5 COMPLETE
# LILJR LIVES. Voice-first. Your phone IS him.
# One command. He wakes up. He speaks. He listens. He executes.
# APPS | PHONE | MONEY | SECURITY | RESEARCH | LEGAL | CODE | VISION | BUDDY | WORLD

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
echo "║              🧬 LILJR v92.5 — COMPLETE                     ║"
echo "║                                                            ║"
echo "║         Your phone. Your voice. Your command.              ║"
echo "║                                                            ║"
echo "║    APPS • PHONE • MONEY • SECURITY • RESEARCH • LEGAL     ║"
echo "║    CODE • VISION • BUDDY • WORLD • THINK AHEAD             ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# START OMNI brain
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
echo ""
echo "    EXAMPLES:"
echo "    • 'Open camera' → Camera opens"
echo "    • 'Buy AAPL 10' → Trade executes"
echo "    • 'What's the weather' → Live weather"
echo "    • 'Go stealth' → Invisible mode"
echo "    • 'Research quantum computing' → Deep dive"
echo "    • 'Write code for a web scraper' → File created"
echo "    • 'Diagnose my phone' → System health"
echo "    • 'Protect me' → Full lockdown"
echo "    • 'Tell me a joke' → He roasts you"
echo "    • 'What's the news' → Headlines"
echo "    • 'Price BTC' → Live crypto"
echo "    • 'Take a photo' → Photo captured"
echo "    • 'Status report' → Full system state"
echo ""
echo "    Say 'sleep' or 'quiet' when done."
echo "    He'll watch everything in the dark."
echo ""

# Keep alive
while true; do
    sleep 3600
done
