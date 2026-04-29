#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# LILJR CONTROL v6.2 — Honest State, Real Checks
# Run: bash ~/lj <command> [args]
# ═══════════════════════════════════════════════════════════════

BASE="http://localhost:8000"
CMD="$1"
shift 2>/dev/null || true

case "$CMD" in
  start)
    cd ~/liljr-autonomous/backend 2>/dev/null || {
        echo "❌ Backend directory not found. Run: bash ~/lj install"
        exit 1
    }
    nohup python server_v6.py > ~/liljr.log 2>&1 &
    sleep 2
    HEALTH=$(curl -s "$BASE/api/health" 2>/dev/null)
    if [ -n "$HEALTH" ]; then
        echo "$HEALTH"
    else
        echo "⚠️ Server starting (check: bash ~/lj log)"
    fi
    ;;
  stop)
    pkill -9 -f "server_v6" && echo "Stopped" || echo "Not running"
    ;;
  status)
    HEALTH=$(curl -s "$BASE/api/health" 2>/dev/null)
    if [ -n "$HEALTH" ]; then
        echo "$HEALTH"
    else
        echo "Not running"
    fi
    ;;
  install)
    # Clone repo if missing
    if [ ! -d "$HOME/liljr-autonomous" ]; then
        echo "📦 Cloning repo..."
        cd ~ && git clone https://github.com/signsafepro-create/liljr-autonomous.git
    fi
    pip install flask flask-cors requests 2>&1 | tail -3
    echo "Done"
    ;;
  # ─── STATE ───
  state)
    if [ -f "$HOME/liljr_state.json" ]; then
        cat "$HOME/liljr_state.json"
    else
        echo "No state file"
        echo ""
        echo "Start server: bash ~/lj start"
        echo "Or init blank: bash ~/lj state-init"
    fi
    ;;
  state-init)
    cat > "$HOME/liljr_state.json" << 'EOF'
{
  "version": "6.2",
  "created_at": "",
  "watchlist": [],
  "rules": [],
  "portfolio": {"cash": 10000.0, "positions": []},
  "trades": [],
  "notes": "Initial state"
}
EOF
    # Fill in current timestamp
    python3 -c "
import json, datetime
with open('$HOME/liljr_state.json', 'r') as f:
    d = json.load(f)
d['created_at'] = datetime.datetime.now().isoformat()
with open('$HOME/liljr_state.json', 'w') as f:
    json.dump(d, f, indent=2)
" 2>/dev/null || sed -i "s/\"created_at\": \"\"/\"created_at\": \"$(date -Iseconds)\"/" "$HOME/liljr_state.json"
    echo "✅ Blank state created at $HOME/liljr_state.json"
    echo "Start server: bash ~/lj start"
    ;;
  # ─── PHONE ───
  text|sms)
    curl -s -X POST "$BASE/api/social/sms/send" -H "Content-Type: application/json" -d "{\"number\":\"$1\",\"message\":\"$2\"}" && echo ""
    ;;
  read|inbox)
    curl -s "$BASE/api/social/sms/read?limit=${1:-10}" && echo ""
    ;;
  wa|whatsapp)
    curl -s -X POST "$BASE/api/social/whatsapp/send" -H "Content-Type: application/json" -d "{\"number\":\"$1\",\"message\":\"$2\"}" && echo ""
    ;;
  tg|telegram)
    curl -s -X POST "$BASE/api/social/telegram/send" -H "Content-Type: application/json" -d "{\"message\":\"$1\"}" && echo ""
    ;;
  notify)
    curl -s "$BASE/api/social/notifications" && echo ""
    ;;
  contacts)
    curl -s "$BASE/api/social/contacts" && echo ""
    ;;
  battery)
    curl -s "$BASE/api/phone/battery" && echo ""
    ;;
  tap)
    curl -s -X POST "$BASE/api/phone/tap" -H "Content-Type: application/json" -d "{\"x\":$1,\"y\":$2}" && echo ""
    ;;
  launch)
    curl -s -X POST "$BASE/api/social/open_app" -H "Content-Type: application/json" -d "{\"package\":\"$1\"}" && echo ""
    ;;
  clip)
    curl -s "$BASE/api/social/clipboard" && echo ""
    ;;
  # ─── TRADING ───
  buy)
    curl -s -X POST "$BASE/api/trading/buy" -H "Content-Type: application/json" -d "{\"symbol\":\"$1\",\"qty\":${2:-1}}" && echo ""
    ;;
  sell)
    curl -s -X POST "$BASE/api/trading/sell" -H "Content-Type: application/json" -d "{\"symbol\":\"$1\",\"qty\":${2:-1}}" && echo ""
    ;;
  price)
    curl -s "$BASE/api/trading/price/$1" && echo ""
    ;;
  portfolio)
    curl -s "$BASE/api/trading/portfolio" && echo ""
    ;;
  history)
    curl -s "$BASE/api/trading/history" && echo ""
    ;;
  # ─── WATCHLIST ───
  watch)
    curl -s -X POST "$BASE/api/watchlist" -H "Content-Type: application/json" -d "{\"symbol\":\"$1\",\"target_price\":$2}" && echo ""
    ;;
  unwatch)
    curl -s -X DELETE "$BASE/api/watchlist" -H "Content-Type: application/json" -d "{\"symbol\":\"$1\"}" && echo ""
    ;;
  watches)
    curl -s "$BASE/api/watchlist" && echo ""
    ;;
  check)
    curl -s "$BASE/api/watchlist/check" && echo ""
    ;;
  # ─── AUTO-TRADING ───
  rule)
    curl -s -X POST "$BASE/api/rules" -H "Content-Type: application/json" -d "{\"symbol\":\"$1\",\"condition\":\"$2\",\"target_price\":$3,\"action\":\"$4\",\"qty\":${5:-1}}" && echo ""
    ;;
  rules)
    curl -s "$BASE/api/rules" && echo ""
    ;;
  run)
    curl -s "$BASE/api/rules/run" && echo ""
    ;;
  delrule)
    curl -s -X DELETE "$BASE/api/rules" -H "Content-Type: application/json" -d "{\"id\":$1}" && echo ""
    ;;
  # ─── AI ───
  ai)
    curl -s -X POST "$BASE/api/chat" -H "Content-Type: application/json" -d "{\"message\":\"$*\"}" && echo ""
    ;;
  analyze)
    curl -s -X POST "$BASE/api/ai/analyze" -H "Content-Type: application/json" -d "{\"symbol\":\"$1\"}" && echo ""
    ;;
  # ─── PUSH ───
  push)
    bash ~/lj stop 2>/dev/null || true
    cd ~ && bash ~/liljr-autonomous/scripts/push_all.sh
    ;;
  # ─── FIX REMOTE (if token breaks) ───
  fix-remote)
    read -p "Paste GitHub token (starts with ghp_): " TOKEN
    git -C ~/liljr-autonomous remote set-url origin "https://${TOKEN}@github.com/signsafepro-create/liljr-autonomous.git"
    echo "Remote updated. Test: git -C ~/liljr-autonomous push origin main"
    ;;
  # ─── UTILS ───
  log)
    tail -20 ~/liljr.log 2>/dev/null || echo "No log"
    ;;
  *)
    echo "LilJR v6.2 — bash ~/lj <command> [args]"
    echo ""
    echo "SERVER:"
    echo "  bash ~/lj start              — Start server"
    echo "  bash ~/lj stop               — Stop server"
    echo "  bash ~/lj status             — Check status"
    echo "  bash ~/lj install            — Clone repo + install deps"
    echo "  bash ~/lj push               — Push state + code to GitHub"
    echo ""
    echo "STATE:"
    echo "  bash ~/lj state              — Show saved state"
    echo "  bash ~/lj state-init         — Create blank state file"
    echo ""
    echo "PHONE:"
    echo "  bash ~/lj text +1555123 hi   — Send SMS"
    echo "  bash ~/lj read [10]          — Read SMS"
    echo "  bash ~/lj wa +1555123 hi     — WhatsApp"
    echo "  bash ~/lj tg hello           — Telegram"
    echo "  bash ~/lj notify             — Notifications"
    echo "  bash ~/lj contacts           — Contacts"
    echo "  bash ~/lj battery            — Battery"
    echo "  bash ~/lj tap 500 800        — Tap screen"
    echo "  bash ~/lj launch com.app     — Open app"
    echo "  bash ~/lj clip               — Clipboard"
    echo ""
    echo "TRADING:"
    echo "  bash ~/lj buy AAPL 5         — Buy stock"
    echo "  bash ~/lj sell TSLA          — Sell stock"
    echo "  bash ~/lj price AAPL         — Check price"
    echo "  bash ~/lj portfolio          — Portfolio"
    echo "  bash ~/lj history            — Trade history"
    echo ""
    echo "WATCHLIST:"
    echo "  bash ~/lj watch AAPL 170     — Watch AAPL, alert at <= \$170"
    echo "  bash ~/lj unwatch AAPL       — Remove from watchlist"
    echo "  bash ~/lj watches            — List watchlist"
    echo "  bash ~/lj check              — Check all alerts"
    echo ""
    echo "AUTO-TRADING:"
    echo "  bash ~/lj rule AAPL below 170 buy 5    — Auto-buy rule"
    echo "  bash ~/lj rule TSLA above 300 sell 3   — Auto-sell rule"
    echo "  bash ~/lj rules              — List rules"
    echo "  bash ~/lj run                — Execute triggered rules"
    echo "  bash ~/lj delrule 1          — Delete rule #1"
    echo ""
    echo "AI:"
    echo "  bash ~/lj ai What should I trade?      — Ask AI"
    echo "  bash ~/lj analyze NVDA         — AI stock analysis"
    echo ""
    echo "UTILS:"
    echo "  bash ~/lj log                  — Server log"
    echo "  bash ~/lj fix-remote           — Fix GitHub token"
    ;;
esac
