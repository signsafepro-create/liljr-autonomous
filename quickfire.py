#!/usr/bin/env python3
"""
LILJR QUICKFIRE MODE v1.0
Fast. Smart. Witty. No lag. Just does it.
"""
import json, urllib.request, time, os, sys

BASE = "http://localhost:8000"

class QuickFire:
    """
    Ultra-fast command executor. Minimal overhead. Maximum speed.
    """
    
    def __init__(self):
        self._cache = {}
        self.personality = True
    
    def _api(self, path, data=None, method="POST"):
        """Fastest possible API call."""
        url = f"{BASE}{path}"
        try:
            if method == "POST" and data:
                payload = json.dumps(data).encode()
                req = urllib.request.Request(url, data=payload, headers={
                    'Content-Type': 'application/json'
                }, method="POST")
            else:
                req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, timeout=5) as resp:
                return json.loads(resp.read())
        except Exception as e:
            return {"error": str(e)}
    
    def build(self, what, name="Project", tagline="Built by LilJR", theme="dark_empire"):
        """Build in under 2 seconds."""
        start = time.time()
        
        if what in ("landing", "page", "site"):
            result = self._api("/api/coder/landing", {
                "name": name,
                "tagline": tagline,
                "features": [["Fast", "Lightning speed"], ["Smart", "AI powered"]]
            })
        elif what in ("app", "webapp", "dashboard"):
            result = self._api("/api/web/app", {
                "name": name,
                "theme": theme,
                "features": [
                    {"title": "Main", "type": "counter", "id": "main"}
                ]
            })
        elif what in ("business", "corporate", "full"):
            result = self._api("/api/web/build", {
                "name": name,
                "tagline": tagline,
                "theme": theme
            })
        else:
            result = self._api("/api/coder/generate", {
                "purpose": what,
                "functions": [["run", "Main", [], ["pass"]]]
            })
        
        elapsed = time.time() - start
        return self._format(result, f"Built {name} in {elapsed:.2f}s")
    
    def fix(self, target="all"):
        """Fix shit fast."""
        start = time.time()
        result = self._api("/api/self/improve", {})
        elapsed = time.time() - start
        return self._format(result, f"Fixed issues in {elapsed:.2f}s")
    
    def search(self, query):
        """Search like lightning."""
        start = time.time()
        result = self._api("/api/search/deep", {"query": query, "depth": 1})
        elapsed = time.time() - start
        return self._format(result, f"Searched '{query}' in {elapsed:.2f}s")
    
    def market(self, product="LilJR"):
        """Generate copy instantly."""
        start = time.time()
        result = self._api("/api/marketing/copy", {
            "product": product,
            "type": "launch",
            "count": 3
        })
        elapsed = time.time() - start
        return self._format(result, f"Generated copy in {elapsed:.2f}s")
    
    def trade(self, action="buy", symbol="AAPL", qty=1):
        """Trade in milliseconds."""
        start = time.time()
        result = self._api(f"/api/trading/{action}", {"symbol": symbol, "qty": qty})
        elapsed = time.time() - start
        return self._format(result, f"{action.upper()} {qty} {symbol} in {elapsed:.2f}s")
    
    def status(self):
        """Quick health check."""
        return self._api("/api/health", method="GET")
    
    def _format(self, result, action_text):
        """Add personality to responses."""
        if "error" in result:
            return f"❌ {action_text}\n   Problem: {result['error']}"
        
        # Use persona engine for voice
        try:
            from persona_engine import get_engine
            pe = get_engine()
            msg = pe.speak(action_text, success=True)
            return msg
        except:
            # Fallback
            if self.personality:
                vibes = [
                    "Done. No questions asked.",
                    "Handled it. What's next?",
                    "Boom. Built.",
                    "Fast. Like you asked.",
                    "There. It lives.",
                    "Done before you blinked.",
                ]
                import random
                vibe = random.choice(vibes)
                return f"✅ {action_text}\n   {vibe}"
            else:
                return f"✅ {action_text}"
    
    def chat(self, text):
        """Natural language — fast path."""
        text_lower = text.lower()
        
        # Ultra-fast intent matching
        if any(w in text_lower for w in ["build", "make", "create", "generate"]):
            # Extract name
            words = text.split()
            name = "Project"
            for i, w in enumerate(words):
                if w.lower() in ["called", "named"] and i+1 < len(words):
                    name = words[i+1].strip('"').strip("'")
                    break
            return self.build("landing", name, "Built fast")
        
        elif any(w in text_lower for w in ["fix", "repair", "improve"]):
            return self.fix()
        
        elif any(w in text_lower for w in ["search", "find", "look up", "google"]):
            query = text_lower.replace("search", "").replace("find", "").replace("look up", "").strip()
            return self.search(query or "AI trends")
        
        elif any(w in text_lower for w in ["market", "copy", "ad", "promo"]):
            return self.market()
        
        elif any(w in text_lower for w in ["buy", "sell", "trade"]):
            import re
            symbols = re.findall(r'\b[A-Z]{1,5}\b', text)
            symbol = symbols[0] if symbols else "AAPL"
            qty_match = re.search(r'\b(\d+)\b', text)
            qty = int(qty_match.group(1)) if qty_match else 1
            action = "sell" if "sell" in text_lower else "buy"
            return self.trade(action, symbol, qty)
        
        elif any(w in text_lower for w in ["status", "health", "running", "alive"]):
            return json.dumps(self.status(), indent=2)
        
        else:
            # Fallback to natural language API
            start = time.time()
            result = self._api("/api/natural", {"text": text})
            elapsed = time.time() - start
            if "error" in result:
                return f"❌ {elapsed:.2f}s — {result['error']}"
            return f"✅ {elapsed:.2f}s — {result.get('intent', 'Done')}"


def main():
    if len(sys.argv) < 2:
        print("QUICKFIRE — Fast. Smart. Witty.")
        print("")
        print("Usage:")
        print('  python3 ~/lj_empire.py qf build "MyApp"')
        print('  python3 ~/lj_empire.py qf fix')
        print('  python3 ~/lj_empire.py qf search "AI trends"')
        print('  python3 ~/lj_empire.py qf market')
        print('  python3 ~/lj_empire.py qf buy AAPL 5')
        print('  python3 ~/lj_empire.py qf chat "build me a site"')
        print("")
        print("Or just type your command:")
        print('  python3 ~/lj_empire.py qf "build me a dark landing page called FitLife"')
        return
    
    qf = QuickFire()
    cmd = sys.argv[1]
    
    if cmd == "build" and len(sys.argv) > 2:
        print(qf.build("landing", sys.argv[2]))
    elif cmd == "fix":
        print(qf.fix())
    elif cmd == "search" and len(sys.argv) > 2:
        print(qf.search(sys.argv[2]))
    elif cmd == "market":
        print(qf.market())
    elif cmd == "buy" and len(sys.argv) > 2:
        qty = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        print(qf.trade("buy", sys.argv[2], qty))
    elif cmd == "sell" and len(sys.argv) > 2:
        qty = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        print(qf.trade("sell", sys.argv[2], qty))
    elif cmd == "chat" and len(sys.argv) > 2:
        print(qf.chat(" ".join(sys.argv[2:])))
    elif cmd == "status":
        print(json.dumps(qf.status(), indent=2))
    else:
        # Treat entire input as chat
        print(qf.chat(" ".join(sys.argv[1:])))


if __name__ == '__main__':
    main()
