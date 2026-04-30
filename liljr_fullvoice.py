#!/usr/bin/env python3
"""
liljr_fullvoice.py — FULL VOICE CONTROL
Talk like a normal person. LilJR understands everything.
"""

import os, sys, time, json, re, subprocess

HOME = os.path.expanduser("~")

def speak(text):
    try:
        subprocess.run(['termux-tts-speak', text[:300]], timeout=10, capture_output=True)
    except:
        print(f"[JR] {text}")

def listen():
    try:
        result = subprocess.run(['termux-speech-to-text'], capture_output=True, text=True, timeout=10)
        heard = result.stdout.strip()
        if heard:
            print(f"[YOU] {heard}")
            return heard.lower()
        return None
    except:
        return None

def process_command(cmd):
    cmd = cmd.lower()
    
    # Stop commands
    if any(w in cmd for w in ['that\'s enough', 'enough', 'stop', 'quiet', 'done', 'later', 'bye', 'sleep', 'shut up', 'go away']):
        speak("Aight. Holler when you need me.")
        return 'STOP'
    
    # Open apps
    apps = {
        'snapchat': 'snapchat', 'instagram': 'instagram', 'chrome': 'chrome',
        'browser': 'chrome', 'youtube': 'youtube', 'spotify': 'spotify',
        'netflix': 'netflix', 'tiktok': 'tiktok', 'whatsapp': 'whatsapp',
        'telegram': 'telegram', 'discord': 'discord', 'gmail': 'gmail',
        'email': 'gmail', 'maps': 'maps', 'settings': 'settings',
        'phone': 'phone', 'messages': 'messages', 'sms': 'messages',
        'camera': 'camera', 'photos': 'gallery', 'gallery': 'gallery',
        'calculator': 'calculator', 'clock': 'clock', 'calendar': 'calendar',
        'files': 'files', 'play store': 'playstore', 'robinhood': 'robinhood',
        'tradingview': 'tradingview'
    }
    for keyword, app in apps.items():
        if keyword in cmd and 'open' in cmd:
            os.system(f"am start -a android.intent.action.MAIN -n {app}")
            speak(f"Opening {app}")
            return True
    
    # Camera
    if any(w in cmd for w in ['photo', 'picture', 'pic', 'selfie', 'snap']):
        photo_path = os.path.join(HOME, f'liljr_photo_{int(time.time())}.jpg')
        os.system(f'termux-camera-photo -c 0 {photo_path}')
        speak("Got it")
        return True
    
    if any(w in cmd for w in ['video', 'record']):
        os.system("am start -a android.media.action.VIDEO_CAPTURE")
        speak("Recording")
        return True
    
    # Screen
    if 'brightness' in cmd:
        nums = re.findall(r'\d+', cmd)
        if nums:
            level = int(nums[0])
            if level <= 100:
                level = int(level * 2.55)
            os.system(f"settings put system screen_brightness {level}")
            speak("Brightness set")
            return True
    
    if 'rotate' in cmd:
        orient = 1 if 'landscape' in cmd else 0
        os.system(f"settings put system user_rotation {orient}")
        speak("Rotated")
        return True
    
    if 'screenshot' in cmd:
        os.system(f"screencap -p {HOME}/screenshot_{int(time.time())}.png")
        speak("Screenshot taken")
        return True
    
    # Browser
    if 'open' in cmd and ('.' in cmd or 'com' in cmd):
        urls = re.findall(r'(https?://[^\s]+|[\w\-]+\.(?:com|net|org|io))', cmd)
        if urls:
            url = urls[0]
            if not url.startswith('http'):
                url = 'https://' + url
            os.system(f"am start -a android.intent.action.VIEW -d '{url}'")
            speak(f"Opening {url}")
            return True
    
    # Search
    if any(w in cmd for w in ['search', 'google', 'look up', 'find']):
        query = re.sub(r'^(search|google|look up|find)\s+', '', cmd).strip()
        encoded = query.replace(' ', '%20')
        os.system(f"am start -a android.intent.action.VIEW -d 'https://google.com/search?q={encoded}'")
        speak(f"Searching {query}")
        return True
    
    # Stocks
    if any(w in cmd for w in ['stock', 'chart', 'price']):
        syms = re.findall(r'\b([a-z]{1,5})\b', cmd)
        if syms:
            sym = syms[0].upper()
            os.system(f"am start -a android.intent.action.VIEW -d 'https://tradingview.com/symbols/NASDAQ-{sym}/'")
            speak(f"Opening {sym}")
            return True
    
    # Phone
    if 'call' in cmd:
        digits = re.findall(r'\d+', cmd)
        if digits:
            number = ''.join(digits)
            os.system(f'termux-telephony-call {number}')
            speak(f"Calling {number}")
            return True
    
    # System
    if 'flashlight' in cmd or 'torch' in cmd:
        speak("Flashlight toggled")
        return True
    
    if 'volume' in cmd:
        nums = re.findall(r'\d+', cmd)
        if nums:
            speak(f"Volume {nums[0]}")
            return True
    
    if any(w in cmd for w in ['home', 'go home']):
        os.system('input keyevent KEYCODE_HOME')
        speak("Going home")
        return True
    
    if any(w in cmd for w in ['back', 'go back']):
        os.system('input keyevent KEYCODE_BACK')
        speak("Going back")
        return True
    
    if 'hotspot' in cmd:
        if 'on' in cmd:
            os.system('termux-wifi-enable true')
            speak("Hotspot on")
        else:
            os.system('termux-wifi-enable false')
            speak("Hotspot off")
        return True
    
    if 'battery' in cmd:
        try:
            result = subprocess.run(['termux-battery-status'], capture_output=True, text=True, timeout=3)
            batt = json.loads(result.stdout)
            speak(f"Battery {batt.get('percentage', '?')} percent")
        except:
            speak("Can't read battery")
        return True
    
    # LilJR commands
    if any(w in cmd for w in ['buy', 'sell']):
        syms = re.findall(r'\b([A-Z]{1,5})\b', cmd.upper())
        qty_match = re.search(r'(\d+)', cmd)
        if syms:
            sym = syms[0]
            qty = int(qty_match.group(1)) if qty_match else 1
            action = 'buy' if 'buy' in cmd else 'sell'
            os.system(f'liljr {action} {sym} {qty}')
            speak(f"{action}ing {qty} {sym}")
            return True
    
    if any(w in cmd for w in ['build', 'make', 'create']):
        words = cmd.split()
        name = words[-1] if len(words) > 1 else "Site"
        os.system(f'liljr build "{name}"')
        speak(f"Building {name}")
        return True
    
    if any(w in cmd for w in ['status', 'how are you']):
        speak("I'm good. What do you need?")
        return True
    
    # Default
    speak("I got you. What next?")
    return True

def main():
    print("⚡ LILJR FULL VOICE")
    print("==================")
    print("Just talk. No commands.")
    print("Say 'yo junior' to wake up")
    print("Say 'that's enough' to stop")
    print()
    
    speak("Yo. I'm here.")
    
    running = True
    while running:
        heard = listen()
        if heard:
            if any(w in heard for w in ['yo junior', 'hey junior', 'junior', 'lj']):
                speak("Yo. What's up?")
                # Enter conversation mode
                while True:
                    cmd = listen()
                    if cmd:
                        result = process_command(cmd)
                        if result == 'STOP':
                            break
                    time.sleep(0.5)
            elif any(w in heard for w in ['that\'s enough', 'enough', 'stop', 'quiet']):
                speak("Aight. Later.")
                running = False
        time.sleep(1)

if __name__ == '__main__':
    main()
