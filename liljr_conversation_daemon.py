#!/usr/bin/env python3
"""
liljr_conversation_daemon.py — Background conversation daemon.
Always listening. Wakes up on voice. Stays in conversation mode.
Survives screen off. Survives Android process killing.
"""

import os, sys, time, json, subprocess, signal

HOME = os.path.expanduser("~")
REPO = os.path.join(HOME, 'liljr-autonomous')
PID_FILE = os.path.join(HOME, "liljr_conversation.pid")
LOG_FILE = os.path.join(HOME, "liljr_conversation.log")

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def is_running():
    if not os.path.exists(PID_FILE):
        return False
    try:
        with open(PID_FILE) as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)
        return True
    except:
        return False

def start():
    if is_running():
        print("⚠️ Conversation daemon already running")
        return
    
    print("🎙️ Starting LilJR Conversation Daemon...")
    
    # Acquire wakelock
    try:
        subprocess.run(['termux-wake-lock'], timeout=3, capture_output=True)
        log("Wakelock acquired")
    except:
        pass
    
    # Fork
    pid = os.fork()
    if pid > 0:
        with open(PID_FILE, 'w') as f:
            f.write(str(pid))
        print(f"✅ Daemon started (PID {pid})")
        print(f"📁 Log: {LOG_FILE}")
        print("Just say 'yo junior' or 'hey junior'")
        print("Once awake, keep talking. 60-second conversation window.")
        return
    
    # Child process
    os.setsid()
    sys.stdout = open(LOG_FILE, 'a')
    sys.stderr = sys.stdout
    
    log("Conversation daemon starting...")
    
    # Run conversation loop
    sys.path.insert(0, REPO)
    try:
        # Import and run
        import liljr_conversation as conv
        # Override the main loop to be daemon-friendly
        # Actually, just exec the conversation script
        os.execv(sys.executable, [sys.executable, os.path.join(REPO, 'liljr_conversation.py')])
    except Exception as e:
        log(f"FATAL: {e}")
        time.sleep(10)
        os.execv(sys.executable, [sys.executable] + sys.argv)

def stop():
    if not os.path.exists(PID_FILE):
        print("❌ Not running")
        return
    try:
        with open(PID_FILE) as f:
            pid = int(f.read().strip())
        os.kill(pid, signal.SIGTERM)
        os.remove(PID_FILE)
        subprocess.run(['termux-wake-unlock'], timeout=3)
        print("🛑 Stopped")
    except Exception as e:
        print(f"Error: {e}")

def status():
    if is_running():
        with open(PID_FILE) as f:
            pid = f.read().strip()
        print(f"🎙️ Running (PID {pid})")
        try:
            out = subprocess.run(['tail', '-5', LOG_FILE], capture_output=True, text=True)
            print("\nRecent activity:")
            print(out.stdout)
        except:
            pass
    else:
        print("❌ Not running")
        print(f"Start: python3 {sys.argv[0]} start")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 liljr_conversation_daemon.py [start|stop|status|restart]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == 'start':
        start()
    elif cmd == 'stop':
        stop()
    elif cmd == 'status':
        status()
    elif cmd == 'restart':
        stop()
        time.sleep(2)
        start()
    else:
        print(f"Unknown: {cmd}")
