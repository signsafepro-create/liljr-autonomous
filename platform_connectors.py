#!/usr/bin/env python3
"""
LILJR PLATFORM CONNECTORS v1.0
Universal bridge to any platform. Post, publish, push, connect.
No middlemen. Direct API-to-API communication.
"""
import os, sys, json, urllib.request, urllib.parse, base64, subprocess, re
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# GITHUB CONNECTOR
# ═══════════════════════════════════════════════════════════════

class GitHubConnector:
    def __init__(self, token):
        self.token = token
        self.base = "https://api.github.com"
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'LilJR/1.0'
        }
    
    def _request(self, path, method='GET', data=None):
        url = f"{self.base}{path}"
        try:
            if method == 'GET':
                req = urllib.request.Request(url, headers=self.headers)
            else:
                payload = json.dumps(data).encode() if data else b'{}'
                req = urllib.request.Request(url, data=payload, headers={**self.headers, 'Content-Type': 'application/json'}, method=method)
            
            with urllib.request.urlopen(req, timeout=30) as resp:
                return {"status": "ok", "code": resp.status, "data": json.loads(resp.read())}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def create_repo(self, name, private=True, description=""):
        return self._request('/user/repos', 'POST', {
            "name": name,
            "private": private,
            "description": description,
            "auto_init": True
        })
    
    def list_repos(self):
        return self._request('/user/repos')
    
    def create_file(self, repo, path, content, message="Update"):
        # content must be base64 encoded
        b64 = base64.b64encode(content.encode()).decode()
        return self._request(f'/repos/{repo}/contents/{path}', 'PUT', {
            "message": message,
            "content": b64
        })
    
    def push_files(self, repo, files_dict, message="Bulk update"):
        """Push multiple files to a repo. files_dict = {path: content}"""
        results = {}
        for path, content in files_dict.items():
            r = self.create_file(repo, path, content, message)
            results[path] = r
        return {"status": "pushed", "files": len(files_dict), "results": results}
    
    def create_issue(self, repo, title, body=""):
        return self._request(f'/repos/{repo}/issues', 'POST', {"title": title, "body": body})
    
    def enable_pages(self, repo, branch="main"):
        return self._request(f'/repos/{repo}/pages', 'POST', {"source": {"branch": branch, "path": "/"}})
    
    def get_user(self):
        return self._request('/user')

# ═══════════════════════════════════════════════════════════════
# FACEBOOK / META CONNECTOR
# ═══════════════════════════════════════════════════════════════

class FacebookConnector:
    def __init__(self, access_token, page_id=None):
        self.token = access_token
        self.page_id = page_id
        self.base = "https://graph.facebook.com/v18.0"
    
    def _request(self, path, method='GET', data=None, params=None):
        url = f"{self.base}{path}"
        base_params = {'access_token': self.token}
        if params:
            base_params.update(params)
        url += '?' + urllib.parse.urlencode(base_params)
        
        try:
            if method == 'GET':
                req = urllib.request.Request(url, headers={'User-Agent': 'LilJR/1.0'})
            else:
                payload = urllib.parse.urlencode(data).encode() if data else b''
                req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'}, method=method)
            
            with urllib.request.urlopen(req, timeout=30) as resp:
                return {"status": "ok", "data": json.loads(resp.read())}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def post_to_page(self, message, link=None):
        """Post to Facebook page."""
        if not self.page_id:
            return {"status": "error", "error": "No page_id set"}
        
        params = {"message": message}
        if link:
            params["link"] = link
        
        return self._request(f'/{self.page_id}/feed', 'POST', params)
    
    def post_photo(self, image_url, message=""):
        """Post a photo to page."""
        if not self.page_id:
            return {"status": "error", "error": "No page_id set"}
        
        return self._request(f'/{self.page_id}/photos', 'POST', {
            "url": image_url,
            "caption": message
        })
    
    def get_pages(self):
        """List pages you manage."""
        return self._request('/me/accounts')
    
    def get_insights(self, metric='page_impressions'):
        """Get page insights."""
        if not self.page_id:
            return {"status": "error", "error": "No page_id set"}
        return self._request(f'/{self.page_id}/insights/{metric}')
    
    def create_event(self, name, start_time, description=""):
        """Create a Facebook event."""
        if not self.page_id:
            return {"status": "error", "error": "No page_id set"}
        return self._request(f'/{self.page_id}/events', 'POST', {
            "name": name,
            "start_time": start_time,
            "description": description
        })

# ═══════════════════════════════════════════════════════════════
# TWITTER / X CONNECTOR
# ═══════════════════════════════════════════════════════════════

class TwitterConnector:
    def __init__(self, bearer_token, api_key=None, api_secret=None, access_token=None, access_secret=None):
        self.bearer = bearer_token
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_secret = access_secret
        self.base = "https://api.twitter.com/2"
    
    def _request(self, path, method='GET', data=None):
        url = f"{self.base}{path}"
        headers = {'Authorization': f'Bearer {self.bearer}', 'User-Agent': 'LilJR/1.0'}
        
        try:
            if method == 'GET':
                req = urllib.request.Request(url, headers=headers)
            else:
                payload = json.dumps(data).encode() if data else b'{}'
                req = urllib.request.Request(url, data=payload, headers={**headers, 'Content-Type': 'application/json'}, method=method)
            
            with urllib.request.urlopen(req, timeout=30) as resp:
                return {"status": "ok", "data": json.loads(resp.read())}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def tweet(self, text):
        """Post a tweet."""
        # Twitter API v2 requires OAuth 2.0 or OAuth 1.0a
        # This is a simplified version - real implementation needs proper OAuth
        return self._request('/tweets', 'POST', {"text": text})
    
    def get_timeline(self, user_id, max_results=10):
        """Get user's timeline."""
        return self._request(f'/users/{user_id}/tweets?max_results={max_results}')
    
    def search(self, query, max_results=10):
        """Search tweets."""
        encoded = urllib.parse.quote(query)
        return self._request(f'/tweets/search/recent?query={encoded}&max_results={max_results}')

# ═══════════════════════════════════════════════════════════════
# TELEGRAM CONNECTOR
# ═══════════════════════════════════════════════════════════════

class TelegramConnector:
    def __init__(self, bot_token, chat_id=None):
        self.token = bot_token
        self.chat_id = chat_id
        self.base = f"https://api.telegram.org/bot{bot_token}"
    
    def _request(self, method, data=None):
        url = f"{self.base}/{method}"
        try:
            if data:
                payload = json.dumps(data).encode()
                req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
            else:
                req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, timeout=15) as resp:
                return {"status": "ok", "data": json.loads(resp.read())}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def send_message(self, text, chat_id=None):
        cid = chat_id or self.chat_id
        if not cid:
            return {"status": "error", "error": "No chat_id"}
        return self._request('sendMessage', {"chat_id": cid, "text": text, "parse_mode": "Markdown"})
    
    def get_updates(self, limit=10):
        return self._request('getUpdates', {"limit": limit})

# ═══════════════════════════════════════════════════════════════
# WEBHOOK / GENERIC API CONNECTOR
# ═══════════════════════════════════════════════════════════════

class WebhookConnector:
    """Universal webhook sender. Can hit any URL."""
    
    @staticmethod
    def send(url, method='POST', headers=None, data=None, json_data=None):
        try:
            req_headers = dict(headers or {})
            
            if json_data:
                payload = json.dumps(json_data).encode()
                req_headers['Content-Type'] = 'application/json'
            elif data:
                payload = urllib.parse.urlencode(data).encode()
                req_headers['Content-Type'] = 'application/x-www-form-urlencoded'
            else:
                payload = b''
            
            req = urllib.request.Request(url, data=payload if payload else None, headers=req_headers, method=method)
            
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode('utf-8', errors='ignore')
                try:
                    parsed = json.loads(body)
                except:
                    parsed = {"raw": body[:1000]}
                return {"status": "ok", "code": resp.status, "data": parsed}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    @staticmethod
    def batch_send(requests_list):
        """Send multiple webhooks. requests_list = [{url, method, data, headers}]"""
        results = []
        for req in requests_list:
            r = WebhookConnector.send(
                req.get('url'),
                req.get('method', 'POST'),
                req.get('headers'),
                req.get('data'),
                req.get('json_data')
            )
            results.append({"url": req.get('url'), "result": r})
        return {"status": "batch_complete", "sent": len(requests_list), "results": results}

# ═══════════════════════════════════════════════════════════════
# APP PUBLISHER
# ═══════════════════════════════════════════════════════════════

class AppPublisher:
    """Publish apps to various platforms."""
    
    @staticmethod
    def generate_web_app(name, content, deploy_to=None):
        """Generate a web app and optionally deploy."""
        app_html = f"""<!DOCTYPE html>
<html>
<head><title>{name}</title><meta name="viewport" content="width=device-width"></head>
<body>{content}</body>
</html>"""
        
        result = {"status": "generated", "name": name, "size": len(app_html)}
        
        if deploy_to == 'github_pages':
            # Would need GitHub connector
            result["deploy"] = "Use GitHub connector to push to gh-pages branch"
        
        return result
    
    @staticmethod
    def generate_landing_page(title, description, cta="Sign Up", features=None):
        """Generate a landing page."""
        features_html = ""
        if features:
            features_html = "<ul>" + "".join(f"<li>{f}</li>" for f in features) + "</ul>"
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: sans-serif; margin: 0; padding: 40px; background: #0a0a0a; color: #fff; }}
        .hero {{ text-align: center; padding: 60px 20px; }}
        h1 {{ font-size: 3em; background: linear-gradient(90deg,#00f0ff,#7000ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .cta {{ display: inline-block; padding: 15px 40px; background: #00f0ff; color: #000; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 20px; }}
        .features {{ max-width: 800px; margin: 40px auto; }}
        .features li {{ padding: 10px 0; border-bottom: 1px solid #333; }}
    </style>
</head>
<body>
    <div class="hero">
        <h1>{title}</h1>
        <p>{description}</p>
        <a href="#" class="cta">{cta}</a>
    </div>
    <div class="features">{features_html}</div>
</body>
</html>"""

# ═══════════════════════════════════════════════════════════════
# AGENT BRIDGE — Talk to other AI systems
# ═══════════════════════════════════════════════════════════════

class AgentBridge:
    """Bridge to talk to other AI agents and services."""
    
    @staticmethod
    def send_to_agent(agent_url, message, context=None):
        """Send a message to another agent."""
        return WebhookConnector.send(agent_url, 'POST', None, None, {
            "message": message,
            "context": context or {},
            "from": "liljr",
            "timestamp": str(datetime.now())
        })
    
    @staticmethod
    def broadcast(agents, message):
        """Send to multiple agents."""
        results = []
        for agent in agents:
            r = AgentBridge.send_to_agent(agent.get('url'), message, agent.get('context'))
            results.append({"agent": agent.get('name'), "result": r})
        return {"status": "broadcast_complete", "results": results}

# ═══════════════════════════════════════════════════════════════
# PLATFORM ORCHESTRATOR — The brain that coordinates everything
# ═══════════════════════════════════════════════════════════════

class PlatformOrchestrator:
    def __init__(self, connections=None):
        self.connections = connections or {}
        self.github = None
        self.facebook = None
        self.twitter = None
        self.telegram = None
        self._init_from_connections()
    
    def _init_from_connections(self):
        """Initialize connectors from saved connections."""
        for name, conn in self.connections.items():
            ctype = conn.get('type', '')
            if ctype == 'github':
                self.github = GitHubConnector(conn.get('token'))
            elif ctype == 'facebook':
                self.facebook = FacebookConnector(conn.get('token'), conn.get('page_id'))
            elif ctype == 'twitter':
                self.twitter = TwitterConnector(conn.get('bearer'))
            elif ctype == 'telegram':
                self.telegram = TelegramConnector(conn.get('token'), conn.get('chat_id'))
    
    def cross_post(self, message, platforms):
        """Post the same message to multiple platforms."""
        results = {}
        
        for platform in platforms:
            if platform == 'github' and self.github:
                # Create an issue as a "post"
                r = self.github.create_issue('your-repo', message[:50], message)
                results['github'] = r
            
            elif platform == 'facebook' and self.facebook:
                r = self.facebook.post_to_page(message)
                results['facebook'] = r
            
            elif platform == 'twitter' and self.twitter:
                r = self.twitter.tweet(message)
                results['twitter'] = r
            
            elif platform == 'telegram' and self.telegram:
                r = self.telegram.send_message(message)
                results['telegram'] = r
        
        return {"status": "cross_posted", "platforms": platforms, "results": results}
    
    def deploy_everywhere(self, files, message="Deploy"):
        """Push code to GitHub AND announce on social."""
        results = {}
        
        if self.github:
            # Push to GitHub
            repo = self.connections.get('github', {}).get('default_repo', 'your-repo')
            r = self.github.push_files(repo, files, message)
            results['github'] = r
            
            # Announce
            if self.telegram:
                self.telegram.send_message(f"🚀 Deployed to GitHub: {message}")
        
        return results
    
    def build_and_publish(self, app_name, app_content, platforms):
        """Build an app and publish to platforms."""
        # Generate the app
        html = AppPublisher.generate_landing_page(app_name, app_content)
        
        results = {"generated": True, "name": app_name}
        
        if 'github_pages' in platforms and self.github:
            # Push index.html to repo
            repo = self.connections.get('github', {}).get('default_repo')
            if repo:
                r = self.github.create_file(repo, 'index.html', html, f"Publish {app_name}")
                results['github_pages'] = r
        
        if 'facebook' in platforms and self.facebook:
            # Share link
            r = self.facebook.post_to_page(f"Check out {app_name}!", "https://your-github-pages-url")
            results['facebook'] = r
        
        return results

# ═══════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("LilJR Platform Connectors v1.0")
        print("Usage: python platform_connectors.py <action> [args]")
        print()
        print("Actions:")
        print("  github-create-repo NAME 'Description' — Create GitHub repo")
        print("  github-list — List your repos")
        print("  github-push REPO FILE_PATH CONTENT — Push file to repo")
        print("  facebook-post 'Message' — Post to Facebook page")
        print("  facebook-pages — List your pages")
        print("  twitter-tweet 'Hello world' — Post tweet")
        print("  telegram-send 'Hello' CHAT_ID — Send Telegram message")
        print("  webhook URL METHOD '{json}' — Send webhook")
        print("  cross-post 'Hello' facebook,twitter,telegram")
        print("  generate-app NAME 'Description' — Generate landing page")
        sys.exit(1)
    
    action = sys.argv[1]
    
    # GitHub actions
    if action == 'github-create-repo':
        token = os.environ.get('GITHUB_TOKEN', '')
        if not token:
            print("Set GITHUB_TOKEN env var")
            sys.exit(1)
        gh = GitHubConnector(token)
        r = gh.create_repo(sys.argv[2], private=True, description=sys.argv[3] if len(sys.argv) > 3 else "")
        print(json.dumps(r, indent=2))
    
    elif action == 'github-list':
        token = os.environ.get('GITHUB_TOKEN', '')
        gh = GitHubConnector(token)
        r = gh.list_repos()
        for repo in r.get('data', [])[:10]:
            print(f"  {repo['full_name']} ({repo['stargazers_count']} stars)")
    
    elif action == 'github-push':
        token = os.environ.get('GITHUB_TOKEN', '')
        gh = GitHubConnector(token)
        r = gh.create_file(sys.argv[2], sys.argv[3], sys.argv[4])
        print(json.dumps(r, indent=2))
    
    # Facebook actions
    elif action == 'facebook-post':
        token = os.environ.get('FACEBOOK_TOKEN', '')
        page = os.environ.get('FACEBOOK_PAGE_ID', '')
        fb = FacebookConnector(token, page)
        r = fb.post_to_page(sys.argv[2])
        print(json.dumps(r, indent=2))
    
    # Twitter actions
    elif action == 'twitter-tweet':
        bearer = os.environ.get('TWITTER_BEARER', '')
        tw = TwitterConnector(bearer)
        r = tw.tweet(sys.argv[2])
        print(json.dumps(r, indent=2))
    
    # Telegram actions
    elif action == 'telegram-send':
        token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
        chat = sys.argv[3] if len(sys.argv) > 3 else os.environ.get('TELEGRAM_CHAT_ID', '')
        tg = TelegramConnector(token, chat)
        r = tg.send_message(sys.argv[2])
        print(json.dumps(r, indent=2))
    
    # Webhook
    elif action == 'webhook':
        url = sys.argv[2]
        method = sys.argv[3] if len(sys.argv) > 3 else 'POST'
        data = sys.argv[4] if len(sys.argv) > 4 else None
        r = WebhookConnector.send(url, method, None, None, json.loads(data) if data else None)
        print(json.dumps(r, indent=2))
    
    # Generate app
    elif action == 'generate-app':
        name = sys.argv[2]
        desc = sys.argv[3] if len(sys.argv) > 3 else ""
        html = AppPublisher.generate_landing_page(name, desc)
        with open(f'{name}.html', 'w') as f:
            f.write(html)
        print(f"Generated {name}.html ({len(html)} chars)")
    
    else:
        print(f"Unknown action: {action}")
