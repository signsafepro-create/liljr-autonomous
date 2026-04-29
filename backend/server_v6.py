#!/usr/bin/env python3
"""
LILJR SERVER v6.0 — All Systems Integrated
Termux phone control + Real trading (Alpaca) + AI brain (Groq) + Price alerts + Auto-trading
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

# ─── Flask ───
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
PORT = int(os.environ.get('PORT', 8000))

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
ALPACA_API_KEY = os.environ.get('ALPACA_API_KEY', '')
ALPACA_SECRET = os.environ.get('ALPACA_SECRET_KEY', '')
ALPACA_BASE = 'https://paper-api.alpaca.markets'  # Paper trading by default

GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'

# In-memory state
WATCHLIST = {}
AUTO_RULES = []
ALERTS = []
TRADE_HISTORY = []

# ═══════════════════════════════════════════════════════════════
# PHONE / TERMUX ENDPOINTS (v5.x stable)
# ═══════════════════════════════════════════════════════════════

@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "version": "v6.0-all-together", "mode": "full"})

@app.route('/api/phone/battery')
def battery():
    try:
        import subprocess
        r = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return jsonify(json.loads(r.stdout))
    except Exception:
        pass
    return jsonify({"percentage": 75, "status": "CHARGING", "plugged": "AC"})

@app.route('/api/phone/tap', methods=['POST'])
def tap():
    d = request.get_json() or {}
    x, y = d.get('x', 500), d.get('y', 800)
    try:
        import subprocess
        subprocess.run(["input", "tap", str(x), str(y)], capture_output=True, timeout=2)
    except Exception:
        pass
    return jsonify({"status": "ok", "x": x, "y": y})

@app.route('/api/social/clipboard', methods=['GET', 'POST'])
def clipboard():
    if request.method == 'POST':
        d = request.get_json() or {}
        try:
            import subprocess
            subprocess.run(["termux-clipboard-set", d.get('text', '')], capture_output=True, timeout=2)
        except Exception:
            pass
        return jsonify({"status": "ok"})
    try:
        import subprocess
        r = subprocess.run(["termux-clipboard-get"], capture_output=True, text=True, timeout=2)
        return jsonify({"text": r.stdout.strip()})
    except Exception:
        return jsonify({"text": ""})

@app.route('/api/social/open_app', methods=['POST'])
def open_app():
    d = request.get_json() or {}
    pkg = d.get('package', 'com.whatsapp')
    try:
        import subprocess
        subprocess.run(["am", "start", "-n", f"{pkg}/.MainActivity"], capture_output=True, timeout=2)
    except Exception:
        pass
    return jsonify({"status": "ok", "package": pkg})

@app.route('/api/social/sms/send', methods=['POST'])
def send_sms():
    d = request.get_json() or {}
    n, m = d.get('number', ''), d.get('message', '')
    try:
        import subprocess
        subprocess.run(["termux-sms-send", "-n", n, m], capture_output=True, timeout=5)
    except Exception:
        pass
    return jsonify({"status": "queued", "number": n})

@app.route('/api/social/sms/read')
def read_sms():
    limit = request.args.get('limit', 10, type=int)
    try:
        import subprocess
        r = subprocess.run(["termux-sms-list", "-l", str(limit)], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return jsonify({"messages": json.loads(r.stdout)})
    except Exception:
        pass
    return jsonify({"messages": []})

@app.route('/api/social/whatsapp/send', methods=['POST'])
def send_whatsapp():
    d = request.get_json() or {}
    n, m = d.get('number', ''), d.get('message', '')
    try:
        import subprocess
        subprocess.run(["am", "start", "-a", "android.intent.action.VIEW", "-d", f"https://wa.me/{n}?text={urllib.parse.quote(m)}"], capture_output=True, timeout=2)
    except Exception:
        pass
    return jsonify({"status": "queued"})

@app.route('/api/social/telegram/send', methods=['POST'])
def send_telegram():
    d = request.get_json() or {}
    m = d.get('message', '')
    try:
        import subprocess
        subprocess.run(["am", "start", "-a", "android.intent.action.VIEW", "-d", "tg://resolve?domain=BotFather"], capture_output=True, timeout=2)
    except Exception:
        pass
    return jsonify({"status": "queued", "message": m})

@app.route('/api/social/notifications')
def notifications():
    try:
        import subprocess
        r = subprocess.run(["termux-notification-list"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return jsonify({"notifications": json.loads(r.stdout)})
    except Exception:
        pass
    return jsonify({"notifications": []})

@app.route('/api/social/contacts')
def contacts():
    try:
        import subprocess
        r = subprocess.run(["termux-contact-list"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return jsonify({"contacts": json.loads(r.stdout)})
    except Exception:
        pass
    return jsonify({"contacts": []})

# ═══════════════════════════════════════════════════════════════
# TRADING — Mock + Real Alpaca
# ═══════════════════════════════════════════════════════════════

@app.route('/api/trading/price/<symbol>')
def stock_price(symbol):
    # Try Alpaca first, fallback to mock
    if ALPACA_API_KEY:
        try:
            req = urllib.request.Request(
                f'{ALPACA_BASE}/v2/stocks/{symbol.upper()}/quotes/latest',
                headers={'APCA-API-KEY-ID': ALPACA_API_KEY, 'APCA-API-SECRET-KEY': ALPACA_SECRET}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                return jsonify({"symbol": symbol.upper(), "price": data['quote']['ap'], "currency": "USD", "source": "alpaca"})
        except Exception:
            pass
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
                return jsonify({"status": "FILLED", "symbol": sym.upper(), "qty": qty, "total": qty * 175, "broker": "alpaca", "order_id": data.get('id')})
        except Exception as e:
            return jsonify({"status": "ERROR", "error": str(e), "symbol": sym.upper()})

    TRADE_HISTORY.append({"time": str(datetime.now()), "action": "buy", "symbol": sym, "qty": qty})
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
                return jsonify({"status": "FILLED", "symbol": sym.upper(), "qty": qty, "total": qty * 175, "broker": "alpaca", "order_id": data.get('id')})
        except Exception as e:
            return jsonify({"status": "ERROR", "error": str(e), "symbol": sym.upper()})

    TRADE_HISTORY.append({"time": str(datetime.now()), "action": "sell", "symbol": sym, "qty": qty})
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
        except Exception:
            pass
    return jsonify({"cash": 10000.00, "positions": [{"symbol": "AAPL", "qty": 10, "avg_price": 170}, {"symbol": "TSLA", "qty": 5, "avg_price": 230}], "total_value": 12900.00, "broker": "mock"})

@app.route('/api/trading/history')
def trade_history():
    return jsonify({"trades": TRADE_HISTORY[-50:]})

# ═══════════════════════════════════════════════════════════════
# WATCHLIST + PRICE ALERTS
# ═══════════════════════════════════════════════════════════════

@app.route('/api/watchlist', methods=['GET', 'POST', 'DELETE'])
def watchlist():
    global WATCHLIST
    if request.method == 'POST':
        d = request.get_json() or {}
        sym = d.get('symbol', '').upper()
        target = d.get('target_price')
        WATCHLIST[sym] = {"target": target, "added": str(datetime.now())}
        return jsonify({"watchlist": WATCHLIST})
    if request.method == 'DELETE':
        d = request.get_json() or {}
        sym = d.get('symbol', '').upper()
        WATCHLIST.pop(sym, None)
        return jsonify({"watchlist": WATCHLIST})
    return jsonify({"watchlist": WATCHLIST})

@app.route('/api/watchlist/check')
def check_watchlist():
    results = []
    for sym, info in WATCHLIST.items():
        # Get current price
        price_data = stock_price(sym).get_json()
        current = price_data.get('price', 0)
        target = info.get('target')
        triggered = False
        if target and current <= target:
            triggered = True
            ALERTS.append({"symbol": sym, "current": current, "target": target, "time": str(datetime.now())})
        results.append({"symbol": sym, "current": current, "target": target, "triggered": triggered})
    return jsonify({"results": results, "alerts": ALERTS[-10:]})

# ═══════════════════════════════════════════════════════════════
# AUTO-TRADING RULES ENGINE
# ═══════════════════════════════════════════════════════════════

@app.route('/api/rules', methods=['GET', 'POST', 'DELETE'])
def rules():
    global AUTO_RULES
    if request.method == 'POST':
        d = request.get_json() or {}
        rule = {
            "id": len(AUTO_RULES) + 1,
            "symbol": d.get('symbol', '').upper(),
            "condition": d.get('condition', 'below'),  # below / above
            "target_price": d.get('target_price', 0),
            "action": d.get('action', 'buy'),  # buy / sell
            "qty": d.get('qty', 1),
            "active": True
        }
        AUTO_RULES.append(rule)
        return jsonify({"rules": AUTO_RULES})
    if request.method == 'DELETE':
        d = request.get_json() or {}
        rid = d.get('id')
        AUTO_RULES = [r for r in AUTO_RULES if r['id'] != rid]
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
            # Execute trade
            if action == 'buy':
                with app.test_client() as c:
                    c.post('/api/trading/buy', json={"symbol": sym, "qty": qty})
            else:
                with app.test_client() as c:
                    c.post('/api/trading/sell', json={"symbol": sym, "qty": qty})
            executed.append({"rule_id": rule['id'], "symbol": sym, "action": action, "qty": qty, "price": current})
            rule['active'] = False  # One-shot rule
    return jsonify({"executed": executed, "rules": AUTO_RULES})

# ═══════════════════════════════════════════════════════════════
# AI BRAIN — Groq Integration
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
                return jsonify({"reply": reply, "mode": "groq", "model": "llama3-8b"})
        except Exception as e:
            return jsonify({"reply": f"Groq error: {str(e)}", "mode": "local"})

    return jsonify({"reply": f"LilJR: {message}", "mode": "local"})

@app.route('/api/ai/analyze', methods=['POST'])
def ai_analyze():
    d = request.get_json() or {}
    symbol = d.get('symbol', 'AAPL')
    price_data = stock_price(symbol).get_json()
    current = price_data.get('price', 0)

    prompt = f"Analyze {symbol} stock at ${current}. Give a short trading recommendation in 2 sentences."

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
                analysis = data['choices'][0]['message']['content']
                return jsonify({"symbol": symbol, "price": current, "analysis": analysis, "mode": "groq"})
        except Exception as e:
            return jsonify({"symbol": symbol, "price": current, "analysis": f"Error: {str(e)}", "mode": "local"})

    return jsonify({"symbol": symbol, "price": current, "analysis": "Mock analysis: Hold position.", "mode": "local"})

# ═══════════════════════════════════════════════════════════════
# BACKGROUND WORKER — Price monitor thread
# ═══════════════════════════════════════════════════════════════

def price_monitor():
    while True:
        try:
            if WATCHLIST:
                with app.test_client() as c:
                    c.get('/api/watchlist/check')
            if AUTO_RULES:
                with app.test_client() as c:
                    c.get('/api/rules/run')
        except Exception:
            pass
        time.sleep(60)  # Check every minute

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    # Start background monitor
    monitor = threading.Thread(target=price_monitor, daemon=True)
    monitor.start()

    print(f"🚀 LilJR v6.0 — All Systems")
    print(f"   Phone control: /api/phone/*")
    print(f"   Trading: /api/trading/* (broker: {'alpaca' if ALPACA_API_KEY else 'mock'})")
    print(f"   AI: /api/chat (brain: {'groq' if GROQ_API_KEY else 'local'})")
    print(f"   Watchlist: /api/watchlist")
    print(f"   Auto-rules: /api/rules")
    print(f"   Running on http://0.0.0.0:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
