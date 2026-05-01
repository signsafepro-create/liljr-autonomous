#!/usr/bin/env python3
"""
liljr_voice_daemon.py — Runs 24/7 in background, even when screen is off.
Uses wakelock to prevent Android from killing it.
"""

import os, sys, time, subprocess, signal

HOME = os.path.expanduser("~")
PID_FILE = os.path.join(HOME, "liljr_voice_daemon.pid")
LOG_FILE = os.path.join(HOME, "liljr_voice_daemon.log")

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

def start_daemon():
    if is_running():
        print("⚠️ Voice daemon already running")
        return
    
    print("🎙️ Starting LilJR Voice Daemon...")
    
    # Acquire wakelock so Android doesn't kill us
    try:
        subprocess.run(['termux-wake-lock'], timeout=3)
        log("Wakelock acquired")
    except:
        log("Wakelock failed (termux-api not installed?)")
    
    # Fork to background
    pid = os.fork()
    if pid > 0:
        # Parent: save PID and exit
        with open(PID_FILE, 'w') as f:
            f.write(str(pid))
        print(f"✅ Daemon started (PID {pid})")
        print(f"📁 Log: {LOG_FILE}")
        print("Say 'hey junior' to wake me up")
        return
    
    # Child: daemon process
    os.setsid()  # New session, detach from terminal
    
    # Redirect stdout/stderr to log
    sys.stdout = open(LOG_FILE, 'a')
    sys.stderr = sys.stdout
    
    log("Voice daemon starting...")
    
    # Import and run the soul
    sys.path.insert(0, os.path.join(HOME, 'liljr-autonomous'))
    try:
        from liljr_android_soul import AndroidSoul, VoiceEngine, NotificationGuardian, ScreenWatcher
        
        soul = AndroidSoul()
        voice = VoiceEngine(soul)
        guardian = NotificationGuardian(soul, voice)
        watcher = ScreenWatcher(soul, voice)
        
        # Announce startup (quietly if night)
        hour = time.localtime().tm_hour
        if 23 <= hour or hour <= 7:
            log("Night mode — silent startup")
        else:
            voice.speak("LilJR voice daemon active.")
        
        # Start threads
        import threading
        threads = [
            threading.Thread(target=voice.listen_for_wake, daemon=True),
            threading.Thread(target=guardian.monitor, daemon=True),
            threading.Thread(target=watcher.watch, daemon=True)
        ]
        for t in threads:
            t.start()
        
        log("All threads started")
        
        # Keep alive forever
        while True:
            time.sleep(60)
            # Health ping
            log(f"Heartbeat — conversations: {soul.state['total_conversations']}, commands: {soul.state['commands_executed']}")
            
    except Exception as e:
        log(f"FATAL: {str(e)}")
        time.sleep(10)
        # Try restart
        os.execv(sys.executable, [sys.executable] + sys.argv)

def stop_daemon():
    if not os.path.exists(PID_FILE):
        print("❌ No PID file found")
        return
    
    try:
        with open(PID_FILE) as f:
            pid = int(f.read().strip())
        os.kill(pid, signal.SIGTERM)
        os.remove(PID_FILE)
        
        # Release wakelock
        subprocess.run(['termux-wake-unlock'], timeout=3)
        
        print("🛑 Voice daemon stopped")
    except Exception as e:
        print(f"Error stopping: {e}")

def status_daemon():
    if is_running():
        with open(PID_FILE) as f:
            pid = f.read().strip()
        print(f"🎙️ Voice daemon RUNNING (PID {pid})")
        print(f"📁 Log: {LOG_FILE}")
        # Show last few log lines
        try:
            result = subprocess.run(['tail', '-5', LOG_FILE], capture_output=True, text=True)
            print("\nLast activity:")
            print(result.stdout)
        except:
            pass
    else:
        print("❌ Voice daemon NOT running")
        print(f"Start with: python3 {sys.argv[0]} start")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 liljr_voice_daemon.py [start|stop|status|restart]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == 'start':
        start_daemon()
    elif cmd == 'stop':
        stop_daemon()
    elif cmd == 'status':
        status_daemon()
    elif cmd == 'restart':
        stop_daemon()
        time.sleep(2)
        start_daemon()
    else:
        print(f"Unknown command: {cmd}")
