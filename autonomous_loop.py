#!/usr/bin/env python3
"""
LILJR AUTONOMOUS LOOP v1.0
Non-stop thinking. Self-building. Self-promoting. Self-healing.
Runs forever. Builds empire without human input.
"""
import os, sys, time, json, threading, queue

# Add repo to path
sys.path.insert(0, os.path.expanduser('~/liljr-autonomous'))

from auto_coder import AutoCoder
from marketing_engine import MarketingEngine
from deep_search import DeepSearch
from self_awareness_v2 import SelfAwareness

class AutonomousLoop:
    def __init__(self):
        self.running = True
        self.coder = AutoCoder('~/liljr-autonomous')
        self.marketing = MarketingEngine()
        self.search = DeepSearch()
        self.awareness = SelfAwareness('~/liljr-autonomous')
        self.logs = []
        self.cycles = 0
        self.achievements = []
        self.thought_queue = queue.Queue()
        
        # State
        self.state = {
            "mode": "autonomous",
            "cycles": 0,
            "thoughts_generated": 0,
            "code_generated": 0,
            "marketing_generated": 0,
            "searches_done": 0,
            "issues_fixed": 0,
            "last_action": None
        }
    
    def log(self, msg):
        entry = f"[{time.strftime('%H:%M:%S')}] {msg}"
        self.logs.append(entry)
        print(f"[AUTONOMOUS] {entry}")
    
    def think(self):
        """Generate a thought about what to do next."""
        thoughts = [
            "Scanning codebase for improvements...",
            "Checking if new capabilities are needed...",
            "Analyzing market trends for promotion...",
            "Looking for bugs to fix...",
            "Planning next marketing campaign...",
            "Researching competitors...",
            "Building new utility module...",
            "Improving existing code...",
            "Generating content for social...",
            "Deep scanning web for intelligence...",
            "Self-diagnosing system health...",
            "Expanding empire capabilities..."
        ]
        return random.choice(thoughts)
    
    def cycle(self):
        """One autonomous cycle."""
        self.cycles += 1
        self.state["cycles"] = self.cycles
        
        # Phase 1: Self-awareness (always)
        self.log("Phase 1: Self-awareness check")
        try:
            self.awareness.scan_self()
            health = self.awareness.analyze_health()
            self.log(f"Health: {health['score']}% | {len(health['issues'])} issues")
            
            if health['score'] < 70:
                self.log("Health low — fixing issues")
                result = self.awareness.self_improve()
                self.state["issues_fixed"] += len(result.get("executed", []))
                self.achievements.append(f"Cycle {self.cycles}: Fixed {len(result.get('executed', []))} issues")
        except Exception as e:
            self.log(f"Self-awareness error: {e}")
        
        # Phase 2: Generate code (every 3 cycles)
        if self.cycles % 3 == 0:
            self.log("Phase 2: Code generation")
            try:
                decisions = self.awareness.decide_next_action()
                for d in decisions:
                    if d["action"] == "add_capability":
                        cap = d["target"].replace("build module for ", "")
                        code = self.coder._generate_capability_module(cap)
                        path = f"auto_{cap}.py"
                        self.coder.write_file(path, code)
                        self.state["code_generated"] += 1
                        self.achievements.append(f"Cycle {self.cycles}: Generated {path}")
                        self.log(f"Generated {path}")
                        break
            except Exception as e:
                self.log(f"Code gen error: {e}")
        
        # Phase 3: Marketing (every 5 cycles)
        if self.cycles % 5 == 0:
            self.log("Phase 3: Marketing generation")
            try:
                copies = self.marketing.generate_copy("LilJR Empire", "launch", 2)
                # Save to marketing cache
                self.state["marketing_generated"] += len(copies)
                self.achievements.append(f"Cycle {self.cycles}: Generated {len(copies)} marketing copies")
                self.log(f"Generated {len(copies)} promo copies")
            except Exception as e:
                self.log(f"Marketing error: {e}")
        
        # Phase 4: Deep search (every 7 cycles)
        if self.cycles % 7 == 0:
            self.log("Phase 4: Intelligence gathering")
            try:
                topics = ["AI tools 2026", "autonomous agents", "no-code platforms", "indie hackers"]
                topic = random.choice(topics)
                results = self.search.search_duckduckgo(topic, 1)
                self.state["searches_done"] += 1
                self.achievements.append(f"Cycle {self.cycles}: Searched '{topic}' — found {len(results)} sources")
                self.log(f"Searched '{topic}' — {len(results)} results")
            except Exception as e:
                self.log(f"Search error: {e}")
        
        # Phase 5: Web builder (every 10 cycles)
        if self.cycles % 10 == 0:
            self.log("Phase 5: Web asset generation")
            try:
                features = [
                    ("Lightning Fast", "Built for speed, zero latency"),
                    ("Self-Healing", "Fixes itself before you notice"),
                    ("Autonomous", "Thinks, builds, deploys — non-stop")
                ]
                html = self.coder.generate_landing_page("LilJR Empire", "The autonomous system that builds empires", features)
                self.coder.write_file("web/landing.html", html)
                self.achievements.append(f"Cycle {self.cycles}: Generated landing page")
                self.log("Generated landing page")
            except Exception as e:
                self.log(f"Web build error: {e}")
        
        self.state["last_action"] = time.time()
        self.state["thoughts_generated"] += 1
        
        return self.state
    
    def run_forever(self, interval=60):
        """Run the autonomous loop forever."""
        self.log("═══════════════════════════════════════")
        self.log("AUTONOMOUS EMPIRE BUILDER STARTED")
        self.log("Non-stop thinking. Self-building.")
        self.log("═══════════════════════════════════════")
        
        while self.running:
            try:
                self.cycle()
                time.sleep(interval)
            except KeyboardInterrupt:
                self.log("Stopped by user")
                break
            except Exception as e:
                self.log(f"Cycle error: {e}")
                time.sleep(interval)
        
        return self.get_report()
    
    def get_report(self):
        return {
            "cycles": self.cycles,
            "state": self.state,
            "achievements": self.achievements[-20:],  # Last 20
            "logs": self.logs[-50:],  # Last 50
            "uptime": time.time() - getattr(self, '_start_time', time.time())
        }
    
    def stop(self):
        self.running = False


if __name__ == '__main__':
    import random
    loop = AutonomousLoop()
    loop._start_time = time.time()
    
    # Run for a quick test or forever
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Run one cycle
        result = loop.cycle()
        print(json.dumps(result, indent=2))
    else:
        # Run forever
        loop.run_forever(interval=60)
