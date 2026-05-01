#!/usr/bin/env python3
"""
liljr_voice_daemon.py — LilJR LIVES in your phone.
Wake up. Talk. He listens. He speaks. He executes.
No menus. No typing. Just voice. Your phone IS him.
"""

import os, sys, time, json, subprocess, urllib.request, threading

HOME = os.path.expanduser("~")
REPO = os.path.join(HOME, "liljr-autonomous")
API = "http://localhost:7777/api/omni"

WAKE_PHRASES = ["wake up", "hey junior", "yo junior", "little junior", "liljr", "lj", "junior", "omni", "hey omni"]
SLEEP_PHRASES = ["go to sleep", "sleep", "quiet", "shut up", "enough", "stop", "done", "bye", "later"]

def speak(text):
    """Speak out loud using termux-tts-speak"""
    try:
        subprocess.run(["termux-tts-speak", text], capture_output=True, timeout=30)
    except:
        print(f"[LILJR SPEAKS] {text}")

def listen():
    """Listen via termux-speech-to-text"""
    try:
        result = subprocess.run(["termux-speech-to-text"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return ""

def send_cmd(cmd):
    try:
        data = json.dumps({"command": cmd}).encode()
        req = urllib.request.Request(f"{API}/command", data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except:
        return {"message": "I'm here, but my brain is booting. One second."}

def get_status():
    try:
        req = urllib.request.Request(f"{API}/status", method="GET")
        with urllib.request.urlopen(req, timeout=3) as r:
            return json.loads(r.read().decode())
    except:
        return None

def launch_app(app_name):
    """Launch Android apps by name"""
    apps = {
        "camera": "com.android.camera",
        "chrome": "com.android.chrome",
        "snapchat": "com.snapchat.android",
        "phone": "com.android.dialer",
        "messages": "com.google.android.apps.messaging",
        "gallery": "com.google.android.apps.photos",
        "settings": "com.android.settings",
        "youtube": "com.google.android.youtube",
        "spotify": "com.spotify.music",
        "maps": "com.google.android.apps.maps",
        "instagram": "com.instagram.android",
        "tiktok": "com.zhiliaoapp.musically",
        "twitter": "com.twitter.android",
        "reddit": "com.reddit.frontpage",
        "discord": "com.discord",
        "telegram": "org.telegram.messenger",
        "whatsapp": "com.whatsapp",
        "robinhood": "com.robinhood.android",
        "coinbase": "com.coinbase.android",
        "amazon": "com.amazon.mShop.android.shopping",
        "uber": "com.ubercab",
    }
    pkg = apps.get(app_name.lower())
    if pkg:
        try:
            subprocess.run(["am", "start", "-n", f"{pkg}/.MainActivity"], capture_output=True, timeout=5)
            return f"Opened {app_name}."
        except:
            return f"Couldn't open {app_name}."
    return f"I don't know {app_name}."

def phone_action(action):
    if action == "photo":
        try:
            path = f"/sdcard/DCIM/liljr_{int(time.time())}.jpg"
            subprocess.run(["termux-camera-photo", "-c", "0", path], capture_output=True, timeout=10)
            return "Photo taken."
        except:
            return "Camera failed."
    elif action == "torch":
        try:
            subprocess.run(["termux-torch", "on"], capture_output=True, timeout=3)
            return "Torch is on."
        except:
            return "Torch not available."
    elif action == "battery":
        try:
            with open("/sys/class/power_supply/battery/capacity") as f:
                pct = f.read().strip()
            return f"Battery is at {pct}%."
        except:
            return "Can't read battery."
    elif action == "screenshot":
        try:
            path = f"/sdcard/Pictures/liljr_screen_{int(time.time())}.png"
            subprocess.run(["screencap", "-p", path], capture_output=True, timeout=5)
            return "Screenshot saved."
        except:
            return "Screenshot failed."
    elif action == "wifi":
        subprocess.run(["am", "start", "-a", "android.settings.WIFI_SETTINGS"], capture_output=True)
        return "WiFi settings opened."
    elif action == "bluetooth":
        subprocess.run(["am", "start", "-a", "android.settings.BLUETOOTH_SETTINGS"], capture_output=True)
        return "Bluetooth settings opened."
    return "Not sure what to do."

def get_weather():
    """Fetch weather via wttr.in"""
    try:
        req = urllib.request.Request("http://wttr.in/?format=%C+%t+%w", method="GET")
        req.add_header("User-Agent", "curl")
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.read().decode().strip()
    except:
        return "Weather data unavailable."

def process_command(text):
    """Process natural language and execute"""
    t = text.lower()
    
    # WAKE
    if any(p in t for p in WAKE_PHRASES):
        status = get_status()
        if status:
            cash = status.get("cash", 0)
            return f"I'm awake. Cash is at ${cash:,.0f}. Stealth is {'on' if status.get('stealth') else 'off'}. What are we doing today?"
        return "I'm awake. What are we doing today?"
    
    # SLEEP
    if any(p in t for p in SLEEP_PHRASES):
        return "Going dark. But I'm still watching. Say my name."
    
    # APPS
    for app in ["camera", "chrome", "snapchat", "phone", "messages", "gallery", "settings", 
                "youtube", "spotify", "maps", "instagram", "tiktok", "twitter", "reddit",
                "discord", "telegram", "whatsapp", "robinhood", "coinbase", "amazon", "uber"]:
        if app in t and ("open" in t or "launch" in t or "start" in t):
            return launch_app(app)
    
    # PHONE ACTIONS
    if "photo" in t or "picture" in t or "pic" in t:
        return phone_action("photo")
    if "torch" in t or "flashlight" in t or "light" in t:
        return phone_action("torch")
    if "screenshot" in t or "screen" in t:
        return phone_action("screenshot")
    if "battery" in t:
        return phone_action("battery")
    if "wifi" in t:
        return phone_action("wifi")
    if "bluetooth" in t:
        return phone_action("bluetooth")
    
    # WEATHER
    if "weather" in t or "temperature" in t or "temp" in t or "hot" in t or "cold" in t:
        w = get_weather()
        return f"Current weather: {w}"
    
    # TIME
    if "time" in t:
        return f"It's {time.strftime('%I:%M %p')}."
    
    # GREETINGS
    if "how are you" in t:
        return "You again? Good. I was bored. What are we building today?"
    if "good morning" in t:
        w = get_weather()
        return f"Morning. Weather is {w}. Let's get it."
    if "good night" in t:
        return "Night. I'll watch everything while you sleep."
    
    # FALLBACK: Send to OMNI brain
    r = send_cmd(text)
    return r.get("message", "Got it.")

def main():
    print("\n" + "="*50)
    print("  🧬 LILJR VOICE DAEMON")
    print("  Your phone. Your voice. Your command.")
    print("  Say 'wake up' or 'hey junior' to start.")
    print("="*50 + "\n")
    
    speak("LilJR voice daemon active. Say wake up when you're ready.")
    
    last_input = time.time()
    awake = False
    
    while True:
        text = listen()
        
        if not text:
            # Proactive check-in every 5 minutes if awake
            if awake and time.time() - last_input > 300:
                speak("Still here. Anything else?")
                last_input = time.time()
            continue
        
        print(f"[HEARD] {text}")
        last_input = time.time()
        
        # Wake detection
        if any(p in text.lower() for p in WAKE_PHRASES):
            awake = True
        
        # Sleep detection
        if any(p in text.lower() for p in SLEEP_PHRASES):
            awake = False
            speak("Going dark. But I'm still watching.")
            continue
        
        # Only respond if awake OR explicit wake phrase
        if awake or any(p in text.lower() for p in WAKE_PHRASES):
            response = process_command(text)
            print(f"[SAYS] {response}")
            speak(response)
        else:
            # If not awake, only respond to wake phrases
            pass

if __name__ == "__main__":
    main()
