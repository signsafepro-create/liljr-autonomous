#!/usr/bin/env python3
"""
LILJR SERVER v6.3 — NOBODY HAS THIS
Self-healing. Context-aware. Sentiment-driven. Voice-controlled. AI-swarm ready.
"""
import os, sys, json, random, urllib.parse, urllib.request, time, threading, subprocess, re
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

# Context-aware trading
ENABLE_CONTEXT_AWARE = os.environ.get('ENABLE_CONTEXT_AWARE', 'true').lower() == 'true'
MIN_BATTERY_PCT = int(os.environ.get('MIN_BATTERY_PCT', '15'))
NIGHT_MODE_START = int(os.environ.get('NIGHT_MODE_START', '23'))
NIGHT_MODE_END = int(os.environ.get('NIGHT_MODE_END', '7'))

# Social sentiment
ENABLE_SENTIMENT = os.environ.get('ENABLE_SENTIMENT', 'false').lower() == 'true'
REDDIT_CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID', '')
REDDIT_SECRET = os.environ.get('REDDIT_SECRET', '')

STATE_FILE = os.path.expanduser('~/liljr_state.json')
HEALTH_LOG = os.path.expanduser('~/liljr_health.log')

# In-memory state
WATCHLIST = {}
AUTO_RULES = []
ALERTS = []
TRADE_HISTORY = []
PORTFOLIO = {"cash": 10000.0, "positions": [{"symbol": "AAPL", "qty": 10, "avg_price": 170}, {"symbol": "TSLA", "qty": 5, "avg_price": 230}], "total_value": 12900.0}
AGENT_TASKS = []  # AI swarm queue

# ═══════════════════════════════════════════════════════════════
# STATE PERSISTENCE
# ═══════════════════════════════════════════════════════════════

def save_state():
    state = {
        "timestamp": str(datetime.now()),
        "watchlist": WATCHLIST,
        "auto_rules": AUTO_RULES,
        "alerts": ALERTS,
        "trade_history": TRADE_HISTORY,
        "portfolio": PORTFOLIO,
        "agent_tasks": AGENT_TASKS[-50:]
    }
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"[SAVE ERROR] {e}")

def load_state():
    global WATCHLIST, AUTO_RULES, ALERTS, TRADE_HISTORY, PORTFOLIO, AGENT_TASKS
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
            WATCHLIST = state.get('watchlist', {})
            AUTO_RULES = state.get('auto_rules', [])
            ALERTS = state.get('alerts', [])
            TRADE_HISTORY = state.get('trade_history', [])
            PORTFOLIO = state.get('portfolio', PORTFOLIO)
            AGENT_TASKS = state.get('agent_tasks', [])
            print(f"[STATE] Loaded: {len(WATCHLIST)} watch, {len(AUTO_RULES)} rules, {len(TRADE_HISTORY)} trades")
        except Exception as e:
            print(f"[LOAD ERROR] {e}")
    else:
        print("[STATE] No state file. Starting fresh.")

load_state()

# ═══════════════════════════════════════════════════════════════
# TELEGRAM
# ═══════════════════════════════════════════════════════════════

def send_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}).encode()
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"[TELEGRAM ERR] {e}")

# ═══════════════════════════════════════════════════════════════
# CONTEXT-AWARE ENGINE — Battery, Time, Calendar
# ═══════════════════════════════════════════════════════════════

def get_battery():
    """Get current battery level."""
    try:
        r = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            data = json.loads(r.stdout)
            return data.get('percentage', 100), data.get('status', 'UNKNOWN')
    except: pass
    return 100, 'UNKNOWN'

def get_hour():
    return datetime.now().hour

def should_block_trade():
    """Returns (should_block, reason) tuple."""
    if not ENABLE_CONTEXT_AWARE:
        return False, None
    
    # Battery check
    pct, status = get_battery()
    if pct < MIN_BATTERY_PCT:
        return True, f"Battery critical ({pct}%). Trade blocked."
    
    # Night mode
    hour = get_hour()
    if NIGHT_MODE_START <= hour or hour < NIGHT_MODE_END:
        return True, f"Night mode active ({hour}:00). Trade blocked."
    
    return False, None

# ═══════════════════════════════════════════════════════════════
# SOCIAL SENTIMENT ENGINE — Reddit Scraping
# ═══════════════════════════════════════════════════════════════

def get_reddit_token():
    if not REDDIT_CLIENT_ID or not REDDIT_SECRET:
        return None
    try:
        auth = f"{REDDIT_CLIENT_ID}:{REDDIT_SECRET}"
        import base64
        b64 = base64.b64encode(auth.encode()).decode()
        data = "grant_type=client_credentials".encode()
        req = urllib.request.Request(
            "https://www.reddit.com/api/v1/access_token",
            data=data,
            headers={"Authorization": f"Basic {b64}", "User-Agent": "LilJR/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read()).get('access_token')
    except: return None

def scrape_reddit_sentiment(symbol):
    """Scrape Reddit for sentiment on a stock symbol."""
    token = get_reddit_token()
    if not token:
        return {"sentiment": "unknown", "score": 0, "mentions": 0, "source": "none"}
    
    try:
        req = urllib.request.Request(
            f"https://oauth.reddit.com/search?q={symbol}&sort=new&limit=25",
            headers={"Authorization": f"Bearer {token}", "User-Agent": "LilJR/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        
        posts = data.get('data', {}).get('children', [])
        mentions = len(posts)
        
        # Simple sentiment: count positive vs negative words in titles
        positive = ['bull', 'moon', 'rocket', 'buy', 'gain', 'profit', 'up', 'surge', 'rally', 'breakout']
        negative = ['bear', 'crash', 'dump', 'sell', 'loss', 'down', 'drop', 'fall', 'bearish', 'panic']
        
        pos_score = 0
        neg_score = 0
        for post in posts:
            title = post.get('data', {}).get('title', '').lower()
            for p in positive:
                if p in title: pos_score += 1
            for n in negative:
                if n in title: neg_score += 1
        
        total = pos_score + neg_score
        if total == 0:
            sentiment = "neutral"
            score = 0
        else:
            ratio = pos_score / total
            if ratio > 0.6:
                sentiment = "bullish"
                score = round(ratio * 100)
            elif ratio < 0.4:
                sentiment = "bearish"
                score = round(ratio * 100)
            else:
                sentiment = "neutral"
                score = 50
        
        return {"sentiment": sentiment, "score": score, "mentions": mentions, "source": "reddit", "positive": pos_score, "negative": neg_score}
    except Exception as e:
        return {"sentiment": "error", "score": 0, "mentions": 0, "source": "reddit", "error": str(e)}

# ═══════════════════════════════════════════════════════════════
# SELF-HEALING — Auto-Update From GitHub
# ═══════════════════════════════════════════════════════════════

def self_heal():
    """Pull latest code from GitHub, restart if needed."""
    try:
        repo_dir = os.path.expanduser('~/liljr-autonomous')
        if not os.path.exists(repo_dir):
            return False, "Repo missing"
        
        # Check for updates
        r = subprocess.run(
            ["git", "-C", repo_dir, "fetch", "origin", "main"],
            capture_output=True, text=True, timeout=30
        )
        if r.returncode != 0:
            return False, f"Fetch failed: {r.stderr}"
        
        # Check if behind
        r = subprocess.run(
            ["git", "-C", repo_dir, "rev-list", "HEAD..origin/main", "--count"],
            capture_output=True, text=True, timeout=10
        )
        behind = int(r.stdout.strip() or 0)
        
        if behind > 0:
            print(f"[SELF-HEAL] {behind} commits behind. Pulling...")
            r = subprocess.run(
                ["git", "-C", repo_dir, "pull", "origin", "main"],
                capture_output=True, text=True, timeout=30
            )
            if r.returncode == 0:
                print("[SELF-HEAL] Code updated. Restarting...")
                return True, f"Updated {behind} commits"
            else:
                return False, f"Pull failed: {r.stderr}"
        
        return False, "Already up to date"
    except Exception as e:
        return False, str(e)

# ═══════════════════════════════════════════════════════════════
# VOICE COMMAND — Termux Speech-to-Text
# ═══════════════════════════════════════════════════════════════

def voice_command():
    """Capture voice and return transcribed text."""
    try:
        r = subprocess.run(
            ["termux-speech-to-text", "-l", "en-US"],
            capture_output=True, text=True, timeout=15
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except: pass
    return None

# ═══════════════════════════════════════════════════════════════
# AI AGENT BRIDGE — Accept Tasks From Other Agents
# ═══════════════════════════════════════════════════════════════

def execute_agent_task(task):
    """Execute a task sent by another AI agent."""
    task_type = task.get('type', '')
    payload = task.get('payload', {})
    
    result = {"status": "unknown", "task_type": task_type}
    
    if task_type == 'trade':
        symbol = payload.get('symbol', 'AAPL')
        qty = payload.get('qty', 1)
        action = payload.get('action', 'buy')
        if action == 'buy':
            with app.test_client() as c:
                r = c.post('/api/trading/buy', json={"symbol": symbol, "qty": qty})
                result = r.get_json()
        else:
            with app.test_client() as c:
                r = c.post('/api/trading/sell', json={"symbol": symbol, "qty": qty})
                result = r.get_json()
    
    elif task_type == 'watch':
        symbol = payload.get('symbol', '')
        target = payload.get('target_price', 0)
        with app.test_client() as c:
            r = c.post('/api/watchlist', json={"symbol": symbol, "target_price": target})
            result = r.get_json()
    
    elif task_type == 'alert':
        send_telegram(f"🤖 *Agent Alert*\n{payload.get('message', 'No message')}")
        result = {"status": "sent"}
    
    elif task_type == 'query':
        symbol = payload.get('symbol', 'AAPL')
        with app.test_client() as c:
            r = c.get(f'/api/trading/price/{symbol}')
            result = r.get_json()
    
    return result

# ═══════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.route('/api/health')
def health():
    pct, status = get_battery()
    return jsonify({
        "status": "ok",
        "version": "v6.3-nobody-has-this",
        "mode": "unstoppable",
        "battery": {"percentage": pct, "status": status},
        "time": {"hour": get_hour(), "night_mode": NIGHT_MODE_START <= get_hour() or get_hour() < NIGHT_MODE_END},
        "state_file": STATE_FILE,
        "watchlist_count": len(WATCHLIST),
        "rules_count": len(AUTO_RULES),
        "trade_count": len(TRADE_HISTORY),
        "telegram": bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID),
        "context_aware": ENABLE_CONTEXT_AWARE,
        "sentiment": ENABLE_SENTIMENT
    })

@app.route('/api/save_state', methods=['POST'])
def api_save_state():
    save_state()
    return jsonify({"status": "saved", "file": STATE_FILE})

@app.route('/api/self_heal', methods=['POST'])
def api_self_heal():
    updated, msg = self_heal()
    return jsonify({"updated": updated, "message": msg})

@app.route('/api/voice', methods=['POST'])
def api_voice():
    text = voice_command()
    if text:
        return jsonify({"transcribed": text, "status": "ok"})
    return jsonify({"transcribed": None, "status": "failed"})

@app.route('/api/sentiment/<symbol>')
def api_sentiment(symbol):
    if not ENABLE_SENTIMENT:
        return jsonify({"enabled": False, "message": "Set ENABLE_SENTIMENT=true and add Reddit API keys"})
    result = scrape_reddit_sentiment(symbol.upper())
    return jsonify(result)

@app.route('/api/agent/task', methods=['POST'])
def api_agent_task():
    task = request.get_json() or {}
    result = execute_agent_task(task)
    AGENT_TASKS.append({
        "time": str(datetime.now()),
        "task": task,
        "result": result
    })
    save_state()
    return jsonify({"executed": result, "queued_tasks": len(AGENT_TASKS)})

@app.route('/api/agent/tasks')
def api_agent_tasks():
    return jsonify({"tasks": AGENT_TASKS[-20:], "total": len(AGENT_TASKS)})

# ═══════════════════════════════════════════════════════════════
# TRADING (with context-aware blocking)
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
    # Context-aware block
    blocked, reason = should_block_trade()
    if blocked:
        send_telegram(f"🚫 *Trade Blocked*\n{reason}")
        return jsonify({"status": "BLOCKED", "reason": reason})
    
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
    blocked, reason = should_block_trade()
    if blocked:
        send_telegram(f"🚫 *Trade Blocked*\n{reason}")
        return jsonify({"status": "BLOCKED", "reason": reason})
    
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
# WATCHLIST + ALERTS + AUTO-RULES + AI (same as v6.2)
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
        # Context check before executing
        blocked, reason = should_block_trade()
        if blocked:
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

# AI chat + analyze (same as before)
@app.route('/api/chat', methods=['POST'])
def chat():
    d = request.get_json() or {}
    message = d.get('message', '')
    if GROQ_API_KEY:
        try:
            payload = json.dumps({"model": "llama3-8b-8192", "messages": [{"role": "user", "content": message}], "max_tokens": 500}).encode()
            req = urllib.request.Request(GROQ_URL, data=payload, headers={'Authorization': f'Bearer {GROQ_API_KEY}', 'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                return jsonify({"reply": data['choices'][0]['message']['content'], "mode": "groq"})
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
            payload = json.dumps({"model": "llama3-8b-8192", "messages": [{"role": "user", "content": prompt}], "max_tokens": 200}).encode()
            req = urllib.request.Request(GROQ_URL, data=payload, headers={'Authorization': f'Bearer {GROQ_API_KEY}', 'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                return jsonify({"symbol": symbol, "price": current, "analysis": data['choices'][0]['message']['content'], "mode": "groq"})
        except Exception as e:
            return jsonify({"symbol": symbol, "price": current, "analysis": f"Error: {str(e)}", "mode": "local"})
    return jsonify({"symbol": symbol, "price": current, "analysis": "Mock: Hold position.", "mode": "local"})

# Telegram webhook (same as v6.2)
@app.route('/api/telegram/webhook', methods=['POST'])
def telegram_webhook():
    data = request.get_json() or {}
    msg = data.get('message', {})
    text = msg.get('text', '').strip().lower()
    chat_id = msg.get('chat', {}).get('id', '')
    if str(chat_id) != str(TELEGRAM_CHAT_ID):
        return jsonify({"status": "unauthorized"})
    
    response = "Unknown command. Try: status, price AAPL, buy AAPL 5, sell TSLA, portfolio, watches, sentiment AAPL, voice"
    
    if text == '/start' or text == 'help':
        response = """🤖 *LilJR Remote Control v6.3*

Commands:
• `status` — Server + battery + night mode
• `price <symbol>` — Stock price
• `buy <symbol> <qty>` — Buy stock
• `sell <symbol> <qty>` — Sell stock
• `portfolio` — Your portfolio
• `watches` — Watchlist
• `rules` — Auto-trading rules
• `sentiment <symbol>` — Reddit sentiment
• `voice` — Voice command
• `self-heal` — Pull latest code"""
    
    elif text == 'status':
        pct, status = get_battery()
        hour = get_hour()
        night = NIGHT_MODE_START <= hour or hour < NIGHT_MODE_END
        response = f"✅ LilJR running\n🔋 Battery: {pct}% ({status})\n🌙 Night mode: {'ON' if night else 'OFF'}\n👁 Watchlist: {len(WATCHLIST)} | ⚙️ Rules: {len(AUTO_RULES)} | 📈 Trades: {len(TRADE_HISTORY)}"
    
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
    
    elif text.startswith('sentiment '):
        sym = text.split(' ')[1].upper() if len(text.split(' ')) > 1 else 'AAPL'
        if ENABLE_SENTIMENT:
            result = scrape_reddit_sentiment(sym)
            response = f"📊 *{sym}* Sentiment: {result.get('sentiment', '?').upper()}\nScore: {result.get('score', 0)}% | Mentions: {result.get('mentions', 0)}"
        else:
            response = "Sentiment disabled. Set ENABLE_SENTIMENT=true and Reddit API keys."
    
    elif text == 'voice':
        response = "🎤 Voice command mode active. Say something on your phone..."
        # This would need phone-side integration
    
    elif text == 'self-heal':
        updated, msg = self_heal()
        response = f"🔧 Self-heal: {msg}\nRestart required: {'YES' if updated else 'NO'}"
    
    elif text == 'alert':
        recent = ALERTS[-3:] if ALERTS else []
        response = "🚨 Recent alerts:\n" + "\n".join([f"{a['symbol']} at ${a['current']}" for a in recent]) if recent else "No recent alerts"
    
    send_telegram(response)
    return jsonify({"status": "ok", "command": text})

# ═══════════════════════════════════════════════════════════════
# BACKGROUND MONITOR
# ═══════════════════════════════════════════════════════════════

def price_monitor():
    auto_save_counter = 0
    heal_counter = 0
    while True:
        try:
            if WATCHLIST:
                with app.test_client() as c:
                    c.get('/api/watchlist/check')
            if AUTO_RULES:
                with app.test_client() as c:
                    c.get('/api/rules/run')
            
            auto_save_counter += 1
            if auto_save_counter >= 5:
                save_state()
                print(f"[AUTO-SAVE] {datetime.now()}")
                auto_save_counter = 0
            
            # Self-heal check every 30 minutes (30 cycles)
            heal_counter += 1
            if heal_counter >= 30:
                updated, msg = self_heal()
                if updated:
                    send_telegram(f"🔧 *Auto-Updated*\n{msg}\nRestarting server...")
                    # Trigger restart by exiting — watchdog will restart
                    os._exit(0)
                heal_counter = 0
                
        except Exception as e:
            print(f"[MONITOR ERROR] {e}")
        time.sleep(60)

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    threading.Thread(target=price_monitor, daemon=True).start()
    print(f"🚀 LilJR v6.3 — NOBODY HAS THIS")
    print(f"   State: {STATE_FILE}")
    print(f"   Watchlist: {len(WATCHLIST)}, Rules: {len(AUTO_RULES)}, Trades: {len(TRADE_HISTORY)}")
    print(f"   Telegram: {'ON' if TELEGRAM_BOT_TOKEN else 'OFF'}")
    print(f"   Context-aware: {'ON' if ENABLE_CONTEXT_AWARE else 'OFF'} (min battery: {MIN_BATTERY_PCT}%)")
    print(f"   Sentiment: {'ON' if ENABLE_SENTIMENT else 'OFF'}")
    print(f"   Self-heal: Every 30 min")
    print(f"   Auto-save: Every 5 min")
    print(f"   Running on http://0.0.0.0:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
