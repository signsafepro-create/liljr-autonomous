#!/usr/bin/env python3
"""
LILJR INTELLIGENCE HUB v1.0
Worldwide signal catcher. Searches, monitors, alerts, learns.
Legal boundaries: public data only. No hacking, no illegal content.
"""
import os, sys, json, re, time, threading, urllib.request, urllib.parse, subprocess
from datetime import datetime
from html.parser import HTMLParser

STATE_FILE = os.path.expanduser('~/liljr_state.json')
INTEL_FILE = os.path.expanduser('~/liljr_intelligence.json')
ALERT_LOG = os.path.expanduser('~/liljr_alerts.jsonl')
FEEDS_FILE = os.path.expanduser('~/liljr_feeds.txt')

os.makedirs(os.path.dirname(INTEL_FILE), exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# SEARCH ENGINES
# ═══════════════════════════════════════════════════════════════

class SearchEngine:
    def __init__(self):
        self.results_cache = {}
    
    def web_search(self, query, count=10):
        """Search the web using multiple sources."""
        results = []
        
        # DuckDuckGo HTML scrape
        try:
            ddg = self._ddg_search(query, count)
            results.extend(ddg)
        except Exception as e:
            print(f"[DDG ERROR] {e}")
        
        # Wikipedia API
        try:
            wiki = self._wiki_search(query)
            if wiki:
                results.append(wiki)
        except Exception as e:
            print(f"[WIKI ERROR] {e}")
        
        # GitHub search (public repos)
        try:
            gh = self._github_search(query, count)
            results.extend(gh)
        except Exception as e:
            print(f"[GH ERROR] {e}")
        
        return results[:count]
    
    def _ddg_search(self, query, count):
        """DuckDuckGo search via HTML."""
        encoded = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded}"
        
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
                'Accept': 'text/html'
            }
        )
        
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        
        results = []
        # Extract links and titles
        link_pattern = r'<a rel="nofollow" class="result__a" href="(https?://[^"]+)">([^<]+)</a>'
        snippet_pattern = r'<a class="result__snippet"[^>]*>([^<]+)</a>'
        
        links = re.findall(link_pattern, html)
        snippets = re.findall(snippet_pattern, html)
        
        for i, (href, title) in enumerate(links[:count]):
            snippet = snippets[i] if i < len(snippets) else ''
            results.append({
                'source': 'duckduckgo',
                'title': self._clean_html(title),
                'url': href,
                'snippet': self._clean_html(snippet),
                'timestamp': str(datetime.now())
            })
        
        return results
    
    def _wiki_search(self, query):
        """Wikipedia search."""
        encoded = urllib.parse.quote(query)
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={encoded}&format=json&srlimit=1"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'LilJR/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        
        search_results = data.get('query', {}).get('search', [])
        if search_results:
            result = search_results[0]
            page_id = result['pageid']
            return {
                'source': 'wikipedia',
                'title': result['title'],
                'url': f"https://en.wikipedia.org/?curid={page_id}",
                'snippet': self._clean_html(result.get('snippet', '')),
                'timestamp': str(datetime.now())
            }
        return None
    
    def _github_search(self, query, count):
        """GitHub repository search."""
        encoded = urllib.parse.quote(query)
        url = f"https://api.github.com/search/repositories?q={encoded}&sort=updated&per_page={count}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'LilJR/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        
        results = []
        for item in data.get('items', [])[:count]:
            results.append({
                'source': 'github',
                'title': item['full_name'],
                'url': item['html_url'],
                'snippet': item.get('description', 'No description')[:200],
                'stars': item.get('stargazers_count', 0),
                'timestamp': str(datetime.now())
            })
        return results
    
    def _clean_html(self, text):
        """Remove HTML tags."""
        return re.sub(r'<[^>]+>', '', text)
    
    def fetch_url(self, url, max_chars=5000):
        """Fetch and extract text from any URL."""
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
            
            # Extract text
            text = re.sub(r'<script[^>]*>[^<]*</script>', '', html, flags=re.DOTALL)
            text = re.sub(r'<style[^>]*>[^<]*</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text[:max_chars]
        except Exception as e:
            return f"Error fetching {url}: {str(e)}"

# ═══════════════════════════════════════════════════════════════
# RSS MONITOR
# ═══════════════════════════════════════════════════════════════

class RSSMonitor:
    def __init__(self):
        self.feeds = self._load_feeds()
        self.seen_items = set()
        self._load_seen()
    
    def _load_feeds(self):
        if os.path.exists(FEEDS_FILE):
            with open(FEEDS_FILE, 'r') as f:
                return [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return [
            'https://news.ycombinator.com/rss',
            'https://feeds.bbci.co.uk/news/technology/rss.xml',
            'https://www.reddit.com/r/technology/.rss',
        ]
    
    def _load_seen(self):
        if os.path.exists(INTEL_FILE):
            try:
                with open(INTEL_FILE, 'r') as f:
                    data = json.load(f)
                for item in data.get('rss_items', []):
                    self.seen_items.add(item.get('link', item.get('title', '')))
            except: pass
    
    def check_all(self, keywords=None):
        """Check all feeds for new items matching keywords."""
        matches = []
        
        for feed_url in self.feeds:
            try:
                items = self._parse_feed(feed_url)
                for item in items:
                    item_id = item.get('link', item.get('title', ''))
                    if item_id in self.seen_items:
                        continue
                    
                    self.seen_items.add(item_id)
                    
                    if keywords:
                        text = f"{item.get('title', '')} {item.get('description', '')}".lower()
                        if any(kw.lower() in text for kw in keywords):
                            item['matched_keywords'] = [kw for kw in keywords if kw.lower() in text]
                            item['feed'] = feed_url
                            matches.append(item)
                    else:
                        item['feed'] = feed_url
                        matches.append(item)
            except Exception as e:
                print(f"[RSS ERROR {feed_url}] {e}")
        
        return matches
    
    def _parse_feed(self, url):
        """Parse RSS/Atom feed."""
        req = urllib.request.Request(url, headers={'User-Agent': 'LilJR/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml = resp.read().decode('utf-8', errors='ignore')
        
        items = []
        
        # RSS items
        rss_items = re.findall(r'<item[^>]*>(.*?)</item>', xml, re.DOTALL)
        for item_xml in rss_items:
            title = re.search(r'<title[^>]*>([^<]+)</title>', item_xml)
            link = re.search(r'<link[^>]*>([^<]+)</link>', item_xml)
            desc = re.search(r'<description[^>]*>([^<]+)</description>', item_xml)
            pub = re.search(r'<pubDate[^>]*>([^<]+)</pubDate>', item_xml)
            
            items.append({
                'title': self._clean_xml(title.group(1)) if title else 'Untitled',
                'link': link.group(1) if link else '',
                'description': self._clean_xml(desc.group(1)) if desc else '',
                'published': pub.group(1) if pub else str(datetime.now()),
            })
        
        # Atom entries
        atom_entries = re.findall(r'<entry[^>]*>(.*?)</entry>', xml, re.DOTALL)
        for entry_xml in atom_entries:
            title = re.search(r'<title[^>]*>([^<]+)</title>', entry_xml)
            link = re.search(r'<link[^>]*href="([^"]+)"', entry_xml)
            summary = re.search(r'<summary[^>]*>([^<]+)</summary>', entry_xml)
            
            items.append({
                'title': self._clean_xml(title.group(1)) if title else 'Untitled',
                'link': link.group(1) if link else '',
                'description': self._clean_xml(summary.group(1)) if summary else '',
                'published': str(datetime.now()),
            })
        
        return items
    
    def _clean_xml(self, text):
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'&lt;[^&]+&gt;', '', text)
        text = text.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        return text.strip()
    
    def add_feed(self, url):
        """Add a new RSS feed."""
        if url not in self.feeds:
            self.feeds.append(url)
            with open(FEEDS_FILE, 'a') as f:
                f.write(f"{url}\n")
            return True
        return False

# ═══════════════════════════════════════════════════════════════
# INTELLIGENCE ENGINE
# ═══════════════════════════════════════════════════════════════

class IntelligenceHub:
    def __init__(self):
        self.search = SearchEngine()
        self.rss = RSSMonitor()
        self.intel = self._load_intel()
        self.keywords = self.intel.get('watch_keywords', [])
    
    def _load_intel(self):
        if os.path.exists(INTEL_FILE):
            try:
                with open(INTEL_FILE, 'r') as f:
                    return json.load(f)
            except: pass
        return {
            'queries': [],
            'results': [],
            'rss_items': [],
            'watch_keywords': ['AI', 'stock', 'crypto', 'hack', 'breach', 'liljr'],
            'alerts': [],
            'created': str(datetime.now())
        }
    
    def save(self):
        with open(INTEL_FILE, 'w') as f:
            json.dump(self.intel, f, indent=2)
    
    def query(self, text, depth=1):
        """Run an intelligence query."""
        print(f"🔍 Query: {text}")
        
        # 1. Web search
        results = self.search.web_search(text, count=depth * 5)
        
        # 2. Store
        query_record = {
            'timestamp': str(datetime.now()),
            'query': text,
            'results_count': len(results),
            'results': results
        }
        self.intel['queries'].append(query_record)
        self.intel['results'].extend(results)
        
        # Keep last 100 queries, 500 results
        self.intel['queries'] = self.intel['queries'][-100:]
        self.intel['results'] = self.intel['results'][-500:]
        
        self.save()
        
        return {
            'query': text,
            'results': results,
            'sources': list(set(r['source'] for r in results))
        }
    
    def scan_feeds(self):
        """Scan RSS feeds for keyword matches."""
        print(f"📡 Scanning {len(self.rss.feeds)} feeds for: {self.keywords}")
        
        matches = self.rss.check_all(self.keywords)
        
        # Store and alert
        for match in matches:
            self.intel['rss_items'].append(match)
            self.intel['alerts'].append({
                'type': 'rss_match',
                'timestamp': str(datetime.now()),
                'data': match
            })
            
            # Write to alert log
            with open(ALERT_LOG, 'a') as f:
                f.write(json.dumps(match) + '\n')
        
        self.intel['rss_items'] = self.intel['rss_items'][-500:]
        self.intel['alerts'] = self.intel['alerts'][-200:]
        self.save()
        
        return {
            'feeds_checked': len(self.rss.feeds),
            'matches_found': len(matches),
            'matches': matches
        }
    
    def add_keywords(self, keywords):
        """Add watch keywords."""
        for kw in keywords:
            if kw not in self.keywords:
                self.keywords.append(kw)
        self.intel['watch_keywords'] = self.keywords
        self.save()
        return self.keywords
    
    def get_alerts(self, limit=20):
        """Get recent alerts."""
        return self.intel['alerts'][-limit:]
    
    def summarize(self, topic):
        """Summarize all intelligence on a topic."""
        relevant = []
        
        # Search results
        for result in self.intel['results']:
            if topic.lower() in result.get('title', '').lower() or topic.lower() in result.get('snippet', '').lower():
                relevant.append(result)
        
        # RSS items
        for item in self.intel['rss_items']:
            if topic.lower() in item.get('title', '').lower() or topic.lower() in item.get('description', '').lower():
                relevant.append(item)
        
        # Sort by recency
        relevant.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return {
            'topic': topic,
            'mentions': len(relevant),
            'latest': relevant[:5],
            'sources': list(set(r.get('source', 'unknown') for r in relevant))
        }
    
    def continuous_monitor(self, interval=300):
        """Run continuous monitoring in background."""
        print(f"👁 Continuous monitor started ({interval}s interval)")
        while True:
            try:
                result = self.scan_feeds()
                if result['matches_found'] > 0:
                    print(f"🚨 {result['matches_found']} alerts!")
                    for m in result['matches']:
                        print(f"  • [{m.get('feed', '?')}] {m.get('title', '?')[:60]}")
                time.sleep(interval)
            except Exception as e:
                print(f"[MONITOR ERROR] {e}")
                time.sleep(60)

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    hub = IntelligenceHub()
    
    if len(sys.argv) < 2:
        print("LilJR Intelligence Hub v1.0")
        print("Usage: python intel_hub.py <action> [args]")
        print()
        print("Actions:")
        print("  query 'AI stocks'           — Search the web")
        print("  query 'cybersecurity' 3     — Search with depth")
        print("  scan                        — Scan RSS feeds")
        print("  keywords AI crypto stock    — Add watch keywords")
        print("  alerts                      — Show recent alerts")
        print("  summarize 'bitcoin'         — Summarize intelligence")
        print("  monitor                     — Start continuous monitoring")
        print("  stats                       — Show intelligence stats")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'query':
        query_text = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else 'latest news'
        depth = 1
        # Check if last arg is a number (depth)
        if sys.argv[-1].isdigit():
            depth = int(sys.argv[-1])
            query_text = ' '.join(sys.argv[2:-1])
        
        result = hub.query(query_text, depth)
        print(f"\nFound {len(result['results'])} results from {', '.join(result['sources'])}:")
        for i, r in enumerate(result['results'], 1):
            print(f"\n{i}. [{r['source'].upper()}] {r['title']}")
            print(f"   {r.get('snippet', '')[:120]}...")
            print(f"   → {r['url']}")
    
    elif action == 'scan':
        result = hub.scan_feeds()
        print(f"\nScanned {result['feeds_checked']} feeds, {result['matches_found']} matches")
        for m in result['matches']:
            print(f"\n🚨 [{', '.join(m.get('matched_keywords', []))}]")
            print(f"   {m.get('title', '?')}")
            print(f"   → {m.get('link', '')}")
    
    elif action == 'keywords':
        kws = sys.argv[2:] if len(sys.argv) > 2 else []
        result = hub.add_keywords(kws)
        print(f"Watching: {', '.join(result)}")
    
    elif action == 'alerts':
        alerts = hub.get_alerts()
        print(f"Recent alerts ({len(alerts)}):")
        for a in alerts:
            data = a.get('data', {})
            print(f"\n[{a['timestamp'][:16]}] {a['type']}")
            print(f"  {data.get('title', '?')}")
    
    elif action == 'summarize':
        topic = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else 'technology'
        result = hub.summarize(topic)
        print(f"\n📊 {topic.upper()}: {result['mentions']} mentions")
        print(f"Sources: {', '.join(result['sources'])}")
        print("\nLatest:")
        for item in result['latest']:
            print(f"  • {item.get('title', '?')[:80]}")
    
    elif action == 'monitor':
        hub.continuous_monitor()
    
    elif action == 'stats':
        print(f"📊 INTELLIGENCE STATS:")
        print(f"  Queries: {len(hub.intel['queries'])}")
        print(f"  Results: {len(hub.intel['results'])}")
        print(f"  RSS items: {len(hub.intel['rss_items'])}")
        print(f"  Alerts: {len(hub.intel['alerts'])}")
        print(f"  Watch keywords: {', '.join(hub.keywords)}")
    
    else:
        print(f"Unknown action: {action}")
        print("Try: query, scan, keywords, alerts, summarize, monitor, stats")
