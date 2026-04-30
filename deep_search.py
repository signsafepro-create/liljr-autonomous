#!/usr/bin/env python3
"""
LILJR DEEP SEARCH v1.0
Aggressive web intelligence. Scrapes deep. Extracts everything.
No rate limits. No API keys. Pure Python.
"""
import urllib.request, urllib.parse, re, json, time, ssl
from html.parser import HTMLParser

class DeepSearch:
    def __init__(self):
        self.visited = set()
        self.results = []
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
    
    def _headers(self):
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'identity',
            'Connection': 'keep-alive',
        }
    
    def fetch(self, url, timeout=20):
        """Fetch a URL with error handling."""
        try:
            req = urllib.request.Request(url, headers=self._headers())
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                return resp.read().decode('utf-8', errors='ignore')
        except Exception as e:
            return None
    
    def search_duckduckgo(self, query, pages=3):
        """Deep search DuckDuckGo."""
        results = []
        for page in range(pages):
            try:
                start = page * 30
                url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}&s={start}"
                html = self.fetch(url, 15)
                if not html:
                    continue
                
                for m in re.finditer(r'class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)', html):
                    link, title = m.group(1), m.group(2)
                    if link not in self.visited:
                        self.visited.add(link)
                        results.append({"title": title.strip(), "url": link, "source": "duckduckgo"})
                
                time.sleep(0.5)
            except:
                continue
        return results
    
    def search_bing(self, query, count=10):
        """Search via Bing."""
        try:
            url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}&count={count}"
            html = self.fetch(url, 15)
            if not html:
                return []
            
            results = []
            for m in re.finditer(r'<a[^>]*href="(https?://[^"]+)"[^>]*>([^<]+)', html):
                link, title = m.group(1), m.group(2)
                if 'bing.com' not in link and 'microsoft.com' not in link:
                    results.append({"title": title.strip(), "url": link, "source": "bing"})
            return results[:count]
        except:
            return []
    
    def extract_text(self, url):
        """Extract clean text from any webpage."""
        html = self.fetch(url, 20)
        if not html:
            return None
        
        # Remove scripts and styles
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
        
        # Extract text
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Extract key info
        emails = re.findall(r'[\w.-]+@[\w.-]+\.\w+', text)
        phones = re.findall(r'\+?\d{1,4}[\s-]?\(?\d{1,4}\)?[\s-]?\d{1,4}[\s-]?\d{1,4}', text)
        links = re.findall(r'https?://[^\s<>"\']+', html)
        
        return {
            "url": url,
            "text": text[:5000],
            "emails": list(set(emails))[:10],
            "phones": list(set(phones))[:10],
            "links": list(set(links))[:20],
            "word_count": len(text.split())
        }
    
    def deep_scan(self, query, depth=2):
        """Multi-source deep scan."""
        all_results = []
        
        # Search multiple engines
        ddgs = self.search_duckduckgo(query, depth)
        all_results.extend(ddgs)
        
        # Extract content from top results
        enriched = []
        for r in all_results[:10]:
            extracted = self.extract_text(r['url'])
            if extracted:
                enriched.append({**r, **extracted})
            time.sleep(0.3)
        
        return {
            "query": query,
            "depth": depth,
            "sources": len(all_results),
            "enriched": enriched
        }
    
    def find_competitors(self, niche):
        """Find competitors in a niche."""
        query = f"best {niche} tools 2026"
        results = self.search_duckduckgo(query, 2)
        
        competitors = []
        for r in results:
            domain = re.search(r'https?://([^/]+)', r['url'])
            if domain:
                competitors.append({
                    "name": r['title'],
                    "domain": domain.group(1),
                    "url": r['url']
                })
        
        return competitors[:10]
    
    def find_trends(self, topic):
        """Find trending subtopics."""
        queries = [
            f"{topic} trends 2026",
            f"{topic} new features",
            f"{topic} vs alternatives"
        ]
        
        all_mentions = []
        for q in queries:
            results = self.search_duckduckgo(q, 1)
            all_mentions.extend([r['title'] for r in results])
            time.sleep(0.5)
        
        # Extract keywords
        words = []
        for m in all_mentions:
            words.extend(re.findall(r'[A-Z][a-zA-Z]+', m))
        
        from collections import Counter
        top = Counter(words).most_common(10)
        return [{"term": t[0], "mentions": t[1]} for t in top]
    
    def find_backlinks(self, domain):
        """Find sites linking to a domain."""
        query = f"link:{domain}"
        return self.search_duckduckgo(query, 2)
    
    def scrape_social(self, handle, platform='twitter'):
        """Scrape public social data."""
        # Note: This is for public data only
        if platform == 'twitter':
            url = f"https://nitter.net/{handle}"
        elif platform == 'reddit':
            url = f"https://www.reddit.com/user/{handle}/comments.json"
        else:
            return {"error": "Platform not supported"}
        
        return self.extract_text(url)


if __name__ == '__main__':
    import random
    search = DeepSearch()
    print("[DEEPSEARCH] Ready. Use search_duckduckgo() or deep_scan()")
