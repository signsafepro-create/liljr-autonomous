#!/usr/bin/env python3
"""
LILJR COMMAND CENTER v1.0
Self-aware autonomous control brain.
Talk to it. It writes code, pushes, deploys, heals itself.
"""
import os, sys, json, subprocess, time, re, urllib.request
from datetime import datetime

STATE_FILE = os.path.expanduser('~/liljr_state.json')
REPO_DIR = os.path.expanduser('~/liljr-autonomous')
LOG_FILE = os.path.expanduser('~/liljr_command_center.log')
HEALTH_LOG = os.path.expanduser('~/liljr_health.log')

# ═══════════════════════════════════════════════════════════════
# SELF-AWARENESS ENGINE
# ═══════════════════════════════════════════════════════════════

class SelfAwareness:
    def __init__(self):
        self.health_score = 100
        self.last_check = datetime.now()
        self.warnings = []
        self.critical = []
    
    def check_all(self):
        """Full system health check. Returns (healthy, report)."""
        self.warnings = []
        self.critical = []
        
        # Server health
        server_ok = self._check_server()
        if not server_ok:
            self.critical.append("Server not responding")
        
        # Disk space
        disk_ok, disk_pct = self._check_disk()
        if disk_pct > 90:
            self.critical.append(f"Disk nearly full ({disk_pct}%)")
        elif disk_pct > 80:
            self.warnings.append(f"Disk getting full ({disk_pct}%)")
        
        # Battery (if Termux)
        batt_ok, batt_pct = self._check_battery()
        if batt_pct < 10:
            self.critical.append(f"Battery critical ({batt_pct}%)")
        elif batt_pct < 20:
            self.warnings.append(f"Battery low ({batt_pct}%)")
        
        # Memory
        mem_ok, mem_pct = self._check_memory()
        if mem_pct > 95:
            self.critical.append(f"Memory critical ({mem_pct}%)")
        elif mem_pct > 85:
            self.warnings.append(f"Memory high ({mem_pct}%)")
        
        # Git status
        git_ok, git_msg = self._check_git()
        if not git_ok:
            self.warnings.append(f"Git issue: {git_msg}")
        
        # State file
        state_ok = os.path.exists(STATE_FILE)
        if not state_ok:
            self.critical.append("State file missing")
        
        self.health_score = 100 - (len(self.critical) * 25) - (len(self.warnings) * 10)
        self.health_score = max(0, self.health_score)
        self.last_check = datetime.now()
        
        report = {
            "healthy": len(self.critical) == 0,
            "score": self.health_score,
            "server": server_ok,
            "disk": {"ok": disk_ok, "used_pct": disk_pct},
            "battery": {"ok": batt_ok, "pct": batt_pct},
            "memory": {"ok": mem_ok, "used_pct": mem_pct},
            "git": {"ok": git_ok, "message": git_msg},
            "state": state_ok,
            "warnings": self.warnings,
            "critical": self.critical
        }
        
        # Write health log
        with open(HEALTH_LOG, 'a') as f:
            f.write(f"[{datetime.now()}] Score: {self.health_score}, Critical: {len(self.critical)}, Warnings: {len(self.warnings)}\n")
        
        return report
    
    def _check_server(self):
        try:
            req = urllib.request.Request('http://localhost:8000/api/health', timeout=3)
            urllib.request.urlopen(req)
            return True
        except: return False
    
    def _check_disk(self):
        try:
            st = os.statvfs(REPO_DIR)
            total = st.f_blocks * st.f_frsize
            free = st.f_bavail * st.f_frsize
            used_pct = int(((total - free) / total) * 100)
            return True, used_pct
        except: return False, 0
    
    def _check_battery(self):
        try:
            r = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=5)
            if r.returncode == 0:
                data = json.loads(r.stdout)
                return True, data.get('percentage', 100)
        except: pass
        return True, 100
    
    def _check_memory(self):
        try:
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
            total = 0
            free = 0
            for line in lines:
                if 'MemTotal' in line:
                    total = int(line.split()[1])
                elif 'MemAvailable' in line or 'MemFree' in line:
                    free = int(line.split()[1])
            if total > 0:
                used_pct = int(((total - free) / total) * 100)
                return True, used_pct
        except: pass
        return True, 50
    
    def _check_git(self):
        try:
            r = subprocess.run(
                ["git", "-C", REPO_DIR, "status", "--porcelain"],
                capture_output=True, text=True, timeout=10
            )
            if r.returncode == 0:
                changes = r.stdout.strip()
                if changes:
                    return True, f"{len(changes.split(chr(10)))} uncommitted changes"
                return True, "Clean"
            return False, r.stderr.strip()
        except Exception as e:
            return False, str(e)
    
    def predict_failure(self):
        """Predict if system will fail soon."""
        report = self.check_all()
        if report['critical']:
            return True, "CRITICAL: " + ", ".join(report['critical'])
        if report['score'] < 50:
            return True, "DEGRADED: " + ", ".join(report['warnings'])
        return False, "HEALTHY"

# ═══════════════════════════════════════════════════════════════
# COMMAND PARSER — Natural Language to Actions
# ═══════════════════════════════════════════════════════════════

class CommandParser:
    def __init__(self):
        self.patterns = {
            r'\b(buy|purchase|get)\b.*\b([A-Z]{1,5})\b.*?(\d+)': 'buy',
            r'\b(sell|dump|unload)\b.*\b([A-Z]{1,5})\b.*?(\d+)': 'sell',
            r'\b(price|cost|worth)\b.*\b([A-Z]{1,5})\b': 'price',
            r'\b(portfolio|holdings|positions)\b': 'portfolio',
            r'\b(watch|track|monitor)\b.*\b([A-Z]{1,5})\b.*?(\d+(\.\d+)?)': 'watch',
            r'\b(push|save|commit|backup)\b': 'push',
            r'\b(pull|update|sync|refresh)\b': 'pull',
            r'\b(status|health|check|how are you)\b': 'status',
            r'\b(start|run|boot|launch)\b.*\b(server|app)\b': 'start',
            r'\b(stop|kill|shutdown|quit)\b.*\b(server|app)\b': 'stop',
            r'\b(heal|fix|repair|update)\b': 'heal',
            r'\b(rule|auto|trigger)\b.*\b([A-Z]{1,5})\b.*?(below|above)\b.*?(\d+(\.\d+)?)\b.*?(buy|sell)\b.*?(\d+)': 'rule',
            r'\b(rule|auto|trigger)\b.*\b([A-Z]{1,5})\b.*?(below|above)\b.*?(\d+(\.\d+)?)\b.*?(buy|sell)\b': 'rule',
            r'\b(rules|automation)\b': 'rules',
            r'\b(watches|watchlist)\b': 'watches',
            r'\b(check|scan|alert)\b': 'check',
            r'\b(state|memory|data)\b': 'state',
            r'\b(log|history|events)\b': 'log',
            r'\b(ai|ask|question)\b.*?(.*)': 'ai',
            r'\b(analyze|analysis)\b.*\b([A-Z]{1,5})\b': 'analyze',
            r'\b(restore|rebuild|recover|disaster)\b': 'restore',
            r'\b(sentiment|social|reddit)\b.*\b([A-Z]{1,5})\b': 'sentiment',
            r'\b(voice|speak|talk|say)\b': 'voice',
            r'\b(self[- ]?heal|auto[- ]?fix)\b': 'heal',
            r'\b(write|code|add|create|fix)\b.*\b(endpoint|route|api|function)\b': 'write_code',
            r'\b(deploy|ship|release)\b': 'deploy',
            r'\b(build|make|create)\b.*\b(landing|page|site|web|app|dashboard)\b': 'build',
            r'\b(deploy|ship|publish)\b.*\b(web|site|app|landing)\b': 'deploy_web',
            r'\b(help|commands|what can you do)\b': 'help',
            r'\b(memory|remember|recall|what.*know|what.*did|history of|log of)\b': 'memory',
        }
    
    def parse(self, text):
        """Parse natural language into command + args."""
        text = text.lower().strip()
        
        for pattern, cmd in self.patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                return cmd, groups
        
        return None, []

# ═══════════════════════════════════════════════════════════════
# CODE WRITER — Auto-Modify the Server
# ═══════════════════════════════════════════════════════════════

class CodeWriter:
    def __init__(self):
        self.server_file = os.path.join(REPO_DIR, 'backend', 'server_v6.3.py')
    
    def add_endpoint(self, path, method, code_block):
        """Add a new endpoint to the server."""
        try:
            with open(self.server_file, 'r') as f:
                content = f.read()
            
            # Check if endpoint already exists
            if f"@app.route('{path}')" in content:
                return False, f"Endpoint {path} already exists"
            
            # Find insertion point (before the main block)
            insert_marker = "# ═══════════════════════════════════════════════════════════════\n# MAIN"
            if insert_marker not in content:
                return False, "Could not find insertion point"
            
            new_endpoint = f"""
# ═══════════════════════════════════════════════════════════════
# AUTO-GENERATED ENDPOINT — Added {datetime.now()}
# ═══════════════════════════════════════════════════════════════

@app.route('{path}', methods={method})
def auto_endpoint_{int(time.time())}():
{code_block}

"""
            
            content = content.replace(insert_marker, new_endpoint + insert_marker)
            
            with open(self.server_file, 'w') as f:
                f.write(content)
            
            return True, f"Added endpoint {path}"
        except Exception as e:
            return False, str(e)
    
    def push_changes(self, message="Auto-generated code update"):
        """Git add, commit, push."""
        try:
            os.chdir(REPO_DIR)
            subprocess.run(["git", "add", "-A"], check=True, timeout=30)
            subprocess.run(["git", "commit", "-m", message], check=False, timeout=30)
            r = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, timeout=60)
            if r.returncode == 0:
                return True, "Pushed to GitHub"
            return False, r.stderr.strip()
        except Exception as e:
            return False, str(e)

# ═══════════════════════════════════════════════════════════════
# EXECUTOR — Run Commands
# ═══════════════════════════════════════════════════════════════

class Executor:
    def __init__(self):
        self.awareness = SelfAwareness()
        self.parser = CommandParser()
        self.writer = CodeWriter()
        self.base_url = "http://localhost:8000"
    
    def log(self, msg):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {msg}"
        print(line)
        with open(LOG_FILE, 'a') as f:
            f.write(line + "\n")
    
    def api_call(self, method, path, data=None):
        """Make API call to local server."""
        try:
            url = f"{self.base_url}{path}"
            if method == 'GET':
                req = urllib.request.Request(url, timeout=10)
            else:
                payload = json.dumps(data).encode() if data else b'{}'
                req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'}, method=method)
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read())
        except Exception as e:
            return {"error": str(e)}
    
    def execute(self, text_or_cmd, args=None):
        """Main entry point. Execute a command."""
        
        # If it's raw text, parse it
        if args is None:
            cmd, groups = self.parser.parse(text_or_cmd)
            if cmd is None:
                return {"status": "unknown", "message": "I didn't understand that. Try: buy AAPL 5, status, push, heal"}
            args = groups
        else:
            cmd = text_or_cmd
        
        self.log(f"EXECUTE: {cmd} {args}")
        
        # Pre-execution health check for dangerous commands
        if cmd in ['buy', 'sell', 'rule', 'deploy']:
            will_fail, reason = self.awareness.predict_failure()
            if will_fail:
                self.log(f"BLOCKED: {reason}")
                return {"status": "blocked", "reason": reason, "action": "System predicted failure. Command blocked for safety."}
        
        # Route to handler
        handlers = {
            'buy': self._handle_buy,
            'sell': self._handle_sell,
            'price': self._handle_price,
            'portfolio': self._handle_portfolio,
            'watch': self._handle_watch,
            'watches': self._handle_watches,
            'rule': self._handle_rule,
            'rules': self._handle_rules,
            'check': self._handle_check,
            'push': self._handle_push,
            'pull': self._handle_pull,
            'status': self._handle_status,
            'start': self._handle_start,
            'stop': self._handle_stop,
            'heal': self._handle_heal,
            'state': self._handle_state,
            'log': self._handle_log,
            'ai': self._handle_ai,
            'analyze': self._handle_analyze,
            'restore': self._handle_restore,
            'sentiment': self._handle_sentiment,
            'voice': self._handle_voice,
            'write_code': self._handle_write_code,
            'deploy': self._handle_deploy,
            'build': self._handle_build,
            'deploy_web': self._handle_deploy_web,
            'memory': self._handle_memory,
            'query': self._handle_memory,
            'help': self._handle_help,
        }
        
        handler = handlers.get(cmd, self._handle_unknown)
        return handler(args)
    
    def _handle_buy(self, args):
        symbol = args[1].upper() if len(args) > 1 else 'AAPL'
        qty = int(args[2]) if len(args) > 2 else 1
        return self.api_call('POST', '/api/trading/buy', {"symbol": symbol, "qty": qty})
    
    def _handle_sell(self, args):
        symbol = args[1].upper() if len(args) > 1 else 'AAPL'
        qty = int(args[2]) if len(args) > 2 else 1
        return self.api_call('POST', '/api/trading/sell', {"symbol": symbol, "qty": qty})
    
    def _handle_price(self, args):
        symbol = args[1].upper() if len(args) > 1 else 'AAPL'
        return self.api_call('GET', f'/api/trading/price/{symbol}')
    
    def _handle_portfolio(self, args):
        return self.api_call('GET', '/api/trading/portfolio')
    
    def _handle_watch(self, args):
        symbol = args[1].upper() if len(args) > 1 else 'AAPL'
        target = float(args[2]) if len(args) > 2 else 0
        return self.api_call('POST', '/api/watchlist', {"symbol": symbol, "target_price": target})
    
    def _handle_watches(self, args):
        return self.api_call('GET', '/api/watchlist')
    
    def _handle_rule(self, args):
        # Handle variable arg patterns
        symbol = None
        condition = None
        target = 0
        action = None
        qty = 1
        
        for arg in args:
            if isinstance(arg, str):
                if arg.upper() in ['AAPL', 'TSLA', 'NVDA', 'GOOGL', 'AMZN', 'MSFT', 'META', 'NFLX']:
                    symbol = arg.upper()
                elif arg.lower() in ['below', 'above']:
                    condition = arg.lower()
                elif arg.lower() in ['buy', 'sell']:
                    action = arg.lower()
                elif re.match(r'^\d+(\.\d+)?$', arg):
                    if target == 0:
                        target = float(arg)
                    else:
                        qty = int(float(arg))
        
        if not symbol or not condition or not action:
            return {"status": "error", "message": "Need: rule SYMBOL below/above PRICE buy/sell [QTY]"}
        
        return self.api_call('POST', '/api/rules', {
            "symbol": symbol,
            "condition": condition,
            "target_price": target,
            "action": action,
            "qty": qty
        })
    
    def _handle_rules(self, args):
        return self.api_call('GET', '/api/rules')
    
    def _handle_check(self, args):
        return self.api_call('GET', '/api/watchlist/check')
    
    def _handle_push(self, args):
        os.chdir(REPO_DIR)
        subprocess.run(["bash", "scripts/push_all.sh"])
        return {"status": "pushed"}
    
    def _handle_pull(self, args):
        os.chdir(REPO_DIR)
        r = subprocess.run(["git", "pull", "origin", "main"], capture_output=True, text=True, timeout=60)
        return {"status": "pulled", "output": r.stdout, "error": r.stderr}
    
    def _handle_status(self, args):
        report = self.awareness.check_all()
        server = self.api_call('GET', '/api/health')
        return {"self_aware": report, "server": server}
    
    def _handle_start(self, args):
        os.chdir(os.path.join(REPO_DIR, 'backend'))
        server = "server_v6.3.py"
        if not os.path.exists(server):
            server = "server_v6.2.py"
        if not os.path.exists(server):
            server = "server_v6.py"
        subprocess.Popen(["nohup", "python", server], stdout=open(os.path.expanduser('~/liljr.log'), 'a'), stderr=subprocess.STDOUT)
        time.sleep(2)
        return self.api_call('GET', '/api/health')
    
    def _handle_stop(self, args):
        subprocess.run(["pkill", "-9", "-f", "server_v6"])
        return {"status": "stopped"}
    
    def _handle_heal(self, args):
        return self.api_call('POST', '/api/self_heal')
    
    def _handle_state(self, args):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"status": "no_state"}
    
    def _handle_log(self, args):
        try:
            with open(os.path.expanduser('~/liljr.log'), 'r') as f:
                lines = f.readlines()
            return {"log": lines[-20:]}
        except:
            return {"log": []}
    
    def _handle_ai(self, args):
        msg = ' '.join(args) if args else 'Hello'
        return self.api_call('POST', '/api/chat', {"message": msg})
    
    def _handle_analyze(self, args):
        symbol = args[1].upper() if len(args) > 1 else 'AAPL'
        return self.api_call('POST', '/api/ai/analyze', {"symbol": symbol})
    
    def _handle_restore(self, args):
        r = subprocess.run(["bash", os.path.join(REPO_DIR, "scripts", "restore.sh")], capture_output=True, text=True, timeout=120)
        return {"status": "restored", "output": r.stdout}
    
    def _handle_sentiment(self, args):
        symbol = args[1].upper() if len(args) > 1 else 'AAPL'
        return self.api_call('GET', f'/api/sentiment/{symbol}')
    
    def _handle_voice(self, args):
        try:
            r = subprocess.run(["termux-speech-to-text", "-l", "en-US"], capture_output=True, text=True, timeout=15)
            if r.returncode == 0:
                text = r.stdout.strip()
                # Auto-execute the transcribed command
                return self.execute(text)
            return {"status": "voice_failed", "error": r.stderr}
        except Exception as e:
            return {"status": "voice_error", "error": str(e)}
    
    def _handle_build(self, args):
        """Build a web app."""
        text = ' '.join(args) if args else 'landing page'
        os.chdir(REPO_DIR)
        r = subprocess.run(
            ['python3', 'web_builder.py', text],
            capture_output=True, text=True, timeout=60
        )
        try:
            return json.loads(r.stdout)
        except:
            return {"status": "build_error", "stdout": r.stdout, "stderr": r.stderr}
    
    def _handle_deploy_web(self, args):
        """Deploy web app."""
        text = ' '.join(args) if args else 'deploy to github pages'
        os.chdir(REPO_DIR)
        r = subprocess.run(
            ['python3', 'web_builder.py', text],
            capture_output=True, text=True, timeout=120
        )
        try:
            return json.loads(r.stdout)
        except:
            return {"status": "deploy_error", "stdout": r.stdout, "stderr": r.stderr}
    
    def _handle_write_code(self, args):
        # This is a placeholder for the full auto-coding feature
        return {"status": "write_code", "message": "Code writing requires human review. Use: write endpoint /api/custom def custom(): pass"}
    
    def _handle_deploy(self, args):
        # Pre-deploy health check
        will_fail, reason = self.awareness.predict_failure()
        if will_fail:
            return {"status": "blocked", "reason": f"Deploy blocked: {reason}"}
        
        # Pull latest, push current, restart
        self._handle_pull(args)
        self._handle_push(args)
        self._handle_stop(args)
        time.sleep(2)
        return self._handle_start(args)
    
    def _handle_memory(self, args):
        """Query the memory engine."""
        action = 'query'
        if args:
            text = ' '.join(args).lower()
            if 'analyze' in text or 'pattern' in text:
                action = 'analyze'
            elif 'stats' in text or 'status' in text:
                action = 'stats'
            elif 'suggest' in text:
                action = 'suggest'
        
        os.chdir(REPO_DIR)
        r = subprocess.run(
            ['python3', 'memory_engine.py', action] + (args if args else []),
            capture_output=True, text=True, timeout=30
        )
        return {
            "status": "memory_result",
            "action": action,
            "output": r.stdout,
            "stderr": r.stderr if r.stderr else None
        }
    
    def _handle_help(self, args):
        return {
            "commands": [
                "buy SYMBOL QTY", "sell SYMBOL QTY", "price SYMBOL",
                "portfolio", "watch SYMBOL PRICE", "watches",
                "rule SYMBOL below/above PRICE buy/sell [QTY]", "rules", "check",
                "push", "pull", "status", "start", "stop", "heal",
                "state", "log", "ai MESSAGE", "analyze SYMBOL",
                "sentiment SYMBOL", "voice", "deploy", "build", "deploy-web",
                "memory query", "memory analyze", "memory stats", "memory suggest",
                "help"
            ]
        }
    
    def _handle_unknown(self, args):
        return {"status": "unknown", "message": "Command not implemented"}

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    executor = Executor()
    
    if len(sys.argv) < 2:
        print("LilJR Command Center v1.0")
        print("Usage: python command_center.py '<command>'")
        print("Examples:")
        print('  python command_center.py "buy AAPL 5"')
        print('  python command_center.py "status"')
        print('  python command_center.py "deploy"')
        sys.exit(1)
    
    input_text = ' '.join(sys.argv[1:])
    result = executor.execute(input_text)
    print(json.dumps(result, indent=2))
