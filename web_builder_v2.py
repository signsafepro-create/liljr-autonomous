#!/usr/bin/env python3
"""
LILJR WEB BUILDER v2.0 — Self-Modifying, Self-Publishing, Self-Healing
Builds web apps, business sites, landing pages from natural language.
Changes its own look. Deploys itself. Autonomous.
"""
import os, json, re, time, random, base64

class WebBuilderV2:
    THEMES = {
        'dark_empire': {
            'bg': '#0a0a0a', 'fg': '#e0e0e0', 'accent': '#00f0ff',
            'secondary': '#7000ff', 'card_bg': '#111', 'card_border': '#222',
            'btn_bg': '#00f0ff', 'btn_fg': '#000', 'font': 'system-ui, sans-serif',
            'gradient': 'linear-gradient(90deg, #00f0ff, #7000ff)',
            'shadow': '0 0 40px rgba(0,240,255,0.2)', 'radius': '12px'
        },
        'light_pro': {
            'bg': '#ffffff', 'fg': '#111111', 'accent': '#0066ff',
            'secondary': '#00cc88', 'card_bg': '#f8f9fa', 'card_border': '#e9ecef',
            'btn_bg': '#0066ff', 'btn_fg': '#fff', 'font': 'system-ui, sans-serif',
            'gradient': 'linear-gradient(90deg, #0066ff, #00cc88)',
            'shadow': '0 4px 20px rgba(0,0,0,0.08)', 'radius': '8px'
        },
        'corporate': {
            'bg': '#f5f7fa', 'fg': '#1a1a2e', 'accent': '#1a1a2e',
            'secondary': '#16213e', 'card_bg': '#fff', 'card_border': '#e1e4e8',
            'btn_bg': '#1a1a2e', 'btn_fg': '#fff', 'font': '"Segoe UI", Roboto, sans-serif',
            'gradient': 'linear-gradient(135deg, #1a1a2e, #16213e)',
            'shadow': '0 2px 12px rgba(0,0,0,0.06)', 'radius': '6px'
        },
        'playful': {
            'bg': '#faf0e6', 'fg': '#2c1810', 'accent': '#ff6b6b',
            'secondary': '#4ecdc4', 'card_bg': '#fff', 'card_border': '#ffe0e0',
            'btn_bg': '#ff6b6b', 'btn_fg': '#fff', 'font': '"Comic Sans MS", cursive, sans-serif',
            'gradient': 'linear-gradient(45deg, #ff6b6b, #4ecdc4)',
            'shadow': '0 8px 32px rgba(255,107,107,0.15)', 'radius': '20px'
        },
        'minimal': {
            'bg': '#fff', 'fg': '#000', 'accent': '#000',
            'secondary': '#666', 'card_bg': '#fff', 'card_border': '#000',
            'btn_bg': '#000', 'btn_fg': '#fff', 'font': '"Helvetica Neue", Arial, sans-serif',
            'gradient': 'none', 'shadow': 'none', 'radius': '0px'
        },
        'cyberpunk': {
            'bg': '#0d0221', 'fg': '#c77dff', 'accent': '#ff006e',
            'secondary': '#8338ec', 'card_bg': '#1a0a2e', 'card_border': '#ff006e',
            'btn_bg': '#ff006e', 'btn_fg': '#fff', 'font': '"Courier New", monospace',
            'gradient': 'linear-gradient(90deg, #ff006e, #8338ec)',
            'shadow': '0 0 30px rgba(255,0,110,0.4)', 'radius': '4px'
        }
    }

    def __init__(self, base_path='~/liljr-autonomous/web'):
        self.base = os.path.expanduser(base_path)
        os.makedirs(self.base, exist_ok=True)
        self.history = []

    def _theme_css(self, theme_name):
        t = self.THEMES.get(theme_name, self.THEMES['dark_empire'])
        return f"""
:root {{--bg:{t['bg']};--fg:{t['fg']};--accent:{t['accent']};--secondary:{t['secondary']};--card:{t['card_bg']};--border:{t['card_border']};}}
body{{font-family:{t['font']};margin:0;padding:0;background:var(--bg);color:var(--fg);line-height:1.6}}
.container{{max-width:1200px;margin:0 auto;padding:40px 20px}}
h1,h2,h3{{margin:0 0 20px}}
.gradient-text{{background:{t['gradient']};-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800}}
.card{{background:{t['card_bg']};border:1px solid {t['card_border']};border-radius:{t['radius']};padding:24px;margin:16px 0;box-shadow:{t['shadow']}}}
.btn{{display:inline-block;padding:14px 36px;background:{t['btn_bg']};color:{t['btn_fg']};text-decoration:none;border-radius:{t['radius']};font-weight:bold;transition:all 0.3s;border:none;cursor:pointer}}
.btn:hover{{transform:translateY(-2px);box-shadow:{t['shadow']}}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}}
.hero{{text-align:center;padding:100px 20px;background:{t['gradient'] if t['gradient']!='none' else t['bg']};color:{'#fff' if t['gradient']!='none' else t['fg']}}}
.hero h1{{font-size:3.5em;margin-bottom:20px}}
.nav{{display:flex;justify-content:space-between;align-items:center;padding:20px 40px;background:rgba(255,255,255,0.05);backdrop-filter:blur(10px);position:sticky;top:0;z-index:100}}
.nav a{{color:var(--fg);text-decoration:none;margin-left:24px;font-weight:500}}
.footer{{text-align:center;padding:60px 20px;border-top:1px solid var(--border);margin-top:60px}}
.price{{font-size:2.5em;font-weight:800;color:var(--accent)}}
@media(max-width:600px){{.hero h1{{font-size:2.2em}}.nav{{flex-direction:column;padding:12px}}}}
""".strip()

    def generate_business_site(self, business_name, tagline, sections, theme='dark_empire', pages=None):
        """Generate a complete multi-page business website."""
        pages = pages or ['index']
        generated = {}
        
        for page in pages:
            html = self._build_page(business_name, tagline, sections, theme, page)
            path = f"{page}.html"
            full = os.path.join(self.base, path)
            with open(full, 'w') as f:
                f.write(html)
            generated[page] = {"path": path, "size": len(html)}
            self.history.append({"time": time.time(), "action": "build", "page": page, "theme": theme})
        
        return {"status": "built", "pages": generated, "theme": theme, "base": self.base}

    def _build_page(self, name, tagline, sections, theme, active_page):
        t = self.THEMES.get(theme, self.THEMES['dark_empire'])
        nav_links = ""
        for p in ['index', 'features', 'pricing', 'about', 'contact']:
            nav_links += f'<a href="{p}.html">{p.title()}</a>'
        
        body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {tagline}</title>
<style>
{self._theme_css(theme)}
</style>
</head>
<body>
<nav class="nav">
    <div style="font-size:1.4em;font-weight:bold">{name}</div>
    <div>{nav_links}</div>
</nav>
"""
        
        for section in sections:
            body += self._render_section(section, t)
        
        body += f"""
<div class="footer">
    <p>&copy; {time.strftime('%Y')} {name}. Built by LilJR Empire.</p>
    <p style="opacity:0.5">Autonomous. Unstoppable. Yours.</p>
</div>
</body>
</html>
"""
        return body

    def _render_section(self, section, theme):
        stype = section.get('type', 'text')
        if stype == 'hero':
            return f"""
<div class="hero">
    <h1>{section.get('title', 'Welcome')}</h1>
    <p style="font-size:1.3em;max-width:600px;margin:0 auto 30px">{section.get('text', '')}</p>
    <a href="{section.get('cta_link', '#')}" class="btn">{section.get('cta', 'Get Started')}</a>
</div>
"""
        elif stype == 'features':
            cards = ''.join([f'<div class="card"><h3>⚡ {f["title"]}</h3><p>{f["desc"]}</p></div>' for f in section.get('items', [])])
            return f'<div class="container"><h2 style="text-align:center">{section.get("title", "Features")}</h2><div class="grid">{cards}</div></div>'
        elif stype == 'pricing':
            cards = ''.join([f'<div class="card" style="text-align:center"><h3>{p["name"]}</h3><div class="price">{p["price"]}</div><p>{p["desc"]}</p><a href="#" class="btn">{p.get("cta", "Choose")}</a></div>' for p in section.get('plans', [])])
            return f'<div class="container"><h2 style="text-align:center">{section.get("title", "Pricing")}</h2><div class="grid">{cards}</div></div>'
        elif stype == 'testimonials':
            cards = ''.join([f'<div class="card"><p style="font-style:italic">"{t["quote"]}"</p><p style="text-align:right;font-weight:bold">— {t["author"]}</p></div>' for t in section.get('items', [])])
            return f'<div class="container"><h2 style="text-align:center">{section.get("title", "What People Say")}</h2><div class="grid">{cards}</div></div>'
        elif stype == 'stats':
            stats = ''.join([f'<div style="text-align:center"><div style="font-size:2.5em;font-weight:bold;color:var(--accent)">{s["value"]}</div><div>{s["label"]}</div></div>' for s in section.get('items', [])])
            return f'<div class="container"><div class="card" style="display:flex;justify-content:space-around;flex-wrap:wrap">{stats}</div></div>'
        elif stype == 'cta':
            return f'<div class="container" style="text-align:center;padding:80px 20px"><h2>{section.get("title", "Ready?")}</h2><p>{section.get("text", "")}</p><a href="{section.get("link", "#")}" class="btn" style="font-size:1.2em;padding:18px 48px">{section.get("cta", "Start Now")}</a></div>'
        elif stype == 'image':
            return f'<div class="container" style="text-align:center"><img src="{section.get("src", "")}" alt="{section.get("alt", "")}" style="max-width:100%;border-radius:12px"></div>'
        else:
            return f'<div class="container"><h2>{section.get("title", "")}</h2><p>{section.get("text", "")}</p></div>'

    def generate_web_app(self, app_name, features, theme='dark_empire'):
        """Generate an interactive web app with JS."""
        t = self.THEMES.get(theme, self.THEMES['dark_empire'])
        
        # Build interactive components
        components = []
        for feat in features:
            cid = feat.get('id', 'component')
            if feat.get('type') == 'counter':
                components.append(f'<div class="card"><h3>{feat["title"]}</h3><div id="{cid}" style="font-size:3em;color:var(--accent)">0</div><button class="btn" onclick="increment(\'{cid}\')">+</button></div>')
            elif feat.get('type') == 'form':
                fields = ''.join([f'<input type="text" placeholder="{f}" style="padding:12px;margin:8px 0;width:100%;background:var(--card);border:1px solid var(--border);color:var(--fg);border-radius:8px">' for f in feat.get('fields', ['Name'])])
                components.append(f'<div class="card"><h3>{feat["title"]}</h3>{fields}<button class="btn" onclick="alert(\'Submitted!\')">Submit</button></div>')
            elif feat.get('type') == 'display':
                components.append(f'<div class="card"><h3>{feat["title"]}</h3><div id="{cid}" style="padding:20px;background:var(--card);border-radius:8px">{feat.get("content", "Loading...")}</div></div>')
            else:
                components.append(f'<div class="card"><h3>{feat["title"]}</h3><p>{feat.get("desc", "")}</p></div>')
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{app_name}</title>
<style>
{self._theme_css(theme)}
</style>
</head>
<body>
<nav class="nav"><div style="font-size:1.4em;font-weight:bold">{app_name}</div></nav>
<div class="hero">
    <h1>{app_name}</h1>
    <p>Interactive. Autonomous. Built by LilJR.</p>
</div>
<div class="container">
    <div class="grid">
        {''.join(components)}
    </div>
</div>
<script>
const state = {{}};
function increment(id) {{
    state[id] = (state[id] || 0) + 1;
    document.getElementById(id).innerText = state[id];
}}
function update(id, content) {{
    document.getElementById(id).innerHTML = content;
}}
console.log("[LILJR] {app_name} loaded. State:", state);
</script>
</body>
</html>
"""
        path = os.path.join(self.base, f"{app_name.lower().replace(' ', '_')}_app.html")
        with open(path, 'w') as f:
            f.write(html)
        return {"status": "built", "path": path, "type": "web_app", "theme": theme}

    def restyle(self, page_name, new_theme):
        """Change the theme of an existing page."""
        path = os.path.join(self.base, f"{page_name}.html")
        if not os.path.exists(path):
            return {"error": f"Page {page_name} not found"}
        
        with open(path, 'r') as f:
            content = f.read()
        
        # Extract sections from old page
        sections = self._extract_sections(content)
        
        # Rebuild with new theme
        # Parse title
        title_match = re.search(r'<title>(.*?) —', content)
        name = title_match.group(1) if title_match else "Site"
        tagline = "Restyled"
        
        new_html = self._build_page(name, tagline, sections, new_theme, page_name)
        
        with open(path, 'w') as f:
            f.write(new_html)
        
        self.history.append({"time": time.time(), "action": "restyle", "page": page_name, "theme": new_theme})
        return {"status": "restyled", "page": page_name, "theme": new_theme}

    def _extract_sections(self, html):
        """Extract sections from existing HTML for restyling."""
        sections = []
        # Simple extraction — find divs with class container or hero
        for div in re.findall(r'<div class="(hero|container)"[^>]*>(.*?)</div>', html, re.DOTALL):
            cls, content = div
            if cls == 'hero':
                h1 = re.search(r'<h1>(.*?)</h1>', content)
                p = re.search(r'<p[^>]*>(.*?)</p>', content)
                a = re.search(r'<a href="([^"]+)"[^>]*>(.*?)</a>', content)
                sections.append({
                    "type": "hero",
                    "title": h1.group(1) if h1 else "",
                    "text": p.group(1) if p else "",
                    "cta": a.group(2) if a else "",
                    "cta_link": a.group(1) if a else "#"
                })
            else:
                h2 = re.search(r'<h2>(.*?)</h2>', content)
                p = re.search(r'<p>(.*?)</p>', content)
                sections.append({
                    "type": "text",
                    "title": h2.group(1) if h2 else "",
                    "text": p.group(1) if p else ""
                })
        return sections

    def modify_page(self, page_name, instruction):
        """Modify a page based on natural language instruction."""
        path = os.path.join(self.base, f"{page_name}.html")
        if not os.path.exists(path):
            return {"error": f"Page {page_name} not found"}
        
        with open(path, 'r') as f:
            content = f.read()
        
        instruction = instruction.lower()
        
        # Parse common instructions
        if 'change color' in instruction or 'change theme' in instruction or 'make it' in instruction:
            # Detect theme
            for theme_name in self.THEMES.keys():
                if theme_name.replace('_', ' ') in instruction or theme_name in instruction:
                    return self.restyle(page_name, theme_name)
            # Default: dark_empire
            return self.restyle(page_name, 'dark_empire')
        
        elif 'add section' in instruction or 'add' in instruction:
            # Add a new section
            if 'pricing' in instruction:
                new_section = {
                    "type": "pricing",
                    "title": "Pricing",
                    "plans": [
                        {"name": "Starter", "price": "$9", "desc": "Perfect for beginners", "cta": "Start"},
                        {"name": "Pro", "price": "$29", "desc": "For serious builders", "cta": "Go Pro"},
                        {"name": "Empire", "price": "$99", "desc": "Everything unlimited", "cta": "Build Empire"}
                    ]
                }
            elif 'testimonial' in instruction or 'review' in instruction:
                new_section = {
                    "type": "testimonials",
                    "title": "What People Say",
                    "items": [
                        {"quote": "This changed everything for my business.", "author": "Alex K."},
                        {"quote": "Built my landing page in seconds. Unreal.", "author": "Sarah M."}
                    ]
                }
            elif 'stats' in instruction or 'numbers' in instruction:
                new_section = {
                    "type": "stats",
                    "items": [
                        {"value": "10K+", "label": "Users"},
                        {"value": "99.9%", "label": "Uptime"},
                        {"value": "24/7", "label": "Support"}
                    ]
                }
            else:
                new_section = {"type": "text", "title": "New Section", "text": "Content added by LilJR."}
            
            # Insert before footer
            footer_idx = content.rfind('<div class="footer">')
            if footer_idx > 0:
                section_html = self._render_section(new_section, self.THEMES['dark_empire'])
                content = content[:footer_idx] + section_html + '\n' + content[footer_idx:]
            
            with open(path, 'w') as f:
                f.write(content)
            return {"status": "modified", "page": page_name, "action": "added_section", "section": new_section["type"]}
        
        elif 'change title' in instruction or 'rename' in instruction:
            new_title = instruction.replace('change title to', '').replace('rename to', '').strip()
            if new_title:
                content = re.sub(r'<title>.*?</title>', f'<title>{new_title}</title>', content)
                with open(path, 'w') as f:
                    f.write(content)
                return {"status": "modified", "page": page_name, "action": "title_change", "new_title": new_title}
        
        return {"status": "no_change", "page": page_name, "instruction": instruction, "suggestion": "Try: 'change theme to light_pro', 'add pricing section', 'change title to New Name'"}

    def deploy_to_github(self, repo_name, branch='main'):
        """Push web assets to GitHub and enable Pages."""
        web_dir = self.base
        import subprocess
        
        # Initialize git in web dir if not already
        if not os.path.exists(os.path.join(web_dir, '.git')):
            subprocess.run(['git', 'init'], cwd=web_dir, capture_output=True)
            subprocess.run(['git', 'checkout', '-b', branch], cwd=web_dir, capture_output=True)
        
        # Add all files
        subprocess.run(['git', 'add', '.'], cwd=web_dir, capture_output=True)
        subprocess.run(['git', 'commit', '-m', f'Auto-deploy {time.strftime("%Y-%m-%d %H:%M:%S")}'], cwd=web_dir, capture_output=True)
        
        # Push to GitHub (requires remote to be set)
        result = subprocess.run(['git', 'push', 'origin', branch], cwd=web_dir, capture_output=True, text=True)
        
        # Return GitHub Pages URL
        url = f"https://{repo_name.split('/')[0]}.github.io/{repo_name.split('/')[-1]}"
        return {
            "status": "deployed" if result.returncode == 0 else "push_failed",
            "url": url,
            "output": result.stdout,
            "errors": result.stderr
        }

    def list_sites(self):
        """List all generated sites."""
        sites = []
        for f in os.listdir(self.base):
            if f.endswith('.html'):
                path = os.path.join(self.base, f)
                sites.append({
                    "name": f,
                    "size": os.path.getsize(path),
                    "modified": os.path.getmtime(path)
                })
        return sites

    def get_history(self):
        return self.history[-20:]


# CLI usage
if __name__ == '__main__':
    import sys
    builder = WebBuilderV2()
    
    if len(sys.argv) < 2:
        print("Usage: python3 web_builder_v2.py <build|app|restyle|modify|deploy|list>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'build':
        name = sys.argv[2] if len(sys.argv) > 2 else 'MyBusiness'
        tagline = sys.argv[3] if len(sys.argv) > 3 else 'Built by LilJR'
        theme = sys.argv[4] if len(sys.argv) > 4 else 'dark_empire'
        sections = [
            {"type": "hero", "title": name, "text": tagline, "cta": "Get Started"},
            {"type": "features", "title": "Features", "items": [
                {"title": "Lightning Fast", "desc": "Zero latency, instant response"},
                {"title": "Bulletproof", "desc": "Never goes down, never loses data"},
                {"title": "Self-Healing", "desc": "Fixes itself before you notice"}
            ]},
            {"type": "pricing", "title": "Pricing", "plans": [
                {"name": "Free", "price": "$0", "desc": "Start building today", "cta": "Start Free"},
                {"name": "Pro", "price": "$19", "desc": "For serious builders", "cta": "Go Pro"},
                {"name": "Empire", "price": "$49", "desc": "Unlimited everything", "cta": "Build Empire"}
            ]},
            {"type": "cta", "title": "Ready to dominate?", "text": "Join thousands building with LilJR.", "cta": "Start Now"}
        ]
        result = builder.generate_business_site(name, tagline, sections, theme)
        print(json.dumps(result, indent=2))
    
    elif cmd == 'app':
        name = sys.argv[2] if len(sys.argv) > 2 else 'MyApp'
        theme = sys.argv[3] if len(sys.argv) > 3 else 'dark_empire'
        features = [
            {"title": "Counter", "type": "counter", "id": "counter1"},
            {"title": "Contact Form", "type": "form", "fields": ["Name", "Email", "Message"]},
            {"title": "Status", "type": "display", "id": "status", "content": "System operational"}
        ]
        result = builder.generate_web_app(name, features, theme)
        print(json.dumps(result, indent=2))
    
    elif cmd == 'restyle':
        page = sys.argv[2] if len(sys.argv) > 2 else 'index'
        theme = sys.argv[3] if len(sys.argv) > 3 else 'cyberpunk'
        print(json.dumps(builder.restyle(page, theme), indent=2))
    
    elif cmd == 'modify':
        page = sys.argv[2] if len(sys.argv) > 2 else 'index'
        instruction = ' '.join(sys.argv[3:]) if len(sys.argv) > 3 else 'add pricing section'
        print(json.dumps(builder.modify_page(page, instruction), indent=2))
    
    elif cmd == 'deploy':
        repo = sys.argv[2] if len(sys.argv) > 2 else 'user/repo'
        print(json.dumps(builder.deploy_to_github(repo), indent=2))
    
    elif cmd == 'list':
        print(json.dumps(builder.list_sites(), indent=2))
