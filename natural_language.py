#!/usr/bin/env python3
"""
LILJR NATURAL LANGUAGE COMMANDER
Talk to LilJR like you talk to me. It understands, builds, fixes, creates.
"""
import re, json, os, sys

class NaturalCommander:
    """
    Parses natural language and routes to the right engine.
    """
    
    def __init__(self, engine=None):
        self.engine = engine
        self.history = []
    
    def parse(self, text):
        """
        Main entry: take a sentence, figure out what to do.
        Returns: {action, params, response}
        """
        text_lower = text.lower().strip()
        self.history.append(text)
        
        # ═══ BUILD / CREATE ═══
        if any(w in text_lower for w in ['build', 'create', 'make', 'generate']):
            return self._handle_build(text, text_lower)
        
        # ═══ FIX / IMPROVE ═══
        if any(w in text_lower for w in ['fix', 'repair', 'improve', 'upgrade', 'optimize']):
            return self._handle_fix(text, text_lower)
        
        # ═══ MODIFY / CHANGE ═══
        if any(w in text_lower for w in ['change', 'modify', 'update', 'restyle', 'redesign']):
            return self._handle_modify(text, text_lower)
        
        # ═══ SEARCH / RESEARCH ═══
        if any(w in text_lower for w in ['search', 'find', 'research', 'look up', 'google']):
            return self._handle_search(text, text_lower)
        
        # ═══ TRADE / BUY / SELL ═══
        if any(w in text_lower for w in ['buy', 'sell', 'trade', 'purchase']):
            return self._handle_trade(text, text_lower)
        
        # ═══ DEPLOY / PUSH ═══
        if any(w in text_lower for w in ['deploy', 'push', 'publish', 'upload', 'host']):
            return self._handle_deploy(text, text_lower)
        
        # ═══ ANALYZE / SCAN ═══
        if any(w in text_lower for w in ['analyze', 'scan', 'check', 'audit', 'review']):
            return self._handle_analyze(text, text_lower)
        
        # ═══ CHAT / GENERAL ═══
        return self._handle_chat(text, text_lower)
    
    def _handle_build(self, text, text_lower):
        """Build websites, apps, modules, landing pages."""
        
        # Extract name
        name = self._extract_quoted(text) or self._extract_name(text_lower) or "Project"
        
        # Extract tagline/description
        tagline = self._extract_after(text_lower, ['for', 'called', 'named', 'about']) or "Built by LilJR"
        
        # Detect type
        if any(w in text_lower for w in ['landing page', 'landing', 'homepage']):
            return {
                "action": "build_landing",
                "params": {"name": name, "tagline": tagline},
                "intent": f"Building landing page: {name}"
            }
        
        elif any(w in text_lower for w in ['web app', 'app', 'dashboard', 'tool']):
            theme = self._extract_theme(text_lower)
            return {
                "action": "build_web_app",
                "params": {"name": name, "theme": theme},
                "intent": f"Building web app: {name}"
            }
        
        elif any(w in text_lower for w in ['business site', 'website', 'site', 'corporate']):
            theme = self._extract_theme(text_lower)
            return {
                "action": "build_business_site",
                "params": {"name": name, "tagline": tagline, "theme": theme},
                "intent": f"Building business site: {name}"
            }
        
        elif any(w in text_lower for w in ['python', 'module', 'script', 'code', 'function']):
            purpose = tagline
            return {
                "action": "generate_code",
                "params": {"purpose": purpose, "name": name},
                "intent": f"Generating Python module: {name}"
            }
        
        elif any(w in text_lower for w in ['marketing', 'ad', 'copy', 'headline', 'social post']):
            product = name
            return {
                "action": "generate_marketing",
                "params": {"product": product, "type": "launch"},
                "intent": f"Generating marketing copy for: {product}"
            }
        
        else:
            # Default: business site
            theme = self._extract_theme(text_lower)
            return {
                "action": "build_business_site",
                "params": {"name": name, "tagline": tagline, "theme": theme},
                "intent": f"Building site: {name}"
            }
    
    def _handle_fix(self, text, text_lower):
        """Fix code, errors, issues."""
        if any(w in text_lower for w in ['my app', 'my code', 'project', 'files']):
            return {
                "action": "self_improve",
                "params": {},
                "intent": "Auto-fixing all issues in codebase"
            }
        elif any(w in text_lower for w in ['server', 'api', 'endpoint']):
            return {
                "action": "self_improve",
                "params": {"target": "server"},
                "intent": "Fixing server issues"
            }
        else:
            return {
                "action": "self_improve",
                "params": {},
                "intent": "Auto-fixing system"
            }
    
    def _handle_modify(self, text, text_lower):
        """Change existing things."""
        # Extract page name
        page = self._extract_quoted(text) or self._extract_name(text_lower) or "index"
        
        # Extract theme
        theme = self._extract_theme(text_lower)
        
        # Extract instruction
        instruction = self._extract_after(text_lower, ['to', 'with', 'by', 'and'])
        
        if theme and not instruction:
            return {
                "action": "restyle",
                "params": {"page": page, "theme": theme},
                "intent": f"Restyling {page} with {theme} theme"
            }
        elif instruction:
            return {
                "action": "modify_page",
                "params": {"page": page, "instruction": instruction},
                "intent": f"Modifying {page}: {instruction}"
            }
        else:
            return {
                "action": "modify_page",
                "params": {"page": page, "instruction": text},
                "intent": f"Modifying {page}"
            }
    
    def _handle_search(self, text, text_lower):
        """Deep search the web."""
        # Remove search keywords to get the query
        query = text
        for kw in ['search', 'find', 'research', 'look up', 'google']:
            query = query.lower().replace(kw, '').strip()
        # Clean up
        query = query.replace('for', '').replace('about', '').strip()
        query = query.strip('"').strip("'")
        
        return {
            "action": "deep_search",
            "params": {"query": query, "depth": 2},
            "intent": f"Deep searching: {query}"
        }
    
    def _handle_trade(self, text, text_lower):
        """Buy or sell stocks."""
        # Extract symbol
        symbols = re.findall(r'\b[A-Z]{1,5}\b', text)
        symbol = symbols[0] if symbols else 'AAPL'
        
        # Extract quantity
        qty_match = re.search(r'\b(\d+)\b', text)
        qty = int(qty_match.group(1)) if qty_match else 1
        
        if 'sell' in text_lower:
            return {
                "action": "sell",
                "params": {"symbol": symbol, "qty": qty},
                "intent": f"Selling {qty} shares of {symbol}"
            }
        else:
            return {
                "action": "buy",
                "params": {"symbol": symbol, "qty": qty},
                "intent": f"Buying {qty} shares of {symbol}"
            }
    
    def _handle_deploy(self, text, text_lower):
        """Deploy to GitHub or web."""
        repo = self._extract_quoted(text) or "user/repo"
        return {
            "action": "deploy",
            "params": {"repo": repo},
            "intent": f"Deploying to {repo}"
        }
    
    def _handle_analyze(self, text, text_lower):
        """Analyze code or project."""
        return {
            "action": "coder_analyze",
            "params": {},
            "intent": "Analyzing entire codebase"
        }
    
    def _handle_chat(self, text, text_lower):
        """General chat — try to figure out what they want."""
        # Try to detect implicit intents
        if any(w in text_lower for w in ['website', 'page', 'site', 'html']):
            return self._handle_build(text, text_lower)
        elif any(w in text_lower for w in ['stock', 'price', 'market', 'portfolio']):
            return {
                "action": "portfolio",
                "params": {},
                "intent": "Showing portfolio"
            }
        elif any(w in text_lower for w in ['theme', 'color', 'dark', 'light', 'style']):
            return self._handle_modify(text, text_lower)
        else:
            # Fallback: treat as a build request with the whole text as description
            return {
                "action": "build_business_site",
                "params": {
                    "name": "Project",
                    "tagline": text,
                    "theme": self._extract_theme(text_lower) or "dark_empire"
                },
                "intent": f"Building from description: {text[:50]}..."
            }
    
    # ═══ HELPERS ═══
    
    def _extract_quoted(self, text):
        """Extract text inside quotes."""
        match = re.search(r'["\']([^"\']+)["\']', text)
        return match.group(1) if match else None
    
    def _extract_name(self, text_lower):
        """Extract a name after keywords like 'called', 'named', 'for'."""
        patterns = [
            r'(?:called|named)\s+([a-z0-9_\s]+?)(?:\s+(?:that|with|for|about|and)\s|$)',
            r'for\s+([a-z0-9_\s]+?)(?:\s+(?:that|with|about|and)\s|$)',
            r'(?:make|build|create)\s+(?:a|an)?\s*([a-z]+)\s+([a-z0-9_]+)',
        ]
        for pat in patterns:
            match = re.search(pat, text_lower)
            if match:
                return match.group(1).strip().title()
        return None
    
    def _extract_theme(self, text_lower):
        """Extract theme name."""
        themes = ['dark_empire', 'light_pro', 'cyberpunk', 'nature', 'minimalist', 'corporate']
        for t in themes:
            if t in text_lower:
                return t
        # Partial matches
        if 'dark' in text_lower:
            return 'dark_empire'
        elif 'light' in text_lower:
            return 'light_pro'
        elif 'cyber' in text_lower or 'neon' in text_lower:
            return 'cyberpunk'
        elif 'green' in text_lower or 'nature' in text_lower:
            return 'nature'
        elif 'minimal' in text_lower or 'clean' in text_lower:
            return 'minimalist'
        elif 'corporate' in text_lower or 'business' in text_lower:
            return 'corporate'
        return 'dark_empire'
    
    def _extract_after(self, text_lower, keywords):
        """Extract text after certain keywords."""
        for kw in keywords:
            if kw in text_lower:
                idx = text_lower.find(kw) + len(kw)
                return text_lower[idx:].strip()[:100]
        return None
    
    def execute(self, text, base_url="http://localhost:8000"):
        """
        Parse + execute. Returns full result.
        """
        import urllib.request
        
        parsed = self.parse(text)
        action = parsed["action"]
        params = parsed["params"]
        
        def api_post(path, data):
            payload = json.dumps(data).encode()
            req = urllib.request.Request(
                f"{base_url}{path}",
                data=payload,
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        
        def api_get(path):
            req = urllib.request.Request(f"{base_url}{path}")
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        
        result = {"intent": parsed["intent"], "action": action}
        
        try:
            if action == "build_landing":
                result["output"] = api_post("/api/coder/landing", params)
            
            elif action == "build_web_app":
                result["output"] = api_post("/api/web/app", params)
            
            elif action == "build_business_site":
                result["output"] = api_post("/api/web/build", params)
            
            elif action == "generate_code":
                result["output"] = api_post("/api/coder/generate", {
                    "purpose": params.get("purpose", "utility"),
                    "functions": [["run", "Main function", [], ["pass"]]]
                })
            
            elif action == "generate_marketing":
                result["output"] = api_post("/api/marketing/copy", {
                    "product": params.get("product", "LilJR"),
                    "type": params.get("type", "launch"),
                    "count": 3
                })
            
            elif action == "restyle":
                result["output"] = api_post("/api/web/restyle", params)
            
            elif action == "modify_page":
                result["output"] = api_post("/api/web/modify", params)
            
            elif action == "deep_search":
                result["output"] = api_post("/api/search/deep", params)
            
            elif action == "buy":
                result["output"] = api_post("/api/trading/buy", params)
            
            elif action == "sell":
                result["output"] = api_post("/api/trading/sell", params)
            
            elif action == "deploy":
                result["output"] = api_post("/api/web/deploy", params)
            
            elif action == "self_improve":
                result["output"] = api_post("/api/self/improve", {})
            
            elif action == "coder_analyze":
                result["output"] = api_get("/api/coder/analyze")
            
            elif action == "portfolio":
                result["output"] = api_get("/api/trading/portfolio")
            
            else:
                result["output"] = {"status": "unknown_action", "action": action}
        
        except Exception as e:
            result["error"] = str(e)
        
        return result


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("LILJR NATURAL LANGUAGE COMMANDER")
        print("Usage: python3 natural_language.py 'your command here'")
        print("")
        print("Examples:")
        print('  python3 natural_language.py "build a landing page for my fitness app"')
        print('  python3 natural_language.py "make it dark theme"')
        print('  python3 natural_language.py "fix my code"')
        print('  python3 natural_language.py "search AI trends"')
        print('  python3 natural_language.py "buy 5 shares of AAPL"')
        print('  python3 natural_language.py "deploy to myrepo/site"')
        return
    
    text = ' '.join(sys.argv[1:])
    cmdr = NaturalCommander()
    
    print(f"🧠 You said: \"{text}\"")
    print("")
    
    # Show parsed intent
    parsed = cmdr.parse(text)
    print(f"🎯 Intent: {parsed['intent']}")
    print(f"🔧 Action: {parsed['action']}")
    print("")
    
    # Execute
    print("⚡ Executing...")
    result = cmdr.execute(text)
    
    print("")
    print("═" * 50)
    print("RESULT:")
    print(json.dumps(result, indent=2, default=str))


if __name__ == '__main__':
    main()
