#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# LILJR DISASTER RECOVERY — One command rebuilds everything
# Run: curl -s https://raw.githubusercontent.com/signsafepro-create/liljr-autonomous/main/scripts/restore.sh | bash
# ═══════════════════════════════════════════════════════════════

echo "🆘 LILJR DISASTER RECOVERY"
echo "==========================="

# 1. Install dependencies
echo "📦 Installing deps..."
pkg update -y 2>/dev/null || true
pkg install -y git python 2>/dev/null || apt-get install -y git python3 2>/dev/null || true
pip install flask flask-cors requests 2>&1 | tail -3

# 2. Clone/pull repo
echo "📦 Restoring repo..."
if [ -d "$HOME/liljr-autonomous/.git" ]; then
    cd "$HOME/liljr-autonomous" && git pull origin main
else
    rm -rf "$HOME/liljr-autonomous"
    cd "$HOME" && git clone https://github.com/signsafepro-create/liljr-autonomous.git
fi

# 3. Install lj command
cp "$HOME/liljr-autonomous/scripts/lj.sh" "$HOME/lj"
chmod +x "$HOME/lj"

# 4. Restore state from GitHub if local is missing
if [ ! -f "$HOME/liljr_state.json" ] && [ -f "$HOME/liljr-autonomous/state/liljr_state.json" ]; then
    cp "$HOME/liljr-autonomous/state/liljr_state.json" "$HOME/liljr_state.json"
    echo "✅ State restored from GitHub backup"
fi

# 5. Start server
echo "🚀 Starting server..."
bash "$HOME/lj" start

# 6. Start watchdog
echo "👁 Starting watchdog..."
nohup bash "$HOME/liljr-autonomous/scripts/watchdog.sh" > /dev/null 2>&1 &

echo ""
echo "✅ DISASTER RECOVERY COMPLETE"
echo "============================="
echo ""
echo "Everything is running:"
echo "  • Server: bash ~/lj status"
echo "  • Watchdog: ps | grep watchdog"
echo "  • Push: bash ~/lj push"
echo ""
echo "If you had a Telegram bot configured, set it again:"
echo "  export TELEGRAM_BOT_TOKEN=..."
echo "  export TELEGRAM_CHAT_ID=..."
echo ""
echo "You're unstoppable again."