#!/bin/bash
# ═════════════════════════════════════════════════════════════════
# LILJR REBUILD v6.1 — Download fresh from GitHub, no embedded code
# Run: cd ~ && bash rebuild.sh
# ═════════════════════════════════════════════════════════════════

set -e

cd ~ || exit 1

echo "🔥 REBUILDING LILJR v6.1 — Persistent State"
echo "============================================"

# 1. Clean slate (but KEEP state file)
echo "Cleaning..."
pkill -9 -f "python" 2>/dev/null || true
rm -rf liljr-autonomous

# 2. Clone repo
echo "Cloning from GitHub..."
git clone https://github.com/signsafepro-create/liljr-autonomous.git

# 3. Install deps
echo "Installing Flask..."
cd ~/liljr-autonomous/backend
pip install flask flask-cors requests 2>&1 | tail -3

# 4. Restore state if backup exists
if [ -f "~/liljr_state.json" ]; then
    echo "Restoring state..."
    cp ~/liljr_state.json ~/liljr-autonomous/state/ 2>/dev/null || true
fi

# 5. Download latest control script
echo "Updating control script..."
curl -s https://raw.githubusercontent.com/signsafepro-create/liljr-autonomous/main/scripts/lj.sh > ~/lj 2>/dev/null || cp ~/liljr-autonomous/scripts/lj.sh ~/lj
chmod +x ~/lj

# 6. Start server
echo "Starting server..."
cd ~/liljr-autonomous/backend
nohup python server_v6.py > ~/liljr.log 2>&1 &
sleep 2

# 7. Verify
echo ""
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✅ LILJR v6.1 IS RUNNING"
    curl -s http://localhost:8000/api/health
    echo ""
else
    echo "⚠️ Check: bash ~/lj log"
fi

echo ""
echo "Commands:"
echo "  bash ~/lj status"
echo "  bash ~/lj battery"
echo "  bash ~/lj text +1555123 hello"
echo "  bash ~/lj buy AAPL 5"
echo "  bash ~/lj watch AAPL 170"
echo "  bash ~/lj rule AAPL below 170 buy 5"
echo "  bash ~/lj ai What should I trade?"
echo "  bash ~/lj push              — Save everything to GitHub"
