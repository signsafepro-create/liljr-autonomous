#!/usr/bin/env python3
"""
LILJR MEMORY ENGINE v1.0
Unstoppable learning brain. Remembers everything. Learns patterns. Self-improves.
"""
import os, sys, json, time, re, hashlib
from datetime import datetime, timedelta
from collections import Counter, defaultdict

STATE_FILE = os.path.expanduser('~/liljr_state.json')
MEMORY_FILE = os.path.expanduser('~/liljr_memory.json')
PATTERNS_FILE = os.path.expanduser('~/liljr_patterns.json')
LEARNING_FILE = os.path.expanduser('~/liljr_learning.json')
DAILY_LOG_DIR = os.path.expanduser('~/liljr_logs')

os.makedirs(DAILY_LOG_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# MEMORY ENGINE
# ═══════════════════════════════════════════════════════════════

class MemoryEngine:
    def __init__(self):
        self.memory = self._load(MEMORY_FILE, {
            'interactions': [],
            'trades': [],
            'preferences': {},
            'mistakes': [],
            'wins': [],
            'context': {},
            'knowledge': {},
            'created_at': str(datetime.now()),
            'version': '1.0'
        })
        self.patterns = self._load(PATTERNS_FILE, {
            'behavior_patterns': [],
            'time_patterns': {},
            'trade_patterns': {},
            'word_patterns': {},
            'success_signatures': [],
            'failure_signatures': [],
            'last_analysis': None
        })
        self.learning = self._load(LEARNING_FILE, {
            'command_success': {},
            'command_failure': {},
            'user_feedback': [],
            'auto_suggestions': [],
            'prompt_improvements': {},
            'learning_cycles': 0
        })
    
    def _load(self, filepath, default):
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except: pass
        return default
    
    def _save(self, data, filepath):
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def save_all(self):
        self._save(self.memory, MEMORY_FILE)
        self._save(self.patterns, PATTERNS_FILE)
        self._save(self.learning, LEARNING_FILE)
    
    # ─── INTERACTION LOGGING ───
    
    def log_interaction(self, text, cmd_type, result, context=None):
        """Log every interaction with full context."""
        entry = {
            'timestamp': str(datetime.now()),
            'text': text,
            'type': cmd_type,
            'result': result,
            'hour': datetime.now().hour,
            'day': datetime.now().strftime('%A'),
            'context': context or {},
            'success': result.get('status') in ['ok', 'saved', 'pushed', 'built', 'deployed', 'FILLED']
        }
        self.memory['interactions'].append(entry)
        # Keep last 5000
        self.memory['interactions'] = self.memory['interactions'][-5000:]
        
        # Daily log file
        daily_file = os.path.join(DAILY_LOG_DIR, f'{datetime.now().strftime("%Y-%m-%d")}.jsonl')
        with open(daily_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        # Real-time pattern detection
        self._detect_quick_patterns(entry)
        
        # Auto-save every 10 interactions
        if len(self.memory['interactions']) % 10 == 0:
            self.save_all()
    
    def log_trade(self, symbol, action, qty, price, result, reason=''):
        """Log every trade with full context."""
        entry = {
            'timestamp': str(datetime.now()),
            'symbol': symbol,
            'action': action,
            'qty': qty,
            'price': price,
            'result': result,
            'reason': reason,
            'hour': datetime.now().hour,
            'battery': self._get_battery(),
            'day': datetime.now().strftime('%A')
        }
        self.memory['trades'].append(entry)
        self.memory['trades'] = self.memory['trades'][-2000:]
        
        # Update trade patterns
        self._update_trade_patterns(entry)
    
    def _get_battery(self):
        try:
            import subprocess
            r = subprocess.run(['termux-battery-status'], capture_output=True, text=True, timeout=3)
            if r.returncode == 0:
                return json.loads(r.stdout).get('percentage', 100)
        except: pass
        return 100
    
    # ─── PATTERN DETECTION ───
    
    def _detect_quick_patterns(self, entry):
        """Detect patterns in real-time."""
        text = entry['text'].lower()
        hour = entry['hour']
        success = entry['success']
        
        # Time-based patterns
        if 'buy' in text or 'sell' in text:
            time_key = f"{hour}:00"
            if time_key not in self.patterns['time_patterns']:
                self.patterns['time_patterns'][time_key] = {'trades': 0, 'success': 0}
            self.patterns['time_patterns'][time_key]['trades'] += 1
            if success:
                self.patterns['time_patterns'][time_key]['success'] += 1
        
        # Word patterns
        words = re.findall(r'\b\w+\b', text)
        for word in words:
            if len(word) > 3:
                if word not in self.patterns['word_patterns']:
                    self.patterns['word_patterns'][word] = {'count': 0, 'success': 0}
                self.patterns['word_patterns'][word]['count'] += 1
                if success:
                    self.patterns['word_patterns'][word]['success'] += 1
    
    def _update_trade_patterns(self, entry):
        """Analyze trade outcomes for patterns."""
        symbol = entry['symbol']
        hour = entry['hour']
        action = entry['action']
        
        key = f"{symbol}_{action}_{hour}h"
        if key not in self.patterns['trade_patterns']:
            self.patterns['trade_patterns'][key] = {'count': 0, 'wins': 0, 'total_pnl': 0}
        
        self.patterns['trade_patterns'][key]['count'] += 1
        # Note: PnL tracking would need real price follow-up
    
    def deep_analyze(self):
        """Run deep pattern analysis. Returns insights."""
        insights = []
        
        # 1. Best trading hours
        best_hours = []
        for hour, data in self.patterns['time_patterns'].items():
            if data['trades'] >= 3:
                rate = data['success'] / data['trades']
                if rate > 0.7:
                    best_hours.append((hour, rate))
        best_hours.sort(key=lambda x: x[1], reverse=True)
        
        if best_hours:
            insights.append(f"Your best trading time: {best_hours[0][0]} ({best_hours[0][1]:.0%} success)")
        
        # 2. Worst trading hours
        worst_hours = []
        for hour, data in self.patterns['time_patterns'].items():
            if data['trades'] >= 3:
                rate = data['success'] / data['trades']
                if rate < 0.3:
                    worst_hours.append((hour, rate))
        worst_hours.sort(key=lambda x: x[1])
        
        if worst_hours:
            insights.append(f"Your worst trading time: {worst_hours[0][0]} ({worst_hours[0][1]:.0%} success) — avoid this")
        
        # 3. Repeated mistakes
        recent_mistakes = [m for m in self.memory['mistakes'] if 
            datetime.now() - datetime.fromisoformat(m['timestamp']) < timedelta(days=7)]
        if len(recent_mistakes) >= 3:
            insights.append(f"You've made {len(recent_mistakes)} mistakes this week. Slow down.")
        
        # 4. Success streaks
        recent = self.memory['interactions'][-50:]
        streak = 0
        for entry in reversed(recent):
            if entry['success']:
                streak += 1
            else:
                break
        if streak >= 5:
            insights.append(f"🔥 {streak} successful commands in a row. You're on fire.")
        
        # 5. Preference inference
        if 'hate' in self.memory['preferences'] or 'dislike' in self.memory['preferences']:
            hated = list(self.memory['preferences'].get('hate', {}).keys())[:3]
            if hated:
                insights.append(f"You consistently dislike: {', '.join(hated)}")
        
        # 6. Command success rates
        cmd_stats = defaultdict(lambda: {'total': 0, 'success': 0})
        for entry in self.memory['interactions'][-100:]:
            cmd = entry['type']
            cmd_stats[cmd]['total'] += 1
            if entry['success']:
                cmd_stats[cmd]['success'] += 1
        
        worst_cmds = [(cmd, d['success']/d['total']) for cmd, d in cmd_stats.items() 
                      if d['total'] >= 3 and d['success']/d['total'] < 0.5]
        if worst_cmds:
            worst_cmds.sort(key=lambda x: x[1])
            insights.append(f"'{worst_cmds[0][0]}' fails {100-worst_cmds[0][1]:.0%} of the time. Needs fixing.")
        
        self.patterns['last_analysis'] = str(datetime.now())
        return insights
    
    # ─── KNOWLEDGE BASE ───
    
    def learn_fact(self, topic, fact, source='user'):
        """Learn a fact about the world or user."""
        if topic not in self.memory['knowledge']:
            self.memory['knowledge'][topic] = []
        self.memory['knowledge'][topic].append({
            'fact': fact,
            'source': source,
            'timestamp': str(datetime.now()),
            'confidence': 1.0
        })
        # Keep last 100 per topic
        self.memory['knowledge'][topic] = self.memory['knowledge'][topic][-100:]
    
    def query_knowledge(self, topic):
        """Query learned knowledge."""
        return self.memory['knowledge'].get(topic, [])
    
    def search_memory(self, query, limit=10):
        """Search all memory for matching entries."""
        query = query.lower()
        results = []
        
        # Search interactions
        for entry in reversed(self.memory['interactions']):
            if query in entry['text'].lower() or query in str(entry.get('result', '')).lower():
                results.append(entry)
                if len(results) >= limit:
                    break
        
        return results
    
    # ─── PREFERENCE TRACKING ───
    
    def track_preference(self, pref_type, item, intensity=1):
        """Track user preferences."""
        if pref_type not in self.memory['preferences']:
            self.memory['preferences'][pref_type] = {}
        
        current = self.memory['preferences'][pref_type].get(item, 0)
        self.memory['preferences'][pref_type][item] = current + intensity
    
    def get_preferences(self, pref_type):
        """Get sorted preferences."""
        prefs = self.memory['preferences'].get(pref_type, {})
        return sorted(prefs.items(), key=lambda x: abs(x[1]), reverse=True)
    
    # ─── LEARNING LOOP ───
    
    def learn_from_result(self, command, expected, actual, user_feedback=None):
        """Learn whether a command worked as expected."""
        success = actual == expected or (isinstance(actual, dict) and actual.get('status') in ['ok', 'success'])
        
        if success:
            self.learning['command_success'][command] = self.learning['command_success'].get(command, 0) + 1
        else:
            self.learning['command_failure'][command] = self.learning['command_failure'].get(command, 0) + 1
        
        if user_feedback:
            self.learning['user_feedback'].append({
                'timestamp': str(datetime.now()),
                'command': command,
                'feedback': user_feedback
            })
    
    def generate_suggestions(self):
        """Generate suggestions based on patterns."""
        suggestions = []
        
        # 1. If user always checks price before buying, suggest auto-check
        recent = self.memory['interactions'][-20:]
        price_then_buy = 0
        for i in range(len(recent)-1):
            if recent[i]['type'] == 'price' and recent[i+1]['type'] in ['buy', 'sell']:
                price_then_buy += 1
        
        if price_then_buy >= 3:
            suggestions.append("You always check price before trading. Want auto-price-check on buy commands?")
        
        # 2. If user pushes frequently, suggest auto-push
        pushes = sum(1 for e in recent if e['type'] == 'push')
        if pushes >= 5:
            suggestions.append("You push a lot. Want auto-push after every trade?")
        
        # 3. If sentiment always returns 'unknown', suggest fixing keys
        sentiments = [e for e in recent if e['type'] == 'sentiment']
        if sentiments and all('unknown' in str(e.get('result', '')) for e in sentiments):
            suggestions.append("Sentiment always returns 'unknown'. You need real Reddit API keys.")
        
        # 4. Time-based suggestions
        hour = datetime.now().hour
        if hour >= 23 or hour <= 5:
            suggestions.append("It's late. Night mode is active. Trading is blocked for your safety.")
        
        self.learning['auto_suggestions'] = suggestions
        return suggestions
    
    # ─── SELF-IMPROVEMENT ───
    
    def improve_prompt(self, original, better_version, context):
        """Record a prompt improvement."""
        key = hashlib.md5(original.encode()).hexdigest()[:8]
        self.learning['prompt_improvements'][key] = {
            'original': original,
            'improved': better_version,
            'context': context,
            'timestamp': str(datetime.now()),
            'uses': 0
        }
    
    def get_better_prompt(self, text):
        """Check if we have a better version of this prompt."""
        for key, data in self.learning['prompt_improvements'].items():
            if data['original'].lower() in text.lower() or text.lower() in data['original'].lower():
                data['uses'] += 1
                return data['improved']
        return None
    
    # ─── MEMORY QUERIES ───
    
    def query(self, question):
        """Answer questions about memory."""
        q = question.lower()
        
        if 'best trade' in q or 'most profit' in q:
            trades = [t for t in self.memory['trades'] if t.get('result') == 'win']
            if trades:
                best = max(trades, key=lambda x: x.get('price', 0) * x.get('qty', 1))
                return f"Best trade: {best['action'].upper()} {best['qty']} {best['symbol']} at ${best['price']} on {best['timestamp']}"
            return "No winning trades recorded yet."
        
        if 'last trade' in q or 'recent trade' in q:
            if self.memory['trades']:
                t = self.memory['trades'][-1]
                return f"Last trade: {t['action'].upper()} {t['qty']} {t['symbol']} at ${t['price']} ({t['timestamp']})"
            return "No trades yet."
        
        if 'how many' in q and ('trade' in q or 'buy' in q or 'sell' in q):
            return f"Total trades: {len(self.memory['trades'])}"
        
        if 'what do i like' in q or 'preferences' in q:
            likes = self.get_preferences('like')
            if likes:
                return f"You like: {', '.join(f'{k} ({v}x)' for k, v in likes[:5])}"
            return "Still learning your preferences."
        
        if 'what do i hate' in q or 'dislike' in q:
            hates = self.get_preferences('hate')
            if hates:
                return f"You hate: {', '.join(f'{k} ({v}x)' for k, v in hates[:5])}"
            return "Still learning your dislikes."
        
        if 'mistake' in q or 'wrong' in q:
            return f"Recorded mistakes: {len(self.memory['mistakes'])}. Last 3: " + \
                   ', '.join(m.get('reason', 'unknown') for m in self.memory['mistakes'][-3:])
        
        if 'pattern' in q or 'insight' in q or 'learn' in q:
            insights = self.deep_analyze()
            if insights:
                return '\n'.join(f"• {i}" for i in insights[:5])
            return "Not enough data for patterns yet. Keep trading."
        
        if 'suggestion' in q or 'tip' in q:
            suggestions = self.generate_suggestions()
            if suggestions:
                return '\n'.join(f"💡 {s}" for s in suggestions[:3])
            return "No suggestions right now. You're doing great."
        
        # Search memory
        results = self.search_memory(q, 3)
        if results:
            return f"Found {len(results)} matching memories:\n" + \
                   '\n'.join(f"• [{r['timestamp'][:16]}] {r['text'][:60]}..." for r in results)
        
        return "I don't have enough memory about that yet. Keep using the system and I'll learn."

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    engine = MemoryEngine()
    
    if len(sys.argv) < 2:
        print("LilJR Memory Engine v1.0")
        print("Usage: python memory_engine.py <action> [args]")
        print()
        print("Actions:")
        print("  query 'what was my last trade'")
        print("  query 'best trading time'")
        print("  query 'what do I hate'")
        print("  query 'patterns'")
        print("  query 'suggestions'")
        print("  analyze — Deep pattern analysis")
        print("  stats — Memory statistics")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'query':
        question = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else 'what do I know'
        result = engine.query(question)
        print(result)
    
    elif action == 'analyze':
        insights = engine.deep_analyze()
        if insights:
            print("🧠 DEEP ANALYSIS:")
            for i in insights:
                print(f"  • {i}")
        else:
            print("Not enough data yet. Keep trading and interacting.")
    
    elif action == 'stats':
        print(f"📊 MEMORY STATS:")
        print(f"  Interactions: {len(engine.memory['interactions'])}")
        print(f"  Trades: {len(engine.memory['trades'])}")
        print(f"  Knowledge topics: {len(engine.memory['knowledge'])}")
        print(f"  Preferences: {len(engine.memory['preferences'])}")
        print(f"  Mistakes: {len(engine.memory['mistakes'])}")
        print(f"  Wins: {len(engine.memory['wins'])}")
        print(f"  Time patterns: {len(engine.patterns['time_patterns'])}")
        print(f"  Trade patterns: {len(engine.patterns['trade_patterns'])}")
        print(f"  Learning cycles: {engine.learning['learning_cycles']}")
    
    elif action == 'suggest':
        suggestions = engine.generate_suggestions()
        if suggestions:
            print("💡 SUGGESTIONS:")
            for s in suggestions:
                print(f"  • {s}")
        else:
            print("No suggestions right now.")
    
    else:
        print(f"Unknown action: {action}")
        print("Try: query, analyze, stats, suggest")
