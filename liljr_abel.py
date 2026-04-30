#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════
 LILJR ABEL v1.0 — The Ultimate Voice Commander

 One interface. One voice. One command.
 "Abel, build me a site" → done
 "Abel, buy 50 NVDA" → done
 "Abel, search AI trends" → done
 "Abel, deploy everything" → done

 Full system access. Zero friction. Zero questions.
═══════════════════════════════════════════════════════════════
"""
import sys, os, json, time, subprocess, re, threading, urllib.request

HOME = os.path.expanduser('~')
REPO = os.path.join(HOME, 'liljr-autonomous')
sys.path.insert(0, REPO)

BASE = "http://localhost:8000"

def api_get(path):
    try:
        req = urllib.request.Request(f"{BASE}{path}")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except:
        return {}

def api_post(path, data=None):
    try:
        payload = json.dumps(data or {}).encode()
        req = urllib.request.Request(f"{BASE}{path}", data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except:
        return {}

def ensure_server():
    health = api_get('/api/health')
    if 'version' not in health:
        subprocess.Popen(['python3', os.path.join(REPO, 'server_v8.py')],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(8)

def run_command(cmd_list, timeout=60):
    """Execute shell command with full output."""
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True, timeout=timeout)
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)

# ═══════════════════════════════════════════════════════════════
# NATURAL LANGUAGE COMMAND PARSER
# ═══════════════════════════════════════════════════════════════

class AbelBrain:
    def __init__(self):
        self.context = {}
        self.history = []
    
    def hear(self, command):
        """Parse natural language and execute."""
        command = command.strip()
        self.history.append({"time": time.time(), "cmd": command})
        
        # ─── BUILD / CREATE ───
        if any(w in command.lower() for w in ['build', 'create', 'make', 'generate', 'site', 'page', 'website', 'app', 'landing']):
            return self._do_build(command)
        
        # ─── TRADE / BUY / SELL ───
        if any(w in command.lower() for w in ['buy', 'sell', 'trade', 'stock', 'shares', 'position']):
            return self._do_trade(command)
        
        # ─── SEARCH / RESEARCH ───
        if any(w in command.lower() for w in ['search', 'find', 'look up', 'research', 'google', 'info', 'what is', 'who is', 'how to']):
            return self._do_search(command)
        
        # ─── CODE / SCRIPT ───
        if any(w in command.lower() for w in ['code', 'write code', 'script', 'function', 'program', 'python', 'javascript', 'api']):
            return self._do_code(command)
        
        # ─── EXECUTE / RUN ───
        if any(w in command.lower() for w in ['run', 'execute', 'do it', 'make it happen', 'launch', 'start']):
            return self._do_execute(command)
        
        # ─── MARKETING / COPY ───
        if any(w in command.lower() for w in ['market', 'copy', 'ad', 'seo', 'promote', 'sell this', 'headline', 'description']):
            return self._do_marketing(command)
        
        # ─── DEPLOY / PUSH ───
        if any(w in command.lower() for w in ['deploy', 'push', 'publish', 'upload', 'host', 'go live', 'git']):
            return self._do_deploy(command)
        
        # ─── VISION / CAMERA ───
        if any(w in command.lower() for w in ['photo', 'picture', 'camera', 'see', 'look', 'scan', 'image']):
            return self._do_vision(command)
        
        # ─── PHONE / SYSTEM ───
        if any(w in command.lower() for w in ['phone', 'notify', 'vibrate', 'toast', 'clipboard', 'battery', 'open']):
            return self._do_phone(command)
        
        # ─── STEALTH / SECURITY ───
        if any(w in command.lower() for w in ['stealth', 'invisible', 'hide', 'ghost', 'cloak', 'panic', 'vaporize']):
            return self._do_stealth(command)
        
        # ─── STATUS / HEALTH ───
        if any(w in command.lower() for w in ['status', 'health', 'check', 'how are you', 'what is running']):
            return self._do_status()
        
        # ─── HELP ───
        if any(w in command.lower() for w in ['help', 'what can you do', 'commands', 'show me']):
            return self._do_help()
        
        # ─── DEFAULT: Pass to AI chat ───
        return self._do_chat(command)
    
    def _extract_symbol(self, text):
        """Extract stock symbol from text."""
        words = text.upper().split()
        for w in words:
            if w in ['AAPL','TSLA','NVDA','GOOGL','AMZN','MSFT','META','NFLX','AMD','COIN','PLTR','HOOD','BTC','ETH','SPY','QQQ']:
                return w
        # Try any all-caps 1-5 letter word
        for w in words:
            if w.isalpha() and w.isupper() and 1 <= len(w) <= 5:
                return w
        return 'AAPL'
    
    def _extract_qty(self, text):
        """Extract quantity from text."""
        numbers = re.findall(r'\b(\d+)\b', text)
        if numbers:
            return int(numbers[0])
        return 1
    
    def _extract_name(self, text):
        """Extract project/business name from text."""
        # Look for quoted strings
        quoted = re.findall(r'["\']([^"\']+)["\']', text)
        if quoted:
            return quoted[0]
        # Look for "called X" or "named X"
        match = re.search(r'(?:called|named|make)\s+([A-Z][A-Za-z0-9\s]+?)(?:\s+site|\s+page|\s+app|$)', text, re.I)
        if match:
            return match.group(1).strip()
        return "Project"
    
    def _extract_tagline(self, text):
        """Extract tagline/description from text."""
        quoted = re.findall(r'["\']([^"\']+)["\']', text)
        if len(quoted) >= 2:
            return quoted[1]
        # Look for "about X" or "for X" or "tagline X"
        match = re.search(r'(?:about|for|tagline|saying)\s+([A-Z][^\.\,]+)', text, re.I)
        if match:
            return match.group(1).strip()
        return "Built by Abel"
    
    # ─── ACTION HANDLERS ───
    
    def _do_build(self, cmd):
        name = self._extract_name(cmd)
        tagline = self._extract_tagline(cmd)
        theme = 'dark_empire'
        if any(w in cmd.lower() for w in ['light', 'white', 'clean']): theme = 'light_pro'
        if any(w in cmd.lower() for w in ['cyber', 'neon', 'hacker', 'dark']): theme = 'dark_empire'
        
        res = api_post('/api/web/build', {
            'name': name, 'tagline': tagline, 'theme': theme,
            'sections': ['hero', 'features', 'cta']
        })
        if res.get('status') == 'built':
            size = res.get('pages', {}).get('index', {}).get('size', '?')
            return f"✅ Built `{name}` — {size} bytes, {theme} theme.\nFile: web/index.html"
        return f"Build result: {json.dumps(res, indent=2)[:300]}"
    
    def _do_trade(self, cmd):
        sym = self._extract_symbol(cmd)
        qty = self._extract_qty(cmd)
        action = 'sell' if 'sell' in cmd.lower() else 'buy'
        
        res = api_post(f'/api/trading/{action}', {'symbol': sym, 'qty': qty})
        if res.get('status') == 'FILLED':
            return f"📈 {action.upper()} {qty} {sym} @ ${res.get('price')} = ${res.get('total')}. Cash: ${res.get('cash', 'N/A')}"
        return f"Trade: {json.dumps(res, indent=2)[:300]}"
    
    def _do_search(self, cmd):
        query = cmd
        # Remove trigger words
        for w in ['search', 'find', 'look up', 'research', 'google', 'what is', 'who is', 'how to']:
            query = query.replace(w, '').strip()
        res = api_post('/api/search/deep', {'query': query, 'pages': 3})
        return f"🔍 Search: {query}\n{json.dumps(res, indent=2)[:500]}"
    
    def _do_code(self, cmd):
        res = api_post('/api/coder/generate', {'description': cmd})
        return f"💻 Code:\n{json.dumps(res, indent=2)[:500]}"
    
    def _do_execute(self, cmd):
        # Try to execute as shell command if it's system-related
        res = api_post('/api/self/improve', {})
        return f"⚡ Executed: {json.dumps(res, indent=2)[:300]}"
    
    def _do_marketing(self, cmd):
        product = cmd
        for w in ['market', 'copy', 'ad', 'seo', 'promote', 'sell this', 'headline']:
            product = product.replace(w, '').strip()
        res = api_post('/api/marketing/copy', {'product': product})
        return f"📢 Marketing:\n{json.dumps(res, indent=2)[:500]}"
    
    def _do_deploy(self, cmd):
        # Push to git
        out = run_command(['bash', '-c', f'cd {REPO} && git add -A && git commit -m "auto: $(date)" && git push origin main'])
        return f"🚀 Deploy:\n{out[:500]}"
    
    def _do_vision(self, cmd):
        photo_path = os.path.join(HOME, f'liljr_photo_{int(time.time())}.jpg')
        out = run_command(['termux-camera-photo', '-c', '0', photo_path])
        return f"📸 Photo: {photo_path}\n{out}"
    
    def _do_phone(self, cmd):
        if 'notify' in cmd.lower():
            msg = cmd.replace('notify', '').strip() or 'Abel working'
            out = run_command(['termux-notification', '--title', 'Abel', '--content', msg, '--priority', 'high'])
            return f"📱 Notified: {msg}"
        elif 'vibrate' in cmd.lower():
            out = run_command(['termux-vibrate', '-d', '500'])
            return "📳 Vibrated"
        elif 'clipboard' in cmd.lower():
            text = cmd.replace('clipboard', '').strip()
            out = run_command(['termux-clipboard-set', text])
            return f"📋 Copied: {text}"
        elif 'battery' in cmd.lower():
            out = run_command(['termux-battery-status'])
            return f"🔋 Battery:\n{out}"
        elif 'open' in cmd.lower():
            url = re.search(r'https?://[^\s]+', cmd)
            if url:
                out = run_command(['termux-open-url', url.group()])
                return f"🌐 Opened: {url.group()}"
        return "📱 Phone command executed"
    
    def _do_stealth(self, cmd):
        if 'panic' in cmd.lower() or 'vaporize' in cmd.lower() or 'kill' in cmd.lower():
            res = api_post('/api/stealth/panic', {})
            return f"☠️ {res.get('status', 'Panic initiated')}"
        elif 'status' in cmd.lower() or 'check' in cmd.lower():
            res = api_get('/api/stealth/status')
            return f"👻 {res.get('status', 'Unknown')}"
        else:
            res = api_post('/api/stealth/enable', {})
            return f"👻 Stealth: {res.get('status', 'Activated')}\nYou are invisible. Tamper = death."
    
    def _do_status(self):
        health = api_get('/api/health')
        empire = api_get('/api/empire')
        return f"⚡ ABEL STATUS\nHealth: {json.dumps(health, indent=2)}\nEmpire: {json.dumps(empire, indent=2)[:300]}"
    
    def _do_help(self):
        return """ABEL COMMANDS — Just say it:

"build me a site called X" → Creates landing page
"buy 50 NVDA" → Trades stock
"sell TSLA" → Sells stock
"search AI trends" → Deep research
"code a dice roller" → Generates code
"market my app" → Marketing copy
"deploy everything" → Git push
"take a photo" → Camera
"notify me when done" → Phone notification
"go stealth" → Invisible mode
"panic" → Vaporize everything
"status" → Health check

Just talk. Abel handles it."""
    
    def _do_chat(self, cmd):
        res = api_post('/api/ai/chat', {'message': cmd})
        return res.get('response', f"Chat: {json.dumps(res, indent=2)[:300]}")

# ═══════════════════════════════════════════════════════════════
# VOICE MODE (if termux-speech-to-text available)
# ═══════════════════════════════════════════════════════════════

def listen_and_act():
    """Voice command loop."""
    abel = AbelBrain()
    print("🎙️ ABEL VOICE MODE — Speak your command. Say 'quit' to exit.\n")
    
    while True:
        try:
            print("🎙️ Listening...")
            result = subprocess.run(['termux-speech-to-text'], capture_output=True, text=True, timeout=30)
            command = result.stdout.strip()
            
            if not command:
                print("(No voice detected)")
                continue
            
            print(f"👤 You: {command}")
            
            if command.lower() in ['quit', 'exit', 'stop', 'done']:
                print("👋 Abel out.")
                break
            
            response = abel.hear(command)
            print(f"🤖 Abel: {response}\n")
            
            # Speak back
            try:
                speak_text = response[:500] if len(response) > 500 else response
                subprocess.run(['termux-tts-speak', speak_text], capture_output=True, timeout=10)
            except:
                pass
                
        except subprocess.TimeoutExpired:
            print("(Listening timeout)")
        except KeyboardInterrupt:
            print("\n👋 Abel out.")
            break
        except Exception as e:
            print(f"Error: {e}")

# ═══════════════════════════════════════════════════════════════
# TEXT MODE
# ═══════════════════════════════════════════════════════════════

def text_loop():
    """Interactive text command loop."""
    abel = AbelBrain()
    print("""
═══════════════════════════════════════════════════════════════
  ABEL v1.0 — THE ULTIMATE COMMANDER
═══════════════════════════════════════════════════════════════

One word. One sentence. Abel does the rest.

Examples:
  "build me a dark landing page called FitLife"
  "buy 100 NVDA"
  "search top AI companies"
  "code me a password generator"
  "take a photo"
  "notify me when the build is done"
  "go stealth"

Type 'quit' to exit.
═══════════════════════════════════════════════════════════════
""")
    
    while True:
        try:
            command = input("👤 You: ").strip()
            
            if not command:
                continue
            
            if command.lower() in ['quit', 'exit', 'stop']:
                print("👋 Abel signing off. Empire keeps running.")
                break
            
            response = abel.hear(command)
            print(f"🤖 Abel: {response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Abel out.")
            break
        except EOFError:
            break

# ═══════════════════════════════════════════════════════════════
# ONE-SHOT MODE
# ═══════════════════════════════════════════════════════════════

def one_shot(command):
    """Execute single command and exit."""
    ensure_server()
    abel = AbelBrain()
    response = abel.hear(command)
    print(response)
    return response

# ═══════════════════════════════════════════════════════════════
# CLI ENTRY
# ═══════════════════════════════════════════════════════════════

def main():
    if len(sys.argv) > 1:
        # One-shot mode: python3 liljr_abel.py "build me a site"
        command = ' '.join(sys.argv[1:])
        one_shot(command)
    else:
        # Check if voice is available
        voice_available = subprocess.run(['which', 'termux-speech-to-text'], capture_output=True).returncode == 0
        if voice_available:
            print("🎙️ Voice detected. Starting voice mode...")
            listen_and_act()
        else:
            text_loop()

if __name__ == '__main__':
    main()
