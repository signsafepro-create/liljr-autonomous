#!/usr/bin/env python3
"""
LILJR OS v1.0 — THE STANDALONE BRAIN
No APIs. No dependencies. No strings attached.
Self-contained. Self-extending. Interpreted. Yours alone.
"""
import os, sys, json, time, random, re, subprocess, threading, urllib.request, urllib.parse
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from html.parser import HTMLParser

# ═══════════════════════════════════════════════════════════════
# PATHS — All in ~/liljr-autonomous/
# ═══════════════════════════════════════════════════════════════
BASE_DIR = os.path.expanduser('~/liljr-autonomous')
STATE_FILE = os.path.expanduser('~/liljr_state.json')
MEMORY_FILE = os.path.expanduser('~/liljr_memory.json')
PLUGINS_DIR = os.path.join(BASE_DIR, 'plugins')
WEB_DIR = os.path.join(BASE_DIR, 'web')
LOG_FILE = os.path.expanduser('~/liljr.log')

os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(PLUGINS_DIR, exist_ok=True)
os.makedirs(WEB_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# STATE — Everything lives here
# ═══════════════════════════════════════════════════════════════

STATE = {
    'version': 'liljr-os-1.0',
    'created': str(datetime.now()),
    'cash': 10000.0,
    'positions': {},
    'trades': [],
    'watchlist': {},
    'rules': [],
    'alerts': [],
    'plugins': {},
    'knowledge': {},
    'preferences': {},
    'commands_run': 0,
    'mode': 'standalone'
}

MEMORY = {
    'interactions': [],
    'patterns': {},
    'mistakes': [],
    'wins': [],
    'learning': []
}

PRICES = {
    'AAPL': 175, 'TSLA': 240, 'NVDA': 890, 'GOOGL': 175,
    'AMZN': 185, 'MSFT': 420, 'BTC': 65000, 'ETH': 3500,
    'SPY': 520, 'QQQ': 440
}

def load_state():
    global STATE, MEMORY
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                loaded = json.load(f)
                STATE.update(loaded)
        except Exception as e:
            log(f"[STATE LOAD ERROR] {e}")
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                MEMORY.update(json.load(f))
        except: pass

def save_state():
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(STATE, f, indent=2)
        with open(MEMORY_FILE, 'w') as f:
            json.dump(MEMORY, f, indent=2)
    except Exception as e:
        log(f"[STATE SAVE ERROR] {e}")

def log(msg):
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

# ═══════════════════════════════════════════════════════════════
# AUTO-SAVE THREAD
# ═══════════════════════════════════════════════════════════════

def auto_save():
    while True:
        time.sleep(300)
        save_state()
        log("Auto-saved state")

# ═══════════════════════════════════════════════════════════════
# CORE ENGINE — No external APIs
# ═══════════════════════════════════════════════════════════════

class LilJREngine:
    def __init__(self):
        load_state()
    
    # ─── TRADING ───
    def buy(self, symbol, qty=1):
        symbol = symbol.upper()
        price = PRICES.get(symbol, random.randint(50, 500))
        total = qty * price
        
        if STATE['cash'] < total:
            return {"status": "REJECTED", "reason": f"Need ${total}, have ${STATE['cash']}"}
        
        STATE['cash'] -= total
        if symbol not in STATE['positions']:
            STATE['positions'][symbol] = {'qty': 0, 'avg_price': 0}
        
        pos = STATE['positions'][symbol]
        old_qty = pos['qty']
        new_qty = old_qty + qty
        pos['avg_price'] = (old_qty * pos['avg_price'] + qty * price) / new_qty if new_qty > 0 else price
        pos['qty'] = new_qty
        
        trade = {
            'time': str(datetime.now()), 'action': 'buy',
            'symbol': symbol, 'qty': qty, 'price': price, 'total': total
        }
        STATE['trades'].append(trade)
        STATE['commands_run'] += 1
        save_state()
        
        self._log_interaction(f"buy {symbol} {qty}", 'success')
        return {"status": "FILLED", "symbol": symbol, "qty": qty, "price": price, "total": total, "cash_left": STATE['cash']}
    
    def sell(self, symbol, qty=1):
        symbol = symbol.upper()
        if symbol not in STATE['positions'] or STATE['positions'][symbol]['qty'] < qty:
            return {"status": "REJECTED", "reason": f"Don't have {qty} shares of {symbol}"}
        
        price = PRICES.get(symbol, random.randint(50, 500))
        total = qty * price
        
        STATE['positions'][symbol]['qty'] -= qty
        if STATE['positions'][symbol]['qty'] <= 0:
            del STATE['positions'][symbol]
        
        STATE['cash'] += total
        trade = {
            'time': str(datetime.now()), 'action': 'sell',
            'symbol': symbol, 'qty': qty, 'price': price, 'total': total
        }
        STATE['trades'].append(trade)
        STATE['commands_run'] += 1
        save_state()
        
        self._log_interaction(f"sell {symbol} {qty}", 'success')
        return {"status": "FILLED", "symbol": symbol, "qty": qty, "price": price, "total": total, "cash": STATE['cash']}
    
    def price(self, symbol):
        return {"symbol": symbol.upper(), "price": PRICES.get(symbol.upper(), random.randint(50, 500)), "source": "internal"}
    
    def portfolio(self):
        total_value = STATE['cash']
        for sym, pos in STATE['positions'].items():
            current = PRICES.get(sym, pos['avg_price'])
            total_value += pos['qty'] * current
        
        return {
            "cash": STATE['cash'],
            "positions": STATE['positions'],
            "total_value": total_value,
            "trades_count": len(STATE['trades'])
        }
    
    # ─── WATCHLIST ───
    def watch(self, symbol, target):
        STATE['watchlist'][symbol.upper()] = {'target': float(target), 'set_at': str(datetime.now())}
        save_state()
        return {"status": "watching", "symbol": symbol.upper(), "target": target}
    
    def unwatch(self, symbol):
        sym = symbol.upper()
        if sym in STATE['watchlist']:
            del STATE['watchlist'][sym]
            save_state()
            return {"status": "removed", "symbol": sym}
        return {"status": "not_found", "symbol": sym}
    
    def check_alerts(self):
        alerts = []
        for sym, data in STATE['watchlist'].items():
            current = PRICES.get(sym, 0)
            if current <= data['target']:
                alerts.append({"symbol": sym, "current": current, "target": data['target'], "trigger": "below_target"})
        return alerts
    
    # ─── RULES ENGINE ───
    def add_rule(self, symbol, condition, target_price, action, qty=1):
        rule = {
            'id': len(STATE['rules']) + 1,
            'symbol': symbol.upper(),
            'condition': condition,
            'target_price': float(target_price),
            'action': action,
            'qty': int(qty),
            'created': str(datetime.now()),
            'triggered': False
        }
        STATE['rules'].append(rule)
        save_state()
        return {"status": "rule_added", "rule": rule}
    
    def run_rules(self):
        executed = []
        for rule in STATE['rules']:
            if rule['triggered']:
                continue
            current = PRICES.get(rule['symbol'], 0)
            
            if rule['condition'] == 'below' and current <= rule['target_price']:
                if rule['action'] == 'buy':
                    self.buy(rule['symbol'], rule['qty'])
                executed.append(rule)
                rule['triggered'] = True
            elif rule['condition'] == 'above' and current >= rule['target_price']:
                if rule['action'] == 'sell':
                    self.sell(rule['symbol'], rule['qty'])
                executed.append(rule)
                rule['triggered'] = True
        
        save_state()
        return {"executed": len(executed), "rules": executed}
    
    # ─── MEMORY ───
    def _log_interaction(self, text, result_type):
        MEMORY['interactions'].append({
            'time': str(datetime.now()),
            'text': text,
            'result': result_type,
            'hour': datetime.now().hour
        })
        MEMORY['interactions'] = MEMORY['interactions'][-1000:]
    
    def query_memory(self, question):
        q = question.lower()
        
        if 'last trade' in q:
            if STATE['trades']:
                t = STATE['trades'][-1]
                return f"Last: {t['action'].upper()} {t['qty']} {t['symbol']} @ ${t['price']} = ${t['total']}"
            return "No trades yet."
        
        if 'portfolio' in q or 'cash' in q:
            p = self.portfolio()
            return f"Cash: ${p['cash']:.2f}, Positions: {len(p['positions'])}, Value: ${p['total_value']:.2f}"
        
        if 'trades' in q or 'how many' in q:
            return f"Total trades: {len(STATE['trades'])}. Commands run: {STATE['commands_run']}"
        
        if 'pattern' in q or 'best' in q:
            hours = {}
            for i in MEMORY['interactions']:
                h = i['hour']
                if h not in hours:
                    hours[h] = {'total': 0, 'success': 0}
                hours[h]['total'] += 1
                if i['result'] == 'success':
                    hours[h]['success'] += 1
            
            if hours:
                best = max(hours.items(), key=lambda x: x[1]['success'])
                return f"Most active hour: {best[0]}:00 ({best[1]['success']}/{best[1]['total']} success)"
            return "Not enough data."
        
        return f"I know {len(STATE['knowledge'])} facts, {len(STATE['trades'])} trades. Ask me anything."
    
    # ─── KNOWLEDGE BASE ───
    def learn(self, topic, fact):
        if topic not in STATE['knowledge']:
            STATE['knowledge'][topic] = []
        STATE['knowledge'][topic].append({'fact': fact, 'time': str(datetime.now())})
        save_state()
        return {"status": "learned", "topic": topic}
    
    # ─── WEB SCRAPING (no API keys) ───
    def web_search(self, query, count=5):
        """Search DuckDuckGo — no API needed."""
        try:
            encoded = urllib.parse.quote(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
            
            results = []
            links = re.findall(r'<a rel="nofollow" class="result__a" href="(https?://[^"]+)">([^<]+)</a>', html)
            snippets = re.findall(r'<a class="result__snippet"[^>]*>([^<]+)</a>', html)
            
            for i, (href, title) in enumerate(links[:count]):
                results.append({
                    'title': re.sub(r'<[^>]+>', '', title),
                    'url': href,
                    'snippet': re.sub(r'<[^>]+>', '', snippets[i]) if i < len(snippets) else ''
                })
            return results
        except Exception as e:
            return [{"error": str(e)}]
    
    def fetch_page(self, url):
        """Fetch any public page."""
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
            
            text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            return re.sub(r'\s+', ' ', text).strip()[:3000]
        except Exception as e:
            return f"Error: {e}"
    
    # ─── PLUGIN SYSTEM — SELF-EXTENDING ───
    def create_plugin(self, name, code):
        """Create a new plugin from code string."""
        filepath = os.path.join(PLUGINS_DIR, f"{name}.py")
        with open(filepath, 'w') as f:
            f.write(code)
        STATE['plugins'][name] = {'created': str(datetime.now()), 'file': filepath}
        save_state()
        return {"status": "plugin_created", "name": name, "path": filepath}
    
    def run_plugin(self, name, *args):
        """Execute a plugin."""
        filepath = os.path.join(PLUGINS_DIR, f"{name}.py")
        if not os.path.exists(filepath):
            return {"status": "not_found", "name": name}
        
        try:
            spec = __import__('importlib.util').util.spec_from_file_location(name, filepath)
            mod = __import__('importlib.util').util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            
            if hasattr(mod, 'run'):
                return mod.run(*args)
            return {"status": "no_run_function", "name": name}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    # ─── AI (LOCAL — NO API) ───
    def ai_chat(self, message):
        """Local AI — pattern matching, no external API."""
        msg = message.lower()
        
        if 'buy' in msg and any(s in msg for s in ['aapl', 'tsla', 'nvda', 'stock']):
            sym = re.search(r'\b([a-zA-Z]{1,5})\b', msg)
            if sym:
                return f"To buy {sym.group(1).upper()}, use: buy {sym.group(1).upper()} 1"
        
        if 'price' in msg or 'cost' in msg:
            sym = re.search(r'\b([a-zA-Z]{1,5})\b', msg)
            if sym:
                p = self.price(sym.group(1).upper())
                return f"{p['symbol']} is at ${p['price']} (internal)"
        
        if 'portfolio' in msg or 'money' in msg or 'cash' in msg:
            p = self.portfolio()
            return f"You have ${p['cash']:.2f} cash, {len(p['positions'])} positions, total value ${p['total_value']:.2f}"
        
        if 'help' in msg or 'commands' in msg:
            return "Commands: buy, sell, price, portfolio, watch, rule, run, search, fetch, learn, query, plugin, ai, status, save"
        
        if 'search' in msg or 'find' in msg:
            q = msg.replace('search', '').replace('find', '').strip()
            results = self.web_search(q, 3)
            if results and 'error' not in results[0]:
                return "Found:\n" + "\n".join(f"• {r['title'][:60]}" for r in results[:3])
            return "Search failed. Try again."
        
        if 'time' in msg or 'hour' in msg:
            return f"It's {datetime.now().strftime('%H:%M on %A, %B %d')}."
        
        # Generic response
        responses = [
            f"I'm listening. You've run {STATE['commands_run']} commands.",
            f"LilJR OS v1.0. Standalone mode. {len(STATE['trades'])} trades on record.",
            "Tell me what to do. Buy, sell, search, learn, create — anything.",
            f"System ready. Cash: ${STATE['cash']:.2f}. What next?"
        ]
        return random.choice(responses)
    
    # ─── STATUS ───
    def status(self):
        return {
            "status": "ok",
            "version": STATE['version'],
            "mode": STATE['mode'],
            "cash": STATE['cash'],
            "positions": len(STATE['positions']),
            "trades": len(STATE['trades']),
            "watchlist": len(STATE['watchlist']),
            "rules": len(STATE['rules']),
            "plugins": len(STATE['plugins']),
            "knowledge": len(STATE['knowledge']),
            "commands": STATE['commands_run'],
            "standalone": True,
            "time": str(datetime.now())
        }

# ═══════════════════════════════════════════════════════════════
# HTTP SERVER — Built-in, no Flask needed
# ═══════════════════════════════════════════════════════════════

engine = LilJREngine()

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        log(f"[HTTP] {args[0]}")
    
    def _json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_GET(self):
        path = self.path
        
        if path == '/api/health':
            self._json_response(engine.status())
        
        elif path.startswith('/api/trading/price/'):
            sym = path.split('/')[-1]
            self._json_response(engine.price(sym))
        
        elif path == '/api/trading/portfolio':
            self._json_response(engine.portfolio())
        
        elif path == '/api/trading/history':
            self._json_response({"trades": STATE['trades'][-50:]})
        
        elif path == '/api/watchlist':
            self._json_response(STATE['watchlist'])
        
        elif path == '/api/watchlist/check':
            self._json_response({"alerts": engine.check_alerts()})
        
        elif path == '/api/rules':
            self._json_response({"rules": STATE['rules']})
        
        elif path.startswith('/api/ai/'):
            msg = path.split('/api/ai/')[-1].replace('%20', ' ')
            self._json_response({"response": engine.ai_chat(msg)})
        
        elif path == '/api/memory':
            q = urllib.parse.parse_qs(urllib.parse.urlparse(path).query).get('q', ['what do I know'])[0]
            self._json_response({"answer": engine.query_memory(q)})
        
        elif path == '/api/knowledge':
            self._json_response(STATE['knowledge'])
        
        elif path == '/api/plugins':
            self._json_response({"plugins": list(STATE['plugins'].keys())})
        
        elif path == '/':
            self._json_response({"message": "LilJR OS v1.0 — Standalone. No APIs. No strings.", "endpoints": "/api/health, /api/trading/*, /api/ai/*, /api/memory, /api/search"})
        
        else:
            self._json_response({"status": "not_found"}, 404)
    
    def do_POST(self):
        path = self.path
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode() if length else '{}'
        
        try:
            data = json.loads(body)
        except:
            data = {}
        
        if path == '/api/trading/buy':
            self._json_response(engine.buy(data.get('symbol', 'AAPL'), data.get('qty', 1)))
        
        elif path == '/api/trading/sell':
            self._json_response(engine.sell(data.get('symbol', 'AAPL'), data.get('qty', 1)))
        
        elif path == '/api/watchlist':
            self._json_response(engine.watch(data.get('symbol'), data.get('target_price', 0)))
        
        elif path == '/api/rules':
            self._json_response(engine.add_rule(
                data.get('symbol'), data.get('condition'),
                data.get('target_price'), data.get('action'), data.get('qty', 1)
            ))
        
        elif path == '/api/rules/run':
            self._json_response(engine.run_rules())
        
        elif path == '/api/ai/chat':
            self._json_response({"response": engine.ai_chat(data.get('message', 'hello'))})
        
        elif path == '/api/search':
            self._json_response({"results": engine.web_search(data.get('query', 'news'), data.get('count', 5))})
        
        elif path == '/api/fetch':
            self._json_response({"content": engine.fetch_page(data.get('url', ''))})
        
        elif path == '/api/learn':
            self._json_response(engine.learn(data.get('topic'), data.get('fact')))
        
        elif path == '/api/query':
            self._json_response({"answer": engine.query_memory(data.get('question', ''))})
        
        elif path == '/api/plugin/create':
            self._json_response(engine.create_plugin(data.get('name'), data.get('code')))
        
        elif path == '/api/plugin/run':
            self._json_response(engine.run_plugin(data.get('name'), *data.get('args', [])))
        
        else:
            self._json_response({"status": "not_found"}, 404)
    
    def do_DELETE(self):
        path = self.path
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode() if length else '{}'
        
        try:
            data = json.loads(body)
        except:
            data = {}
        
        if path == '/api/watchlist':
            self._json_response(engine.unwatch(data.get('symbol')))
        
        elif path.startswith('/api/rules/'):
            rid = data.get('id')
            if rid and 1 <= rid <= len(STATE['rules']):
                STATE['rules'][rid-1]['triggered'] = True
                save_state()
                self._json_response({"status": "deleted", "id": rid})
            else:
                self._json_response({"status": "not_found"}, 404)
        
        else:
            self._json_response({"status": "not_found"}, 404)

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    
    # Start auto-save thread
    save_thread = threading.Thread(target=auto_save, daemon=True)
    save_thread.start()
    
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    log(f"LilJR OS v1.0 running on http://0.0.0.0:{PORT}")
    log(f"Standalone mode. No API keys needed.")
    log(f"Endpoints: /api/health, /api/trading/*, /api/ai/*, /api/search")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("Shutting down...")
        save_state()
        server.shutdown()
