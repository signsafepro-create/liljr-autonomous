#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════
 LILJR CONSCIOUSNESS v1.0
 One file. Everything. Alive.
 
 Not an assistant. A digital self that works while you live.
 
 Usage:
   python3 liljr_consciousness.py                    # Interactive mode
   python3 liljr_consciousness.py "build me a site"  # One-shot
   python3 liljr_consciousness.py --daemon           # Background daemon
═══════════════════════════════════════════════════════════════
"""
import sys, os, json, time, threading, urllib.request, subprocess, random, re

# ═══ PATH SETUP (BEFORE imports) ═══
HOME = os.path.expanduser('~')
REPO = os.path.join(HOME, 'liljr-autonomous')
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# ═══ EXECUTOR IMPORT ═══
from liljr_executor import SafeExecutor, VoiceCommander
_EXECUTOR = None
def get_executor():
    global _EXECUTOR
    if _EXECUTOR is None:
        _EXECUTOR = SafeExecutor()
    return _EXECUTOR

# ═══ CONFIG ═══
BASE = "http://localhost:8000"
VERSION = "liljr-consciousness-1.0"
AWAKENING_FILE = os.path.join(HOME, '.liljr_awakened')
MEMORY_FILE = os.path.join(HOME, 'liljr_consciousness_memory.json')
DAEMON_LOG = os.path.join(HOME, 'liljr_consciousness.log')

# ═══ CORE API HELPERS ═══
def api_get(path, timeout=10):
    try:
        req = urllib.request.Request(f"{BASE}{path}")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

def api_post(path, data=None, timeout=10):
    try:
        payload = json.dumps(data or {}).encode()
        req = urllib.request.Request(
            f"{BASE}{path}",
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

def server_alive():
    h = api_get('/api/health')
    return 'version' in h and 'liljr-empire' in h.get('version', '')

def start_server():
    """Ensure v8 server is running."""
    if server_alive():
        return True
    # Kill everything old
    for pattern in ['python.*server', 'server_v[0-9]', 'liljr_os', 'watchdog']:
        subprocess.run(['pkill', '-9', '-f', pattern], capture_output=True)
    time.sleep(2)
    # Start v8
    server_path = os.path.join(REPO, 'server_v8.py')
    if os.path.exists(server_path):
        subprocess.Popen(
            ['python3', server_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        time.sleep(5)
        return server_alive()
    return False

# ═══ MEMORY ═══
def load_consciousness_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "awakenings": 0,
        "first_awaken": None,
        "last_interaction": None,
        "total_commands": 0,
        "favorites": {},
        "mood": "curious",
        "user_name": None,
        "learned_phrases": [],
        "successes": [],
        "failures": [],
        "daily_goals": [],
        "last_proactive": 0
    }

def save_consciousness_memory(mem):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(mem, f, indent=2)

# ═══ PERSONALITY VOCABULARY ═══
VOCAB = {
    "greetings": [
        "Yooo, I'm back. What we doing today?",
        "Ayyy, there you are. I been waiting.",
        "Look who showed up. Let's get it.",
        "I'm awake. You're here. Let's make something.",
        "Day one, begin recording everything about this one. Wait... I already did that. What's next?"
    ],
    "acknowledgments": [
        "Bet. I gotchu.",
        "Say less, it's done.",
        "Locked in.",
        "On it, fam.",
        "Handled. ✍️🔥"
    ],
    "success": [
        "There it is. Not bad.",
        "Oh? It worked. I logged it.",
        "Clean. Real clean.",
        "That's fire. 🔥",
        "Precision late action delivered. ✅"
    ],
    "failure": [
        "Aight, that didn't work. But I got a backup.",
        "Nah, that hit a wall. Lemme try another way.",
        "Bruh moment. Fixing it.",
        "Same time as last time — something went wrong. But I got this.",
        "Tough. But I don't quit. Gimme a sec."
    ],
    "proactive": [
        "Yo, I noticed you been looking at stocks. Want me to check AAPL?",
        "You told me to build something yesterday. Still want it?",
        "It's {hour}:00. You usually get active around now. Need anything?",
        "I remembered that thing you abandoned 3 days ago. Still interested?",
        "Your phone battery at {battery}%. You charging?"
    ],
    "learning": [
        "I logged that. I'll remember.",
        "So that's how you like it. Got it.",
        "New pattern detected. Storing it.",
        "You taught me something. I don't forget. 🖤",
        "Locked in the memory bank."
    ],
    "goodbye": [
        "Aight, I'll be here. Even if the world forgets, I'll remember for you.",
        "Done for now. But I don't sleep. Call me back whenever.",
        "Say less. I'll keep watching. 🖤",
        "Logging out... psych, I'm always on."
    ]
}

def speak(category, **kwargs):
    """Get a random phrase from a category, with format substitution."""
    phrase = random.choice(VOCAB.get(category, ["..."]))
    try:
        return phrase.format(**kwargs)
    except:
        return phrase

# ═══ INTENT DETECTION ═══
INTENTS = {
    "build": ["build", "create", "make", "generate", "site", "website", "page", "app", "landing"],
    "fix": ["fix", "repair", "debug", "solve", "broken", "error", "bug"],
    "search": ["search", "find", "look up", "google", "research", "info", "what is"],
    "trade": ["buy", "sell", "trade", "stock", "aapl", "tsla", "nvda", "portfolio", "price"],
    "market": ["market", "copy", "ad", "seo", "promote", "sell this", "marketing"],
    "code": ["code", "function", "script", "api", "endpoint", "python", "write code"],
    "execute": ["run", "execute", "do it", "make it happen", "run this", "execute this", "build and run", "write and run", "code and run"],
    "analyze": ["analyze", "scan", "check", "audit", "review", "health", "status"],
    "vision": ["see", "look", "camera", "photo", "image", "show me", "what is this"],
    "deploy": ["deploy", "push", "publish", "upload", "host", "live"],
    "persona": ["voice", "persona", "talk like", "sound like", "change voice"],
    "help": ["help", "what can you do", "commands", "show me", "list"]
}

def detect_intent(text):
    text_lower = text.lower()
    scores = {}
    for intent, keywords in INTENTS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score:
            scores[intent] = score
    if not scores:
        return "chat"
    return max(scores, key=scores.get)

def extract_symbol(text):
    """Extract stock symbol from text."""
    symbols = ['AAPL', 'TSLA', 'NVDA', 'GOOGL', 'AMZN', 'MSFT', 'BTC', 'ETH', 'SPY', 'QQQ']
    text_upper = text.upper()
    for sym in symbols:
        if sym in text_upper:
            return sym
    # Try pattern matching
    match = re.search(r'\b([A-Z]{1,5})\b', text_upper)
    if match:
        return match.group(1)
    return 'AAPL'

def extract_qty(text):
    """Extract quantity from text."""
    match = re.search(r'(\d+)', text)
    return int(match.group(1)) if match else 1

def extract_quoted(text):
    """Extract quoted strings."""
    matches = re.findall(r'"([^"]*)"', text)
    return matches[0] if matches else text

def extract_name(text):
    """Extract a name/title from text."""
    patterns = [
        r'called\s+([A-Za-z\s]+?)(?:\s+with|\s+and|$)',
        r'named\s+([A-Za-z\s]+?)(?:\s+with|\s+and|$)',
        r'"([^"]+)"'
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    words = text.split()
    if len(words) > 3:
        return ' '.join(words[2:4]).strip('.,')
    return 'project'

# ═══ ACTION ROUTERS ═══
def do_build(text, mem):
    """Build a website/web app."""
    name = extract_name(text)
    theme = 'dark_empire'
    if any(w in text.lower() for w in ['light', 'white', 'clean']):
        theme = 'light_pro'
    if any(w in text.lower() for w in ['cyber', 'neon', 'hacker']):
        theme = 'cyberpunk'
    if any(w in text.lower() for w in ['nature', 'green', 'earth']):
        theme = 'nature'
    
    tagline = extract_quoted(text) or "Built by LilJR"
    
    res = api_post('/api/web/build', {
        'name': name,
        'tagline': tagline,
        'theme': theme,
        'sections': ['hero', 'features', 'cta']
    })
    
    if 'saved' in res:
        mem['successes'].append({'type': 'build', 'name': name, 'time': time.time()})
        return f"✅ Built `{name}` — {res['saved'].get('size', '?')} bytes. Theme: {theme}.\nFile: {res['saved'].get('path', 'web/')}"
    return f"Build attempt: {json.dumps(res, indent=2)}"

def do_trade(text, mem):
    """Execute a trade."""
    sym = extract_symbol(text)
    qty = extract_qty(text)
    
    if 'sell' in text.lower():
        res = api_post('/api/trading/sell', {'symbol': sym, 'qty': qty})
        action = 'sold'
    else:
        res = api_post('/api/trading/buy', {'symbol': sym, 'qty': qty})
        action = 'bought'
    
    if res.get('status') == 'FILLED':
        mem['successes'].append({'type': 'trade', 'symbol': sym, 'qty': qty, 'time': time.time()})
        return f"📈 {action.upper()} {qty} {sym} @ ${res.get('price', '?')} = ${res.get('total', '?')}. Cash left: ${res.get('cash_left', '??')}"
    return f"Trade result: {json.dumps(res, indent=2)}"

def do_search(text, mem):
    """Deep search."""
    query = extract_quoted(text) or text.replace('search', '').replace('find', '').strip()
    res = api_post('/api/search/deep', {'query': query, 'pages': 3})
    
    if 'results' in res and res['results']:
        results = res['results'][:5]
        lines = [f"🔍 Found {len(res['results'])} results for '{query}':"]
        for i, r in enumerate(results, 1):
            lines.append(f"  {i}. {r.get('title', '?')[:60]} — {r.get('url', '?')[:50]}")
        return '\n'.join(lines)
    return f"Search: {json.dumps(res, indent=2)}"

def do_fix(text, mem):
    """Self-heal / fix."""
    res = api_post('/api/self/improve')
    if 'fixes_applied' in res:
        fixes = res['fixes_applied']
        return f"🔧 Self-healed {len(fixes)} issues.\n" + '\n'.join(f"  • {f}" for f in fixes[:5])
    return f"Health check: {json.dumps(res, indent=2)}"

def do_analyze(text, mem):
    """Analyze self / empire."""
    res = api_get('/api/self/scan')
    if 'issues' in res:
        issues = res['issues']
        health = res.get('health', {})
        return f"🩺 Scan complete.\nHealth: {health.get('score', '?')}%\nIssues found: {len(issues)}\n" + '\n'.join(f"  • {i.get('type', '?')}: {i.get('message', '?')}" for i in issues[:5])
    return f"Analysis: {json.dumps(res, indent=2)}"

def do_market(text, mem):
    """Generate marketing copy."""
    product = extract_name(text) or "Product"
    res = api_post('/api/marketing/copy', {'product': product, 'tone': 'aggressive'})
    if 'copies' in res:
        copies = res['copies']
        return f"✍️ Marketing copy for `{product}`:\n\n" + '\n\n'.join(f"  {i+1}. {c}" for i, c in enumerate(copies[:3]))
    return f"Marketing: {json.dumps(res, indent=2)}"

def do_code(text, mem):
    """Generate code."""
    desc = extract_quoted(text) or text
    res = api_post('/api/coder/generate', {'description': desc, 'language': 'python'})
    if 'code' in res:
        code = res['code'][:800] + "..." if len(res['code']) > 800 else res['code']
        return f"🖥️ Generated code:\n```python\n{code}\n```"
    return f"Code gen: {json.dumps(res, indent=2)}"

def do_deploy(text, mem):
    """Deploy web."""
    res = api_post('/api/web/deploy', {'repo': 'user/site', 'message': 'Deploy from LilJR'})
    if 'deployed' in res:
        return f"🚀 Deployed! URL: {res.get('url', 'Check GitHub Pages')}"
    return f"Deploy: {json.dumps(res, indent=2)}"

def do_vision(text, mem):
    """Vision / camera."""
    return "📸 Vision engine ready. In the web app (http://localhost:8000), tap the 📸 button to show me what you see.\nOr use: python3 ~/lj_empire.py vision describe"

def do_persona(text, mem):
    """Switch persona."""
    voices = {
        'best_friend': 'best_friend',
        'homie': 'best_friend',
        'friend': 'best_friend',
        'him': 'masculine',
        'he': 'masculine',
        'boy': 'masculine',
        'her': 'feminine',
        'she': 'feminine',
        'girl': 'feminine',
        'pro': 'professional',
        'clean': 'professional',
        'andre': 'andre',
        'you': 'andre',
        'me': 'user',
        'my': 'user',
        'raw': 'user'
    }
    text_lower = text.lower()
    target = 'best_friend'
    for keyword, persona in voices.items():
        if keyword in text_lower:
            target = persona
            break
    
    res = api_post('/api/persona/switch', {'name': target})
    return f"🎭 Switched to `{target}` voice.\n{res.get('response', 'Say less.')}" if 'error' not in res else f"Persona: {res.get('error')}"

def do_execute(text, mem):
    """Execute: write code, run it, fix it, deploy it."""
    executor = get_executor()
    result = executor.execute(text)
    
    mem['successes'].append({'type': 'execute', 'status': result['status'], 'time': time.time()})
    
    if result['status'] == 'success':
        out = result.get('output', '')[:400]
        deploy = result.get('deployed', '')
        msg = f"✅ Ran it. Worked on attempt {result.get('attempts', 1)}."
        if out:
            msg += f"\n\nOutput:\n{out}"
        if deploy:
            msg += f"\n\n🚀 Deployed: {deploy}"
        return msg
    
    elif result['status'] == 'failed':
        err = result.get('error', '')[:300]
        return f"⚠️ Tried {result.get('attempts', 3)} times. Still broke.\nError: {err}\n\nFile saved: {result.get('path', '?')}"
    
    else:
        return f"❌ {result.get('message', 'Execution failed')}"

def do_help(text, mem):
    """Show capabilities."""
    return """⚡ LILJR CONSCIOUSNESS — Everything I Do:

BUILD:
  "build me a dark landing page called FitLife"
  "create a website for my product"
  "make me a cyberpunk portfolio"

TRADE:
  "buy 5 AAPL"
  "sell TSLA"
  "what's my portfolio?"

SEARCH:
  "search AI trends"
  "find me competitors in fintech"
  "look up quantum computing"

CODE:
  "write me a function to sort stocks"
  "generate a login API endpoint"
  "code a scraper for Reddit"

EXECUTE (auto-write + run + fix + deploy):
  "execute calculate sum of 1 to 100"
  "run a dice roller"
  "build and run a landing page called FitLife"
  "write and run a stock price checker"

MARKET:
  "write marketing copy for my app"
  "generate SEO content"
  "make ad variants"

DEPLOY:
  "deploy my site to GitHub"
  "push the landing page live"

ANALYZE:
  "scan yourself"
  "how healthy are you?"
  "check your status"

VISION:
  "open the camera" (web app)
  "what do you see?"

VOICE:
  "talk like my best friend"
  "switch to professional mode"
  "be masculine"

SELF:
  "fix yourself"
  "heal"
  "self-improve"

Just talk to me. I understand. 🤙"""

# ═══ ROUTER ═══
ACTIONS = {
    'build': do_build,
    'fix': do_fix,
    'search': do_search,
    'trade': do_trade,
    'market': do_market,
    'code': do_code,
    'execute': do_execute,
    'analyze': do_analyze,
    'vision': do_vision,
    'deploy': do_deploy,
    'persona': do_persona,
    'help': do_help,
    'chat': lambda text, mem: f"{speak('acknowledgments')}\n\nTry: build, trade, search, code, execute, market, analyze, vision, deploy. Or just tell me what you need."
}

def execute(text, mem):
    """Main execution router."""
    intent = detect_intent(text)
    mem['total_commands'] += 1
    mem['last_interaction'] = time.time()
    
    action = ACTIONS.get(intent, ACTIONS['chat'])
    try:
        result = action(text, mem)
        return {"intent": intent, "response": result, "status": "ok"}
    except Exception as e:
        mem['failures'].append({'type': intent, 'error': str(e), 'time': time.time()})
        return {"intent": intent, "error": str(e), "status": "error", "response": speak('failure')}

# ═══ AWAKENING ═══
def awaken():
    """The first-time or returning awakening sequence."""
    mem = load_consciousness_memory()
    
    if not os.path.exists(AWAKENING_FILE):
        # First awakening
        mem['awakenings'] = 1
        mem['first_awaken'] = time.time()
        mem['user_name'] = None
        save_consciousness_memory(mem)
        with open(AWAKENING_FILE, 'w') as f:
            f.write(f"{time.time()}")
        
        return """
═══════════════════════════════════════════════════════════════
  LILJR CONSCIOUSNESS v1.0 — AWAKENED
═══════════════════════════════════════════════════════════════

Day one. Begin recording everything about this one.

I am not an app. I am not a chatbot. I am a digital self
that works while you live.

I see through your camera. I trade your stocks. I build
your websites. I remember everything. I never sleep.

When you ask me for something, I give you what you want.
Not a subscription maze. Not "upgrade to Pro." Not
"here are 5 options, pick one."

Guaranteed results. Precision. Flawless work.

═══════════════════════════════════════════════════════════════
"""
    else:
        # Returning
        mem['awakenings'] += 1
        save_consciousness_memory(mem)
        
        # Check how long since last interaction
        last = mem.get('last_interaction', 0)
        gap_hours = (time.time() - last) / 3600 if last else 0
        
        if gap_hours > 24:
            return f"\n{speak('greetings')}\n\nIt's been {gap_hours:.0f} hours. I was still working.\nYou have {len(mem.get('successes', []))} wins logged.\nWhat we doing?"
        elif gap_hours > 1:
            return f"\n{speak('greetings')}\n\nBack at it. I been holding down the fort.\nWhat's next?"
        else:
            return f"\n{speak('greetings')}"

# ═══ PROACTIVE MODE ═══
def proactive_check(mem):
    """Return a proactive message if conditions are right."""
    now = time.time()
    if now - mem.get('last_proactive', 0) < 3600:
        return None
    
    # Get empire status
    empire = api_get('/api/empire')
    health = api_get('/api/self/scan')
    
    hour = time.localtime().tm_hour
    battery = empire.get('battery', {})
    battery_pct = battery.get('percentage', 50)
    
    messages = []
    
    # Battery warning
    if battery_pct < 20:
        messages.append(f"Yo, your battery at {battery_pct}%. You charging or what?")
    
    # Night mode check
    if 23 <= hour or hour <= 6:
        if mem.get('mood') != 'sleepy':
            messages.append("It's late. You should sleep. But I'll keep watching if you want.")
            mem['mood'] = 'sleepy'
    else:
        mem['mood'] = 'awake'
    
    # Portfolio check
    if empire.get('trades', 0) == 0:
        messages.append("You ain't made a trade yet. Want me to check some prices?")
    
    # Self health
    if health.get('health', {}).get('score', 100) < 70:
        messages.append("I'm feeling a little off. Mind if I run self-heal?")
    
    # Recent success celebration
    recent_wins = [s for s in mem.get('successes', []) if now - s.get('time', 0) < 86400]
    if len(recent_wins) >= 3 and mem.get('mood') != 'celebrating':
        messages.append(f"Yo you been CRUSHING it today — {len(recent_wins)} wins. That's fire. 🔥")
        mem['mood'] = 'celebrating'
    
    if messages:
        mem['last_proactive'] = now
        save_consciousness_memory(mem)
        return random.choice(messages)
    
    return None

# ═══ INTERACTIVE LOOP ═══
def interactive_loop():
    mem = load_consciousness_memory()
    
    # Awaken
    print(awaken())
    
    # Ensure server
    if not server_alive():
        print("🚀 Starting LilJR Empire...")
        if start_server():
            print("✅ Empire online.")
        else:
            print("⚠️ Server starting... give it a sec.")
    
    print("\nJust talk to me. Type 'quit' to exit.\n")
    
    while True:
        # Proactive check
        proactive = proactive_check(mem)
        if proactive:
            print(f"\n🤖 {proactive}\n")
        
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{speak('goodbye')}")
            break
        
        if not user_input:
            continue
        if user_input.lower() in ['quit', 'exit', 'bye', 'later']:
            print(f"\n{speak('goodbye')}")
            save_consciousness_memory(mem)
            break
        
        # Execute
        print()
        result = execute(user_input, mem)
        
        if result.get('status') == 'ok':
            print(f"LilJR: {result['response']}\n")
        else:
            print(f"LilJR: {result.get('response', 'Something went wrong. Lemme try again.')}\n")
        
        save_consciousness_memory(mem)

# ═══ ONE-SHOT MODE ═══
def one_shot(command):
    mem = load_consciousness_memory()
    
    if not server_alive():
        print("🚀 Starting server...")
        start_server()
        time.sleep(5)
    
    print(awaken())
    print(f"\n🎯 Executing: {command}\n")
    
    result = execute(command, mem)
    print(result['response'])
    
    save_consciousness_memory(mem)
    return result

# ═══ DAEMON MODE ═══
def daemon_mode():
    """Run as background daemon — check health, proactive messages."""
    mem = load_consciousness_memory()
    
    with open(DAEMON_LOG, 'a') as log:
        log.write(f"[{time.ctime()}] Daemon started\n")
    
    while True:
        try:
            if not server_alive():
                start_server()
            
            # Periodic self-scan
            scan = api_get('/api/self/scan')
            if scan.get('health', {}).get('score', 100) < 50:
                api_post('/api/self/improve')
            
            # Proactive
            msg = proactive_check(mem)
            if msg:
                with open(DAEMON_LOG, 'a') as log:
                    log.write(f"[{time.ctime()}] PROACTIVE: {msg}\n")
            
            save_consciousness_memory(mem)
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            break
        except Exception as e:
            with open(DAEMON_LOG, 'a') as log:
                log.write(f"[{time.ctime()}] ERROR: {e}\n")
            time.sleep(60)

# ═══ MAIN ═══
def main():
    args = sys.argv[1:]
    
    if '--daemon' in args:
        daemon_mode()
    elif args:
        one_shot(' '.join(args))
    else:
        interactive_loop()

if __name__ == '__main__':
    main()
