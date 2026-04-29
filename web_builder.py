#!/usr/bin/env python3
"""
LILJR WEB BUILDER v1.0
Talk to it, it builds and deploys full web apps.
Generates HTML/CSS/JS from text, deploys to Vercel/Netlify.
"""
import os, sys, json, subprocess, re, time
from datetime import datetime

REPO_DIR = os.path.expanduser('~/liljr-autonomous')
DEPLOY_DIR = os.path.expanduser('~/liljr-deploy')

# ═══════════════════════════════════════════════════════════════
# FRONTEND TEMPLATES
# ═══════════════════════════════════════════════════════════════

LANDING_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: {{bg_color}}; color: {{text_color}}; }
        .hero { min-height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 2rem; }
        .hero h1 { font-size: clamp(2.5rem, 8vw, 6rem); font-weight: 900; margin-bottom: 1rem; background: linear-gradient(135deg, {{accent_color}}, {{accent2_color}}); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .hero p { font-size: clamp(1rem, 3vw, 1.5rem); max-width: 600px; margin-bottom: 2rem; opacity: 0.8; }
        .cta { display: inline-block; padding: 1rem 2rem; background: {{accent_color}}; color: white; text-decoration: none; border-radius: 50px; font-weight: 700; font-size: 1.1rem; transition: transform 0.2s, box-shadow 0.2s; }
        .cta:hover { transform: translateY(-3px); box-shadow: 0 10px 40px rgba(0,0,0,0.3); }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem; padding: 4rem 2rem; max-width: 1200px; margin: 0 auto; }
        .feature { background: {{card_bg}}; padding: 2rem; border-radius: 20px; transition: transform 0.2s; }
        .feature:hover { transform: translateY(-5px); }
        .feature h3 { font-size: 1.3rem; margin-bottom: 0.5rem; color: {{accent_color}}; }
        .feature p { opacity: 0.7; line-height: 1.6; }
        footer { text-align: center; padding: 2rem; opacity: 0.5; font-size: 0.9rem; }
        @media (max-width: 768px) { .features { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <section class="hero">
        <h1>{{headline}}</h1>
        <p>{{subtitle}}</p>
        <a href="{{cta_link}}" class="cta">{{cta_text}}</a>
    </section>
    <section class="features">
        {{features}}
    </section>
    <footer>{{footer}}</footer>
</body>
</html>"""

DASHBOARD_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f0f23; color: #e0e0e0; }
        .sidebar { position: fixed; left: 0; top: 0; width: 250px; height: 100vh; background: #1a1a2e; padding: 2rem 1rem; }
        .sidebar h2 { font-size: 1.5rem; margin-bottom: 2rem; color: #00d4ff; }
        .nav-item { display: block; padding: 0.8rem 1rem; color: #a0a0a0; text-decoration: none; border-radius: 10px; margin-bottom: 0.5rem; transition: all 0.2s; }
        .nav-item:hover, .nav-item.active { background: #00d4ff22; color: #00d4ff; }
        .main { margin-left: 250px; padding: 2rem; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
        .stat-card { background: #1a1a2e; padding: 1.5rem; border-radius: 15px; border: 1px solid #2a2a4e; }
        .stat-card h4 { font-size: 0.9rem; color: #a0a0a0; margin-bottom: 0.5rem; }
        .stat-card .value { font-size: 2rem; font-weight: 700; color: #00d4ff; }
        .content-area { background: #1a1a2e; border-radius: 15px; padding: 2rem; min-height: 400px; }
        @media (max-width: 768px) { .sidebar { display: none; } .main { margin-left: 0; } }
    </style>
</head>
<body>
    <nav class="sidebar">
        <h2>{{title}}</h2>
        {{nav_items}}
    </nav>
    <main class="main">
        <div class="header">
            <h1>{{page_title}}</h1>
            <span>{{user}}</span>
        </div>
        <div class="stats">
            {{stats}}
        </div>
        <div class="content-area">
            {{content}}
        </div>
    </main>
</body>
</html>"""

# ═══════════════════════════════════════════════════════════════
# APP BUILDER
# ═══════════════════════════════════════════════════════════════

class WebBuilder:
    def __init__(self):
        self.deploy_dir = DEPLOY_DIR
        os.makedirs(self.deploy_dir, exist_ok=True)
    
    def build_landing(self, config):
        """Build a landing page from config dict."""
        defaults = {
            'title': 'LilJR',
            'headline': 'The Future is Autonomous',
            'subtitle': 'Trade. Build. Deploy. All from your phone.',
            'cta_text': 'Get Started',
            'cta_link': '#',
            'bg_color': '#0a0a1a',
            'text_color': '#ffffff',
            'accent_color': '#00d4ff',
            'accent2_color': '#ff6b6b',
            'card_bg': '#111122',
            'footer': 'Built with LilJR',
            'features': [
                {'title': 'Autonomous Trading', 'desc': 'AI-powered trades that run 24/7 while you sleep.'},
                {'title': 'Self-Healing', 'desc': 'Detects crashes, pulls fixes, restarts itself.'},
                {'title': 'Voice Control', 'desc': 'Talk to your terminal. It listens and executes.'},
            ]
        }
        defaults.update(config)
        
        # Build features HTML
        features_html = ''
        for feat in defaults['features']:
            features_html += f'<div class="feature"><h3>{feat["title"]}</h3><p>{feat["desc"]}</p></div>'
        defaults['features'] = features_html
        
        html = LANDING_PAGE_TEMPLATE
        for key, val in defaults.items():
            html = html.replace(f'{{{{{key}}}}}', str(val))
        
        filepath = os.path.join(self.deploy_dir, 'index.html')
        with open(filepath, 'w') as f:
            f.write(html)
        
        return filepath
    
    def build_dashboard(self, config):
        """Build a dashboard from config."""
        defaults = {
            'title': 'LilJR Dashboard',
            'page_title': 'Overview',
            'user': 'Admin',
            'nav_items': [
                {'label': 'Overview', 'href': '#', 'active': True},
                {'label': 'Trades', 'href': '#trades'},
                {'label': 'Watchlist', 'href': '#watchlist'},
                {'label': 'Settings', 'href': '#settings'},
            ],
            'stats': [
                {'label': 'Portfolio Value', 'value': '$12,900'},
                {'label': 'Active Trades', 'value': '7'},
                {'label': 'Win Rate', 'value': '68%'},
                {'label': 'Alerts', 'value': '3'},
            ],
            'content': '<p>Welcome to your command center.</p>'
        }
        defaults.update(config)
        
        nav_html = ''
        for item in defaults['nav_items']:
            active = ' active' if item.get('active') else ''
            nav_html += f'<a href="{item["href"]}" class="nav-item{active}">{item["label"]}</a>'
        defaults['nav_items'] = nav_html
        
        stats_html = ''
        for stat in defaults['stats']:
            stats_html += f'<div class="stat-card"><h4>{stat["label"]}</h4><div class="value">{stat["value"]}</div></div>'
        defaults['stats'] = stats_html
        
        html = DASHBOARD_TEMPLATE
        for key, val in defaults.items():
            html = html.replace(f'{{{{{key}}}}}', str(val))
        
        filepath = os.path.join(self.deploy_dir, 'dashboard.html')
        with open(filepath, 'w') as f:
            f.write(html)
        
        return filepath
    
    def deploy_to_vercel(self, project_name='liljr-app'):
        """Deploy current build to Vercel."""
        os.chdir(self.deploy_dir)
        
        # Initialize if needed
        if not os.path.exists(os.path.join(self.deploy_dir, '.git')):
            subprocess.run(['git', 'init'], check=False)
            subprocess.run(['git', 'add', '.'], check=False)
            subprocess.run(['git', 'commit', '-m', 'Initial deploy'], check=False)
        
        # Check for Vercel CLI
        vercel_check = subprocess.run(['which', 'vercel'], capture_output=True, text=True)
        if vercel_check.returncode != 0:
            # Try npx
            deploy_cmd = ['npx', 'vercel', '--yes', '--prod']
        else:
            deploy_cmd = ['vercel', '--yes', '--prod']
        
        r = subprocess.run(deploy_cmd, capture_output=True, text=True, timeout=120)
        
        return {
            'success': r.returncode == 0,
            'stdout': r.stdout,
            'stderr': r.stderr,
            'url': self._extract_url(r.stdout)
        }
    
    def _extract_url(self, text):
        """Extract Vercel URL from deploy output."""
        match = re.search(r'https://[a-z0-9-]+\.vercel\.app', text)
        return match.group(0) if match else None
    
    def push_to_github_pages(self, repo_name='liljr-app'):
        """Deploy as GitHub Pages."""
        os.chdir(self.deploy_dir)
        
        if not os.path.exists(os.path.join(self.deploy_dir, '.git')):
            subprocess.run(['git', 'init'], check=False)
        
        # Set remote
        remote_url = f'https://github.com/signsafepro-create/{repo_name}.git'
        subprocess.run(['git', 'remote', 'add', 'origin', remote_url], check=False)
        
        subprocess.run(['git', 'add', '.'], check=False)
        subprocess.run(['git', 'commit', '-m', f'Deploy {datetime.now()}'], check=False)
        r = subprocess.run(['git', 'push', '-u', 'origin', 'main', '--force'], capture_output=True, text=True, timeout=60)
        
        return {
            'success': r.returncode == 0,
            'url': f'https://signsafepro-create.github.io/{repo_name}' if r.returncode == 0 else None,
            'error': r.stderr if r.returncode != 0 else None
        }

# ═══════════════════════════════════════════════════════════════
# COMMAND PROCESSOR
# ═══════════════════════════════════════════════════════════════

def process_command(text):
    """Process a natural language build command."""
    builder = WebBuilder()
    
    text = text.lower().strip()
    
    # Build landing page
    if any(word in text for word in ['landing', 'homepage', 'front page', 'site']):
        config = {}
        
        # Extract title/headline
        if 'for' in text:
            config['title'] = text.split('for')[1].strip().title()
            config['headline'] = config['title']
        
        filepath = builder.build_landing(config)
        return {
            'status': 'built',
            'type': 'landing_page',
            'filepath': filepath,
            'message': f'Landing page built at {filepath}'
        }
    
    # Build dashboard
    if any(word in text for word in ['dashboard', 'app', 'panel', 'control']):
        config = {}
        if 'for' in text:
            config['title'] = text.split('for')[1].strip().title()
        
        filepath = builder.build_dashboard(config)
        return {
            'status': 'built',
            'type': 'dashboard',
            'filepath': filepath,
            'message': f'Dashboard built at {filepath}'
        }
    
    # Deploy
    if any(word in text for word in ['deploy', 'push', 'ship', 'launch', 'publish']):
        if 'vercel' in text or 'now' in text:
            result = builder.deploy_to_vercel()
        else:
            result = builder.push_to_github_pages()
        
        return {
            'status': 'deployed' if result['success'] else 'failed',
            'result': result
        }
    
    return {'status': 'unknown', 'message': 'Try: build landing page for my app, build dashboard, deploy to vercel'}

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("LilJR Web Builder v1.0")
        print("Usage: python web_builder.py '<command>'")
        print('Examples:')
        print('  python web_builder.py "build landing page for liljr"')
        print('  python web_builder.py "build dashboard"')
        print('  python web_builder.py "deploy to vercel"')
        sys.exit(1)
    
    text = ' '.join(sys.argv[1:])
    result = process_command(text)
    print(json.dumps(result, indent=2))
