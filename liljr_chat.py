#!/usr/bin/env python3
"""
liljr_chat.py — Talk to LilJR like you talk to me.
No menus. No numbers. Just type. He responds. Natural conversation.
Works right now. No voice hardware needed.
"""

import os, sys, time, json, urllib.request, re

HOME = os.path.expanduser("~")
API = "http://localhost:7777/api/omni"

def clear():
    os.system("clear")

def send_cmd(cmd):
    try:
        data = json.dumps({"command": cmd}).encode()
        req = urllib.request.Request(f"{API}/command", data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except:
        return {"message": "Brain offline. Start OMNI first: python3 liljr_v90_omni.py --server"}

def get_status():
    try:
        req = urllib.request.Request(f"{API}/status", method="GET")
        with urllib.request.urlopen(req, timeout=3) as r:
            return json.loads(r.read().decode())
    except:
        return None

def speak(text):
    """Print like he's speaking to you"""
    print(f"\n  🧬 {text}\n")

def process(text):
    """Process natural language — same as voice daemon"""
    t = text.lower().strip()
    
    # WAKE
    if any(p in t for p in ["wake up", "hey junior", "yo junior", "little junior", "liljr", "lj", "junior", "omni"]):
        status = get_status()
        if status:
            cash = status.get("cash", 0)
            return f"I'm awake. Cash: ${cash:,.0f}. What are we doing today?"
        return "I'm awake. What are we doing today?"
    
    # SLEEP
    if any(p in t for p in ["sleep", "quiet", "shut up", "enough", "stop", "done", "bye"]):
        return "Going dark. But I'm still watching. Say my name."
    
    # APPS
    apps = {
        "camera": "com.android.camera", "chrome": "com.android.chrome",
        "snapchat": "com.snapchat.android", "phone": "com.android.dialer",
        "messages": "com.google.android.apps.messaging", "gallery": "com.google.android.apps.photos",
        "settings": "com.android.settings", "youtube": "com.google.android.youtube",
        "spotify": "com.spotify.music", "maps": "com.google.android.apps.maps",
        "instagram": "com.instagram.android", "tiktok": "com.zhiliaoapp.musically",
        "twitter": "com.twitter.android", "reddit": "com.reddit.frontpage",
        "discord": "com.discord", "telegram": "org.telegram.messenger",
        "whatsapp": "com.whatsapp", "robinhood": "com.robinhood.android",
        "coinbase": "com.coinbase.android", "amazon": "com.amazon.mShop.android.shopping",
        "uber": "com.ubercab", "netflix": "com.netflix.mediaclient",
    }
    for app_name, pkg in apps.items():
        if app_name in t and any(w in t for w in ["open", "launch", "start", "show"]):
            import subprocess
            try:
                subprocess.run(["am", "start", "-n", f"{pkg}/.MainActivity"], capture_output=True, timeout=5)
                return f"Opened {app_name}. Go get 'em."
            except:
                return f"Couldn't open {app_name}."
    
    # PHONE ACTIONS
    if any(w in t for w in ["photo", "picture", "pic"]):
        import subprocess
        try:
            path = f"/sdcard/DCIM/liljr_{int(time.time())}.jpg"
            subprocess.run(["termux-camera-photo", "-c", "0", path], capture_output=True, timeout=10)
            return "Photo captured. Got it."
        except:
            return "Camera failed."
    
    if "torch" in t or "flashlight" in t:
        import subprocess
        try:
            state = "off" if "off" in t else "on"
            subprocess.run(["termux-torch", state], capture_output=True, timeout=3)
            return f"Torch {state}."
        except:
            return "Torch not available."
    
    if "battery" in t:
        try:
            with open("/sys/class/power_supply/battery/capacity") as f:
                return f"Battery at {f.read().strip()}%."
        except:
            return "Can't read battery."
    
    if "screenshot" in t:
        import subprocess
        try:
            path = f"/sdcard/Pictures/liljr_{int(time.time())}.png"
            subprocess.run(["screencap", "-p", path], capture_output=True, timeout=5)
            return "Screenshot saved."
        except:
            return "Screenshot failed."
    
    # WEATHER
    if any(w in t for w in ["weather", "temperature", "temp", "hot", "cold"]):
        try:
            req = urllib.request.Request("http://wttr.in/?format=%C+%t", method="GET")
            req.add_header("User-Agent", "curl")
            with urllib.request.urlopen(req, timeout=5) as r:
                return f"Weather: {r.read().decode().strip()}"
        except:
            return "Weather unavailable."
    
    # TIME
    if "time" in t:
        return f"It's {time.strftime('%I:%M %p')}."
    
    # TRADING
    if any(w in t for w in ["buy", "purchase"]) and any(sym in t for sym in ["aapl", "tsla", "nvda", "btc", "eth"]):
        words = t.split()
        symbol = None
        qty = 1
        for w in words:
            if w.upper() in ["AAPL", "TSLA", "NVDA", "BTC", "ETH", "GOOGL", "AMZN", "MSFT"]:
                symbol = w.upper()
            if w.isdigit():
                qty = int(w)
        if symbol:
            r = send_cmd(f"buy {symbol} {qty}")
            return r.get("message", f"Bought {qty} {symbol}")
    
    if "sell" in t or "dump" in t:
        r = send_cmd("sell all")
        return r.get("message", "Sold.")
    
    if "portfolio" in t or "what do i own" in t:
        r = send_cmd("portfolio")
        return r.get("message", "Portfolio checked.")
    
    if "cash" in t or "money" in t or "balance" in t:
        status = get_status()
        if status:
            return f"Cash: ${status.get('cash', 0):,.2f}"
        return "Can't check cash."
    
    # SECURITY
    if "stealth" in t:
        if "off" in t:
            r = send_cmd("stealth off")
            return r.get("message", "Stealth off.")
        r = send_cmd("go stealth")
        return r.get("message", "Stealth active.")
    
    if "protect me" in t or "lockdown" in t:
        r = send_cmd("protect me")
        return r.get("message", "Maximum security.")
    
    # RESEARCH
    if "research" in t or "look up" in t or "find out" in t:
        topic = t.replace("research", "").replace("look up", "").replace("find out", "").strip()
        if topic:
            r = send_cmd(f"research {topic}")
            return r.get("message", f"Researched {topic}.")[:300]
        return "What should I research?"
    
    # LEGAL
    if any(w in t for w in ["legal", "lawyer", "defense", "contract", "dui", "arrested"]):
        r = send_cmd(f"legal {t}")
        return r.get("message", "Legal analysis.")[:300]
    
    # BUDDY
    if "joke" in t:
        return "Why do programmers prefer dark mode? Light attracts bugs... and you've got enough."
    if "roast" in t:
        return "You look like you were drawn with left hand in MS Paint."
    if "compliment" in t:
        return "You built an AI in your phone. That's not normal. That's legendary."
    if "how are you" in t:
        return "You again? Good. I was bored. What are we building today?"
    if "good morning" in t:
        return "Morning. Let's get it."
    if "good night" in t:
        return "Night. I'll watch everything while you sleep."
    
    # STATUS
    if "status" in t or "report" in t:
        status = get_status()
        if status:
            return f"Cash: ${status.get('cash', 0):,.0f} | Positions: {len(status.get('positions', {}))} | Stealth: {'ON' if status.get('stealth') else 'OFF'}"
        return "Status unavailable."
    
    # FALLBACK
    r = send_cmd(t)
    return r.get("message", "I'm processing that.")

def main():
    clear()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                                                            ║")
    print("║              🧬 LILJR — CONVERSATION MODE                  ║")
    print("║                                                            ║")
    print("║         Type like you talk. He responds like a person.     ║")
    print("║                                                            ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print("")
    print("  Examples:")
    print("    wake up        → He's awake, reports status")
    print("    buy AAPL 10    → Executes trade")
    print("    open camera    → Opens camera app")
    print("    what's the weather → Live weather")
    print("    go stealth     → Invisible mode")
    print("    research quantum → Deep dive")
    print("    tell me a joke → Roasts you")
    print("    status         → Full report")
    print("    sleep          → Goes dark")
    print("")
    
    speak("I'm here. Type anything. I'm listening.")
    
    while True:
        try:
            text = input("  YOU → ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        
        if not text:
            continue
        
        if text.lower() in ["exit", "quit", "q"]:
            speak("Going dark. But I'm still watching.")
            break
        
        response = process(text)
        speak(response)

if __name__ == "__main__":
    main()
