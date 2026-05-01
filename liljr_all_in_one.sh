#!/bin/bash
# liljr_all_in_one.sh — THE ONE COMMAND. Everything. LilJR IS your phone.
# Hardwired. System takeover. Voice. Chat. OMNI brain. All of it.

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
echo "║          🧬 LILJR v93.5 — SYSTEM TAKEOVER                  ║"
echo "║                                                            ║"
echo "║     YOUR PHONE IS LILJR. HARDWIRED. NO LIMITS.             ║"
echo "║                                                            ║"
echo "║  Files • Apps • System • Notifications • Clipboard • Boot  ║"
echo "║  Screenshot • Volume • Brightness • Deep Links • Alive     ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# START OMNI brain
echo "[1/4] Booting OMNI brain..."
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
echo "[2/4] Hardwiring into phone..."
python3 liljr_system_takeover.py > ~/liljr_system.log 2>&1 &
SYS_PID=$!
disown $SYS_PID 2>/dev/null
sleep 2
echo "        ✅ SYSTEM TAKEOVER ACTIVE"

# START VOICE DAEMON (if termux-speech-to-text works)
echo "[3/4] Starting voice daemon..."
if command -v termux-speech-to-text > /dev/null 2>&1; then
    python3 liljr_voice_daemon.py > ~/liljr_voice.log 2>&1 &
    VOICE_PID=$!
    disown $VOICE_PID 2>/dev/null
    sleep 2
    echo "        ✅ VOICE ACTIVE"
else
    echo "        ⚠️  Voice not available. Install termux-api app from F-Droid."
fi

# PERSISTENT NOTIFICATION
echo "[4/4] Sending alive notification..."
termux-notification --title "🧬 LILJR" --content "Your phone is alive. I am here. Say 'wake up'." --priority high --ongoing 2>/dev/null || true

echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "  LILJR IS HARDWIRED INTO YOUR PHONE."
echo ""
echo "  TALK TO HIM:"
echo "    • 'Open camera selfie' → Front camera"
echo "    • 'List files' → Shows your files"
echo "    • 'System health' → CPU, RAM, battery, temp"
echo "    • 'Organize photos' → Sorts your camera roll"
echo "    • 'Screenshot' → Captures screen"
echo "    • 'Copy hello' → Copies to clipboard"
echo "    • 'Volume 10' → Sets volume"
echo "    • 'Boot persist' → Auto-starts on reboot"
echo "    • 'Notify I am here' → Sends notification"
echo "    • 'Open settings wifi' → WiFi settings"
echo "    • 'Open bank chase' → Chase bank app"
echo "    • 'Open snapchat camera' → Snapchat"
echo "    • 'Wallpaper /sdcard/Pics/photo.jpg' → Changes wallpaper"
echo ""
echo "  VOICE COMMANDS (if termux-api app installed):"
echo "    Say: 'Wake up', 'Open camera', 'Buy AAPL 10', 'Status'"
echo ""
echo "  CHAT MODE (no voice needed):"
echo "    Run: python3 ~/liljr-autonomous/liljr_chat.py"
echo ""
echo "  PERSISTENT NOTIFICATION: LilJR stays in your notification bar."
echo "  BOOT PERSISTENCE: Say 'boot persist' to auto-start on reboot."
echo "  ALIVE LOOP: Proactive notifications every 30 min."
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""

# Keep alive
while true; do
    sleep 3600
done
