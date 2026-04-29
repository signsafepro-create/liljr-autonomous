#!/usr/bin/env python3
"""
LILJR SERVER v6.2 — UNSTOPPABLE
Auto-reload state. Auto-save every 5 min. Telegram remote control.
Push alerts. One command rebuilds from GitHub.
"""
import os
import sys
import json
import random
import urllib.parse
import urllib.request
import time
import threading
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
PORT = int(os.environ.get('PORT', 8000))

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════
ALPACA_API_KEY = os.environ.get('ALPACA_API_KEY', '')
ALPACA_SECRET = os.environ.get('ALPACA_SECRET_KEY', '')
ALPACA_BASE = 'https://paper-api.alpaca.markets'

GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

# ─── STATE FILE ───
STATE_FILE = os.path.expanduser('~/liljr_state.json')

# In-memory state
WATCHLIST = {}
AUTO_RULES = []
ALERTS = []
TRADE_HISTORY = []
PORTFOLIO = {"cash": 10000.0, "positions": [{"symbol": "AAPL", "qty": 10, "avg_price": 170}, {"symbol": "TSLA", "qty": 5, "avg_price": 230}], "total_value": 12900.0}

# ═══════════════════════════════════════════════════════════════
# STATE PERSISTENCE — Never Lose Memory
# ═══════════════════════════════════════════════════════════════

def save_state():
    """Save all state to disk."""
    state = {
        "timestamp": str(datetime.now()),
        "watchlist": WATCHLIST,
        "auto_rules": AUTO_RULES,
        "alerts": ALERTS,
        "trade_history": TRADE_HISTORY,
        "portfolio": PORTFOLIO
    }
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"[SAVE ERROR] {e}")

def load_state():
    """Load state from disk on startup."""
    global WATCHLIST, AUTO_RULES, ALERTS, TRADE_HISTORY, PORTFOLIO
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
            WATCHLIST = state.get('watchlist', {})
            AUTO_RULES = state.get('auto_rules', [])
            ALERTS = state.get('alerts', [])
            TRADE_HISTORY = state.get('trade_history', [])
            PORTFOLIO = state.get('portfolio', PORTFOLIO)
            print(f"[STATE] Loaded from {STATE_FILE}")
            print(f"[STATE] Watchlist: {len(WATCHLIST)} items, Rules: {len(AUTO_RULES)}, Trades: {len(TRADE_HISTORY)}")
        except Exception as e:
            print(f"[LOAD ERROR] {e}")
    else:
        print(f"[STATE] No state file found. Starting fresh.")

# Load immediately
load_state()

# ═══════════════════════════════════════════════════════════════
# TELEGRAM NOTIFICATIONS — Alert When Things Happen
# ═══════════════════════════════════════════════════════════════

def send_telegram(message):
    """Send a message to Telegram if configured."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}).encode()
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"[TELEGRAM ERROR] {e}")

# ═══════════════════════════════════════════════════════════════
# PHONE / TERMUX
# ═══════════════════════════════════════════════════════════════

@app.route('/api/health')
def health():
    return jsonify({
        "status": "ok",
        "version": "v6.2-unstoppable",
        "mode": "full",
        "state_file": STATE_FILE,
        "watchlist_count": len(WATCHLIST),
        "rules_count": len(AUTO_RULES),
        "trade_count": len(TRADE_HISTORY),
        "telegram": bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
    })

@app.route('/api/save_state', methods=['POST'])
def api_save_state():
    save_state()
    return jsonify({"status": "saved", "file": STATE_FILE})

@app.route('/api/phone/battery')
def battery():
    try:
        import subprocess
        r = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return jsonify(json.loads(r.stdout))
    except: pass
    return jsonify({"percentage": 75, "status": "CHARGING"})

@app.route('/api/phone/tap', methods=['POST'])
def tap():
    d = request.get_json() or {}
    x, y = d.get('x', 500), d.get('y', 800)
    try:
        import subprocess
        subprocess.run(["input", "tap", str(x), str(y)], capture_output=True, timeout=2)
    except: pass
    return jsonify({"status": "ok", "x": x, "y": y})

@app.route('/api/social/clipboard', methods=['GET', 'POST'])
def clipboard():
    if request.method == 'POST':
        d = request.get_json() or {}
        try:
            import subprocess
            subprocess.run(["termux-clipboard-set", d.get('text', '')], capture_output=True, timeout=2)
        except: pass
        return jsonify({"status": "ok"})
    try:
        import subprocess
        r = subprocess.run(["termux-clipboard-get"], capture_output=True, text=True, timeout=2)
        return jsonify({"text": r.stdout.strip()})
    except: return jsonify({"text": ""})

@app.route('/api/social/open_app', methods=['POST'])
def open_app():
    d = request.get_json() or {}
    pkg = d.get('package', 'com.whatsapp')
    try:
        import subprocess
        subprocess.run(["am", "start", "-n", f"{pkg}/.MainActivity"], capture_output=True, timeout=2)
    except: pass
    return jsonify({"status": "ok", "package": pkg})

@app.route('/api/social/sms/send', methods=['POST'])
def send_sms():
    d = request.get_json() or {}
    n, m = d.get('number', ''), d.get('message', '')
    try:
        import subprocess
        subprocess.run(["termux-sms-send", "-n", n, m], capture_output=True, timeout=5)
    except: pass
    return jsonify({"status": "queued", "number": n})

@app.route('/api/social/sms/read')
def read_sms():
    limit = request.args.get('limit', 10, type=int)
    try:
        import subprocess
        r = subprocess.run(["termux-sms-list", "-l", str(limit)], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return jsonify({"messages": json.loads(r.stdout)})
    except: pass
    return jsonify({"messages": []})

@app.route('/api/social/whatsapp/send', methods=['POST'])
def send_whatsapp():
    d = request.get_json() or {}
    n, m = d.get('number', ''), d.get('message', '')
    try:
        import subprocess
        subprocess.run(["am", "start", "-a", "android.intent.action.VIEW", "-d", f"https://wa.me/{n}?text={urllib.parse.quote(m)}"], capture_output=True, timeout=2)
    except: pass
    return jsonify({"status": "queued"})

@app.route('/api/social/telegram/send', methods=['POST'])
def send_telegram_api():
    d = request.get_json() or {}
    m = d.get('message', '')
    send_telegram(m)
    return jsonify({"status": "queued", "message": m})

@app.route('/api/social/notifications')
def notifications():
    try:
        import subprocess
        r = subprocess.run(["termux-notification-list"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return jsonify({"notifications": json.loads(r.stdout)})
    except: pass
    return jsonify({"notifications": []})

@app.route('/api/social/contacts')
def contacts():
    try:
        import subprocess
        r = subprocess.run(["termux-contact-list"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return jsonify({"contacts": json.loads(r.stdout)})
    except: pass
    return jsonify({"contacts": []})

# ═══════════════════════════════════════════════════════════════
# TRADING
# ═══════════════════════════════════════════════════════════════

@app.route('/api/trading/price/<symbol>')
def stock_price(symbol):
    if ALPACA_API_KEY:
        try:
            req = urllib.request.Request(
                f'{ALPACA_BASE}/v2/stocks/{symbol.upper()}/quotes/latest',
                headers={'APCA-API-KEY-ID': ALPACA_API_KEY, 'APCA-API-SECRET-KEY': ALPACA_SECRET}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                return jsonify({"symbol": symbol.upper(), "price": data['quote']['ap'], "currency": "USD", "source": "alpaca"})
        except: pass
    base = {"AAPL": 175, "TSLA": 240, "NVDA": 890, "GOOGL": 175, "AMZN": 185, "MSFT": 420}
    return jsonify({"symbol": symbol.upper(), "price": base.get(symbol.upper(), random.randint(50, 500)), "currency": "USD", "source": "mock"})

@app.route('/api/trading/buy', methods=['POST'])
def buy_stock():
    d = request.get_json() or {}
    sym = d.get('symbol', 'AAPL')
    qty = d.get('qty') or 1

    if ALPACA_API_KEY:
        try:
            payload = json.dumps({"symbol": sym.upper(), "qty": qty, "side": "buy", "type": "market", "time_in_force": "day"}).encode()
            req = urllib.request.Request(
                f'{ALPACA_BASE}/v2/orders',
                data=payload,
                headers={'APCA-API-KEY-ID': ALPACA_API_KEY, 'APCA-API-SECRET-KEY': ALPACA_SECRET, 'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                TRADE_HISTORY.append({"time": str(datetime.now()), "action": "buy", "symbol": sym, "qty": qty})
                save_state()
                send_telegram(f"📈 *BOUGHT* {qty} shares of {sym.upper()}")
                return jsonify({"status": "FILLED", "symbol": sym.upper(), "qty": qty, "total": qty * 175, "broker": "alpaca", "order_id": data.get('id')})
        except Exception as e:
            return jsonify({"status": "ERROR", "error": str(e)})

    TRADE_HISTORY.append({"time": str(datetime.now()), "action": "buy", "symbol": sym, "qty": qty})
    PORTFOLIO['cash'] -= qty * 175
    save_state()
    send_telegram(f"📈 *BOUGHT* {qty} shares of {sym.upper()}")
    return jsonify({"status": "FILLED", "symbol": sym.upper(), "qty": qty, "total": qty * 175, "broker": "mock"})

@app.route('/api/trading/sell', methods=['POST'])
def sell_stock():
    d = request.get_json() or {}
    sym = d.get('symbol', 'AAPL')
    qty = d.get('qty') or 1

    if ALPACA_API_KEY:
        try:
            payload = json.dumps({"symbol": sym.upper(), "qty": qty, "side": "sell", "type": "market", "time_in_force": "day"}).encode()
            req = urllib.request.Request(
                f'{ALPACA_BASE}/v2/orders',
                data=payload,
                headers={'APCA-API-KEY-ID': ALPACA_API_KEY, 'APCA-API-SECRET-KEY': ALPACA_SECRET, 'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                TRADE_HISTORY.append({"time": str(datetime.now()), "action": "sell", "symbol": sym, "qty": qty})
                save_state()
                send_telegram(f"📉 *SOLD* {qty} shares of {sym.upper()}")
                return jsonify({"status": "FILLED", "symbol": sym.upper(), "qty": qty, "total": qty * 175, "broker": "alpaca", "order_id": data.get('id')})
        except Exception as e:
            return jsonify({"status": "ERROR", "error": str(e)})

    TRADE_HISTORY.append({"time": str(datetime.now()), "action": "sell", "symbol": sym, "qty": qty})
    PORTFOLIO['cash'] += qty * 175
    save_state()
    send_telegram(f"📉 *SOLD* {qty} shares of {sym.upper()}")
    return jsonify({"status": "FILLED", "symbol": sym.upper(), "qty": qty, "total": qty * 175, "broker": "mock"})

@app.route('/api/trading/portfolio')
def portfolio():
    if ALPACA_API_KEY:
        try:
            req = urllib.request.Request(
                f'{ALPACA_BASE}/v2/positions',
                headers={'APCA-API-KEY-ID': ALPACA_API_KEY, 'APCA-API-SECRET-KEY': ALPACA_SECRET}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                positions = json.loads(resp.read())
                return jsonify({"positions": positions, "broker": "alpaca", "live": True})
        except: pass
    return jsonify({**PORTFOLIO, "broker": "mock"})

@app.route('/api/trading/history')
def trade_history():
    return jsonify({"trades": TRADE_HISTORY[-50:]})

# ═══════════════════════════════════════════════════════════════
# WATCHLIST + ALERTS
# ═══════════════════════════════════════════════════════════════

@app.route('/api/watchlist', methods=['GET', 'POST', 'DELETE'])
def watchlist():
    global WATCHLIST
    if request.method == 'POST':
        d = request.get_json() or {}
        sym = d.get('symbol', '').upper()
        WATCHLIST[sym] = {"target": d.get('target_price'), "added": str(datetime.now())}
        save_state()
        send_telegram(f"👁 Added *{sym}* to watchlist (target: ${d.get('target_price')})")
        return jsonify({"watchlist": WATCHLIST})
    if request.method == 'DELETE':
        d = request.get_json() or {}
        WATCHLIST.pop(d.get('symbol', '').upper(), None)
        save_state()
        return jsonify({"watchlist": WATCHLIST})
    return jsonify({"watchlist": WATCHLIST})

@app.route('/api/watchlist/check')
def check_watchlist():
    results = []
    for sym, info in WATCHLIST.items():
        price_data = stock_price(sym).get_json()
        current = price_data.get('price', 0)
        target = info.get('target')
        triggered = False
        if target and current <= target:
            triggered = True
            alert = {"symbol": sym, "current": current, "target": target, "time": str(datetime.now())}
            ALERTS.append(alert)
            save_state()
            send_telegram(f"🚨 *ALERT* {sym} triggered!\nCurrent: ${current} | Target: ${target}")
        results.append({"symbol": sym, "current": current, "target": target, "triggered": triggered})
    return jsonify({"results": results, "alerts": ALERTS[-10:]})

# ═══════════════════════════════════════════════════════════════
# AUTO-TRADING RULES
# ═══════════════════════════════════════════════════════════════

@app.route('/api/rules', methods=['GET', 'POST', 'DELETE'])
def rules():
    global AUTO_RULES
    if request.method == 'POST':
        d = request.get_json() or {}
        rule = {
            "id": len(AUTO_RULES) + 1,
            "symbol": d.get('symbol', '').upper(),
            "condition": d.get('condition', 'below'),
            "target_price": d.get('target_price', 0),
            "action": d.get('action', 'buy'),
            "qty": d.get('qty', 1),
            "active": True
        }
        AUTO_RULES.append(rule)
        save_state()
        send_telegram(f"⚙️ Auto-rule #{rule['id']}: {rule['action'].upper()} {rule['symbol']} when {rule['condition']} ${rule['target_price']}")
        return jsonify({"rules": AUTO_RULES})
    if request.method == 'DELETE':
        d = request.get_json() or {}
        AUTO_RULES = [r for r in AUTO_RULES if r['id'] != d.get('id')]
        save_state()
        return jsonify({"rules": AUTO_RULES})
    return jsonify({"rules": AUTO_RULES})

@app.route('/api/rules/run')
def run_rules():
    executed = []
    for rule in AUTO_RULES:
        if not rule['active']:
            continue
        sym = rule['symbol']
        price_data = stock_price(sym).get_json()
        current = price_data.get('price', 0)
        target = rule['target_price']
        condition = rule['condition']

        should_execute = False
        if condition == 'below' and current <= target:
            should_execute = True
        elif condition == 'above' and current >= target:
            should_execute = True

        if should_execute:
            action = rule['action']
            qty = rule['qty']
            if action == 'buy':
                with app.test_client() as c:
                    c.post('/api/trading/buy', json={"symbol": sym, "qty": qty})
            else:
                with app.test_client() as c:
                    c.post('/api/trading/sell', json={"symbol": sym, "qty": qty})
            executed.append({"rule_id": rule['id'], "symbol": sym, "action": action, "qty": qty, "price": current})
            rule['active'] = False
            save_state()
    return jsonify({"executed": executed, "rules": AUTO_RULES})

# ═══════════════════════════════════════════════════════════════
# AI — GROQ
# ═══════════════════════════════════════════════════════════════

@app.route('/api/chat', methods=['POST'])
def chat():
    d = request.get_json() or {}
    message = d.get('message', '')

    if GROQ_API_KEY:
        try:
            payload = json.dumps({
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": message}],
                "max_tokens": 500
            }).encode()
            req = urllib.request.Request(
                GROQ_URL,
                data=payload,
                headers={'Authorization': f'Bearer {GROQ_API_KEY}', 'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                reply = data['choices'][0]['message']['content']
                return jsonify({"reply": reply, "mode": "groq"})
        except Exception as e:
            return jsonify({"reply": f"AI error: {str(e)}", "mode": "local"})

    return jsonify({"reply": f"LilJR: {message}", "mode": "local"})

@app.route('/api/ai/analyze', methods=['POST'])
def ai_analyze():
    d = request.get_json() or {}
    symbol = d.get('symbol', 'AAPL')
    price_data = stock_price(symbol).get_json()
    current = price_data.get('price', 0)
    prompt = f"Analyze {symbol} at ${current}. Trading recommendation in 2 sentences."

    if GROQ_API_KEY:
        try:
            payload = json.dumps({
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200
            }).encode()
            req = urllib.request.Request(
                GROQ_URL,
                data=payload,
                headers={'Authorization': f'Bearer {GROQ_API_KEY}', 'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                return jsonify({"symbol": symbol, "price": current, "analysis": data['choices'][0]['message']['content'], "mode": "groq"})
        except Exception as e:
            return jsonify({"symbol": symbol, "price": current, "analysis": f"Error: {str(e)}", "mode": "local"})

    return jsonify({"symbol": symbol, "price": current, "analysis": "Mock: Hold position.", "mode": "local"})

# ═══════════════════════════════════════════════════════════════
# TELEGRAM BOT WEBHOOK — Remote Control From Anywhere
# ═══════════════════════════════════════════════════════════════

@app.route('/api/telegram/webhook', methods=['POST'])
def telegram_webhook():
    """Receive Telegram bot commands and execute them."""
    data = request.get_json() or {}
    msg = data.get('message', {})
    text = msg.get('text', '').strip().lower()
    chat_id = msg.get('chat', {}).get('id', '')
    
    # Only respond to authorized chat
    if str(chat_id) != str(TELEGRAM_CHAT_ID):
        return jsonify({"status": "unauthorized"})
    
    response = "Unknown command. Try: status, price AAPL, buy AAPL 5, sell TSLA, portfolio, watches"
    
    if text == '/start' or text == 'help':
        response = """🤖 *LilJR Remote Control*

Commands:
• `status` — Server health
• `price <symbol>` — Stock price
• `buy <symbol> <qty>` — Buy stock
• `sell <symbol> <qty>` — Sell stock
• `portfolio` — Your portfolio
• `watches` — Watchlist
• `rules` — Auto-trading rules
• `alert` — Recent alerts"""
    
    elif text == 'status':
        response = f"✅ LilJR running\nWatchlist: {len(WATCHLIST)} | Rules: {len(AUTO_RULES)} | Trades: {len(TRADE_HISTORY)}"
    
    elif text.startswith('price '):
        sym = text.split(' ')[1].upper() if len(text.split(' ')) > 1 else 'AAPL'
        price_data = stock_price(sym).get_json()
        response = f"📊 *{sym}* ${price_data.get('price', 'N/A')}"
    
    elif text.startswith('buy '):
        parts = text.split(' ')
        sym = parts[1].upper() if len(parts) > 1 else 'AAPL'
        qty = int(parts[2]) if len(parts) > 2 else 1
        with app.test_client() as c:
            r = c.post('/api/trading/buy', json={"symbol": sym, "qty": qty})
            data = r.get_json()
            response = f"📈 Bought {qty} {sym} — {data.get('status', '?')}"
    
    elif text.startswith('sell '):
        parts = text.split(' ')
        sym = parts[1].upper() if len(parts) > 1 else 'AAPL'
        qty = int(parts[2]) if len(parts) > 2 else 1
        with app.test_client() as c:
            r = c.post('/api/trading/sell', json={"symbol": sym, "qty": qty})
            data = r.get_json()
            response = f"📉 Sold {qty} {sym} — {data.get('status', '?')}"
    
    elif text == 'portfolio':
        response = f"💰 Cash: ${PORTFOLIO.get('cash', 0)}\nPositions: {len(PORTFOLIO.get('positions', []))}"
    
    elif text == 'watches':
        watches = ', '.join(WATCHLIST.keys()) if WATCHLIST else 'None'
        response = f"👁 Watchlist: {watches}"
    
    elif text == 'rules':
        active = sum(1 for r in AUTO_RULES if r['active'])
        response = f"⚙️ {len(AUTO_RULES)} rules ({active} active)"
    
    elif text == 'alert':
        recent = ALERTS[-3:] if ALERTS else []
        response = "🚨 Recent alerts:\n" + "\n".join([f"{a['symbol']} at ${a['current']}" for a in recent]) if recent else "No recent alerts"
    
    # Reply via Telegram
    send_telegram(response)
    return jsonify({"status": "ok", "command": text})

# ═══════════════════════════════════════════════════════════════
# BACKGROUND MONITOR — Auto-save + Watchlist + Rules
# ═══════════════════════════════════════════════════════════════

def price_monitor():
    """Run every minute: check watchlist, run rules, auto-save state."""
    auto_save_counter = 0
    while True:
        try:
            # Check watchlist and run rules
            if WATCHLIST:
                with app.test_client() as c:
                    c.get('/api/watchlist/check')
            if AUTO_RULES:
                with app.test_client() as c:
                    c.get('/api/rules/run')
            
            # Auto-save every 5 minutes (300 seconds = 5 cycles)
            auto_save_counter += 1
            if auto_save_counter >= 5:
                save_state()
                print(f"[AUTO-SAVE] {datetime.now()}")
                auto_save_counter = 0
                
        except Exception as e:
            print(f"[MONITOR ERROR] {e}")
        time.sleep(60)

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    threading.Thread(target=price_monitor, daemon=True).start()
    print(f"🚀 LilJR v6.2 — UNSTOPPABLE")
    print(f"   State: {STATE_FILE}")
    print(f"   Watchlist: {len(WATCHLIST)}, Rules: {len(AUTO_RULES)}, Trades: {len(TRADE_HISTORY)}")
    print(f"   Telegram: {'ON' if TELEGRAM_BOT_TOKEN else 'OFF'}")
    print(f"   Auto-save: Every 5 minutes")
    print(f"   Running on http://0.0.0.0:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
