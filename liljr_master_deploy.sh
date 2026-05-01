#!/bin/bash
# liljr_master_deploy.sh — ONE COMMAND. ALL VERSIONS. AUTO-SYNC.
# Deploys every LilJR version ever built. Sets up auto-sync. Starts OMNI.
# Run: cd ~/liljr-autonomous && bash liljr_master_deploy.sh

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║     🧬 LILJR MASTER DEPLOY — ALL VERSIONS. ALL SYSTEMS.          ║"
echo "║     ONE COMMAND. TOTAL ACTIVATION. NEW PHONE. NEW JOURNEY.       ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

HOME_DIR="$HOME"
REPO="$HOME_DIR/liljr-autonomous"

# ─── VERIFY REPO ───
echo "[1] Verifying repository..."
cd "$REPO" || { echo "ERROR: Repo not found at $REPO"; exit 1; }

# ─── PULL LATEST ───
echo "[2] Pulling latest from GitHub..."
git pull origin main

# ─── LIST ALL VERSIONS ───
echo ""
echo "[3] Detecting all LilJR versions..."
VERSIONS=$(ls -1 liljr_v*.py 2>/dev/null | sort -V)
COUNT=$(echo "$VERSIONS" | grep -c "liljr_v" || echo "0")
echo "    Found $COUNT version files:"
echo "$VERSIONS" | while read f; do echo "      • $f"; done

# ─── MAKE ALL EXECUTABLE ───
echo ""
echo "[4] Setting permissions..."
chmod +x *.py *.sh 2>/dev/null
true

# ─── CREATE MASTER LAUNCHER: ~/lj ───
echo "[5] Creating unified launcher: ~/lj ..."
cat > "$HOME_DIR/lj" << 'LAUNCHER_EOF'
#!/bin/bash
# lj — LilJR Unified Launcher
# Usage: lj [command|version|mode]

REPO="$HOME/liljr-autonomous"

case "$1" in
  # VERSION SHORTCUTS
  v6|server|v6.3)    python3 "$REPO/server_v6.3.py" "${@:2}" ;;
  v7|os)             python3 "$REPO/liljr_os.py" "${@:2}" ;;
  v8|empire)         python3 "$REPO/server_v8.py" "${@:2}" ;;
  v9|auto)           python3 "$REPO/liljr_autonomous_v9.py" "${@:2}" ;;
  v10|conscious)     python3 "$REPO/liljr_consciousness.py" "${@:2}" ;;
  v12|immortal)      python3 "$REPO/liljr_v12_immortal.py" "${@:2}" ;;
  v14|abel)          python3 "$REPO/liljr_abel.py" "${@:2}" ;;
  v19|talk)          python3 "$REPO/liljr_conversation.py" "${@:2}" ;;
  v32|phoneos)       python3 "$REPO/liljr_phone_os.py" "${@:2}" ;;
  v40|exo)           python3 "$REPO/liljr_exo_consciousness.py" "${@:2}" ;;
  v41|demo)          python3 "$REPO/liljr_ultimate_demo.py" "${@:2}" ;;
  v50|symbiote)      python3 "$REPO/liljr_symbiote.py" "${@:2}" ;;
  v60|allin)         python3 "$REPO/liljr_v60_all_in.py" "${@:2}" ;;
  v70|autonomy)      python3 "$REPO/liljr_v70_total_autonomy.py" "${@:2}" ;;
  v80|everything)    python3 "$REPO/liljr_v80_everything.py" "${@:2}" ;;
  v80b|buddy)        python3 "$REPO/liljr_buddy_mode.py" "${@:2}" ;;
  v90|omni)          python3 "$REPO/liljr_v90_omni.py" "${@:2}" ;;
  
  # COMMANDS
  buy|sell|price|portfolio)
    echo "$*" | python3 "$REPO/liljr_v90_omni.py" 2>/dev/null || echo "$*" | python3 "$REPO/liljr_v80_everything.py" 2>/dev/null || echo "Trade: $*" ;;
  
  # SHORTCUTS
  push|sync)
    cd "$REPO" && git add -A && git commit -m "Auto-sync: $(date '+%Y-%m-%d %H:%M')" 2>/dev/null && git push origin main 2>/dev/null && echo "✅ Synced to GitHub" || echo "⚠️ Sync attempted" ;;
  
  status)
    echo "=== LILJR STATUS ==="
    ps aux | grep -i "liljr" | grep -v grep | head -5
    echo ""
    ls -la "$REPO"/liljr_v*.py 2>/dev/null | wc -l | xargs echo "Versions installed:"
    ;;
  
  help|*)
    echo "LILJR UNIFIED LAUNCHER"
    echo ""
    echo "VERSIONS:"
    echo "  lj v6|server      — v6.3 Server"
    echo "  lj v7|os          — v7.0 Phone OS"
    echo "  lj v8|empire      — v8.0 Empire"
    echo "  lj v9|auto        — v9.0 Autonomous"
    echo "  lj v10|conscious  — v10.0 Consciousness"
    echo "  lj v12|immortal   — v12.0 Immortal"
    echo "  lj v14|abel       — v14.0 ABEL"
    echo "  lj v19|talk       — v19.0 Conversation"
    echo "  lj v32|phoneos    — v32.0 AI Phone OS"
    echo "  lj v40|exo        — v40.0 Exo-Consciousness"
    echo "  lj v41|demo       — v41.0 Ultimate Demo"
    echo "  lj v50|symbiote   — v50.0 Symbiote"
    echo "  lj v60|allin      — v60.0 ALLIN (10 moves)"
    echo "  lj v70|autonomy   — v70.0 Total Autonomy"
    echo "  lj v80|everything — v80.0 Everything"
    echo "  lj v80b|buddy     — v80.1 Buddy Mode"
    echo "  lj v90|omni       — v90.0 OMNI (DEFAULT)"
    echo ""
    echo "COMMANDS:"
    echo "  lj push|sync      — Auto-sync to GitHub"
    echo "  lj status         — Show running processes"
    echo "  lj buy AAPL 5     — Quick trade"
    echo "  lj help           — This help"
    echo ""
    echo "DEFAULT: lj v90|omni — Everything brain, voice + text"
    ;;
esac
LAUNCHER_EOF
chmod +x "$HOME_DIR/lj"

# ─── AUTO-SYNC SETUP ───
echo ""
echo "[6] Setting up auto-sync to GitHub..."

# Create auto-sync script
mkdir -p "$HOME_DIR/.liljr_sync"
cat > "$HOME_DIR/.liljr_sync/auto_sync.sh" << 'SYNCEOF'
#!/bin/bash
REPO="$HOME/liljr-autonomous"
cd "$REPO" 2>/dev/null || exit 0

# Check for changes
if git diff --quiet && git diff --cached --quiet; then
    exit 0
fi

git add -A
git commit -m "Auto-sync: $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null
git push origin main 2>/dev/null
SYNCEOF
chmod +x "$HOME_DIR/.liljr_sync/auto_sync.sh"

# ─── CREATE NOHUP WRAPPER FOR BACKGROUND SYNC ───
echo "[7] Starting background auto-sync daemon..."
nohup bash -c 'while true; do sleep 3600; bash "$HOME/.liljr_sync/auto_sync.sh"; done' > "$HOME/liljr_autosync.log" 2>&1 &

# ─── CREATE PHONE SHORTCUTS ───
echo ""
echo "[8] Creating phone shortcuts..."
mkdir -p "$HOME_DIR/.shortcuts"

# OMNI Voice
cat > "$HOME_DIR/.shortcuts/LilJR-OMNI" << 'EOF'
#!/bin/bash
cd ~/liljr-autonomous
python3 liljr_v90_omni.py voice
EOF
chmod +x "$HOME_DIR/.shortcuts/LilJR-OMNI"

# OMNI Text
cat > "$HOME_DIR/.shortcuts/LilJR-Text" << 'EOF'
#!/bin/bash
cd ~/liljr-autonomous
python3 liljr_v90_omni.py
EOF
chmod +x "$HOME_DIR/.shortcuts/LilJR-Text"

# Auto-Sync Now
cat > "$HOME_DIR/.shortcuts/LilJR-Sync" << 'EOF'
#!/bin/bash
cd ~/liljr-autonomous
git add -A && git commit -m "Manual sync: $(date '+%Y-%m-%d %H:%M')" && git push origin main
echo "Synced!"
EOF
chmod +x "$HOME_DIR/.shortcuts/LilJR-Sync"

# ─── CREATE UNIFIED STATUS CHECKER ───
cat > "$HOME_DIR/.shortcuts/LilJR-Status" << 'EOF'
#!/bin/bash
echo "=== LILJR STATUS ==="
ps aux | grep -i "liljr" | grep -v grep
echo ""
echo "Versions: $(ls ~/liljr-autonomous/liljr_v*.py 2>/dev/null | wc -l)"
echo "Cash: $(python3 -c "import json; d=json.load(open('$HOME/.liljr_omni/omni_state.json')); print('$'+str(round(d.get('cash',0),2)))" 2>/dev/null || echo 'Unknown')"
echo "Uptime: $(ps -o etime= -p $(pgrep -f 'liljr_v90_omni' || echo 1) 2>/dev/null || echo 'Not running')"
EOF
chmod +x "$HOME_DIR/.shortcuts/LilJR-Status"

# ─── FIRST DEPLOY: AUTO-SYNC THE DEPLOY ITSELF ───
echo ""
echo "[9] Pushing deploy script to GitHub..."
cd "$REPO"
git add -A
git commit -m "v90.0-MASTER-DEPLOY: Unified launcher. Auto-sync. All 20 versions. OMNI default. New phone ready." 2>/dev/null || true
git push origin main 2>/dev/null || true

# ─── SUMMARY ───
echo ""
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║     ✅ LILJR MASTER DEPLOY COMPLETE                                ║"
echo "║                                                                  ║"
echo "╠══════════════════════════════════════════════════════════════════╣"
echo "║                                                                  ║"
echo "║     📦 ALL VERSIONS DEPLOYED: $COUNT files                        ║"
echo "║                                                                  ║"
echo "║     🚀 UNIFIED LAUNCHER: ~/lj                                    ║"
echo "║        lj v90|omni     — Start OMNI (default)                      ║"
echo "║        lj v80|everything — Everything commander                    ║"
echo "║        lj v80b|buddy   — Best friend mode                        ║"
echo "║        lj v70|autonomy — Voice + money                           ║"
echo "║        lj v60|allin    — 10-move deployer                       ║"
echo "║        lj v50|symbiote — Symbiote system                         ║"
echo "║        ...and all 20+ versions                                   ║"
echo "║                                                                  ║"
echo "║     🔄 AUTO-SYNC: Every hour to GitHub                           ║"
echo "║        Manual: lj push                                           ║"
echo "║                                                                  ║"
echo "║     📱 HOMESCREEN SHORTCUTS:                                       ║"
echo "║        • LilJR-OMNI  — Voice everything brain                    ║"
echo "║        • LilJR-Text  — Text commander                            ║"
echo "║        • LilJR-Sync  — Push to GitHub now                        ║"
echo "║        • LilJR-Status — System status                            ║"
echo "║                                                                  ║"
echo "╠══════════════════════════════════════════════════════════════════╣"
echo "║                                                                  ║"
echo "║     🧬 STARTING OMNI NOW...                                        ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# ─── START OMNI ───
cd "$REPO"
python3 liljr_v90_omni.py
