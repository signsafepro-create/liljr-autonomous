#!/bin/bash
# liljr_chat_boot.sh — LILJR with CHAT MODE. No voice permissions needed.
# Same power. Just type instead of speak.

cd ~/liljr-autonomous

# Pull latest
git fetch origin main
git reset --hard origin/main

# NUCLEAR KILL
pkill -9 -f "liljr_v90_omni" 2>/dev/null
pkill -9 -f "server_v8" 2>/dev/null
pkill -9 -f "immortal_watchdog" 2>/dev/null
pkill -9 -f "liljr_voice_daemon" 2>/dev/null
pkill -9 -f "liljr_phone_master" 2>/dev/null
pkill -9 -f "liljr_phone_ui" 2>/dev/null
pkill -9 -f "liljr_system_takeover" 2>/dev/null
sleep 1

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║          🧬 LILJR — CHAT MODE (No Voice Needed)            ║"
echo "║                                                            ║"
echo "║         Type naturally. He responds. Full power.           ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# START OMNI brain
echo "[1/3] Booting OMNI brain..."
python3 liljr_v90_omni.py --server > ~/liljr_omni.log 2>&1 &
OMNI_PID=$!
disown $OMNI_PID 2>/dev/null

for i in $(seq 1 10); do
    if curl -s --max-time 1 http://localhost:7777/api/omni/status > /dev/null 2>&1; then
        echo "        ✅ OMNI ONLINE"
        break
    fi
    sleep 1
done

# START SYSTEM TAKEOVER
echo "[2/3] Hardwiring into phone..."
python3 liljr_system_takeover.py > ~/liljr_system.log 2>&1 &
SYS_PID=$!
disown $SYS_PID 2>/dev/null
sleep 2
echo "        ✅ SYSTEM TAKEOVER ACTIVE"

# PERSISTENT NOTIFICATION
echo "[3/3] Activating..."
termux-notification --title "🧬 LILJR CHAT" --content "Type 'wake up' to start. Full system access." --priority high --ongoing 2>/dev/null || true

echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "  TYPE NATURALLY. HE RESPONDS."
echo ""
echo "  Examples:"
echo "    wake up          → Status report"
echo "    buy AAPL 10      → Trade"
echo "    open camera      → Camera opens"
echo "    list files       → Your files"
echo "    system health    → CPU, RAM, battery"
echo "    organize photos  → Sorts camera roll"
echo "    screenshot       → Captures screen"
echo "    go stealth       → Invisible mode"
echo "    protect me       → Full lockdown"
echo "    research quantum → Deep dive"
echo "    tell me a joke   → Roasts you"
echo "    boot persist     → Auto-start on reboot"
echo ""
echo "  Say 'sleep' or 'quiet' when done."
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""

# START CHAT MODE
python3 liljr_chat.py
