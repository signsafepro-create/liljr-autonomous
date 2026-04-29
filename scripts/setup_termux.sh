#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# ONE-SHOT SETUP — Clone, Install, Start, Control
# Paste this ENTIRE block into Termux and hit enter
# ═══════════════════════════════════════════════════════════════

cd ~

# 1. Clone if not exists
if [ ! -d "liljr-autonomous" ]; then
  git clone https://github.com/signsafepro-create/liljr-autonomous.git
fi

cd liljr-autonomous/backend

# 2. Install deps (NO watchfiles/rust bullshit)
pip install fastapi uvicorn requests python-dotenv

# 3. Create control script
mkdir -p ~/bin
cat > ~/bin/liljr << 'CTL'
#!/bin/bash
BASE="http://localhost:8000"
CMD="$1"
shift || true

case "$CMD" in
  start)
    cd ~/liljr-autonomous/backend
    nohup python server.py > ~/liljr.log 2>&1 &
    sleep 2
    curl -s "$BASE/api/health" && echo "" && echo "✅ Server running" || echo "❌ Failed to start"
    ;;
  stop)
    pkill -f "python server.py"
    echo "Stopped"
    ;;
  status)
    curl -s "$BASE/api/health" | python -c "import sys,json; d=json.load(sys.stdin); print(d)" 2>/dev/null || echo "Server not running"
    ;;
  text|sms)
    curl -s -X POST "$BASE/api/social/sms/send" -H "Content-Type: application/json" -d "{\"number\":\"$1\",\"message\":\"$2\"}"
    echo ""
    ;;
  read|inbox)
    curl -s "$BASE/api/social/sms/read?limit=${1:-10}" | python -c "import sys,json; [print(m.get('number','?'),':',m.get('body','')[:60]) for m in json.load(sys.stdin).get('messages',[])]" 2>/dev/null
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
    curl -s "$BASE/api/social/notifications" | python -c "import sys,json; [print(n.get('title','?'),':',n.get('content','')[:50]) for n in json.load(sys.stdin).get('notifications',[])]" 2>/dev/null
    ;;
  contacts)
    curl -s "$BASE/api/social/contacts" | python -c "import sys,json; [print(c.get('name','?'),'-',c.get('number','')) for c in json.load(sys.stdin).get('contacts',[])]" 2>/dev/null
    ;;
  battery)
    curl -s "$BASE/api/phone/battery" | python -c "import sys,json; d=json.load(sys.stdin); print(d)" 2>/dev/null
    ;;
  screenshot)
    curl -s "$BASE/api/phone/screenshot" | python -c "import sys,json; d=json.load(sys.stdin); print(d)" 2>/dev/null
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
    curl -s "$BASE/api/trading/price/$1" | python -c "import sys,json; d=json.load(sys.stdin); print(d)" 2>/dev/null
    ;;
  portfolio)
    curl -s "$BASE/api/trading/portfolio" | python -c "import sys,json; d=json.load(sys.stdin); print(d)" 2>/dev/null
    ;;
  share)
    curl -s -X POST "$BASE/api/social/share/app" -H "Content-Type: application/json" -d "{\"text\":\"$1\",\"app\":\"$2\"}"
    echo ""
    ;;
  post)
    curl -s -X POST "$BASE/api/social/post" -H "Content-Type: application/json" -d "{\"text\":\"$1\",\"platform\":\"$2\"}"
    echo ""
    ;;
  clip)
    curl -s "$BASE/api/social/clipboard" | python -c "import sys,json; d=json.load(sys.stdin); print(d)" 2>/dev/null
    ;;
  log)
    tail -20 ~/liljr.log
    ;;
  *)
    echo "LilJR Control"
    echo "  liljr start"
    echo "  liljr stop"
    echo "  liljr status"
    echo "  liljr text +1555123 'hi'       — SMS"
    echo "  liljr read [10]                 — Read SMS"
    echo "  liljr wa +1555123 'hi'          — WhatsApp"
    echo "  liljr tg 'hello'                — Telegram"
    echo "  liljr notify                    — Notifications"
    echo "  liljr contacts                  — Contacts"
    echo "  liljr battery                   — Battery"
    echo "  liljr screenshot                — Screenshot"
    echo "  liljr tap 500 800               — Tap screen"
    echo "  liljr launch com.whatsapp       — Open app"
    echo "  liljr buy AAPL 5                — Buy stock"
    echo "  liljr sell TSLA                 — Sell stock"
    echo "  liljr price AAPL                — Stock price"
    echo "  liljr portfolio                 — Portfolio"
    echo "  liljr share 'hi' telegram       — Share to app"
    echo "  liljr post 'hi' twitter         — Post social"
    echo "  liljr clip                      — Clipboard"
    echo "  liljr log                       — View server log"
    ;;
esac
CTL
chmod +x ~/bin/liljr

# Add to PATH if not there
if ! echo "$PATH" | grep -q "$HOME/bin"; then
  echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
  export PATH="$HOME/bin:$PATH"
fi

# 4. Start server
cd ~/liljr-autonomous/backend
nohup python server.py > ~/liljr.log 2>&1 &
sleep 3

echo ""
echo "🚀 LILJR READY"
echo "==============="
curl -s http://localhost:8000/api/health && echo "" || echo "⚠️ Server starting... check 'liljr log' in 5 seconds"
echo ""
echo "Commands now work:"
echo "  liljr text +1555123 'hello'"
echo "  liljr wa +1555123 'check this'"
echo "  liljr tg 'system online'"
echo "  liljr notify"
echo "  liljr buy AAPL 5"
echo "  liljr tap 500 800"
echo "  liljr launch com.whatsapp"
echo ""
echo "Type 'liljr' for full help"
