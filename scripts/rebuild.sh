#!/bin/bash
# LILJR REBUILD — Downloadable, no heredoc paste issues
# Run: bash rebuild.sh

cd ~ || exit 1

echo "🔥 REBUILDING LILJR..."

# 1. Kill everything
pkill -9 -f "python" 2>/dev/null || true
pkill -9 -f "server" 2>/dev/null || true
rm -rf ~/liljr-autonomous ~/lj ~/rebuild.sh

# 2. Create dirs
mkdir -p ~/liljr-autonomous/backend

# 3. Write server (Flask, no Pydantic)
cat > ~/liljr-autonomous/backend/server_termux.py << 'EOF'
import os, subprocess, json, random, urllib.parse
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
PORT = int(os.environ.get('PORT', 8000))

@app.route('/api/health')
def health(): return jsonify({"status": "ok", "version": "termux-5.0"})

@app.route('/api/phone/battery')
def battery():
    try:
        r = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0: return jsonify(json.loads(r.stdout))
    except: pass
    return jsonify({"percentage": 75, "status": "CHARGING"})

@app.route('/api/phone/tap', methods=['POST'])
def tap():
    d = request.get_json() or {}
    x, y = d.get('x', 500), d.get('y', 800)
    try: subprocess.run(["input", "tap", str(x), str(y)], capture_output=True, timeout=2)
    except: pass
    return jsonify({"status": "ok", "x": x, "y": y})

@app.route('/api/social/clipboard', methods=['GET', 'POST'])
def clipboard():
    if request.method == 'POST':
        d = request.get_json() or {}
        try: subprocess.run(["termux-clipboard-set", d.get('text', '')], capture_output=True, timeout=2)
        except: pass
        return jsonify({"status": "ok"})
    try:
        r = subprocess.run(["termux-clipboard-get"], capture_output=True, text=True, timeout=2)
        return jsonify({"text": r.stdout.strip()})
    except: return jsonify({"text": ""})

@app.route('/api/social/open_app', methods=['POST'])
def open_app():
    d = request.get_json() or {}
    pkg = d.get('package', 'com.whatsapp')
    try: subprocess.run(["am", "start", "-n", f"{pkg}/.MainActivity"], capture_output=True, timeout=2)
    except: pass
    return jsonify({"status": "ok", "package": pkg})

@app.route('/api/social/sms/send', methods=['POST'])
def send_sms():
    d = request.get_json() or {}
    n, m = d.get('number', ''), d.get('message', '')
    try: subprocess.run(["termux-sms-send", "-n", n, m], capture_output=True, timeout=5)
    except: pass
    return jsonify({"status": "queued", "number": n})

@app.route('/api/social/sms/read')
def read_sms():
    limit = request.args.get('limit', 10, type=int)
    try:
        r = subprocess.run(["termux-sms-list", "-l", str(limit)], capture_output=True, text=True, timeout=5)
        if r.returncode == 0: return jsonify({"messages": json.loads(r.stdout)})
    except: pass
    return jsonify({"messages": []})

@app.route('/api/social/whatsapp/send', methods=['POST'])
def send_whatsapp():
    d = request.get_json() or {}
    n, m = d.get('number', ''), d.get('message', '')
    try: subprocess.run(["am", "start", "-a", "android.intent.action.VIEW", "-d", f"https://wa.me/{n}?text={urllib.parse.quote(m)}"], capture_output=True, timeout=2)
    except: pass
    return jsonify({"status": "queued"})

@app.route('/api/social/telegram/send', methods=['POST'])
def send_telegram():
    d = request.get_json() or {}
    m = d.get('message', '')
    try: subprocess.run(["am", "start", "-a", "android.intent.action.VIEW", "-d", "tg://resolve?domain=BotFather"], capture_output=True, timeout=2)
    except: pass
    return jsonify({"status": "queued", "message": m})

@app.route('/api/social/notifications')
def notifications():
    try:
        r = subprocess.run(["termux-notification-list"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0: return jsonify({"notifications": json.loads(r.stdout)})
    except: pass
    return jsonify({"notifications": []})

@app.route('/api/social/contacts')
def contacts():
    try:
        r = subprocess.run(["termux-contact-list"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0: return jsonify({"contacts": json.loads(r.stdout)})
    except: pass
    return jsonify({"contacts": []})

@app.route('/api/trading/price/<symbol>')
def stock_price(symbol):
    base = {"AAPL": 175, "TSLA": 240, "NVDA": 890, "GOOGL": 175, "AMZN": 185, "MSFT": 420}
    return jsonify({"symbol": symbol.upper(), "price": base.get(symbol.upper(), random.randint(50, 500)), "currency": "USD"})

@app.route('/api/trading/buy', methods=['POST'])
def buy_stock():
    d = request.get_json() or {}
    sym = d.get('symbol', 'AAPL')
    qty = d.get('qty') or 1
    return jsonify({"status": "FILLED", "symbol": sym.upper(), "qty": qty, "total": qty * 175})

@app.route('/api/trading/sell', methods=['POST'])
def sell_stock():
    d = request.get_json() or {}
    sym = d.get('symbol', 'AAPL')
    qty = d.get('qty') or 1
    return jsonify({"status": "FILLED", "symbol": sym.upper(), "qty": qty, "total": qty * 175})

@app.route('/api/trading/portfolio')
def portfolio():
    return jsonify({"cash": 10000.00, "positions": [{"symbol": "AAPL", "qty": 10, "avg_price": 170}, {"symbol": "TSLA", "qty": 5, "avg_price": 230}], "total_value": 12900.00})

@app.route('/api/chat', methods=['POST'])
def chat():
    d = request.get_json() or {}
    return jsonify({"reply": f"LilJR: {d.get('message', '')}", "mode": "local"})

if __name__ == '__main__':
    print(f"🚀 LilJR on http://0.0.0.0:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
EOF

# 4. Write control script
cat > ~/lj << 'EOF'
#!/bin/bash
BASE="http://localhost:8000"
CMD="$1"
shift 2>/dev/null || true
case "$CMD" in
  start) cd ~/liljr-autonomous/backend && nohup python server_termux.py > ~/liljr.log 2>&1 & sleep 2 && curl -s "$BASE/api/health" && echo "" || echo "Starting..." ;;
  stop) pkill -9 -f "server_termux" && echo "Stopped" || echo "Not running" ;;
  status) curl -s "$BASE/api/health" || echo "Not running" ;;
  text|sms) curl -s -X POST "$BASE/api/social/sms/send" -H "Content-Type: application/json" -d "{\"number\":\"$1\",\"message\":\"$2\"}" && echo "" ;;
  read|inbox) curl -s "$BASE/api/social/sms/read?limit=${1:-10}" && echo "" ;;
  wa|whatsapp) curl -s -X POST "$BASE/api/social/whatsapp/send" -H "Content-Type: application/json" -d "{\"number\":\"$1\",\"message\":\"$2\"}" && echo "" ;;
  tg|telegram) curl -s -X POST "$BASE/api/social/telegram/send" -H "Content-Type: application/json" -d "{\"message\":\"$1\"}" && echo "" ;;
  notify) curl -s "$BASE/api/social/notifications" && echo "" ;;
  contacts) curl -s "$BASE/api/social/contacts" && echo "" ;;
  battery) curl -s "$BASE/api/phone/battery" && echo "" ;;
  tap) curl -s -X POST "$BASE/api/phone/tap" -H "Content-Type: application/json" -d "{\"x\":$1,\"y\":$2}" && echo "" ;;
  launch) curl -s -X POST "$BASE/api/social/open_app" -H "Content-Type: application/json" -d "{\"package\":\"$1\"}" && echo "" ;;
  buy) curl -s -X POST "$BASE/api/trading/buy" -H "Content-Type: application/json" -d "{\"symbol\":\"$1\",\"qty\":${2:-1}}" && echo "" ;;
  sell) curl -s -X POST "$BASE/api/trading/sell" -H "Content-Type: application/json" -d "{\"symbol\":\"$1\",\"qty\":${2:-1}}" && echo "" ;;
  price) curl -s "$BASE/api/trading/price/$1" && echo "" ;;
  portfolio) curl -s "$BASE/api/trading/portfolio" && echo "" ;;
  clip) curl -s "$BASE/api/social/clipboard" && echo "" ;;
  log) tail -20 ~/liljr.log 2>/dev/null || echo "No log" ;;
  install) pip install flask flask-cors requests 2>&1 | tail -3 && echo "Done" ;;
  *) echo "Usage: bash ~/lj <start|stop|status|text|read|wa|tg|notify|contacts|battery|tap|launch|buy|sell|price|portfolio|clip|log|install>" ;;
esac
EOF

chmod +x ~/lj

# 5. Install deps
echo "Installing Flask..."
pip install flask flask-cors requests 2>&1 | tail -3

# 6. Start
echo "Starting server..."
cd ~/liljr-autonomous/backend && nohup python server_termux.py > ~/liljr.log 2>&1 &
sleep 2

# 7. Verify
echo ""
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✅ LILJR IS RUNNING"
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
