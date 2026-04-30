#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# LILJR UNSTOPPABLE RESET — Nuclear option. Fresh start. All goodies.
# Kills everything old, wipes logs, starts clean with ALL features.
# ═══════════════════════════════════════════════════════════════

echo "☢️ LILJR UNSTOPPABLE RESET — Starting..."

# 1. KILL EVERYTHING — old and new
pkill -9 -f "python.*server" 2>/dev/null
pkill -9 -f "server_v[0-9]" 2>/dev/null
pkill -9 -f "liljr_os" 2>/dev/null
pkill -9 -f "watchdog" 2>/dev/null
pkill -9 -f "immortal" 2>/dev/null
pkill -9 -f "nohup" 2>/dev/null
pkill -9 python3 2>/dev/null
sleep 2

# 2. Clear ALL logs
rm -f ~/liljr*.log
rm -f ~/liljr_startup.log
rm -f ~/server_test.log
rm -f ~/liljr_bulletproof.log
rm -f ~/liljr_immortal.log
rm -f ~/liljr_watchdog.log

# 3. Remove corrupted backups
rm -f ~/liljr_state.json.bak
rm -f ~/liljr_memory.json.bak
rm -f ~/liljr_empire.db.bak
rm -f ~/liljr_server.pid

# 4. Reset wake lock
termux-wake-unlock 2>/dev/null
sleep 1

# 5. Pull LATEST code
cd ~/liljr-autonomous 2>/dev/null || {
    echo "❌ Repo not found. Cloning..."
    cd ~ && git clone https://github.com/signsafepro-create/liljr-autonomous.git
}
cd ~/liljr-autonomous && git pull origin main 2>/dev/null

# 6. Copy ALL fresh files to home
cp ~/liljr-autonomous/lj_empire.py ~/lj_empire.py 2>/dev/null
cp ~/liljr-autonomous/server_v8.py ~/server_v8.py 2>/dev/null
cp ~/liljr-autonomous/persona_engine.py ~/persona_engine.py 2>/dev/null
cp ~/liljr-autonomous/vision_engine.py ~/vision_engine.py 2>/dev/null
cp ~/liljr-autonomous/quickfire.py ~/quickfire.py 2>/dev/null
cp ~/liljr-autonomous/bulletproof_start.sh ~/bulletproof_start.sh 2>/dev/null
cp ~/liljr-autonomous/hard_reset.sh ~/hard_reset.sh 2>/dev/null

# 7. Verify no python remains
COUNT=$(ps -ef | grep python | grep -v grep | wc -l)
if [ "$COUNT" -gt 0 ]; then
    echo "⚠️ $COUNT python processes still alive. Killing again..."
    killall -9 python3 2>/dev/null
    sleep 1
fi

# 8. Start FRESH with v8 only
echo "🚀 Starting LilJR Empire v8.0 — Unstoppable..."
termux-wake-lock 2>/dev/null || true
cd ~/liljr-autonomous
nohup python3 ~/liljr-autonomous/server_v8.py > ~/liljr_startup.log 2>&1 &
PID=$!
echo "PID: $PID"

sleep 5

# 9. Verify
HEALTH=$(curl -s --max-time 5 http://localhost:8000/api/health 2>/dev/null)
if echo "$HEALTH" | grep -q "liljr-empire-8.0"; then
    echo ""
    echo "═" 55
    echo "✅ LILJR EMPIRE v8.0 RUNNING — UNSTOPPABLE"
    echo "═" 55
    echo ""
    echo "🎭 Personas: python3 ~/lj_empire.py persona list"
    echo "🤙 Best Friend: python3 ~/lj_empire.py persona switch best_friend"
    echo "🎤 Voice: Tap 🎤 in the web app"
    echo "📸 Camera: Tap 📸 to show LilJR what you see"
    echo "⚡ QuickFire: python3 ~/lj_empire.py qf 'build me a site'"
    echo ""
    echo "Open in browser:"
    echo "  http://localhost:8000"
    echo ""
    echo "═══ ALL GOODIES LOADED ═══"
    echo "  • QuickFire (fast + witty)"
    echo "  • Persona Engine (7 voices)"
    echo "  • Vision Engine (camera + learning)"
    echo "  • Web Frontend (dark + camera + voice toggle)"
    echo "  • Natural Language (talk like a friend)"
    echo "  • Self-Awareness (auto-fix)"
    echo "  • Auto-Coder (builds code)"
    echo "  • Marketing Engine (generates copy)"
    echo "  • Deep Search (web intelligence)"
    echo "  • Trading (buy/sell/portfolio)"
    echo "  • Web Builder (landing pages + apps)"
    echo "═" 55
else
    echo "⚠️ Server may need a moment..."
    echo "Check logs: cat ~/liljr_startup.log"
fi

# 10. DO NOT start autonomous loop or watchdog (user wants manual control)
# Clean start. Minimal footprint. Maximum power.

echo ""
echo "☢️ RESET COMPLETE — You're unstoppable now."
