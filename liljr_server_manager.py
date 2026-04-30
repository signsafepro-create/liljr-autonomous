#!/usr/bin/env python3
"""
liljr_server_manager.py — v28.0 BUILT-IN SERVER
Your phone IS the server. No external host needed.

Features:
- One command: start/stop/restart/status
- Auto-restart if it dies
- Public tunnel via ngrok or cloudflared (free)
- Server dashboard at /server
- Serves your sites, API, terminal, phone OS to the WORLD
- Built into deploy — auto-starts on boot
"""

import os, sys, subprocess, time, json, signal, re, threading, urllib.request

HOME = os.path.expanduser("~")
REPO = os.path.join(HOME, "liljr-autonomous")
PID_FILE = os.path.join(HOME, ".liljr_server.pid")
LOG_FILE = os.path.join(HOME, "liljr_server.log")
TUNNEL_FILE = os.path.join(HOME, ".liljr_tunnel.url")
CONFIG_FILE = os.path.join(HOME, ".liljr_server.json")

def _log(msg):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {"port": 8000, "auto_restart": True, "tunnel": "none", "public": False}

def save_config(cfg):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f)

def is_running():
    if not os.path.exists(PID_FILE):
        return False
    try:
        with open(PID_FILE) as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)
        return pid
    except:
        return False

def get_server_pid():
    """Find the server process by checking port 8000."""
    try:
        r = subprocess.run(['lsof', '-i', ':8000'], capture_output=True, text=True, timeout=3)
        for line in r.stdout.split('\n'):
            if 'python' in line and 'LISTEN' in line:
                parts = line.split()
                if len(parts) >= 2:
                    return int(parts[1])
    except:
        pass
    # Fallback: pgrep
    try:
        r = subprocess.run(['pgrep', '-f', 'server_v8.py'], capture_output=True, text=True, timeout=3)
        pids = [int(p) for p in r.stdout.strip().split('\n') if p]
        if pids:
            return pids[0]
    except:
        pass
    return None

def start_server():
    """Start the built-in server."""
    cfg = load_config()
    port = cfg.get("port", 8000)
    
    # Check if already running
    pid = is_running()
    if pid:
        _log(f"✅ Server already running (PID {pid})")
        return {"status": "already_running", "pid": pid, "port": port}
    
    # Kill any old processes on the port
    old_pid = get_server_pid()
    if old_pid:
        try:
            os.kill(old_pid, signal.SIGKILL)
            _log(f"Killed old server (PID {old_pid})")
            time.sleep(2)
        except:
            pass
    
    # Start server
    server_path = os.path.join(REPO, "server_v8.py")
    if not os.path.exists(server_path):
        # Fallback to home copy
        server_path = os.path.join(HOME, "server_v8.py")
    
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["LILJR_PORT"] = str(port)
    
    proc = subprocess.Popen(
        [sys.executable, server_path],
        stdout=open(os.path.join(HOME, "server.log"), 'a'),
        stderr=subprocess.STDOUT,
        cwd=REPO if os.path.exists(REPO) else HOME,
        env=env
    )
    
    # Write PID
    with open(PID_FILE, 'w') as f:
        f.write(str(proc.pid))
    
    _log(f"🚀 Server starting on port {port} (PID {proc.pid})")
    
    # Wait for it to be ready
    for i in range(15):
        time.sleep(1)
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=2)
            _log(f"✅ Server ready at http://127.0.0.1:{port}")
            
            # Start tunnel if configured
            if cfg.get("public"):
                start_tunnel()
            
            return {"status": "started", "pid": proc.pid, "port": port, "url": f"http://127.0.0.1:{port}"}
        except:
            pass
    
    _log("⚠️ Server may still be starting...")
    return {"status": "starting", "pid": proc.pid, "port": port}

def stop_server():
    """Stop the server."""
    pid = is_running()
    if not pid:
        # Try to find it anyway
        pid = get_server_pid()
    
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(2)
            try:
                os.kill(pid, signal.SIGKILL)
            except:
                pass
            _log(f"🛑 Server stopped (PID {pid})")
        except Exception as e:
            _log(f"⚠️ Error stopping: {e}")
    
    # Clean up PID file
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)
    
    # Stop tunnel
    stop_tunnel()
    
    return {"status": "stopped"}

def restart_server():
    """Restart the server."""
    stop_server()
    time.sleep(2)
    return start_server()

def server_status():
    """Get server status."""
    pid = is_running()
    cfg = load_config()
    port = cfg.get("port", 8000)
    
    health = {}
    try:
        r = urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=3)
        health = json.loads(r.read().decode())
    except:
        health = {"status": "unknown"}
    
    tunnel_url = None
    if os.path.exists(TUNNEL_FILE):
        with open(TUNNEL_FILE) as f:
            tunnel_url = f.read().strip()
    
    return {
        "running": bool(pid),
        "pid": pid,
        "port": port,
        "local_url": f"http://127.0.0.1:{port}",
        "tunnel_url": tunnel_url,
        "public": cfg.get("public", False),
        "health": health,
        "config": cfg
    }

def start_tunnel():
    """Start a public tunnel so the world can reach your phone server."""
    cfg = load_config()
    tunnel_type = cfg.get("tunnel", "none")
    port = cfg.get("port", 8000)
    
    if tunnel_type == "none":
        return {"status": "no_tunnel"}
    
    _log(f"🌐 Starting {tunnel_type} tunnel...")
    
    if tunnel_type == "ngrok":
        # ngrok http 8000
        if not os.path.exists(os.path.join(HOME, "ngrok")):
            _log("⚠️ ngrok not found. Install: pkg install ngrok")
            return {"status": "error", "message": "ngrok not installed"}
        
        proc = subprocess.Popen(
            [os.path.join(HOME, "ngrok"), "http", str(port), "--log=stdout"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Wait for URL
        url = None
        for _ in range(30):
            line = proc.stdout.readline()
            if line:
                match = re.search(r'https://[a-z0-9-]+\.ngrok\.io', line)
                if match:
                    url = match.group(0)
                    break
            time.sleep(1)
        
        if url:
            with open(TUNNEL_FILE, 'w') as f:
                f.write(url)
            _log(f"🌐 PUBLIC URL: {url}")
            return {"status": "tunnel_on", "url": url}
    
    elif tunnel_type == "cloudflared":
        # cloudflared tunnel --url http://localhost:8000
        if not os.path.exists(os.path.join(HOME, "cloudflared")):
            _log("⚠️ cloudflared not found. Install: pkg install cloudflared")
            return {"status": "error", "message": "cloudflared not installed"}
        
        proc = subprocess.Popen(
            [os.path.join(HOME, "cloudflared"), "tunnel", "--url", f"http://localhost:{port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        url = None
        for _ in range(30):
            line = proc.stdout.readline()
            if line:
                match = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', line)
                if match:
                    url = match.group(0)
                    break
            time.sleep(1)
        
        if url:
            with open(TUNNEL_FILE, 'w') as f:
                f.write(url)
            _log(f"🌐 PUBLIC URL: {url}")
            return {"status": "tunnel_on", "url": url}
    
    elif tunnel_type == "serveo":
        # SSH reverse tunnel (free, no install)
        _log("🌐 Starting Serveo tunnel via SSH...")
        proc = subprocess.Popen(
            ["ssh", "-o", "StrictHostKeyChecking=no", "-R", f"80:localhost:{port}", "serveo.net"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        url = None
        for _ in range(30):
            line = proc.stdout.readline()
            if line:
                match = re.search(r'https?://[a-z0-9-]+\.serveo\.net', line)
                if match:
                    url = match.group(0)
                    break
            time.sleep(1)
        
        if url:
            with open(TUNNEL_FILE, 'w') as f:
                f.write(url)
            _log(f"🌐 PUBLIC URL: {url}")
            return {"status": "tunnel_on", "url": url}
    
    _log("⚠️ Tunnel failed to start")
    return {"status": "error"}

def stop_tunnel():
    """Stop the tunnel."""
    # Kill ngrok/cloudflared processes
    for proc_name in ["ngrok", "cloudflared", "ssh.*serveo"]:
        try:
            subprocess.run(["pkill", "-f", proc_name], timeout=2)
        except:
            pass
    
    if os.path.exists(TUNNEL_FILE):
        os.remove(TUNNEL_FILE)
    
    _log("🌐 Tunnel stopped")
    return {"status": "tunnel_off"}

def enable_public(tunnel_type="serveo"):
    """Make the server publicly accessible."""
    cfg = load_config()
    cfg["public"] = True
    cfg["tunnel"] = tunnel_type
    save_config(cfg)
    
    _log(f"🌐 Public access enabled via {tunnel_type}")
    
    if is_running():
        start_tunnel()
    else:
        start_server()
    
    return {"status": "public_on", "tunnel": tunnel_type}

def disable_public():
    """Disable public access."""
    cfg = load_config()
    cfg["public"] = False
    save_config(cfg)
    save_config(cfg)
    stop_tunnel()
    _log("🔒 Public access disabled. Local only.")
    return {"status": "public_off"}

def watchdog_loop():
    """Background loop: if server dies, restart it."""
    cfg = load_config()
    if not cfg.get("auto_restart", True):
        return
    
    _log("👁️ Watchdog started. Monitoring server...")
    
    while True:
        time.sleep(10)
        
        if not is_running():
            _log("👁️ Server dead. Resurrecting...")
            start_server()
        
        # Also check tunnel
        if cfg.get("public") and not os.path.exists(TUNNEL_FILE):
            _log("👁️ Tunnel down. Restarting...")
            start_tunnel()

def show_dashboard():
    """Print server dashboard to terminal."""
    status = server_status()
    
    print("")
    print("╔════════════════════════════════════════════════╗")
    print("║       ⚡ LILJR BUILT-IN SERVER               ║")
    print("╚════════════════════════════════════════════════╝")
    print("")
    
    if status["running"]:
        print(f"🟢 STATUS: RUNNING (PID {status['pid']})")
    else:
        print(f"🔴 STATUS: STOPPED")
    
    print(f"📡 Local:   {status['local_url']}")
    
    if status["tunnel_url"]:
        print(f"🌐 Public:  {status['tunnel_url']}")
    else:
        print(f"🔒 Public:  disabled (local only)")
    
    print("")
    print("📊 HEALTH:")
    health = status.get("health", {})
    print(f"   Version:  {health.get('version', '?')}")
    print(f"   Uptime:   {health.get('uptime', 0)//60}m")
    print(f"   Health:   {health.get('health_score', 0)}%")
    print(f"   Trades:   {health.get('trade_count', 0)}")
    print("")
    print("🎛️  CONTROLS:")
    print("   start    → start server")
    print("   stop     → stop server")
    print("   restart  → restart server")
    print("   status   → show this dashboard")
    print("   public   → make public via tunnel")
    print("   private  → disable public access")
    print("")
    print("🌐 ROUTES:")
    print(f"   {status['local_url']}/cloud     → Cloud Dashboard")
    print(f"   {status['local_url']}/phone     → Phone OS")
    print(f"   {status['local_url']}/terminal  → Code Editor")
    print(f"   {status['local_url']}/api/health → Status API")
    print("")

def main():
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    command = args[0] if args else "status"
    
    if command == "start":
        result = start_server()
        print(json.dumps(result, indent=2))
    
    elif command == "stop":
        result = stop_server()
        print(json.dumps(result, indent=2))
    
    elif command == "restart":
        result = restart_server()
        print(json.dumps(result, indent=2))
    
    elif command == "status":
        show_dashboard()
    
    elif command == "public":
        tunnel = args[1] if len(args) > 1 else "serveo"
        result = enable_public(tunnel)
        print(json.dumps(result, indent=2))
    
    elif command == "private":
        result = disable_public()
        print(json.dumps(result, indent=2))
    
    elif command == "watchdog":
        watchdog_loop()
    
    elif command == "health":
        print(json.dumps(server_status(), indent=2))
    
    else:
        print(f"Usage: python3 liljr_server_manager.py [start|stop|restart|status|public|private|watchdog|health]")
        print(f"  start     → Start the built-in server")
        print(f"  stop      → Stop the server")
        print(f"  restart   → Restart the server")
        print(f"  status    → Show dashboard")
        print(f"  public    → Make public (via free tunnel)")
        print(f"  private   → Disable public access")
        print(f"  watchdog  → Run background monitor")
        print(f"  health    → JSON status")
        show_dashboard()

if __name__ == '__main__':
    main()
