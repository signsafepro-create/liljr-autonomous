#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# LILJR TERMUX CONTROL — Fixed filename (was conflict with directory)
# Run: bash ~/lj start
# ═══════════════════════════════════════════════════════════════

BASE="http://localhost:8000"
CMD="$1"
shift 2>/dev/null || true

case "$CMD" in
  start)
    cd ~/liljr-autonomous/backend 2>/dev/null || cd ~/liljr/liljr-autonomous/backend 2>/dev/null
    if [ ! -f "server.py" ]; then
      echo "❌ server.py not found. Cloning repo..."
      cd ~ && rm -rf liljr-autonomous && git clone https://github.com/signsafepro-create/liljr-autonomous.git
      cd ~/liljr-autonomous/backend
      pip install fastapi uvicorn requests python-dotenv 2>&1 | tail -3
    fi
    nohup python server.py > ~/liljr.log 2>&1 &
    sleep 2
    curl -s "$BASE/api/health" && echo "" || echo "⚠️ Server starting... run: bash ~/lj log"
    ;;
  stop)
    pkill -f "python server.py"
    echo "Stopped"
    ;;
  status)
    curl -s "$BASE/api/health" || echo "Server not running"
    ;;
  text|sms)
    curl -s -X POST "$BASE/api/social/sms/send" -H "Content-Type: application/json" -d "{\"number\":\"$1\",\"message\":\"$2\"}"
    echo ""
    ;;
  read|inbox)
    curl -s "$BASE/api/social/sms/read?limit=${1:-10}"
    echo ""
    ;;
  whatsapp|wa)
    curl -s -X POST "$BASE/api/social/whatsapp/send" -H "Content-Type: application/json" -d "{\"number\":\"$1\",\"message\":\"$2\"}"
    echo ""
    ;;
  telegram|tg)
    curl -s -X POST "$BASE/api/social/telegram/send" -H "Content-Type: application/json" -d "{\"message\":\"$1\"}"
    echo ""
    ;;
  notify)
    curl -s "$BASE/api/social/notifications"
    echo ""
    ;;
  contacts)
    curl -s "$BASE/api/social/contacts"
    echo ""
    ;;
  battery)
    curl -s "$BASE/api/phone/battery"
    echo ""
    ;;
  tap)
    curl -s -X POST "$BASE/api/phone/tap" -H "Content-Type: application/json" -d "{\"x\":$1,\"y\":$2}"
    echo ""
    ;;
  launch)
    curl -s -X POST "$BASE/api/social/open_app" -H "Content-Type: application/json" -d "{\"package\":\"$1\"}"
    echo ""
    ;;
  buy)
    curl -s -X POST "$BASE/api/trading/buy" -H "Content-Type: application/json" -d "{\"symbol\":\"$1\",\"qty\":${2:-1}}"
    echo ""
    ;;
  sell)
    curl -s -X POST "$BASE/api/trading/sell" -H "Content-Type: application/json" -d "{\"symbol\":\"$1\",\"qty\":${2:-null}}"
    echo ""
    ;;
  price)
    curl -s "$BASE/api/trading/price/$1"
    echo ""
    ;;
  portfolio)
    curl -s "$BASE/api/trading/portfolio"
    echo ""
    ;;
  clip)
    curl -s "$BASE/api/social/clipboard"
    echo ""
    ;;
  log)
    tail -20 ~/liljr.log 2>/dev/null || echo "No log yet"
    ;;
  setup)
    echo "Setting up LilJR..."
    cd ~
    rm -rf liljr-autonomous
    git clone https://github.com/signsafepro-create/liljr-autonomous.git
    cd liljr-autonomous/backend
    pip install fastapi uvicorn requests python-dotenv 2>&1 | tail -3
    echo "✅ Setup done. Run: bash ~/lj start"
    ;;
  *)
    echo "LilJR Control — bash ~/lj <command> [args]"
    echo ""
    echo "SERVER:"
    echo "  bash ~/lj start       — Start server"
    echo "  bash ~/lj stop        — Stop server"
    echo "  bash ~/lj status      — Check status"
    echo "  bash ~/lj log         — Server log"
    echo "  bash ~/lj setup       — Clone + install deps"
    echo ""
    echo "SMS / MESSAGING:"
    echo "  bash ~/lj text +1555123 'hi'     — Send SMS"
    echo "  bash ~/lj read [10]              — Read SMS"
    echo "  bash ~/lj wa +1555123 'hi'      — WhatsApp"
    echo "  bash ~/lj tg 'hello'             — Telegram"
    echo "  bash ~/lj notify                 — Read notifications"
    echo "  bash ~/lj contacts               — List contacts"
    echo ""
    echo "PHONE CONTROL:"
    echo "  bash ~/lj battery                — Battery status"
    echo "  bash ~/lj tap 500 800            — Tap screen"
    echo "  bash ~/lj launch com.whatsapp   — Open app"
    echo ""
    echo "TRADING:"
    echo "  bash ~/lj buy AAPL 5             — Buy stock"
    echo "  bash ~/lj sell TSLA              — Sell stock"
    echo "  bash ~/lj price AAPL             — Check price"
    echo "  bash ~/lj portfolio              — Portfolio value"
    echo ""
    echo "UTILS:"
    echo "  bash ~/lj clip                   — Read clipboard"
    ;;
esac
