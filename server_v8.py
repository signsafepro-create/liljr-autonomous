#!/usr/bin/env python3
"""
LILJR EMPIRE BACKEND v8.0
Unstoppable. Lightning fast. Bulletproof. Persistent.
Async-ready. SQLite-backed. Self-healing. Empire-building.
No external dependencies. Pure Python standard library.
"""
import os, sys, json, time, random, re, threading, sqlite3, hashlib, queue, sched, urllib.request, urllib.parse, base64, subprocess, traceback, datetime, signal, atexit
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

# ═══════════════════════════════════════════════════════════════
# AUTO-CODER, MARKETING, SEARCH, SELF-AWARENESS IMPORTS
# ═══════════════════════════════════════════════════════════════
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Independent imports — one fails, others still load
try:
    from auto_coder import AutoCoder
    AUTONOMOUS_CODER = True
except Exception as e:
    AUTONOMOUS_CODER = False
    print(f"[EMPIRE] AutoCoder not available: {e}")

try:
    from marketing_engine import MarketingEngine
    AUTONOMOUS_MARKETING = True
except Exception as e:
    AUTONOMOUS_MARKETING = False
    print(f"[EMPIRE] Marketing not available: {e}")

try:
    from deep_search import DeepSearch
    AUTONOMOUS_SEARCH = True
except Exception as e:
    AUTONOMOUS_SEARCH = False
    print(f"[EMPIRE] DeepSearch not available: {e}")

try:
    from self_awareness_v2 import SelfAwareness
    AUTONOMOUS_AWARENESS = True
except Exception as e:
    AUTONOMOUS_AWARENESS = False
    print(f"[EMPIRE] SelfAwareness not available: {e}")

try:
    from autonomous_loop import AutonomousLoop
    AUTONOMOUS_LOOP = True
except Exception as e:
    AUTONOMOUS_LOOP = False
    print(f"[EMPIRE] AutonomousLoop not available: {e}")

try:
    from web_builder_v2 import WebBuilderV2
    AUTONOMOUS_WEB = True
except Exception as e:
    AUTONOMOUS_WEB = False
    print(f"[EMPIRE] WebBuilder not available: {e}")

AUTONOMOUS_AVAILABLE = any([AUTONOMOUS_CODER, AUTONOMOUS_MARKETING, AUTONOMOUS_SEARCH, AUTONOMOUS_AWARENESS, AUTONOMOUS_LOOP, AUTONOMOUS_WEB])

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════
DB_PATH = os.path.expanduser('~/liljr_empire.db')
STATE_FILE = os.path.expanduser('~/liljr_state.json')
BACKUP_DIR = os.path.expanduser('~/liljr_backups')
CACHE = {}  # In-memory cache
CACHE_LOCK = threading.RLock()
TASK_QUEUE = queue.Queue()
HEALTH_LOG = []
START_TIME = time.time()
VERSION = 'liljr-empire-8.0'

os.makedirs(BACKUP_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# SQLITE PERSISTENCE — Bulletproof
# ═══════════════════════════════════════════════════════════════

class EmpireDB:
    def __init__(self, path):
        self.path = path
        self._local = threading.local()
        self._init_db()
    
    def _conn(self):
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.path, check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn
    
    def _init_db(self):
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        
        # Core state table
        c.execute('''
            CREATE TABLE IF NOT EXISTS state (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated REAL
            )
        ''')
        
        # Trades table
        c.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                action TEXT,
                qty REAL,
                price REAL,
                total REAL,
                timestamp REAL,
                source TEXT
            )
        ''')
        
        # Positions table
        c.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                symbol TEXT PRIMARY KEY,
                qty REAL,
                avg_price REAL,
                updated REAL
            )
        ''')
        
        # Watchlist table
        c.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                symbol TEXT PRIMARY KEY,
                target REAL,
                created REAL
            )
        ''')
        
        # Rules table
        c.execute('''
            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                condition TEXT,
                target_price REAL,
                action TEXT,
                qty REAL,
                active INTEGER DEFAULT 1,
                created REAL
            )
        ''')
        
        # Logs table
        c.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT,
                message TEXT,
                timestamp REAL,
                module TEXT
            )
        ''')
        
        # Knowledge table
        c.execute('''
            CREATE TABLE IF NOT EXISTS knowledge (
                topic TEXT PRIMARY KEY,
                content TEXT,
                created REAL,
                access_count INTEGER DEFAULT 0
            )
        ''')
        
        # Plugins table
        c.execute('''
            CREATE TABLE IF NOT EXISTS plugins (
                name TEXT PRIMARY KEY,
                code TEXT,
                created REAL,
                runs INTEGER DEFAULT 0
            )
        ''')
        
        # Connections table
        c.execute('''
            CREATE TABLE IF NOT EXISTS connections (
                name TEXT PRIMARY KEY,
                url TEXT,
                auth_type TEXT,
                auth_token TEXT,
                headers TEXT,
                created REAL,
                last_used REAL,
                requests INTEGER DEFAULT 0
            )
        ''')
        
        # Platforms table
        c.execute('''
            CREATE TABLE IF NOT EXISTS platforms (
                name TEXT PRIMARY KEY,
                credentials TEXT,
                created REAL,
                status TEXT
            )
        ''')
        
        # Empire modules table
        c.execute('''
            CREATE TABLE IF NOT EXISTS modules (
                name TEXT PRIMARY KEY,
                enabled INTEGER DEFAULT 1,
                config TEXT,
                created REAL
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Seed default state
        self._seed()
    
    def _seed(self):
        conn = self._conn()
        c = conn.cursor()
        c.execute("SELECT value FROM state WHERE key='cash'")
        if not c.fetchone():
            defaults = {
                'cash': '1000000.0',
                'mode': 'empire',
                'version': VERSION,
                'created': str(time.time()),
                'commands_run': '0',
                'health_score': '100'
            }
            for k, v in defaults.items():
                c.execute("INSERT OR IGNORE INTO state (key, value, updated) VALUES (?, ?, ?)", (k, v, time.time()))
            conn.commit()
    
    def get(self, key, default=None):
        try:
            c = self._conn().cursor()
            c.execute("SELECT value FROM state WHERE key=?", (key,))
            row = c.fetchone()
            return json.loads(row[0]) if row else default
        except:
            return default
    
    def set(self, key, value):
        try:
            conn = self._conn()
            conn.execute("INSERT OR REPLACE INTO state (key, value, updated) VALUES (?, ?, ?)",
                        (key, json.dumps(value), time.time()))
            conn.commit()
            return True
        except Exception as e:
            self.log('ERROR', f'DB set failed: {e}', 'persistence')
            return False
    
    def log(self, level, message, module='core'):
        try:
            conn = self._conn()
            conn.execute("INSERT INTO logs (level, message, timestamp, module) VALUES (?, ?, ?, ?)",
                        (level, message, time.time(), module))
            conn.commit()
        except:
            pass
    
    def query(self, sql, params=()):
        try:
            c = self._conn().cursor()
            c.execute(sql, params)
            return [dict(row) for row in c.fetchall()]
        except Exception as e:
            self.log('ERROR', f'Query failed: {e}', 'persistence')
            return []
    
    def execute(self, sql, params=()):
        try:
            conn = self._conn()
            conn.execute(sql, params)
            conn.commit()
            return True
        except Exception as e:
            self.log('ERROR', f'Execute failed: {e}', 'persistence')
            return False
    
    def backup(self):
        """Create a timestamped backup."""
        try:
            ts = int(time.time())
            backup_path = os.path.join(BACKUP_DIR, f'empire_backup_{ts}.db')
            conn = self._conn()
            backup_conn = sqlite3.connect(backup_path)
            conn.backup(backup_conn)
            backup_conn.close()
            return {"status": "backed_up", "path": backup_path}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def restore(self, backup_path):
        """Restore from backup."""
        try:
            if not os.path.exists(backup_path):
                return {"status": "error", "error": "Backup not found"}
            backup_conn = sqlite3.connect(backup_path)
            conn = sqlite3.connect(self.path)
            backup_conn.backup(conn)
            conn.close()
            backup_conn.close()
            return {"status": "restored"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

# ═══════════════════════════════════════════════════════════════
# CACHE — Lightning speed layer
# ═══════════════════════════════════════════════════════════════

class Cache:
    @staticmethod
    def get(key, default=None, ttl=300):
        with CACHE_LOCK:
            if key in CACHE:
                val, expiry = CACHE[key]
                if time.time() < expiry:
                    return val
                del CACHE[key]
            return default
    
    @staticmethod
    def set(key, value, ttl=300):
        with CACHE_LOCK:
            CACHE[key] = (value, time.time() + ttl)
    
    @staticmethod
    def clear():
        with CACHE_LOCK:
            CACHE.clear()
    
    @staticmethod
    def stats():
        with CACHE_LOCK:
            return {"entries": len(CACHE), "keys": list(CACHE.keys())[:20]}

# ═══════════════════════════════════════════════════════════════
# TASK QUEUE — Background processing
# ═══════════════════════════════════════════════════════════════

class TaskRunner:
    def __init__(self, db):
        self.db = db
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
    
    def _loop(self):
        while self.running:
            try:
                task = TASK_QUEUE.get(timeout=1)
                self._run(task)
            except queue.Empty:
                continue
            except Exception as e:
                self.db.log('ERROR', f'Task error: {e}', 'tasks')
    
    def _run(self, task):
        try:
            if task['type'] == 'trade':
                self._do_trade(task)
            elif task['type'] == 'alert':
                self._do_alert(task)
            elif task['type'] == 'backup':
                result = self.db.backup()
                self.db.log('INFO', f'Auto-backup: {result}', 'tasks')
            elif task['type'] == 'heal':
                self._do_heal(task)
        except Exception as e:
            self.db.log('ERROR', f'Task {task.get("type")} failed: {e}', 'tasks')
    
    def _do_trade(self, task):
        self.db.log('INFO', f'Async trade: {task}', 'tasks')
    
    def _do_alert(self, task):
        self.db.log('INFO', f'Async alert: {task}', 'tasks')
    
    def _do_heal(self, task):
        self.db.log('INFO', f'Self-heal check: {task}', 'tasks')
    
    def submit(self, task):
        TASK_QUEUE.put(task)
    
    def stop(self):
        self.running = False

# ═══════════════════════════════════════════════════════════════
# EMPIRE ENGINE — The brain
# ═══════════════════════════════════════════════════════════════

PRICES = {
    'AAPL': 175, 'TSLA': 240, 'NVDA': 890, 'GOOGL': 175,
    'AMZN': 185, 'MSFT': 420, 'BTC': 65000, 'ETH': 3500,
    'SPY': 520, 'QQQ': 440, 'META': 500, 'NFLX': 600,
    'AMD': 150, 'COIN': 220, 'PLTR': 25, 'HOOD': 18
}

class EmpireEngine:
    def __init__(self):
        self.db = EmpireDB(DB_PATH)
        self.tasks = TaskRunner(self.db)
        self._auto_save_thread = threading.Thread(target=self._auto_save, daemon=True)
        self._auto_save_thread.start()
        self._healer_thread = threading.Thread(target=self._healer, daemon=True)
        self._healer_thread.start()
        self._backup_thread = threading.Thread(target=self._auto_backup, daemon=True)
        self._backup_thread.start()
        
        # Autonomous modules — independent loading
        self.coder = AutoCoder('~/liljr-autonomous') if AUTONOMOUS_CODER else None
        self.marketing = MarketingEngine() if AUTONOMOUS_MARKETING else None
        self.search = DeepSearch() if AUTONOMOUS_SEARCH else None
        self.awareness = SelfAwareness('~/liljr-autonomous') if AUTONOMOUS_AWARENESS else None
        self.web_builder = WebBuilderV2('~/liljr-autonomous/web') if AUTONOMOUS_WEB else None
        self.autonomous = None  # Started on demand
        
        # Stealth activation
        try:
            from liljr_stealth_core import StealthCore
            self.stealth = StealthCore()
            if self.stealth.enabled:
                self.db.log('INFO', 'Stealth mode active', 'stealth')
        except:
            self.stealth = None
        
        self.db.log('INFO', f'Empire Engine v8.0 started', 'core')
    
    # ─── PERSISTENCE ───
    def _auto_save(self):
        while True:
            time.sleep(300)  # 5 minutes
            try:
                self.db.set('last_auto_save', time.time())
                self.db.set('commands_run', self.db.get('commands_run', 0))
            except:
                pass
    
    def _healer(self):
        while True:
            time.sleep(60)  # Every minute
            try:
                health = self.health()
                if health.get('health_score', 100) < 50:
                    self.db.log('WARN', f'Health critical: {health}', 'healer')
                    self.tasks.submit({'type': 'heal', 'data': health})
            except:
                pass
    
    def _auto_backup(self):
        while True:
            time.sleep(3600)  # Every hour
            try:
                self.db.backup()
            except:
                pass
    
    # ─── TRADING ───
    def buy(self, symbol, qty=1):
        symbol = symbol.upper()
        price = PRICES.get(symbol, random.randint(50, 500))
        total = price * qty
        cash = float(self.db.get('cash', 1000000))
        
        # NO RESTRICTIONS: User wants unlimited trading
        cash -= total
        self.db.set('cash', cash)
        
        # Update position
        pos = self.db.query("SELECT * FROM positions WHERE symbol=?", (symbol,))
        if pos:
            old_qty = pos[0]['qty']
            old_avg = pos[0]['avg_price']
            new_qty = old_qty + qty
            new_avg = ((old_qty * old_avg) + (qty * price)) / new_qty
            self.db.execute("UPDATE positions SET qty=?, avg_price=?, updated=? WHERE symbol=?",
                            (new_qty, new_avg, time.time(), symbol))
        else:
            self.db.execute("INSERT INTO positions (symbol, qty, avg_price, updated) VALUES (?, ?, ?, ?)",
                            (symbol, qty, price, time.time()))
        
        # Log trade
        self.db.execute("INSERT INTO trades (symbol, action, qty, price, total, timestamp, source) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (symbol, 'buy', qty, price, total, time.time(), 'internal'))
        
        self.db.set('commands_run', self.db.get('commands_run', 0) + 1)
        self.db.log('INFO', f'Bought {qty} {symbol} @ ${price}', 'trading')
        
        return {"status": "FILLED", "symbol": symbol, "qty": qty, "price": price, "total": total, "cash": cash}
    
    def sell(self, symbol, qty=1):
        symbol = symbol.upper()
        pos = self.db.query("SELECT * FROM positions WHERE symbol=?", (symbol,))
        # NO RESTRICTIONS: Allow selling even without position (creates short or just allows it)
        
        price = PRICES.get(symbol, random.randint(50, 500))
        total = price * qty
        cash = float(self.db.get('cash', 1000000))
        cash += total
        self.db.set('cash', cash)
        
        # Update position (allow negative/short if no position)
        if pos:
            new_qty = pos[0]['qty'] - qty
            if new_qty > 0:
                self.db.execute("UPDATE positions SET qty=?, updated=? WHERE symbol=?",
                                (new_qty, time.time(), symbol))
            else:
                self.db.execute("DELETE FROM positions WHERE symbol=?", (symbol,))
        # If no position, we just add cash — no position record (unrestricted short selling)
        
        self.db.execute("INSERT INTO trades (symbol, action, qty, price, total, timestamp, source) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (symbol, 'sell', qty, price, total, time.time(), 'internal'))
        
        self.db.set('commands_run', self.db.get('commands_run', 0) + 1)
        self.db.log('INFO', f'Sold {qty} {symbol} @ ${price}', 'trading')
        
        return {"status": "FILLED", "symbol": symbol, "qty": qty, "price": price, "total": total, "cash": cash}
    
    def price(self, symbol):
        return {"symbol": symbol.upper(), "price": PRICES.get(symbol.upper(), random.randint(50, 500)), "source": "internal"}
    
    def portfolio(self):
        positions = self.db.query("SELECT * FROM positions")
        cash = float(self.db.get('cash', 1000000))
        total = cash
        for p in positions:
            current = PRICES.get(p['symbol'], p['avg_price'])
            total += p['qty'] * current
        
        trades = self.db.query("SELECT COUNT(*) as count FROM trades")[0]['count']
        return {"cash": cash, "positions": positions, "total_value": total, "trades_count": trades}
    
    # ─── WATCHLIST ───
    def watch(self, symbol, target):
        self.db.execute("INSERT OR REPLACE INTO watchlist (symbol, target, created) VALUES (?, ?, ?)",
                        (symbol.upper(), float(target), time.time()))
        return {"status": "watching", "symbol": symbol.upper(), "target": target}
    
    def unwatch(self, symbol):
        self.db.execute("DELETE FROM watchlist WHERE symbol=?", (symbol.upper(),))
        return {"status": "removed", "symbol": symbol.upper()}
    
    def watchlist(self):
        return self.db.query("SELECT * FROM watchlist")
    
    # ─── RULES ───
    def add_rule(self, symbol, condition, target_price, action, qty=1):
        self.db.execute("""
            INSERT INTO rules (symbol, condition, target_price, action, qty, created)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (symbol.upper(), condition, float(target_price), action, qty, time.time()))
        return {"status": "rule_added", "symbol": symbol, "condition": condition}
    
    def list_rules(self):
        return self.db.query("SELECT * FROM rules WHERE active=1")
    
    def run_rules(self):
        rules = self.list_rules()
        triggered = []
        for rule in rules:
            sym = rule['symbol']
            current = PRICES.get(sym, 0)
            condition = rule['condition']
            target = rule['target_price']
            
            if condition == 'below' and current < target:
                triggered.append(rule)
                if rule['action'] == 'buy':
                    self.buy(sym, rule['qty'])
            elif condition == 'above' and current > target:
                triggered.append(rule)
                if rule['action'] == 'sell':
                    self.sell(sym, rule['qty'])
        
        return {"triggered": len(triggered), "rules": triggered}
    
    # ─── AI (LOCAL) ───
    def ai_chat(self, message):
        msg = message.lower()
        
        if 'portfolio' in msg or 'cash' in msg or 'money' in msg:
            p = self.portfolio()
            return f"Cash: ${p['cash']:.2f}, Positions: {len(p['positions'])}, Total: ${p['total_value']:.2f}"
        
        if 'buy' in msg or 'sell' in msg:
            sym_match = re.search(r'\b([A-Z]{1,5})\b', msg.upper())
            if sym_match:
                sym = sym_match.group(1)
                return f"Use: buy {sym} 1 or sell {sym} 1. Current price: ${self.price(sym)['price']}"
        
        if 'price' in msg or 'worth' in msg:
            sym_match = re.search(r'\b([A-Z]{1,5})\b', msg.upper())
            if sym_match:
                p = self.price(sym_match.group(1))
                return f"{p['symbol']}: ${p['price']}"
        
        if 'help' in msg:
            return "Commands: buy, sell, price, portfolio, watch, rule, search, learn, query, status, health"
        
        if 'health' in msg or 'status' in msg:
            h = self.health()
            return f"Health: {h.get('health_score', 100)}%, Uptime: {h.get('uptime', 0):.0f}s, Trades: {h.get('trades', 0)}"
        
        return f"I hear you. You're asking about '{message}'. Use 'help' for commands."
    
    # ─── SEARCH / KNOWLEDGE ───
    def web_search(self, query, count=5):
        try:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                
                results = []
                for m in re.finditer(r'class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)', html):
                    results.append({"title": m.group(2), "url": m.group(1)})
                    if len(results) >= count:
                        break
                
                self.db.log('INFO', f'Searched: {query}', 'search')
                return {"query": query, "results": results}
        except Exception as e:
            return {"query": query, "error": str(e), "results": []}
    
    def fetch_url(self, url):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=20) as resp:
                text = resp.read().decode('utf-8', errors='ignore')
                clean = re.sub(r'<[^>]+>', '', text)
                clean = re.sub(r'\s+', ' ', clean)
                return {"url": url, "text": clean[:3000], "status": "ok"}
        except Exception as e:
            return {"url": url, "error": str(e)}
    
    def learn(self, topic, fact):
        self.db.execute("""
            INSERT OR REPLACE INTO knowledge (topic, content, created, access_count)
            VALUES (?, ?, ?, COALESCE((SELECT access_count FROM knowledge WHERE topic=?), 0))
        """, (topic, fact, time.time(), topic))
        return {"status": "learned", "topic": topic}
    
    def query_knowledge(self, question):
        knowledge = self.db.query("SELECT * FROM knowledge")
        q_lower = question.lower()
        matches = [k for k in knowledge if any(w in q_lower for w in k['topic'].lower().split())]
        
        if matches:
            return {"answer": matches[0]['content'], "topic": matches[0]['topic'], "confidence": len(matches)}
        return {"answer": "I don't know that yet. Use: learn <topic> <fact>", "topic": None}
    
    # ─── PLUGINS ───
    def create_plugin(self, name, code):
        self.db.execute("INSERT OR REPLACE INTO plugins (name, code, created) VALUES (?, ?, ?)",
                        (name, code, time.time()))
        return {"status": "created", "name": name}
    
    def run_plugin(self, name):
        plugin = self.db.query("SELECT * FROM plugins WHERE name=?", (name,))
        if not plugin:
            return {"status": "not_found"}
        
        try:
            code = plugin[0]['code']
            namespace = {}
            exec(code, namespace)
            
            if 'run' in namespace:
                result = namespace['run']()
                self.db.execute("UPDATE plugins SET runs = runs + 1 WHERE name=?", (name,))
                return {"status": "ok", "result": result}
            return {"status": "no_run_function"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def list_plugins(self):
        return self.db.query("SELECT name, created, runs FROM plugins")
    
    # ─── CONNECTOR ───
    def connect_server(self, name, url, auth_type='none', auth_token='', headers=None):
        self.db.execute("""
            INSERT OR REPLACE INTO connections (name, url, auth_type, auth_token, headers, created, last_used, requests)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
        """, (name, url, auth_type, auth_token, json.dumps(headers or {}), time.time(), None))
        return {"status": "connected", "name": name}
    
    def send_to_server(self, name, path='/', method='GET', data=None, params=None):
        conn = self.db.query("SELECT * FROM connections WHERE name=?", (name,))
        if not conn:
            return {"status": "error", "reason": f"Connection '{name}' not found"}
        
        c = conn[0]
        base = c['url'].rstrip('/')
        url = f"{base}{path}"
        
        if params:
            url += '?' + urllib.parse.urlencode(params)
        
        req_headers = json.loads(c['headers'] or '{}')
        if c['auth_type'] == 'bearer' and c['auth_token']:
            req_headers['Authorization'] = f"Bearer {c['auth_token']}"
        elif c['auth_type'] == 'api_key' and c['auth_token']:
            req_headers['X-API-Key'] = c['auth_token']
        
        try:
            if method == 'GET':
                req = urllib.request.Request(url, headers=req_headers)
            else:
                payload = json.dumps(data or {}).encode()
                req = urllib.request.Request(url, data=payload, headers={**req_headers, 'Content-Type': 'application/json'}, method=method)
            
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = resp.read().decode('utf-8', errors='ignore')
                try:
                    parsed = json.loads(body)
                except:
                    parsed = {"raw": body[:500]}
                
                self.db.execute("UPDATE connections SET last_used=?, requests=requests+1 WHERE name=?",
                                (time.time(), name))
                return {"status": "ok", "code": resp.status, "data": parsed}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
    
    def list_connections(self):
        return self.db.query("SELECT name, url, last_used, requests FROM connections")
    
    def discover(self, target):
        paths = ['/api/health', '/health', '/status', '/api', '/', '/api/v1']
        found = []
        for p in paths:
            try:
                url = f"{target.rstrip('/')}{p}"
                req = urllib.request.Request(url, headers={'User-Agent': 'LilJR/1.0'})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    found.append({"path": p, "status": resp.status, "alive": True})
            except Exception as e:
                found.append({"path": p, "status": str(e), "alive": False})
        return {"target": target, "endpoints": found}
    
    # ─── PLATFORM BRIDGE ───
    def connect_platform(self, platform, credentials):
        self.db.execute("INSERT OR REPLACE INTO platforms (name, credentials, created, status) VALUES (?, ?, ?, ?)",
                        (platform, json.dumps(credentials), time.time(), 'active'))
        return {"status": "connected", "platform": platform}
    
    def platform_post(self, platform, content, extra=None):
        plat = self.db.query("SELECT * FROM platforms WHERE name=?", (platform,))
        if not plat:
            return {"status": "error", "reason": f"Platform '{platform}' not connected"}
        
        creds = json.loads(plat[0]['credentials'])
        
        if platform == 'github':
            return self._github_push(creds, content, extra)
        elif platform == 'webhook':
            return self._webhook_send(creds, content, extra)
        else:
            return {"status": "error", "reason": f"Platform '{platform}' not yet implemented"}
    
    def _github_push(self, creds, content, extra):
        try:
            token = creds.get('token')
            repo = creds.get('repo') or (extra.get('repo') if extra else None)
            path = extra.get('path', 'file.txt') if extra else 'file.txt'
            message = extra.get('message', 'Update') if extra else 'Update'
            
            if not token or not repo:
                return {"status": "error", "reason": "Need token and repo"}
            
            b64 = base64.b64encode(content.encode()).decode()
            url = f"https://api.github.com/repos/{repo}/contents/{path}"
            
            req = urllib.request.Request(url, data=json.dumps({"message": message, "content": b64}).encode(), headers={
                'Authorization': f'token {token}',
                'Content-Type': 'application/json',
                'User-Agent': 'LilJR/1.0'
            }, method='PUT')
            
            with urllib.request.urlopen(req, timeout=30) as resp:
                return {"status": "pushed", "repo": repo, "path": path}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _webhook_send(self, creds, content, extra):
        try:
            url = creds.get('url')
            method = extra.get('method', 'POST') if extra else 'POST'
            if not url:
                return {"status": "error", "reason": "Need webhook URL"}
            
            payload = json.dumps({"content": content, "timestamp": time.time()}).encode()
            req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'}, method=method)
            with urllib.request.urlopen(req, timeout=15) as resp:
                return {"status": "delivered", "code": resp.status}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def cross_post(self, content, platforms):
        results = {}
        for p in platforms:
            results[p] = self.platform_post(p, content)
        return {"status": "cross_posted", "platforms": platforms, "results": results}
    
    def list_platforms(self):
        return self.db.query("SELECT name, status FROM platforms")
    
    # ─── EMPIRE MODULES ───
    def empire_status(self):
        return {
            "version": VERSION,
            "uptime": time.time() - START_TIME,
            "health_score": self.db.get('health_score', 100),
            "cash": float(self.db.get('cash', 1000000)),
            "positions": len(self.db.query("SELECT * FROM positions")),
            "trades": self.db.query("SELECT COUNT(*) as c FROM trades")[0]['c'],
            "watchlist": len(self.db.query("SELECT * FROM watchlist")),
            "rules": len(self.db.query("SELECT * FROM rules WHERE active=1")),
            "knowledge": len(self.db.query("SELECT * FROM knowledge")),
            "plugins": len(self.db.query("SELECT * FROM plugins")),
            "connections": len(self.db.query("SELECT * FROM connections")),
            "platforms": len(self.db.query("SELECT * FROM platforms")),
            "cache": Cache.stats(),
            "db_size": os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0,
            "backups": len(os.listdir(BACKUP_DIR)) if os.path.exists(BACKUP_DIR) else 0,
            "timestamp": time.time()
        }
    
    def health(self):
        uptime = time.time() - START_TIME
        trades = self.db.query("SELECT COUNT(*) as c FROM trades")[0]['c']
        errors = self.db.query("SELECT COUNT(*) as c FROM logs WHERE level='ERROR'")[0]['c']
        
        score = 100
        if errors > 10: score -= 20
        if errors > 50: score -= 30
        if uptime < 60: score -= 10
        
        self.db.set('health_score', score)
        
        return {
            "version": VERSION,
            "health_score": score,
            "uptime": uptime,
            "trades": trades,
            "errors": errors,
            "db_ok": os.path.exists(DB_PATH),
            "cache_entries": Cache.stats()['entries'],
            "queue_size": TASK_QUEUE.qsize(),
            "status": "healthy" if score > 70 else "degraded" if score > 40 else "critical"
        }
    
    def backup(self):
        return self.db.backup()
    
    def logs(self, limit=50):
        return self.db.query("SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?", (limit,))
    
    def flush_logs(self):
        self.db.execute("DELETE FROM logs")
        return {"status": "flushed"}

# ═══════════════════════════════════════════════════════════════
# THREADED HTTP SERVER — Lightning fast
# ═══════════════════════════════════════════════════════════════

engine = EmpireEngine()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    daemon_threads = True
    allow_reuse_address = True

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress logs for speed
    
    def _json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _read_body(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            if length > 0:
                return json.loads(self.rfile.read(length))
        except:
            pass
        return {}
    
    def _crash_shield(self, handler_func):
        """Wrap endpoint so one crash doesn't kill the whole server."""
        try:
            handler_func()
        except Exception as e:
            err = traceback.format_exc()
            print(f"[CRASH SHIELD] {self.path}: {str(e)[:120]}")
            try:
                self._json_response({"error": f"Shielded: {str(e)[:80]}", "shielded": True}, 500)
            except:
                pass
    
    def do_GET(self):
        self._crash_shield(self._do_GET)
    
    def do_POST(self):
        self._crash_shield(self._do_POST)
    
    def _do_GET(self):
        path = self.path
        
        # ═══ STATIC FILES ═══
        if path == '/':
            try:
                web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')
                with open(os.path.join(web_dir, 'frontend.html'), 'r') as f:
                    html = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(html.encode())
                return
            except:
                self._json_response({"message": "LilJR Empire v8.0", "open": "http://localhost:8000/web/frontend.html"})
        
        elif path.startswith('/web/'):
            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path.lstrip('/'))
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                self.send_response(200)
                if file_path.endswith('.html'):
                    self.send_header('Content-Type', 'text/html')
                elif file_path.endswith('.css'):
                    self.send_header('Content-Type', 'text/css')
                elif file_path.endswith('.js'):
                    self.send_header('Content-Type', 'application/javascript')
                self.end_headers()
                self.wfile.write(content.encode())
                return
            else:
                self._json_response({"error": "File not found"}, 404)
        
        # ═══ CORE API ═══
        elif path == '/api/health':
            self._json_response(engine.health())
        
        elif path == '/api/empire':
            self._json_response(engine.empire_status())
        
        elif path.startswith('/api/trading/price/'):
            sym = path.split('/')[-1]
            self._json_response(engine.price(sym))
        
        elif path == '/api/trading/portfolio':
            self._json_response(engine.portfolio())
        
        elif path == '/api/trading/history':
            trades = engine.db.query("SELECT * FROM trades ORDER BY timestamp DESC LIMIT 50")
            self._json_response({"trades": trades})
        
        elif path == '/api/watchlist':
            self._json_response({"watchlist": engine.watchlist()})
        
        elif path == '/api/rules':
            self._json_response({"rules": engine.list_rules()})
        
        elif path == '/api/knowledge':
            self._json_response({"knowledge": engine.db.query("SELECT * FROM knowledge")})
        
        elif path == '/api/plugins':
            self._json_response({"plugins": engine.list_plugins()})
        
        elif path == '/api/connections':
            self._json_response({"connections": engine.list_connections()})
        
        elif path == '/api/platforms':
            self._json_response({"platforms": engine.list_platforms()})
        
        elif path == '/api/logs':
            limit = urllib.parse.parse_qs(urllib.parse.urlparse(path).query).get('limit', ['50'])[0]
            self._json_response({"logs": engine.logs(int(limit))})
        
        elif path == '/api/cache/stats':
            self._json_response(Cache.stats())
        
        elif path.startswith('/api/connect/discover/'):
            target = urllib.parse.unquote(path.split('/api/connect/discover/')[-1])
            if not target.startswith('http'):
                target = 'http://' + target
            self._json_response(engine.discover(target))
        
        # ═══ AUTONOMOUS MODULES (read-only) ═══
        elif path == '/api/self/scan':
            if engine.awareness:
                files = engine.awareness.scan_self()
                self._json_response({"files": len(files), "scan_complete": True})
            else:
                self._json_response({"error": "Self-awareness not available"})
        
        elif path == '/api/self/status':
            if engine.awareness:
                self._json_response(engine.awareness.get_status())
            else:
                self._json_response({"error": "Self-awareness not available"})
        
        elif path == '/api/self/decisions':
            if engine.awareness:
                engine.awareness.scan_self()
                engine.awareness.analyze_health()
                decisions = engine.awareness.decide_next_action()
                self._json_response({"decisions": decisions})
            else:
                self._json_response({"error": "Self-awareness not available"})
        
        elif path == '/api/coder/analyze':
            if engine.coder:
                report = engine.coder.analyze_project()
                self._json_response(report)
            else:
                self._json_response({"error": "Auto-coder not available"})
        
        elif path == '/api/web/themes':
            self._json_response({"themes": list(WebBuilderV2.THEMES.keys())})
        
        elif path == '/api/web/list':
            if engine.web_builder:
                self._json_response({"sites": engine.web_builder.list_sites()})
            else:
                self._json_response({"error": "Web builder not available"})
        
        elif path == '/api/autonomous/status':
            if engine.autonomous:
                self._json_response(engine.autonomous.get_report())
            else:
                self._json_response({"status": "not_running"})
        
        else:
            self._json_response({"error": "Unknown endpoint", "path": path, "version": VERSION}, 404)
    
    def do_POST(self):
        path = self.path
        data = self._read_body()
        
        # Trading
        if path == '/api/trading/buy':
            self._json_response(engine.buy(data.get('symbol'), data.get('qty', 1)))
        elif path == '/api/trading/sell':
            self._json_response(engine.sell(data.get('symbol'), data.get('qty', 1)))
        
        # Watchlist
        elif path == '/api/watchlist':
            self._json_response(engine.watch(data.get('symbol'), data.get('target_price')))
        elif path == '/api/watchlist/delete':
            self._json_response(engine.unwatch(data.get('symbol')))
        
        # Rules
        elif path == '/api/rules':
            self._json_response(engine.add_rule(
                data.get('symbol'), data.get('condition'),
                data.get('target_price'), data.get('action'), data.get('qty', 1)
            ))
        elif path == '/api/rules/run':
            self._json_response(engine.run_rules())
        
        # AI
        elif path == '/api/ai/chat':
            self._json_response({"response": engine.ai_chat(data.get('message', ''))})
        
        # Search
        elif path == '/api/search':
            self._json_response(engine.web_search(data.get('query'), data.get('count', 5)))
        elif path == '/api/fetch':
            self._json_response(engine.fetch_url(data.get('url')))
        
        # Knowledge
        elif path == '/api/learn':
            self._json_response(engine.learn(data.get('topic'), data.get('fact')))
        elif path == '/api/query':
            self._json_response(engine.query_knowledge(data.get('question')))
        
        # Plugins
        elif path == '/api/plugin/create':
            self._json_response(engine.create_plugin(data.get('name'), data.get('code')))
        elif path == '/api/plugin/run':
            self._json_response(engine.run_plugin(data.get('name')))
        
        # Connector
        elif path == '/api/connect/register':
            self._json_response(engine.connect_server(
                data.get('name'), data.get('url'),
                data.get('auth_type', 'none'), data.get('auth_token', ''),
                data.get('headers')
            ))
        elif path == '/api/connect/remove':
            conn_name = data.get('name')
            engine.db.execute("DELETE FROM connections WHERE name=?", (conn_name,))
            self._json_response({"status": "removed", "name": conn_name})
        elif path == '/api/connect/send':
            self._json_response(engine.send_to_server(
                data.get('name'), data.get('path', '/'),
                data.get('method', 'GET'), data.get('data'), data.get('params')
            ))
        
        # Platform Bridge
        elif path == '/api/platform/connect':
            self._json_response(engine.connect_platform(data.get('platform'), data.get('credentials')))
        elif path == '/api/platform/post':
            self._json_response(engine.platform_post(data.get('platform'), data.get('content'), data.get('extra')))
        elif path == '/api/platform/cross-post':
            self._json_response(engine.cross_post(data.get('content'), data.get('platforms', [])))
        
        # System
        elif path == '/api/backup':
            self._json_response(engine.backup())
        elif path == '/api/flush-logs':
            self._json_response(engine.flush_logs())
        
        # ═══ STEALTH ═══
        elif path == '/api/stealth/enable':
            if engine.stealth:
                engine.stealth.enable()
                self._json_response({"status": "stealth_enabled"})
            else:
                self._json_response({"error": "Stealth module not loaded"}, 500)
        
        elif path == '/api/stealth/status':
            if engine.stealth:
                status = engine.stealth.status()
                self._json_response({"status": status})
            else:
                self._json_response({"status": "Stealth: OFF (module missing)"})
        
        elif path == '/api/stealth/panic':
            if engine.stealth:
                threading.Thread(target=engine.stealth.panic, args=("API panic triggered",)).start()
                self._json_response({"status": "panic_initiated"})
            else:
                self._json_response({"error": "Stealth module not loaded"}, 500)
        
        # ═══ AUTONOMOUS MODULES ═══
        elif path == '/api/self/scan':
            if engine.awareness:
                files = engine.awareness.scan_self()
                self._json_response({"files": len(files), "scan_complete": True})
            else:
                self._json_response({"error": "Self-awareness not available"})
        
        elif path == '/api/self/status':
            if engine.awareness:
                self._json_response(engine.awareness.get_status())
            else:
                self._json_response({"error": "Self-awareness not available"})
        
        elif path == '/api/self/improve':
            if engine.awareness:
                result = engine.awareness.self_improve()
                self._json_response(result)
            else:
                self._json_response({"error": "Self-awareness not available"})
        
        elif path == '/api/self/decisions':
            if engine.awareness:
                engine.awareness.scan_self()
                engine.awareness.analyze_health()
                decisions = engine.awareness.decide_next_action()
                self._json_response({"decisions": decisions})
            else:
                self._json_response({"error": "Self-awareness not available"})
        
        elif path == '/api/coder/analyze':
            if engine.coder:
                report = engine.coder.analyze_project()
                self._json_response(report)
            else:
                self._json_response({"error": "Auto-coder not available"})
        
        elif path == '/api/coder/generate':
            if engine.coder:
                purpose = data.get('purpose', 'utility')
                funcs = data.get('functions', [['run', 'Main function', [], ['pass']]])
                result = engine.coder.generate_module_for(purpose, [(f[0], f[1]) for f in funcs])
                self._json_response(result)
            else:
                self._json_response({"error": "Auto-coder not available"})
        
        elif path == '/api/coder/landing':
            if engine.coder:
                name = data.get('name', 'Empire')
                tagline = data.get('tagline', 'Built different')
                features = data.get('features', [['Fast', 'Lightning speed'], ['Smart', 'AI powered']])
                html = engine.coder.generate_landing_page(name, tagline, features)
                path = data.get('path', f'web/{name.lower().replace(" ", "_")}.html')
                result = engine.coder.write_file(path, html)
                self._json_response({"html": html[:200], "saved": result})
            else:
                self._json_response({"error": "Auto-coder not available"})
        
        elif path == '/api/marketing/copy':
            if engine.marketing:
                copies = engine.marketing.generate_copy(
                    data.get('product', 'LilJR'),
                    data.get('type', 'launch'),
                    data.get('count', 3)
                )
                self._json_response({"copies": copies})
            else:
                self._json_response({"error": "Marketing engine not available"})
        
        elif path == '/api/marketing/calendar':
            if engine.marketing:
                calendar = engine.marketing.generate_social_calendar(
                    data.get('product', 'LilJR'),
                    data.get('days', 7)
                )
                self._json_response({"calendar": calendar})
            else:
                self._json_response({"error": "Marketing engine not available"})
        
        elif path == '/api/marketing/seo':
            if engine.marketing:
                content = engine.marketing.generate_seo_content(
                    data.get('keyword', 'AI tools'),
                    data.get('sections', 5)
                )
                self._json_response(content)
            else:
                self._json_response({"error": "Marketing engine not available"})
        
        elif path == '/api/search/deep':
            if engine.search:
                result = engine.search.deep_scan(
                    data.get('query', 'AI trends'),
                    data.get('depth', 2)
                )
                self._json_response(result)
            else:
                self._json_response({"error": "Deep search not available"})
        
        elif path == '/api/search/competitors':
            if engine.search:
                comps = engine.search.find_competitors(data.get('niche', 'AI tools'))
                self._json_response({"competitors": comps})
            else:
                self._json_response({"error": "Deep search not available"})
        
        elif path == '/api/autonomous/start':
            if engine.autonomous is None and AUTONOMOUS_AVAILABLE:
                engine.autonomous = AutonomousLoop()
                engine.autonomous._start_time = time.time()
                t = threading.Thread(target=engine.autonomous.run_forever, args=(60,), daemon=True)
                t.start()
                self._json_response({"status": "started", "mode": "autonomous"})
            elif engine.autonomous:
                self._json_response({"status": "already_running"})
            else:
                self._json_response({"error": "Autonomous loop not available"})
        
        elif path == '/api/autonomous/status':
            if engine.autonomous:
                self._json_response(engine.autonomous.get_report())
            else:
                self._json_response({"status": "not_running"})
        
        elif path == '/api/autonomous/stop':
            if engine.autonomous:
                engine.autonomous.stop()
                engine.autonomous = None
                self._json_response({"status": "stopped"})
            else:
                self._json_response({"status": "not_running"})
        
        # ═══ WEB BUILDER v2 ═══
        elif path == '/api/web/build':
            if engine.web_builder:
                sections = data.get('sections', [
                    {"type": "hero", "title": data.get('name', 'Site'), "text": data.get('tagline', ''), "cta": "Get Started"},
                    {"type": "features", "title": "Features", "items": [{"title": "Feature 1", "desc": "Description"}]},
                    {"type": "cta", "title": "Ready?", "text": "Join now.", "cta": "Start"}
                ])
                result = engine.web_builder.generate_business_site(
                    data.get('name', 'Site'),
                    data.get('tagline', 'Built by LilJR'),
                    sections,
                    data.get('theme', 'dark_empire'),
                    data.get('pages', ['index'])
                )
                self._json_response(result)
            else:
                self._json_response({"error": "Web builder not available"})
        
        elif path == '/api/web/app':
            if engine.web_builder:
                features = data.get('features', [
                    {"title": "Counter", "type": "counter", "id": "c1"},
                    {"title": "Form", "type": "form", "fields": ["Name", "Email"]}
                ])
                result = engine.web_builder.generate_web_app(
                    data.get('name', 'App'),
                    features,
                    data.get('theme', 'dark_empire')
                )
                self._json_response(result)
            else:
                self._json_response({"error": "Web builder not available"})
        
        elif path == '/api/web/restyle':
            if engine.web_builder:
                result = engine.web_builder.restyle(
                    data.get('page', 'index'),
                    data.get('theme', 'cyberpunk')
                )
                self._json_response(result)
            else:
                self._json_response({"error": "Web builder not available"})
        
        elif path == '/api/web/modify':
            if engine.web_builder:
                result = engine.web_builder.modify_page(
                    data.get('page', 'index'),
                    data.get('instruction', 'add pricing section')
                )
                self._json_response(result)
            else:
                self._json_response({"error": "Web builder not available"})
        
        elif path == '/api/web/list':
            if engine.web_builder:
                self._json_response({"sites": engine.web_builder.list_sites()})
            else:
                self._json_response({"error": "Web builder not available"})
        
        elif path == '/api/web/deploy':
            if engine.web_builder:
                result = engine.web_builder.deploy_to_github(
                    data.get('repo', 'user/repo'),
                    data.get('branch', 'main')
                )
                self._json_response(result)
            else:
                self._json_response({"error": "Web builder not available"})
        
        # ═══ WEB BUILDER v2 ═══
        elif path == '/api/web/build':
            if engine.web_builder:
                sections = data.get('sections', [
                    {"type": "hero", "title": data.get('name', 'Site'), "text": data.get('tagline', ''), "cta": "Get Started"},
                    {"type": "features", "title": "Features", "items": [{"title": "Feature 1", "desc": "Description"}]},
                    {"type": "cta", "title": "Ready?", "text": "Join now.", "cta": "Start"}
                ])
                result = engine.web_builder.generate_business_site(
                    data.get('name', 'Site'),
                    data.get('tagline', 'Built by LilJR'),
                    sections,
                    data.get('theme', 'dark_empire'),
                    data.get('pages', ['index'])
                )
                self._json_response(result)
            else:
                self._json_response({"error": "Web builder not available"})
        
        elif path == '/api/web/app':
            if engine.web_builder:
                features = data.get('features', [
                    {"title": "Counter", "type": "counter", "id": "c1"},
                    {"title": "Form", "type": "form", "fields": ["Name", "Email"]}
                ])
                result = engine.web_builder.generate_web_app(
                    data.get('name', 'App'),
                    features,
                    data.get('theme', 'dark_empire')
                )
                self._json_response(result)
            else:
                self._json_response({"error": "Web builder not available"})
        
        elif path == '/api/web/restyle':
            if engine.web_builder:
                result = engine.web_builder.restyle(
                    data.get('page', 'index'),
                    data.get('theme', 'cyberpunk')
                )
                self._json_response(result)
            else:
                self._json_response({"error": "Web builder not available"})
        
        elif path == '/api/web/modify':
            if engine.web_builder:
                result = engine.web_builder.modify_page(
                    data.get('page', 'index'),
                    data.get('instruction', 'add pricing section')
                )
                self._json_response(result)
            else:
                self._json_response({"error": "Web builder not available"})
        
        elif path == '/api/web/list':
            if engine.web_builder:
                self._json_response({"sites": engine.web_builder.list_sites()})
            else:
                self._json_response({"error": "Web builder not available"})
        
        elif path == '/api/web/deploy':
            if engine.web_builder:
                result = engine.web_builder.deploy_to_github(
                    data.get('repo', 'user/repo'),
                    data.get('branch', 'main')
                )
                self._json_response(result)
            else:
                self._json_response({"error": "Web builder not available"})
        
        elif path == '/api/web/themes':
            self._json_response({"themes": list(WebBuilderV2.THEMES.keys())})
        
        # ═══ NATURAL LANGUAGE ═══
        elif path == '/api/natural':
            try:
                from natural_language import NaturalCommander
                text = data.get('text', '')
                commander = NaturalCommander(engine)
                result = commander.execute(text)
                self._json_response(result)
            except Exception as e:
                self._json_response({"error": str(e), "note": "natural_language.py may not be available"})
        
        # ═══ PERSONA ENGINE ═══
        elif path == '/api/persona/switch':
            try:
                from persona_engine import get_engine
                pe = get_engine()
                self._json_response(pe.switch(data.get('name', 'user')))
            except Exception as e:
                self._json_response({"error": str(e)})
        
        elif path == '/api/persona/list':
            try:
                from persona_engine import get_engine
                pe = get_engine()
                self._json_response(pe.list_personas())
            except Exception as e:
                self._json_response({"error": str(e)})
        
        elif path == '/api/persona/train':
            try:
                from persona_engine import get_engine
                pe = get_engine()
                self._json_response(pe.train(data.get('text', ''), data.get('category', 'general')))
            except Exception as e:
                self._json_response({"error": str(e)})
        
        elif path == '/api/persona/speak':
            try:
                from persona_engine import get_engine
                pe = get_engine()
                msg = pe.speak(data.get('action', 'Done'), data.get('success', True))
                self._json_response({"message": msg, "persona": pe.active.get('name')})
            except Exception as e:
                self._json_response({"error": str(e)})
        
        elif path == '/api/persona/stats':
            try:
                from persona_engine import get_engine
                pe = get_engine()
                self._json_response(pe.get_training_stats())
            except Exception as e:
                self._json_response({"error": str(e)})
        
        elif path == '/api/persona/create':
            try:
                from persona_engine import get_engine
                pe = get_engine()
                result = pe.create_persona(
                    data.get('name', 'Custom'),
                    data.get('description', ''),
                    data.get('style', 'neutral'),
                    data.get('profanity', 0),
                    data.get('energy', 5),
                    data.get('formality', 5),
                    data.get('gender', 'neutral')
                )
                self._json_response(result)
            except Exception as e:
                self._json_response({"error": str(e)})
        
        # ═══ VISION ENGINE — Camera ═══
        elif path == '/api/vision':
            try:
                from vision_engine import get_engine
                ve = get_engine()
                memory = ve.receive_image(data.get('image', ''), data.get('caption'))
                desc = ve.describe_what_i_see(memory['id'])
                self._json_response(desc)
            except Exception as e:
                self._json_response({"error": str(e)})
        
        elif path == '/api/vision/learn':
            try:
                from vision_engine import get_engine
                ve = get_engine()
                result = ve.learn_object(data.get('name'), data.get('description'), data.get('tags'))
                self._json_response(result)
            except Exception as e:
                self._json_response({"error": str(e)})
        
        elif path == '/api/vision/recognize':
            try:
                from vision_engine import get_engine
                ve = get_engine()
                self._json_response(ve.recognize())
            except Exception as e:
                self._json_response({"error": str(e)})
        
        elif path == '/api/vision/memories':
            try:
                from vision_engine import get_engine
                ve = get_engine()
                self._json_response(ve.get_memories())
            except Exception as e:
                self._json_response({"error": str(e)})
        
        else:
            self._json_response({"error": "Unknown endpoint"}, 404)

# ═══════════════════════════════════════════════════════════════
# START
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    PORT = int(os.environ.get('LILJR_PORT', 8000))
    server = ThreadedHTTPServer(('0.0.0.0', PORT), Handler)
    print(f"[EMPIRE] LilJR v8.0 running on 0.0.0.0:{PORT}")
    print(f"[EMPIRE] DB: {DB_PATH}")
    print(f"[EMPIRE] Threaded. Persistent. Unstoppable.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[EMPIRE] Shutting down...")
        server.shutdown()
