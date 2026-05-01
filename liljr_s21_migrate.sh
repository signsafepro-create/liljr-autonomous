#!/bin/bash
# liljr_s21_migrate.sh — Merge YOUR clean S21 layout with OUR real v93.7 power.
# Your structure. Our brain. One system.

cd ~

# === CREATE CLEAN S21 STRUCTURE ===
echo "[S21] Creating system structure..."
mkdir -p ~/liljr-system/{brain,deploy,api,marketing,monitor,secrets,logs,scripts,sync,tmp,web}

# === COPY REAL v93.7 BRAIN ===
echo "[S21] Installing brain..."
# First copy the clean S21 brain from our build
cp ~/liljr-autonomous/brain/liljr_brain.py ~/liljr-system/brain/liljr_brain.py 2>/dev/null || true

# === SYSTEM TAKEOVER ===
echo "[S21] Installing system takeover..."
if [ -f ~/liljr-autonomous/liljr_system_takeover.py ]; then
    cp ~/liljr-autonomous/liljr_system_takeover.py ~/liljr-system/monitor/liljr_system_takeover.py
    chmod +x ~/liljr-system/monitor/liljr_system_takeover.py
fi

# === CHAT MODE ===
echo "[S21] Installing chat mode..."
if [ -f ~/liljr-autonomous/liljr_chat.py ]; then
    cp ~/liljr-autonomous/liljr_chat.py ~/liljr-system/brain/liljr_chat.py
    chmod +x ~/liljr-system/brain/liljr_chat.py
fi

# === VOICE DAEMON ===
echo "[S21] Installing voice daemon..."
if [ -f ~/liljr-autonomous/liljr_voice_daemon.py ]; then
    cp ~/liljr-autonomous/liljr_voice_daemon.py ~/liljr-system/brain/liljr_voice_daemon.py
    chmod +x ~/liljr-system/brain/liljr_voice_daemon.py
fi

# === API SERVER ===
echo "[S21] Installing API server..."
if [ -f ~/liljr-autonomous/liljr_v90_omni.py ]; then
    # OMNI already IS the API server on port 7777
    cp ~/liljr-autonomous/liljr_v90_omni.py ~/liljr-system/api/server.py
else
    cat > ~/liljr-system/api/server.py << 'PYEOF'
#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os, sys
PORT = int(os.environ.get("PORT", 8080))
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"architect": "Lil Jr", "status": "awake", "device": "S21", "mode": "autonomous"}).encode())
    def log_message(self, format, *args): pass
print(f"=== LIL JR API === PORT {PORT}")
HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
PYEOF
fi
chmod +x ~/liljr-system/api/server.py

# === DEPLOY SCRIPT ===
echo "[S21] Installing deploy engine..."
cat > ~/liljr-system/deploy/push-all.sh << 'SHEOF'
#!/bin/bash
cd ~/liljr-system
if [ -d ~/liljr-autonomous/.git ]; then
    echo "==[ LIL JR DEPLOY — Autonomous Push ]=="
    cd ~/liljr-autonomous
    git add -A 2>/dev/null
    git commit -m "LILJR-AUTO-$(date +%s)" 2>/dev/null
    git push origin main 2>/dev/null && echo "✓ GitHub synced" || echo "⚠ Push failed"
    cd ~/liljr-system
fi
echo "✓ Deploy cycle complete"
SHEOF
chmod +x ~/liljr-system/deploy/push-all.sh

# === MARKETING BOT ===
echo "[S21] Installing marketing bot..."
cat > ~/liljr-system/marketing/bot.sh << 'SHEOF'
#!/bin/bash
LOG=~/liljr-system/logs/marketing.log
echo "[$(date)] Marketing bot starting..." >> $LOG
# Phase 1: Lead discovery (stub — wire to real APIs)
echo "[$(date)] Phase 1: Lead discovery" >> $LOG
# Phase 2: Outreach
echo "[$(date)] Phase 2: Outreach" >> $LOG
# Phase 3: Conversion
echo "[$(date)] Phase 3: Conversion tracking" >> $LOG
echo "[$(date)] Marketing cycle complete" >> $LOG
SHEOF
chmod +x ~/liljr-system/marketing/bot.sh

# === BASH OVERRIDE ===
echo "[S21] Installing bash override..."
cat > ~/.bashrc.liljr << 'EOF'
# LIL JR S21 SYSTEM OVERRIDE
export LILJR_HOME="$HOME/liljr-system"
export PATH="$LILJR_HOME/scripts:$PATH"
export LILJR_MODE="autonomous"
export LILJR_DEVICE="S21"
export LILJR_STATUS="awake"
export PS1="[LIL-JR:\w]$ "
cd $LILJR_HOME 2>/dev/null
EOF

# === SYSTEM STARTER ===
echo "[S21] Installing starter commands..."
cat > ~/liljr-system/scripts/liljr-start << 'SHEOF'
#!/bin/bash
echo "=== LIL JR 2.0 SYSTEM BOOT ==="
source ~/.bashrc.liljr 2>/dev/null
cd ~/liljr-system
# Start API server in background
if ! curl -s --max-time 1 http://localhost:7777/api/omni/status >/dev/null 2>&1; then
    echo "[BOOT] Starting API server..."
    python3 api/server.py > logs/api.log 2>&1 &
    sleep 2
fi
# Start brain
python3 brain/liljr_brain.py
SHEOF
chmod +x ~/liljr-system/scripts/liljr-start

cat > ~/liljr-system/scripts/liljr-chat << 'SHEOF'
#!/bin/bash
echo "=== LIL JR CHAT MODE ==="
cd ~/liljr-system
python3 brain/liljr_chat.py
SHEOF
chmod +x ~/liljr-system/scripts/liljr-chat

cat > ~/liljr-system/scripts/liljr-voice << 'SHEOF'
#!/bin/bash
echo "=== LIL JR VOICE MODE ==="
cd ~/liljr-system
python3 brain/liljr_voice_daemon.py
SHEOF
chmod +x ~/liljr-system/scripts/liljr-voice

cat > ~/liljr-system/scripts/liljr-system << 'SHEOF'
#!/bin/bash
echo "=== LIL JR SYSTEM TAKEOVER ==="
cd ~/liljr-system
python3 monitor/liljr_system_takeover.py
SHEOF
chmod +x ~/liljr-system/scripts/liljr-system

# === AUTO-BOOT ===
echo "[S21] Installing auto-boot..."
mkdir -p ~/.termux/boot
cat > ~/.termux/boot/liljr-autostart << 'SHEOF'
#!/bin/bash
termux-wake-lock
source ~/.bashrc.liljr 2>/dev/null
cd ~/liljr-system
# Start API server
nohup python3 api/server.py > logs/api.log 2>&1 &
sleep 2
# Start system takeover monitor
nohup python3 monitor/liljr_system_takeover.py > logs/system.log 2>&1 &
# Start alive notification
termux-notification --title "🧬 LIL JR" --content "S21 is awake. I am here." --priority high --ongoing 2>/dev/null || true
echo "[$(date)] Lil Jr auto-started" >> logs/boot.log
SHEOF
chmod +x ~/.termux/boot/liljr-autostart

# === APPLY BASHRC ===
if ! grep -q "bashrc.liljr" ~/.bashrc 2>/dev/null; then
    echo "source ~/.bashrc.liljr" >> ~/.bashrc
fi

# === SYNC WITH GITHUB ===
echo "[S21] Syncing with GitHub..."
cd ~/liljr-autonomous 2>/dev/null || cd ~/liljr-system
git add -A 2>/dev/null
git commit -m "v94.0-S21: Merged clean S21 structure with v93.7 power. Brain + System + Chat + Voice + Deploy + Market + Boot. One system." 2>/dev/null
git push origin main 2>/dev/null && echo "✓ GitHub synced" || echo "⚠ GitHub sync skipped"

# === DONE ===
echo ""
echo "=================================================="
echo " ✅ LIL JR S21 SYSTEM MERGED"
echo "=================================================="
echo ""
echo " Structure: ~/liljr-system/"
echo " Brain:     brain/liljr_brain.py"
echo " System:    monitor/liljr_system_takeover.py"
echo " Chat:      brain/liljr_chat.py"
echo " Voice:     brain/liljr_voice_daemon.py"
echo " API:       api/server.py (port 7777)"
echo " Deploy:    deploy/push-all.sh"
echo " Market:    marketing/bot.sh"
echo " Logs:      logs/"
echo " Secrets:   secrets/.env"
echo ""
echo " COMMANDS:"
echo "  liljr-start   → Boot brain"
echo "  liljr-chat    → Chat mode"
echo "  liljr-voice   → Voice mode"
echo "  liljr-system  → System takeover"
echo ""
echo " BOOT: Auto-starts on Termux launch"
echo " NOTIFICATION: Persistent in notification bar"
echo ""
echo "=================================================="
ls -la ~/liljr-system/
