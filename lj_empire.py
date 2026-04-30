#!/usr/bin/env python3
"""
LILJR EMPIRE CLI v8.0
Pure Python. No curl. Lightning fast. Bulletproof.
"""
import sys, json, urllib.request, os

BASE = "http://localhost:8000"

def api_get(path):
    try:
        req = urllib.request.Request(f"{BASE}{path}")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

def api_post(path, data=None):
    try:
        payload = json.dumps(data or {}).encode()
        req = urllib.request.Request(f"{BASE}{path}", data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

def main():
    if len(sys.argv) < 2:
        print_help()
        return
    
    cmd = sys.argv[1]
    
    # ═══ SERVER ═══
    if cmd == 'start':
        print("🚀 Starting LilJR Empire v8.0...")
        os.system("pkill -f 'server_v8.py' 2>/dev/null; sleep 1; nohup python3 ~/liljr-autonomous/server_v8.py > /dev/null 2>&1 &")
        import time; time.sleep(2)
        print(json.dumps(api_get('/api/empire'), indent=2))
    
    elif cmd == 'stop':
        os.system("pkill -f 'server_v8.py'")
        print("Stopped.")
    
    elif cmd == 'status':
        print(json.dumps(api_get('/api/health'), indent=2))
    
    elif cmd == 'empire':
        print(json.dumps(api_get('/api/empire'), indent=2))
    
    # ═══ TRADING ═══
    elif cmd == 'buy':
        sym = sys.argv[2] if len(sys.argv) > 2 else 'AAPL'
        qty = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        print(json.dumps(api_post('/api/trading/buy', {"symbol": sym, "qty": qty}), indent=2))
    
    elif cmd == 'sell':
        sym = sys.argv[2] if len(sys.argv) > 2 else 'AAPL'
        qty = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        print(json.dumps(api_post('/api/trading/sell', {"symbol": sym, "qty": qty}), indent=2))
    
    elif cmd == 'price':
        sym = sys.argv[2] if len(sys.argv) > 2 else 'AAPL'
        print(json.dumps(api_get(f'/api/trading/price/{sym}'), indent=2))
    
    elif cmd == 'portfolio':
        print(json.dumps(api_get('/api/trading/portfolio'), indent=2))
    
    elif cmd == 'history':
        print(json.dumps(api_get('/api/trading/history'), indent=2))
    
    # ═══ WATCHLIST ═══
    elif cmd == 'watch':
        sym = sys.argv[2] if len(sys.argv) > 2 else 'AAPL'
        target = float(sys.argv[3]) if len(sys.argv) > 3 else 150.0
        print(json.dumps(api_post('/api/watchlist', {"symbol": sym, "target_price": target}), indent=2))
    
    elif cmd == 'unwatch':
        sym = sys.argv[2] if len(sys.argv) > 2 else 'AAPL'
        print(json.dumps(api_post('/api/watchlist/delete', {"symbol": sym}), indent=2))
    
    elif cmd == 'watches':
        print(json.dumps(api_get('/api/watchlist'), indent=2))
    
    # ═══ RULES ═══
    elif cmd == 'rule':
        sym = sys.argv[2] if len(sys.argv) > 2 else 'AAPL'
        cond = sys.argv[3] if len(sys.argv) > 3 else 'below'
        target = float(sys.argv[4]) if len(sys.argv) > 4 else 150.0
        action = sys.argv[5] if len(sys.argv) > 5 else 'buy'
        qty = int(sys.argv[6]) if len(sys.argv) > 6 else 1
        print(json.dumps(api_post('/api/rules', {"symbol": sym, "condition": cond, "target_price": target, "action": action, "qty": qty}), indent=2))
    
    elif cmd == 'rules':
        print(json.dumps(api_get('/api/rules'), indent=2))
    
    elif cmd == 'run':
        print(json.dumps(api_post('/api/rules/run'), indent=2))
    
    # ═══ AI ═══
    elif cmd == 'ai':
        msg = ' '.join(sys.argv[2:])
        print(json.dumps(api_post('/api/ai/chat', {"message": msg}), indent=2))
    
    # ═══ SEARCH / KNOWLEDGE ═══
    elif cmd == 'search':
        query = ' '.join(sys.argv[2:])
        print(json.dumps(api_post('/api/search', {"query": query, "count": 5}), indent=2))
    
    elif cmd == 'fetch':
        url = sys.argv[2] if len(sys.argv) > 2 else 'https://example.com'
        print(json.dumps(api_post('/api/fetch', {"url": url}), indent=2))
    
    elif cmd == 'learn':
        topic = sys.argv[2] if len(sys.argv) > 2 else 'python'
        fact = sys.argv[3] if len(sys.argv) > 3 else 'is a language'
        print(json.dumps(api_post('/api/learn', {"topic": topic, "fact": fact}), indent=2))
    
    elif cmd == 'query':
        question = ' '.join(sys.argv[2:])
        print(json.dumps(api_post('/api/query', {"question": question}), indent=2))
    
    elif cmd == 'knowledge':
        print(json.dumps(api_get('/api/knowledge'), indent=2))
    
    # ═══ PLUGINS ═══
    elif cmd == 'plugin':
        name = sys.argv[2] if len(sys.argv) > 2 else 'myplugin'
        if len(sys.argv) > 3 and os.path.isfile(sys.argv[3]):
            with open(sys.argv[3]) as f:
                code = f.read()
        else:
            print("Enter plugin code (Ctrl+D when done):")
            code = sys.stdin.read()
        print(json.dumps(api_post('/api/plugin/create', {"name": name, "code": code}), indent=2))
    
    elif cmd == 'run-plugin':
        name = sys.argv[2] if len(sys.argv) > 2 else 'myplugin'
        print(json.dumps(api_post('/api/plugin/run', {"name": name}), indent=2))
    
    elif cmd == 'plugins':
        print(json.dumps(api_get('/api/plugins'), indent=2))
    
    # ═══ CONNECTOR ═══
    elif cmd == 'connect':
        name = sys.argv[2] if len(sys.argv) > 2 else 'server'
        url = sys.argv[3] if len(sys.argv) > 3 else 'http://localhost'
        auth_type = sys.argv[4] if len(sys.argv) > 4 else 'none'
        auth_token = sys.argv[5] if len(sys.argv) > 5 else ''
        print(json.dumps(api_post('/api/connect/register', {"name": name, "url": url, "auth_type": auth_type, "auth_token": auth_token}), indent=2))
    
    elif cmd == 'disconnect':
        name = sys.argv[2] if len(sys.argv) > 2 else 'server'
        print(json.dumps(api_post('/api/connect/remove', {"name": name}), indent=2))
    
    elif cmd == 'connections':
        print(json.dumps(api_get('/api/connections'), indent=2))
    
    elif cmd == 'send':
        name = sys.argv[2] if len(sys.argv) > 2 else 'server'
        path = sys.argv[3] if len(sys.argv) > 3 else '/'
        method = sys.argv[4] if len(sys.argv) > 4 else 'GET'
        data = json.loads(sys.argv[5]) if len(sys.argv) > 5 else {}
        print(json.dumps(api_post('/api/connect/send', {"name": name, "path": path, "method": method, "data": data}), indent=2))
    
    elif cmd == 'discover':
        target = sys.argv[2] if len(sys.argv) > 2 else 'localhost'
        if not target.startswith('http'):
            target = 'http://' + target
        encoded = urllib.request.pathname2url(target)
        print(json.dumps(api_get(f'/api/connect/discover/{encoded}'), indent=2))
    
    # ═══ PLATFORM BRIDGE ═══
    elif cmd == 'platform-connect':
        platform = sys.argv[2] if len(sys.argv) > 2 else 'github'
        creds = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        print(json.dumps(api_post('/api/platform/connect', {"platform": platform, "credentials": creds}), indent=2))
    
    elif cmd == 'post':
        platform = sys.argv[2] if len(sys.argv) > 2 else 'github'
        content = sys.argv[3] if len(sys.argv) > 3 else 'Hello'
        extra = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
        print(json.dumps(api_post('/api/platform/post', {"platform": platform, "content": content, "extra": extra}), indent=2))
    
    elif cmd == 'cross-post':
        content = sys.argv[2] if len(sys.argv) > 2 else 'Hello'
        platforms = sys.argv[3].split(',') if len(sys.argv) > 3 else ['github']
        print(json.dumps(api_post('/api/platform/cross-post', {"content": content, "platforms": platforms}), indent=2))
    
    elif cmd == 'platforms':
        print(json.dumps(api_get('/api/platforms'), indent=2))
    
    # ═══ SYSTEM ═══
    elif cmd == 'backup':
        print(json.dumps(api_post('/api/backup'), indent=2))
    
    elif cmd == 'logs':
        print(json.dumps(api_get('/api/logs'), indent=2))
    
    elif cmd == 'flush-logs':
        print(json.dumps(api_post('/api/flush-logs'), indent=2))
    
    elif cmd == 'cache':
        print(json.dumps(api_get('/api/cache/stats'), indent=2))
    
    # ═══ HELP ═══
    elif cmd in ('help', ''):
        print_help()
    
    else:
        print(f"Unknown: {cmd}")
        print_help()

def print_help():
    print("""LILJR EMPIRE v8.0 — Unstoppable. Lightning. Bulletproof.

SERVER:
  python3 ~/lj_empire.py start        — Start Empire
  python3 ~/lj_empire.py stop         — Stop
  python3 ~/lj_empire.py status       — Health check
  python3 ~/lj_empire.py empire       — Full empire status

TRADING:
  python3 ~/lj_empire.py buy AAPL 5
  python3 ~/lj_empire.py sell TSLA
  python3 ~/lj_empire.py price AAPL
  python3 ~/lj_empire.py portfolio
  python3 ~/lj_empire.py history

WATCHLIST:
  python3 ~/lj_empire.py watch AAPL 170
  python3 ~/lj_empire.py unwatch AAPL
  python3 ~/lj_empire.py watches

AUTO-TRADING:
  python3 ~/lj_empire.py rule AAPL below 150 buy 5
  python3 ~/lj_empire.py rules
  python3 ~/lj_empire.py run

AI (LOCAL):
  python3 ~/lj_empire.py ai What should I buy?

SEARCH / KNOWLEDGE:
  python3 ~/lj_empire.py search bitcoin news
  python3 ~/lj_empire.py fetch https://...
  python3 ~/lj_empire.py learn python "is a language"
  python3 ~/lj_empire.py query what is my cash
  python3 ~/lj_empire.py knowledge

PLUGINS:
  python3 ~/lj_empire.py plugin myplugin
  python3 ~/lj_empire.py run-plugin myplugin
  python3 ~/lj_empire.py plugins

CONNECTOR:
  python3 ~/lj_empire.py connect alpaca https://paper-api.alpaca.markets api_key PKxxx
  python3 ~/lj_empire.py connections
  python3 ~/lj_empire.py send alpaca /v2/account GET
  python3 ~/lj_empire.py discover api.example.com

PLATFORM BRIDGE:
  python3 ~/lj_empire.py platform-connect github '{"token":"ghp_xxx"}'
  python3 ~/lj_empire.py post github "Hello" '{"repo":"user/repo","path":"README.md"}'
  python3 ~/lj_empire.py cross-post "Hello" facebook,twitter,telegram
  python3 ~/lj_empire.py platforms

SYSTEM:
  python3 ~/lj_empire.py backup       — Create DB backup
  python3 ~/lj_empire.py logs         — View system logs
  python3 ~/lj_empire.py flush-logs   — Clear logs
  python3 ~/lj_empire.py cache        — Cache stats
""")

if __name__ == '__main__':
    main()
