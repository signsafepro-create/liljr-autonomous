#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# LILJR CONTROL v6.1 — Persistent State, All Features
# Run: bash ~/lj <command> [args]
# ═══════════════════════════════════════════════════════════════

BASE="http://localhost:8000"
CMD="$1"
shift 2>/dev/null || true

case "$CMD" in
  start)
    cd ~/liljr-autonomous/backend 2>/dev/null
    nohup python server_v6.py > ~/liljr.log 2>&1 &
    sleep 2
    curl -s "$BASE/api/health" && echo "" || echo "⚠️ Starting..."
    ;;
  stop)
    pkill -9 -f "server_v6" && echo "Stopped" || echo "Not running"
    ;;
  status)
    curl -s "$BASE/api/health" || echo "Not running"
    ;;
  install)
    pip install flask flask-cors requests 2>&1 | tail -3 && echo "Done"
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
  # ─── STATE ───
  state)
    cat ~/liljr_state.json 2>/dev/null || echo "No state file"
    ;;
  push)
    bash ~/lj stop
    cd ~ && curl -s https://raw.githubusercontent.com/signsafepro-create/liljr-autonomous/main/scripts/push_all.sh > push_all.sh && bash push_all.sh
    ;;
  # ─── UTILS ───
  log)
    tail -20 ~/liljr.log 2>/dev/null || echo "No log"
    ;;
  *)
    echo "LilJR v6.1 — bash ~/lj <command> [args]"
    echo ""
    echo "SERVER:"
    echo "  bash ~/lj start              — Start server"
    echo "  bash ~/lj stop               — Stop server"
    echo "  bash ~/lj status             — Check status"
    echo "  bash ~/lj install            — Install deps"
    echo "  bash ~/lj push               — Push all to GitHub"
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
    echo "  bash ~/lj watch AAPL 170     — Watch AAPL, alert at <= $170"
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
    echo "STATE:"
    echo "  bash ~/lj state                — Show saved state"
    echo "  bash ~/lj log                  — Server log"
    ;;
esac
