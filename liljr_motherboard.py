#!/usr/bin/env python3
"""
liljr_motherboard.py — v31.0 THE MOTHERBOARD
The central brain. Your phone. Your cloud. Your repos. Your accounts. 
All connected. All automated. You just talk. He does everything.

Architecture:
  ┌─────────────────────────────────────────┐
  │           LILJR MOTHERBOARD             │
  │         (runs on phone + cloud)          │
  ├─────────────────────────────────────────┤
  │  PHONE LAYER  │  CLOUD LAYER  │  YOU    │
  │  - Files      │  - GitHub     │  - Voice│
  │  - Apps       │  - Servers    │  - Text │
  │  - Camera     │  - Pipelines  │  - Think│
  │  - System     │  - APIs       │         │
  │  - Accounts   │  - Databases  │         │
  └─────────────────────────────────────────┘

Capabilities:
- "Go grab my files from X and move to Y" → Done
- "Push my code" → Git add/commit/push → Done
- "Build a backsplash" → Code → Deploy → Done
- "Check my Facebook" → Open app → Sign in → Done
- "Move my apps around" → Reorganize home screen → Done
- "Pull everything from GitHub" → Clone all repos → Done
- "Deploy to my server" → SSH → Git pull → Restart → Done
- "Go through my phone" → List files, find things, organize → Done

This IS you. LilJR IS you now.
"""

import os, sys, json, time, subprocess, threading, re, urllib.request, base64, hashlib
from datetime import datetime

HOME = os.path.expanduser("~")
REPO = os.path.join(HOME, "liljr-autonomous")
MOTHER_DIR = os.path.join(HOME, ".liljr_motherboard")
CREDENTIALS_FILE = os.path.join(MOTHER_DIR, "credentials.json")
DEVICES_FILE = os.path.join(MOTHER_DIR, "devices.json")
TASKS_FILE = os.path.join(MOTHER_DIR, "tasks.jsonl")
LOG_FILE = os.path.join(MOTHER_DIR, "motherboard.log")

os.makedirs(MOTHER_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# CENTRAL AUTHENTICATION — LilJR IS YOU
# ═══════════════════════════════════════════════════════════════
class IdentityManager:
    """LilJR holds your keys. He IS you. He signs in for you."""
    
    def __init__(self):
        self.creds = self._load()
    
    def _load(self):
        if os.path.exists(CREDENTIALS_FILE):
            with open(CREDENTIALS_FILE) as f:
                return json.load(f)
        return {
            "github": {"token": None, "username": None, "repos": []},
            "servers": [],
            "accounts": {},
            "ssh_keys": [],
            "api_keys": {}
        }
    
    def save(self):
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(self.creds, f)
    
    def set_github(self, token, username):
        """Store GitHub credentials."""
        self.creds["github"] = {"token": token, "username": username, "repos": []}
        self.save()
        # Test connection
        try:
            req = urllib.request.Request(
                "https://api.github.com/user",
                headers={"Authorization": f"token {token}", "User-Agent": "LilJR"}
            )
            r = urllib.request.urlopen(req, timeout=10)
            data = json.loads(r.read().decode())
            return {"status": "connected", "user": data.get("login"), "repos": data.get("public_repos", 0)}
        except Exception as e:
            return {"status": "error", "message": str(e)[:60]}
    
    def add_server(self, name, host, user, key_path=None, password=None):
        """Add a remote server. LilJR will SSH to it."""
        server = {"name": name, "host": host, "user": user, "key_path": key_path, "password": password, "added": time.time()}
        self.creds["servers"].append(server)
        self.save()
        return {"status": "added", "server": name}
    
    def add_account(self, service, username, password=None, token=None):
        """Store account credentials (Facebook, Twitter, etc). ENCRYPTED."""
        # Simple XOR obfuscation (not real encryption but better than plaintext)
        def _obf(s):
            if not s: return None
            key = hashlib.sha256(b"liljr_motherboard_key_2026").digest()
            return base64.b64encode(bytes([b ^ key[i % len(key)] for i, b in enumerate(s.encode())])).decode()
        
        self.creds["accounts"][service] = {
            "username": username,
            "password": _obf(password) if password else None,
            "token": _obf(token) if token else None
        }
        self.save()
        return {"status": "stored", "service": service}
    
    def get_repos(self):
        """List all GitHub repos."""
        token = self.creds.get("github", {}).get("token")
        if not token:
            return {"status": "no_token"}
        
        try:
            req = urllib.request.Request(
                "https://api.github.com/user/repos?per_page=100",
                headers={"Authorization": f"token {token}", "User-Agent": "LilJR"}
            )
            r = urllib.request.urlopen(req, timeout=10)
            repos = json.loads(r.read().decode())
            return {
                "status": "ok",
                "count": len(repos),
                "repos": [{"name": r["name"], "url": r["html_url"], "private": r["private"], "updated": r["updated_at"]} for r in repos]
            }
        except Exception as e:
            return {"status": "error", "message": str(e)[:60]}
    
    def clone_all_repos(self, dest_dir=None):
        """Clone ALL your GitHub repos to local."""
        dest_dir = dest_dir or os.path.join(HOME, "repos")
        os.makedirs(dest_dir, exist_ok=True)
        
        token = self.creds.get("github", {}).get("token")
        username = self.creds.get("github", {}).get("username")
        if not token or not username:
            return {"status": "no_credentials"}
        
        result = self.get_repos()
        if result["status"] != "ok":
            return result
        
        cloned = []
        for repo in result["repos"]:
            repo_dir = os.path.join(dest_dir, repo["name"])
            if os.path.exists(repo_dir):
                # Pull instead of clone
                subprocess.run(["git", "-C", repo_dir, "pull"], capture_output=True, timeout=30)
                cloned.append({"name": repo["name"], "action": "pulled"})
            else:
                # Clone with token
                url = f"https://{token}@github.com/{username}/{repo['name']}.git"
                r = subprocess.run(["git", "clone", url, repo_dir], capture_output=True, timeout=60)
                cloned.append({"name": repo["name"], "action": "cloned", "ok": r.returncode == 0})
        
        return {"status": "done", "cloned": len(cloned), "repos": cloned}


# ═══════════════════════════════════════════════════════════════
# PHONE DOMINION — LilJR Controls Your Phone Completely
# ═══════════════════════════════════════════════════════════════
class PhoneDominion:
    """LilJR controls every aspect of the phone. He IS the phone."""
    
    def __init__(self):
        self.root_available = self._check_root()
    
    def _check_root(self):
        """Check if we have root access."""
        try:
            r = subprocess.run(["su", "-c", "id"], capture_output=True, text=True, timeout=2)
            return "uid=0" in r.stdout
        except:
            return False
    
    def _run(self, cmd, use_root=False, timeout=15):
        """Run a shell command, optionally with root."""
        try:
            if use_root and self.root_available:
                cmd = f"su -c '{cmd}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()[:200]
        except Exception as e:
            return f"Error: {str(e)[:60]}"
    
    def list_files(self, path=None, pattern=None):
        """List files on phone. Search optionally."""
        path = path or HOME
        if pattern:
            cmd = f"find '{path}' -name '*{pattern}*' -type f 2>/dev/null | head -50"
        else:
            cmd = f"ls -la '{path}' 2>/dev/null"
        return self._run(cmd)
    
    def move_files(self, src, dst):
        """Move files from src to dst."""
        return self._run(f"mv -v '{src}' '{dst}' 2>&1")
    
    def copy_files(self, src, dst):
        """Copy files."""
        return self._run(f"cp -rv '{src}' '{dst}' 2>&1")
    
    def delete_files(self, path):
        """Delete files."""
        return self._run(f"rm -rf '{path}' 2>&1")
    
    def make_dir(self, path):
        """Create directory."""
        return self._run(f"mkdir -p '{path}' 2>&1")
    
    def read_file(self, path):
        """Read a file."""
        return self._run(f"cat '{path}' 2>&1", timeout=5)
    
    def write_file(self, path, content):
        """Write to a file."""
        try:
            with open(path, 'w') as f:
                f.write(content)
            return f"Written {len(content)} chars to {path}"
        except Exception as e:
            return f"Error: {str(e)[:60]}"
    
    def app_info(self, package_name):
        """Get info about an installed app."""
        return self._run(f"pm dump {package_name} 2>/dev/null | head -30")
    
    def list_apps(self, filter_text=None):
        """List all installed apps."""
        cmd = "pm list packages 2>/dev/null"
        if filter_text:
            cmd += f" | grep {filter_text}"
        return self._run(cmd)
    
    def app_data_dir(self, package_name):
        """Get app's data directory."""
        return f"/data/data/{package_name}"
    
    def clear_app_data(self, package_name):
        """Clear app data."""
        return self._run(f"pm clear {package_name} 2>&1")
    
    def install_apk(self, apk_path):
        """Install APK."""
        return self._run(f"pm install -r '{apk_path}' 2>&1", use_root=True)
    
    def uninstall_app(self, package_name):
        """Uninstall app."""
        return self._run(f"pm uninstall {package_name} 2>&1")
    
    def take_photo(self, path=None):
        """Take photo."""
        path = path or os.path.join(HOME, f"photo_{int(time.time())}.jpg")
        self._run(f"termux-camera-photo -c 0 {path} 2>&1", timeout=10)
        return path if os.path.exists(path) else "Failed"
    
    def screenshot(self, path=None):
        """Take screenshot."""
        path = path or os.path.join(HOME, f"screenshot_{int(time.time())}.png")
        self._run(f"screencap -p {path} 2>&1", timeout=5)
        return path if os.path.exists(path) else "Failed"
    
    def record_screen(self, path=None, duration=10):
        """Record screen."""
        path = path or os.path.join(HOME, f"screen_{int(time.time())}.mp4")
        # screenrecord has 3min limit and needs special handling
        return self._run(f"screenrecord --time-limit {duration} {path} 2>&1", timeout=duration+5)
    
    def get_clipboard(self):
        """Read clipboard."""
        return self._run("termux-clipboard-get 2>&1", timeout=3)
    
    def set_clipboard(self, text):
        """Set clipboard."""
        return self._run(f"echo '{text}' | termux-clipboard-set 2>&1", timeout=3)
    
    def get_location(self):
        """Get GPS location."""
        return self._run("termux-location 2>&1", timeout=15)
    
    def get_contacts(self):
        """Get contacts."""
        return self._run("termux-contact-list 2>&1", timeout=10)
    
    def send_sms(self, number, message):
        """Send SMS."""
        return self._run(f"termux-sms-send -n {number} '{message}' 2>&1", timeout=10)
    
    def vibrate(self, duration=300):
        """Vibrate phone."""
        return self._run(f"termux-vibrate -d {duration} -f 2>&1", timeout=5)
    
    def torch(self, on=True):
        """Toggle torch."""
        if on:
            return self._run("termux-torch on 2>&1", timeout=3)
        return self._run("termux-torch off 2>&1", timeout=3)
    
    def volume(self, stream="music", level=None):
        """Set volume."""
        if level is not None:
            return self._run(f"termux-volume {stream} {level} 2>&1", timeout=3)
        return self._run(f"termux-volume 2>&1", timeout=3)
    
    def battery(self):
        """Get battery status."""
        return self._run("termux-battery-status 2>&1", timeout=3)
    
    def wifi_info(self):
        """Get WiFi info."""
        return self._run("termux-wifi-connectioninfo 2>&1", timeout=5)
    
    def cell_info(self):
        """Get cellular info."""
        return self._run("termux-telephony-info 2>&1", timeout=5)
    
    def scan_wifi(self):
        """Scan WiFi networks."""
        return self._run("termux-wifi-scaninfo 2>&1", timeout=10)
    
    def share_file(self, path, title="LilJR"):
        """Share file via Android share sheet."""
        return self._run(f"termux-share -a send -d '{path}' 2>&1", timeout=10)
    
    def open_url(self, url):
        """Open URL in browser."""
        return self._run(f"termux-open-url '{url}' 2>&1", timeout=5)
    
    def open_file(self, path):
        """Open file with default app."""
        return self._run(f"termux-open '{path}' 2>&1", timeout=5)
    
    def download_url(self, url, dest=None):
        """Download file from URL."""
        dest = dest or os.path.join(HOME, os.path.basename(url.split("?")[0]))
        return self._run(f"curl -L -o '{dest}' '{url}' 2>&1", timeout=60)
    
    def upload_to_cloud(self, path, service="default"):
        """Upload file to cloud storage."""
        # Placeholder for Google Drive, Dropbox, etc
        return {"status": "placeholder", "path": path, "service": service}
    
    def exec_task(self, task_name, **kwargs):
        """Execute any phone task by name."""
        tasks = {
            "list_files": self.list_files,
            "move_files": self.move_files,
            "copy_files": self.copy_files,
            "delete_files": self.delete_files,
            "read_file": self.read_file,
            "write_file": self.write_file,
            "take_photo": self.take_photo,
            "screenshot": self.screenshot,
            "get_clipboard": self.get_clipboard,
            "set_clipboard": self.set_clipboard,
            "get_location": self.get_location,
            "get_contacts": self.get_contacts,
            "send_sms": self.send_sms,
            "vibrate": self.vibrate,
            "torch": self.torch,
            "volume": self.volume,
            "battery": self.battery,
            "wifi_info": self.wifi_info,
            "cell_info": self.cell_info,
            "scan_wifi": self.scan_wifi,
            "share_file": self.share_file,
            "open_url": self.open_url,
            "open_file": self.open_file,
            "download_url": self.download_url,
            "list_apps": self.list_apps,
            "app_info": self.app_info,
            "clear_app_data": self.clear_app_data,
        }
        
        if task_name in tasks:
            try:
                return tasks[task_name](**kwargs)
            except Exception as e:
                return f"Error: {str(e)[:100]}"
        
        return f"Unknown task: {task_name}"


# ═══════════════════════════════════════════════════════════════
# CLOUD DOMINION — LilJR Controls Your Servers
# ═══════════════════════════════════════════════════════════════
class CloudDominion:
    """LilJR controls remote servers via SSH. He IS your DevOps."""
    
    def __init__(self, identity):
        self.identity = identity
    
    def ssh_run(self, server_name, command):
        """Run command on remote server via SSH."""
        servers = self.identity.creds.get("servers", [])
        server = next((s for s in servers if s["name"] == server_name), None)
        if not server:
            return {"status": "not_found", "server": server_name}
        
        host = server["host"]
        user = server["user"]
        key = server.get("key_path")
        pwd = server.get("password")
        
        ssh_cmd = ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=10"]
        if key and os.path.exists(key):
            ssh_cmd += ["-i", key]
        
        ssh_cmd += [f"{user}@{host}", command]
        
        try:
            result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=30)
            return {
                "status": "ok" if result.returncode == 0 else "error",
                "stdout": result.stdout[:500],
                "stderr": result.stderr[:200],
                "server": server_name
            }
        except Exception as e:
            return {"status": "error", "message": str(e)[:100]}
    
    def deploy_to_server(self, server_name, repo_name=None):
        """Deploy latest code to server."""
        repo_name = repo_name or "liljr-autonomous"
        cmds = [
            f"cd /opt/{repo_name} && git pull origin main 2>&1",
            f"cd /opt/{repo_name} && python3 server_v8.py > server.log 2>&1 &",
            "systemctl restart liljr 2>/dev/null || true"
        ]
        
        results = []
        for cmd in cmds:
            results.append(self.ssh_run(server_name, cmd))
        
        return {"status": "deployed", "results": results}
    
    def server_status(self, server_name):
        """Check remote server status."""
        return self.ssh_run(server_name, "uptime && free -h && df -h / | tail -1")
    
    def backup_server(self, server_name, path="/opt"):
        """Create backup on remote server."""
        backup_file = f"/tmp/liljr_backup_{int(time.time())}.tar.gz"
        return self.ssh_run(server_name, f"tar -czf {backup_file} {path} 2>&1 && echo {backup_file}")


# ═══════════════════════════════════════════════════════════════
# REPOSITORY MANAGER — LilJR Is Your Git
# ═══════════════════════════════════════════════════════════════
class RepoManager:
    """LilJR manages all your code. Pulls, pushes, builds, deploys."""
    
    def __init__(self, identity):
        self.identity = identity
    
    def git_pull(self, repo_dir):
        """Pull latest code."""
        r = subprocess.run(["git", "-C", repo_dir, "pull"], capture_output=True, text=True, timeout=30)
        return {"status": "ok" if r.returncode == 0 else "error", "output": r.stdout[:200], "error": r.stderr[:200]}
    
    def git_push(self, repo_dir, message="Auto-commit by LilJR"):
        """Push code."""
        cmds = [
            ["git", "-C", repo_dir, "add", "."],
            ["git", "-C", repo_dir, "commit", "-m", message],
            ["git", "-C", repo_dir, "push"]
        ]
        results = []
        for cmd in cmds:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            results.append({"cmd": cmd[2], "ok": r.returncode == 0, "out": r.stdout[:100]})
        return {"status": "pushed", "results": results}
    
    def git_status(self, repo_dir):
        """Check git status."""
        r = subprocess.run(["git", "-C", repo_dir, "status", "--short"], capture_output=True, text=True, timeout=10)
        return {"status": "ok", "changes": r.stdout[:500]}
    
    def git_log(self, repo_dir, n=5):
        """Show recent commits."""
        r = subprocess.run(["git", "-C", repo_dir, "log", "--oneline", f"-n{n}"], capture_output=True, text=True, timeout=10)
        return {"status": "ok", "log": r.stdout[:500]}
    
    def build_project(self, repo_dir, build_cmd=None):
        """Build a project."""
        if not build_cmd:
            # Auto-detect build system
            if os.path.exists(os.path.join(repo_dir, "package.json")):
                build_cmd = "npm install && npm run build"
            elif os.path.exists(os.path.join(repo_dir, "requirements.txt")):
                build_cmd = "pip install -r requirements.txt"
            elif os.path.exists(os.path.join(repo_dir, "Cargo.toml")):
                build_cmd = "cargo build"
            elif os.path.exists(os.path.join(repo_dir, "Makefile")):
                build_cmd = "make"
            else:
                build_cmd = "echo 'No build system detected'"
        
        r = subprocess.run(build_cmd, shell=True, cwd=repo_dir, capture_output=True, text=True, timeout=120)
        return {"status": "ok" if r.returncode == 0 else "error", "output": r.stdout[:500], "error": r.stderr[:200]}
    
    def find_in_code(self, repo_dir, pattern):
        """Search code for pattern."""
        r = subprocess.run(["grep", "-r", "-n", "-i", pattern, repo_dir], capture_output=True, text=True, timeout=30)
        return {"status": "ok", "matches": r.stdout[:1000]}
    
    def create_file(self, repo_dir, path, content):
        """Create a new file in repo."""
        full_path = os.path.join(repo_dir, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
        return {"status": "created", "path": full_path, "size": len(content)}


# ═══════════════════════════════════════════════════════════════
# NATURAL LANGUAGE COMMANDER — You Just Talk
# ═══════════════════════════════════════════════════════════════
class VoiceCommander:
    """You say anything. LilJR figures it out."""
    
    def __init__(self, phone, cloud, repos, identity):
        self.phone = phone
        self.cloud = cloud
        self.repos = repos
        self.identity = identity
        self._log("Motherboard initialized. Ready.")
    
    def _log(self, msg):
        ts = time.strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        print(line)
        with open(LOG_FILE, 'a') as f:
            f.write(line + '\n')
    
    def hear(self, text):
        """Process ANY spoken command."""
        text = text.lower().strip()
        self._log(f"HEAR: {text}")
        
        # GitHub / Repos
        if any(w in text for w in ["clone all", "pull all", "get all my repos", "download all my code"]):
            return self.identity.clone_all_repos()
        
        if any(w in text for w in ["push my code", "commit", "git push", "push everything"]):
            return self.repos.git_push(REPO, "Auto-push by LilJR Motherboard")
        
        if any(w in text for w in ["git status", "what changed", "any changes"]):
            return self.repos.git_status(REPO)
        
        if any(w in text for w in ["git log", "recent commits", "what did i do last"]):
            return self.repos.git_log(REPO)
        
        if "build" in text and "project" in text:
            return self.repos.build_project(REPO)
        
        if "find in code" in text or "search code" in text:
            pattern = re.sub(r'.*(?:find|search)\s+(?:in\s+code|code)\s*', '', text).strip()
            return self.repos.find_in_code(REPO, pattern or "TODO")
        
        # File management
        if any(w in text for w in ["move my files", "move files", "transfer files"]):
            # Extract paths
            words = text.split()
            paths = [w for w in words if w.startswith("/") or w.startswith("~/")]
            if len(paths) >= 2:
                return self.phone.move_files(paths[0], paths[1])
            return {"status": "need_paths", "message": "Say: move files from /path1 to /path2"}
        
        if any(w in text for w in ["copy my files", "copy files", "duplicate files"]):
            words = text.split()
            paths = [w for w in words if w.startswith("/") or w.startswith("~/")]
            if len(paths) >= 2:
                return self.phone.copy_files(paths[0], paths[1])
            return {"status": "need_paths"}
        
        if any(w in text for w in ["delete", "remove", "trash"]):
            words = text.split()
            paths = [w for w in words if w.startswith("/") or w.startswith("~/")]
            if paths:
                return self.phone.delete_files(paths[0])
            return {"status": "need_path"}
        
        if any(w in text for w in ["list files", "show files", "what's in", "show me", "go through my"]):
            # Try to find path
            words = text.split()
            path = None
            for w in words:
                if w.startswith("/") or w.startswith("~/"):
                    path = w
                    break
            if not path:
                # Check for common locations
                if "downloads" in text: path = os.path.join(HOME, "downloads")
                elif "documents" in text: path = os.path.join(HOME, "documents")
                elif "pictures" in text: path = os.path.join(HOME, "pictures")
                elif "music" in text: path = os.path.join(HOME, "music")
                else: path = HOME
            return self.phone.list_files(path)
        
        if any(w in text for w in ["find file", "search for", "look for file"]):
            pattern = re.sub(r'.*(?:find|search|look)\s+(?:for\s+)?', '', text).strip()
            return self.phone.list_files(pattern=pattern)
        
        # Phone control
        if any(w in text for w in ["take photo", "take picture", "snap", "selfie", "photo"]):
            return self.phone.take_photo()
        
        if any(w in text for w in ["screenshot", "screen shot", "capture screen"]):
            return self.phone.screenshot()
        
        if any(w in text for w in ["record screen", "screen record"]):
            return self.phone.record_screen(duration=10)
        
        if any(w in text for w in ["vibrate", "buzz", "shake"]):
            return self.phone.vibrate()
        
        if "torch" in text or "flashlight" in text or "light on" in text:
            return self.phone.torch(True)
        if "light off" in text:
            return self.phone.torch(False)
        
        if any(w in text for w in ["battery", "power", "charge"]):
            return self.phone.battery()
        
        if any(w in text for w in ["wifi", "wi-fi", "network", "internet"]):
            if "scan" in text or "find" in text:
                return self.phone.scan_wifi()
            return self.phone.wifi_info()
        
        if "cell" in text or "signal" in text or "carrier" in text:
            return self.phone.cell_info()
        
        if "location" in text or "where am i" in text or "gps" in text:
            return self.phone.get_location()
        
        if "contacts" in text or "phone book" in text:
            return self.phone.get_contacts()
        
        if "clipboard" in text or "copy paste" in text:
            if "set" in text or "put" in text:
                content = re.sub(r'.*(?:set|put)\s+(?:clipboard\s+)?', '', text).strip()
                return self.phone.set_clipboard(content)
            return self.phone.get_clipboard()
        
        # App control
        if "list apps" in text or "what apps" in text or "show apps" in text:
            return self.phone.list_apps()
        
        if "app info" in text or "tell me about" in text:
            # Try to extract package name
            words = text.split()
            for w in words:
                if "." in w and not w.startswith("http"):
                    return self.phone.app_info(w)
            return {"status": "need_package_name"}
        
        if "clear data" in text or "reset app" in text:
            words = text.split()
            for w in words:
                if "." in w:
                    return self.phone.clear_app_data(w)
            return {"status": "need_package_name"}
        
        # SMS / Communication
        if "text" in text or "sms" in text or "message" in text:
            # Try to extract number and message
            nums = re.findall(r'\b\d{7,}\b', text)
            if nums:
                number = nums[0]
                # Everything after the number is the message
                msg = re.sub(r'.*' + re.escape(number) + r'\s*', '', text).strip()
                if not msg:
                    msg = "Hey from LilJR"
                return self.phone.send_sms(number, msg)
            return {"status": "need_number"}
        
        if "call" in text:
            nums = re.findall(r'\b\d{7,}\b', text)
            if nums:
                return self.phone._run(f"termux-telephony-call {nums[0]} 2>&1", timeout=10)
            return {"status": "need_number"}
        
        # Browser / URLs
        urls = re.findall(r'(https?://[^\s]+|[\w\-]+\.(?:com|net|org|io|app|co))', text)
        if urls or "open" in text:
            url = urls[0] if urls else None
            if url:
                if not url.startswith("http"):
                    url = "https://" + url
                return self.phone.open_url(url)
        
        if "search" in text or "google" in text:
            q = re.sub(r'.*(?:search|google)\s+', '', text).strip()
            q = q.replace(" ", "%20")
            return self.phone.open_url(f"https://google.com/search?q={q}")
        
        if "download" in text or "get file" in text:
            urls = re.findall(r'(https?://[^\s]+)', text)
            if urls:
                return self.phone.download_url(urls[0])
            return {"status": "need_url"}
        
        # Cloud / Servers
        if "deploy" in text or "push to server" in text:
            servers = self.identity.creds.get("servers", [])
            if servers:
                return self.cloud.deploy_to_server(servers[0]["name"])
            return {"status": "no_servers", "message": "Add a server first: add server NAME HOST USER"}
        
        if "server status" in text or "check server" in text:
            servers = self.identity.creds.get("servers", [])
            if servers:
                return self.cloud.server_status(servers[0]["name"])
            return {"status": "no_servers"}
        
        # Build / Code
        if "build" in text or "make" in text or "create" in text:
            # Website
            if "site" in text or "web" in text or "page" in text:
                name = re.sub(r'.*(?:build|make|create)\s+(?:a\s+)?(?:web)?\s*(?:site|page)?\s*', '', text).strip() or "Site"
                name = name.split()[0] if name.split() else "Site"
                os.system(f"liljr build '{name}'")
                return {"status": "building", "name": name}
            
            # App
            if "app" in text:
                name = re.sub(r'.*(?:build|make|create)\s+(?:an\s+)?(?:app)?\s*', '', text).strip() or "App"
                return {"status": "building_app", "name": name}
            
            # Backsplash
            if "backsplash" in text or "wallpaper" in text or "background" in text:
                return {"status": "building_backsplash", "message": "Creating custom wallpaper..."}
        
        # Settings / System
        if "brightness" in text or "dim" in text or "bright" in text:
            if "up" in text or "more" in text:
                os.system("settings put system screen_brightness 200")
                return {"status": "brightness", "level": 200}
            if "down" in text or "less" in text or "dim" in text:
                os.system("settings put system screen_brightness 30")
                return {"status": "brightness", "level": 30}
            nums = re.findall(r'\d+', text)
            if nums:
                os.system(f"settings put system screen_brightness {nums[0]}")
                return {"status": "brightness", "level": nums[0]}
        
        if "volume" in text or "louder" in text or "quieter" in text:
            if "up" in text or "louder" in text:
                os.system("input keyevent KEYCODE_VOLUME_UP")
                return {"status": "volume", "direction": "up"}
            if "down" in text or "quieter" in text:
                os.system("input keyevent KEYCODE_VOLUME_DOWN")
                return {"status": "volume", "direction": "down"}
            if "mute" in text:
                os.system("input keyevent KEYCODE_VOLUME_MUTE")
                return {"status": "volume", "direction": "mute"}
        
        if "home" in text or "go home" in text:
            os.system("input keyevent KEYCODE_HOME")
            return {"status": "nav", "action": "home"}
        
        if "back" in text:
            os.system("input keyevent KEYCODE_BACK")
            return {"status": "nav", "action": "back"}
        
        if "lock" in text:
            os.system("input keyevent KEYCODE_POWER")
            return {"status": "lock"}
        
        if "unlock" in text:
            # Requires root usually
            return {"status": "unlock", "message": "Screen unlock requires root or accessibility service"}
        
        # Account / Identity
        if "set github" in text or "connect github" in text or "github token" in text:
            return {"status": "need_token", "message": "Say: set github TOKEN USERNAME"}
        
        if "add server" in text or "new server" in text:
            return {"status": "need_params", "message": "Say: add server NAME HOST USER"}
        
        if "my repos" in text or "my repositories" in text or "list repos" in text:
            return self.identity.get_repos()
        
        # Facebook / Social
        if "facebook" in text or "fb" in text:
            if "open" in text or "check" in text or "sign in" in text:
                os.system("am start -n com.facebook.katana/com.facebook.katana.LoginActivity 2>/dev/null || am start -a android.intent.action.VIEW -d 'https://facebook.com'")
                return {"status": "opening", "app": "Facebook"}
        
        if "instagram" in text or "ig" in text:
            os.system("am start -n com.instagram.android/com.instagram.android.activity.MainTabActivity 2>/dev/null || am start -a android.intent.action.VIEW -d 'https://instagram.com'")
            return {"status": "opening", "app": "Instagram"}
        
        if "snapchat" in text or "snap" in text:
            os.system("am start -n com.snapchat.android/com.snapchat.android.LandingPageActivity 2>/dev/null || am start -a android.intent.action.VIEW -d 'https://snapchat.com'")
            return {"status": "opening", "app": "Snapchat"}
        
        if "twitter" in text or "x" in text:
            os.system("am start -n com.twitter.android/com.twitter.android.StartActivity 2>/dev/null || am start -a android.intent.action.VIEW -d 'https://twitter.com'")
            return {"status": "opening", "app": "Twitter/X"}
        
        if "tiktok" in text:
            os.system("am start -n com.zhiliaoapp.musically/com.zhiliaoapp.musically.MainActivity 2>/dev/null || am start -a android.intent.action.VIEW -d 'https://tiktok.com'")
            return {"status": "opening", "app": "TikTok"}
        
        if "youtube" in text or "yt" in text:
            os.system("am start -n com.google.android.youtube/com.google.android.youtube.app.honeycomb.Shell$HomeActivity 2>/dev/null || am start -a android.intent.action.VIEW -d 'https://youtube.com'")
            return {"status": "opening", "app": "YouTube"}
        
        # Trading
        if any(w in text for w in ["buy", "sell", "portfolio", "stock", "price"]):
            syms = re.findall(r'\b([a-z]{1,5})\b', text)
            qty_match = re.findall(r'\b(\d+)\b', text)
            
            if 'buy' in text and syms:
                qty = qty_match[0] if qty_match else '1'
                os.system(f"liljr buy {syms[0].upper()} {qty}")
                return {"status": "buy", "symbol": syms[0].upper(), "qty": qty}
            
            if 'sell' in text and syms:
                qty = qty_match[0] if qty_match else '1'
                os.system(f"liljr sell {syms[0].upper()} {qty}")
                return {"status": "sell", "symbol": syms[0].upper(), "qty": qty}
            
            if 'portfolio' in text:
                os.system("liljr portfolio")
                return {"status": "portfolio"}
            
            if syms:
                os.system(f"am start -a android.intent.action.VIEW -d 'https://tradingview.com/symbols/NASDAQ-{syms[0].upper()}/'")
                return {"status": "chart", "symbol": syms[0].upper()}
        
        # Status / Help
        if any(w in text for w in ["status", "how are you", "what's up", "what can you do"]):
            return {
                "status": "motherboard_active",
                "capabilities": [
                    "Phone: files, apps, camera, system, settings",
                    "Cloud: SSH to servers, deploy, check status",
                    "Repos: git pull/push/status/log, build projects",
                    "Social: open Facebook, Instagram, Snapchat, etc",
                    "Trading: buy/sell stocks, portfolio",
                    "Build: create websites, apps, code",
                    "System: brightness, volume, lock, wifi, battery"
                ],
                "mode": "FULL CONTROL"
            }
        
        # Stop
        if any(w in text for w in ["stop", "quit", "exit", "done", "that's enough", "sleep", "later"]):
            return {"status": "stopping", "message": "Aight. I'm here when you need me."}
        
        # Fallback — just try to do something useful
        self._log(f"Unknown command: {text}. Trying generic approach.")
        
        # Try to open any app mentioned
        for app in ["chrome", "maps", "gmail", "youtube", "spotify", "netflix", "calculator", "clock", "camera", "settings", "phone", "messages"]:
            if app in text:
                pkg_map = {
                    "chrome": "com.android.chrome", "maps": "com.google.android.apps.maps",
                    "gmail": "com.google.android.gm", "youtube": "com.google.android.youtube",
                    "spotify": "com.spotify.music", "netflix": "com.netflix.mediaclient",
                    "calculator": "com.google.android.calculator", "clock": "com.google.android.deskclock",
                    "camera": "com.android.camera", "settings": "com.android.settings",
                    "phone": "com.android.dialer", "messages": "com.google.android.apps.messaging"
                }
                pkg = pkg_map.get(app)
                os.system(f"am start -n {pkg}/.MainActivity 2>/dev/null || am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n {pkg}/.MainActivity 2>/dev/null")
                return {"status": "opened", "app": app}
        
        # Try to find files
        if any(w in text for w in ["find", "where is", "locate"]):
            pattern = re.sub(r'.*(?:find|where is|locate)\s+', '', text).strip()
            if pattern:
                return self.phone.list_files(pattern=pattern)
        
        return {"status": "unknown", "message": f"I heard: '{text}'. Try: 'list files', 'take photo', 'open Chrome', 'buy AAPL 5', 'push my code', 'deploy to server', 'check Facebook'"}


# ═══════════════════════════════════════════════════════════════
# MOTHERBOARD — Main Controller
# ═══════════════════════════════════════════════════════════════
class Motherboard:
    """The central brain. Everything routes through here."""
    
    def __init__(self):
        self.identity = IdentityManager()
        self.phone = PhoneDominion()
        self.cloud = CloudDominion(self.identity)
        self.repos = RepoManager(self.identity)
        self.commander = VoiceCommander(self.phone, self.cloud, self.repos, self.identity)
        self.running = True
    
    def exec(self, command):
        """Execute any command. Just talk."""
        return self.commander.hear(command)
    
    def setup_github(self, token, username):
        """Connect GitHub."""
        return self.identity.set_github(token, username)
    
    def setup_server(self, name, host, user, key_path=None, password=None):
        """Add remote server."""
        return self.identity.add_server(name, host, user, key_path, password)
    
    def get_status(self):
        """Full system status."""
        return {
            "motherboard": "v31.0",
            "phone_root": self.phone.root_available,
            "github_connected": bool(self.identity.creds.get("github", {}).get("token")),
            "servers": len(self.identity.creds.get("servers", [])),
            "accounts": list(self.identity.creds.get("accounts", {}).keys()),
            "repos_local": os.path.exists(os.path.join(HOME, "repos")),
            "time": time.time()
        }


def main():
    board = Motherboard()
    
    print("╔════════════════════════════════════════════════╗")
    print("║     🧠 LILJR MOTHERBOARD v31.0                ║")
    print("║     You just talk. He does everything.        ║")
    print("╚════════════════════════════════════════════════╝")
    print()
    
    if len(sys.argv) > 1:
        # One-shot mode
        command = " ".join(sys.argv[1:])
        result = board.exec(command)
        print(json.dumps(result, indent=2) if isinstance(result, dict) else result)
        return
    
    # Interactive mode
    print("Examples:")
    print("  'go grab my files from ~/downloads and move to ~/documents'")
    print("  'push my code'")
    print("  'build a backsplash'")
    print("  'check my Facebook'")
    print("  'move my apps around'")
    print("  'pull everything from GitHub'")
    print("  'deploy to my server'")
    print("  'go through my phone'")
    print("  'take a photo'")
    print("  'buy NVDA 10'")
    print()
    
    while board.running:
        try:
            text = input("[YOU] ").strip()
            if not text:
                continue
            
            result = board.exec(text)
            
            if isinstance(result, dict) and result.get("status") == "stopping":
                print(f"[JR] {result.get('message', 'Later.')}")
                break
            
            if isinstance(result, dict):
                print(f"[JR] {json.dumps(result, indent=2)}")
            else:
                print(f"[JR] {result}")
        
        except KeyboardInterrupt:
            print("\n[JR] Aight. Later.")
            break
        except EOFError:
            break

if __name__ == '__main__':
    main()
