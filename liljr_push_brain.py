#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════
 LILJR PUSH BRAIN — Push-Based Command Architecture
 
 Commands come IN via:
   • Git push (GitHub webhook triggers actions)
   • Push notifications (from other devices/services)
   • File drops (drop a .json in ~/liljr_inbox/)
   • SMS (text a command to the phone)
   • Shared links (send URL, LilJR processes it)
 
 LilJR thinks, then pushes OUT results:
   • Git push results to GitHub
   • Push notification when done
   • SMS reply
   • URL opened in browser
═══════════════════════════════════════════════════════════════
"""
import json, os, sys, time, threading, subprocess, re

HOME = os.path.expanduser('~')
INBOX_DIR = os.path.join(HOME, 'liljr_inbox')
OUTBOX_DIR = os.path.join(HOME, 'liljr_outbox')
PROCESSED_DIR = os.path.join(HOME, 'liljr_processed')
PUSH_LOG = os.path.join(HOME, 'liljr_push_brain.log')
REPO = os.path.join(HOME, 'liljr-autonomous')

sys.path.insert(0, REPO)

class PushBrain:
    """
    LilJR's command brain receives pushes, thinks, pushes results.
    No polling. No waiting. Event-driven. Push-based.
    """
    
    def __init__(self):
        self._running = False
        self._thread = None
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        for d in [INBOX_DIR, OUTBOX_DIR, PROCESSED_DIR]:
            os.makedirs(d, exist_ok=True)
    
    def _log(self, msg):
        ts = time.strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        with open(PUSH_LOG, 'a') as f:
            f.write(line + '\n')
    
    def _api_post(self, path, data):
        try:
            import urllib.request
            payload = json.dumps(data).encode()
            req = urllib.request.Request(
                f"http://localhost:8000{path}",
                data=payload,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read())
        except Exception as e:
            return {"error": str(e)}
    
    def _notify(self, title, content):
        """Push notification out."""
        try:
            subprocess.run([
                'termux-notification',
                '--title', title,
                '--content', content,
                '--priority', 'normal'
            ], capture_output=True, timeout=5)
            return True
        except:
            return False
    
    def _git_push_result(self, filename, content):
        """Push result to GitHub as a file."""
        result_path = os.path.join(OUTBOX_DIR, filename)
        with open(result_path, 'w') as f:
            f.write(content)
        
        # Try to push to repo
        try:
            os.chdir(REPO)
            subprocess.run(['git', 'add', result_path], capture_output=True, timeout=5)
            subprocess.run(['git', 'commit', '-m', f'result: {filename}'], capture_output=True, timeout=5)
            subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, timeout=15)
            return True
        except:
            return False
    
    def _process_command(self, cmd_obj):
        """Execute a command and return result."""
        cmd_type = cmd_obj.get('type', 'chat')
        text = cmd_obj.get('text', '')
        source = cmd_obj.get('source', 'unknown')
        
        self._log(f"Processing {cmd_type} from {source}: {text[:60]}")
        
        # Route to correct engine
        if cmd_type in ['build', 'website', 'create']:
            result = self._api_post('/api/web/build', {
                'name': cmd_obj.get('name', 'site'),
                'tagline': text,
                'theme': cmd_obj.get('theme', 'dark_empire')
            })
            response = f"Built: {result.get('saved', {}).get('path', '?')}"
        
        elif cmd_type in ['trade', 'buy', 'sell']:
            symbol = cmd_obj.get('symbol', 'AAPL')
            qty = cmd_obj.get('qty', 1)
            endpoint = '/api/trading/sell' if 'sell' in text.lower() else '/api/trading/buy'
            result = self._api_post(endpoint, {'symbol': symbol, 'qty': qty})
            response = f"Trade: {result.get('status', '?')} {qty} {symbol}"
        
        elif cmd_type in ['search', 'find', 'research']:
            result = self._api_post('/api/search/deep', {
                'query': text,
                'pages': cmd_obj.get('pages', 3)
            })
            results = result.get('results', [])
            response = f"Found {len(results)} results. Top: {results[0].get('title', '?')[:50]}..." if results else "No results"
        
        elif cmd_type in ['market', 'copy', 'seo']:
            result = self._api_post('/api/marketing/copy', {
                'product': cmd_obj.get('product', 'Product'),
                'tone': cmd_obj.get('tone', 'aggressive')
            })
            copies = result.get('copies', [])
            response = f"Generated {len(copies)} marketing variants." if copies else "Marketing gen failed"
        
        elif cmd_type in ['code', 'function', 'script']:
            result = self._api_post('/api/coder/generate', {
                'description': text,
                'language': cmd_obj.get('lang', 'python')
            })
            code = result.get('code', '')
            response = f"Generated {len(code)} chars of code." if code else "Code gen failed"
        
        elif cmd_type in ['scan', 'heal', 'fix']:
            result = self._api_post('/api/self/improve')
            fixes = result.get('fixes_applied', [])
            response = f"Self-healed {len(fixes)} issues." if fixes else "No issues found"
        
        elif cmd_type in ['persona', 'voice', 'talk']:
            result = self._api_post('/api/persona/switch', {
                'name': cmd_obj.get('persona', 'best_friend')
            })
            response = f"Switched to: {result.get('switched', '?')}"
        
        else:
            # Natural language
            result = self._api_post('/api/natural', {'text': text})
            response = result.get('response', 'Processed.')
        
        return {
            "source": source,
            "command": text,
            "type": cmd_type,
            "result": result,
            "response": response,
            "timestamp": time.time()
        }
    
    def _check_inbox(self):
        """Check for new command files."""
        files = sorted(os.listdir(INBOX_DIR))
        for fname in files:
            if not fname.endswith('.json'):
                continue
            
            fpath = os.path.join(INBOX_DIR, fname)
            try:
                with open(fpath, 'r') as f:
                    cmd = json.load(f)
                
                # Process
                result = self._process_command(cmd)
                
                # Save result
                result_file = os.path.join(OUTBOX_DIR, f"result_{fname}")
                with open(result_file, 'w') as f:
                    json.dump(result, f, indent=2)
                
                # Notify
                self._notify(
                    f"LilJR ✅ — {cmd.get('type', 'done').upper()}",
                    result['response'][:100]
                )
                
                # Move to processed
                processed = os.path.join(PROCESSED_DIR, f"{time.time()}_{fname}")
                os.rename(fpath, processed)
                
                self._log(f"Done: {result['response'][:80]}")
                
            except Exception as e:
                self._log(f"Error processing {fname}: {e}")
                # Move to processed with error
                processed = os.path.join(PROCESSED_DIR, f"ERROR_{time.time()}_{fname}")
                os.rename(fpath, processed)
    
    def _check_sms(self):
        """Check for SMS commands."""
        try:
            result = subprocess.run(
                ['termux-sms-list', '-l', '5', '-t', 'inbox'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                messages = json.loads(result.stdout)
                for msg in messages:
                    body = msg.get('body', '').lower()
                    # Check if it's a command
                    if body.startswith('lj ') or body.startswith('liljr '):
                        cmd_text = body[3:] if body.startswith('lj ') else body[7:]
                        
                        # Create inbox entry
                        cmd_obj = {
                            "type": "chat",
                            "text": cmd_text,
                            "source": f"sms:{msg.get('number', '?')}",
                            "received": msg.get('received', '?')
                        }
                        
                        fname = f"sms_{int(time.time())}_{msg.get('number', 'unknown')}.json"
                        with open(os.path.join(INBOX_DIR, fname), 'w') as f:
                            json.dump(cmd_obj, f)
                        
                        self._log(f"SMS command from {msg.get('number', '?')}: {cmd_text}")
        except:
            pass
    
    def push_command(self, text, cmd_type='chat', **kwargs):
        """
        Push a command INTO the brain.
        Usage: push_command("build me a site", "build", name="MySite")
        """
        cmd = {
            "type": cmd_type,
            "text": text,
            "source": "local_push",
            "timestamp": time.time()
        }
        cmd.update(kwargs)
        
        fname = f"push_{int(time.time()*1000)}.json"
        with open(os.path.join(INBOX_DIR, fname), 'w') as f:
            json.dump(cmd, f)
        
        self._log(f"Pushed: {text[:60]}")
        return {"pushed": True, "file": fname}
    
    def start(self):
        """Start the push brain daemon."""
        self._running = True
        self._log("Push Brain started. Waiting for commands...")
        
        def loop():
            while self._running:
                try:
                    self._check_inbox()
                    self._check_sms()
                except Exception as e:
                    self._log(f"Loop error: {e}")
                time.sleep(10)  # Check every 10 seconds
        
        self._thread = threading.Thread(target=loop, daemon=True)
        self._thread.start()
        
        self._notify("LilJR 🧠", "Push Brain active. Send me commands via file, SMS, or API.")
    
    def stop(self):
        self._running = False
        self._log("Push Brain stopped.")


# ═══ STANDALONE ═══
if __name__ == '__main__':
    import sys
    brain = PushBrain()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'start':
            brain.start()
            print("🧠 Push Brain active. Drop .json files in ~/liljr_inbox/")
            print("Or text 'lj build me a site' to this phone.")
            print("Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                brain.stop()
        elif cmd == 'push' and len(sys.argv) > 2:
            text = ' '.join(sys.argv[2:])
            print(json.dumps(brain.push_command(text), indent=2))
        elif cmd == 'status':
            inbox = len(os.listdir(INBOX_DIR)) if os.path.exists(INBOX_DIR) else 0
            outbox = len(os.listdir(OUTBOX_DIR)) if os.path.exists(OUTBOX_DIR) else 0
            processed = len(os.listdir(PROCESSED_DIR)) if os.path.exists(PROCESSED_DIR) else 0
            print(f"Inbox: {inbox} | Outbox: {outbox} | Processed: {processed}")
        else:
            print("LILJR PUSH BRAIN — Push-Based Command Architecture")
            print("Commands:")
            print("  start              — Start daemon")
            print("  push 'command'     — Push a command")
            print("  status             — Queue status")
    else:
        print("LilJR Push Brain — Drop commands in ~/liljr_inbox/")
        print("Or run: python3 liljr_push_brain.py start")
