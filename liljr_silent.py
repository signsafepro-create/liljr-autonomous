#!/usr/bin/env python3
"""
liljr_silent.py — SILENT MODE
Tap button. Say ONE word: "Junior". Done.
No beeps. No feedback. No hopping. Just executes.
"""

import os, sys, time, json, re, subprocess

HOME = os.path.expanduser("~")
REPO = os.path.join(HOME, "liljr-autonomous")
sys.path.insert(0, REPO)

# ─── ONE WORD WAKE ───
WAKE_WORDS = ["junior", "juni", "jr"]
STOP_WORDS = ["stop", "done", "enough", "quiet", "sleep", "later", "bye"]
STOP_PHRASES = ["that's enough", "that is enough", "thats enough"]

def _is_stop(text):
    """Check if text is a stop command. Uses word boundaries so 'post' doesn't match 'stop'."""
    if any(p in text for p in STOP_PHRASES):
        return True
    return any(re.search(r'\b' + re.escape(w) + r'\b', text) for w in STOP_WORDS)

def _is_wake(text):
    """Check if text contains a wake word as a whole word."""
    return any(re.search(r'\b' + re.escape(w) + r'\b', text) for w in WAKE_WORDS)

def listen(timeout=8):
    try:
        result = subprocess.run(['termux-speech-to-text'], capture_output=True, text=True, timeout=timeout)
        heard = result.stdout.strip()
        if heard:
            print(f"[YOU] {heard}")
            return heard.lower()
        return None
    except Exception as e:
        return None

def run_cmd(cmd):
    """Run shell command silently."""
    os.system(cmd + " > /dev/null 2>&1")

def open_app(app):
    """Open an Android app by package name. Tries explicit activity then launcher intent."""
    apps = {
        'snapchat': 'com.snapchat.android',
        'instagram': 'com.instagram.android',
        'chrome': 'com.android.chrome',
        'youtube': 'com.google.android.youtube',
        'spotify': 'com.spotify.music',
        'tiktok': 'com.zhiliaoapp.musically',
        'whatsapp': 'com.whatsapp',
        'telegram': 'org.telegram.messenger',
        'discord': 'com.discord',
        'gmail': 'com.google.android.gm',
        'maps': 'com.google.android.apps.maps',
        'phone': 'com.android.dialer',
        'messages': 'com.google.android.apps.messaging',
        'camera': 'com.android.camera',
        'settings': 'com.android.settings',
        'gallery': 'com.android.gallery3d',
        'netflix': 'com.netflix.mediaclient',
        'robinhood': 'com.robinhood.android',
        'tradingview': 'com.tradingview.tradingviewapp',
        'calculator': 'com.google.android.calculator',
        'clock': 'com.google.android.deskclock',
        'calendar': 'com.google.android.calendar',
        'files': 'com.google.android.apps.nbu.files',
        'playstore': 'com.android.vending',
    }
    pkg = apps.get(app)
    if pkg:
        # Try explicit MainActivity, fallback to launcher intent
        run_cmd(f'am start -n {pkg}/.MainActivity 2>/dev/null || am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n {pkg}')
    else:
        run_cmd(f'am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n com.android.settings')

def handle(text):
    text = text.lower().strip()
    
    # Stop
    if _is_stop(text):
        print("[JR] Aight. Later.")
        return False
    
    # App open
    apps = ['snapchat', 'instagram', 'chrome', 'youtube', 'spotify', 'tiktok', 'whatsapp', 'telegram', 'discord', 'gmail', 'maps', 'phone', 'messages', 'camera', 'settings', 'gallery', 'netflix', 'robinhood', 'tradingview', 'calculator', 'clock', 'calendar', 'files', 'playstore']
    for app in apps:
        if app in text:
            open_app(app)
            print(f"[JR] Opened {app}")
            return True
    
    # Photo
    if any(w in text for w in ['photo', 'pic', 'picture', 'selfie']):
        path = os.path.join(HOME, f'liljr_photo_{int(time.time())}.jpg')
        run_cmd(f'termux-camera-photo -c 0 {path}')
        print("[JR] Photo taken")
        return True
    
    # Video
    if any(w in text for w in ['video', 'record']):
        run_cmd('am start -a android.media.action.VIDEO_CAPTURE')
        print("[JR] Recording")
        return True
    
    # Screenshot
    if 'screenshot' in text:
        path = os.path.join(HOME, f'ss_{int(time.time())}.png')
        run_cmd(f'screencap -p {path}')
        print("[JR] Screenshot")
        return True
    
    # Search
    if any(w in text for w in ['search', 'google', 'look up', 'find']):
        q = re.sub(r'^(search|google|look up|find)\s+', '', text).strip()
        q = q.replace(' ', '%20')
        run_cmd(f"am start -a android.intent.action.VIEW -d 'https://google.com/search?q={q}'")
        print(f"[JR] Search: {q}")
        return True
    
    # Stock chart
    syms = re.findall(r'\b([a-z]{1,5})\b', text)
    if syms and any(w in text for w in ['stock', 'chart', 'price']):
        sym = syms[0].upper()
        run_cmd(f"am start -a android.intent.action.VIEW -d 'https://tradingview.com/symbols/NASDAQ-{sym}/'")
        print(f"[JR] Chart: {sym}")
        return True
    
    # Buy
    if 'buy' in text:
        syms = re.findall(r'\b([a-z]{1,5})\b', text)
        nums = re.findall(r'\b(\d+)\b', text)
        if syms:
            sym = syms[0].upper()
            qty = nums[0] if nums else '1'
            run_cmd(f'liljr buy {sym} {qty}')
            print(f"[JR] Buy {qty} {sym}")
            return True
    
    # Sell
    if 'sell' in text:
        syms = re.findall(r'\b([a-z]{1,5})\b', text)
        nums = re.findall(r'\b(\d+)\b', text)
        if syms:
            sym = syms[0].upper()
            qty = nums[0] if nums else '1'
            run_cmd(f'liljr sell {sym} {qty}')
            print(f"[JR] Sell {qty} {sym}")
            return True
    
    # Build
    if any(w in text for w in ['build', 'make', 'create']):
        name = re.sub(r'^(build|make|create)\s+', '', text).strip() or "Site"
        run_cmd(f'liljr build "{name}"')
        print(f"[JR] Building {name}")
        return True
    
    # Portfolio
    if any(w in text for w in ['portfolio', 'positions', 'money', 'cash']):
        run_cmd('liljr portfolio')
        print("[JR] Portfolio")
        return True
    
    # Call
    digits = re.findall(r'\d+', text)
    if 'call' in text and digits:
        num = ''.join(digits)
        run_cmd(f'termux-telephony-call {num}')
        print(f"[JR] Calling {num}")
        return True
    
    # Brightness
    if re.search(r'\b(bright|brighter)\b', text):
        run_cmd('settings put system screen_brightness 200')
        print("[JR] Brighter")
        return True
    if re.search(r'\b(dim|dimmer|dark)\b', text):
        run_cmd('settings put system screen_brightness 30')
        print("[JR] Dimmer")
        return True
    
    # Volume
    if re.search(r'\b(louder|volume up|turn it up)\b', text):
        run_cmd('input keyevent KEYCODE_VOLUME_UP')
        print("[JR] Louder")
        return True
    if re.search(r'\b(quieter|volume down|turn it down)\b', text):
        run_cmd('input keyevent KEYCODE_VOLUME_DOWN')
        print("[JR] Quieter")
        return True
    
    # Home / Back
    if re.search(r'\b(go home|home)\b', text):
        run_cmd('input keyevent KEYCODE_HOME')
        print("[JR] Home")
        return True
    if re.search(r'\b(go back|back)\b', text):
        run_cmd('input keyevent KEYCODE_BACK')
        print("[JR] Back")
        return True
    
    # Flashlight — use word boundaries, 'light' alone is too generic
    if re.search(r'\b(flashlight|torch|light on|light off)\b', text):
        run_cmd('input keyevent KEYCODE_CAMERA')
        print("[JR] Flashlight")
        return True
    
    # Battery
    if 'battery' in text:
        try:
            r = subprocess.run(['termux-battery-status'], capture_output=True, text=True, timeout=3)
            batt = json.loads(r.stdout)
            print(f"[JR] Battery: {batt.get('percentage', '?')}%")
        except:
            print("[JR] Can't read battery")
        return True
    
    # URL
    urls = re.findall(r'(https?://[^\s]+|[\w\-]+\.(?:com|net|org|io))', text)
    if urls:
        url = urls[0]
        if not url.startswith('http'):
            url = 'https://' + url
        run_cmd(f"am start -a android.intent.action.VIEW -d '{url}'")
        print(f"[JR] Open: {url}")
        return True
    
    # Fallback
    print("[JR] What do you mean?")
    return True

def main():
    print("⚡ LILJR SILENT")
    print("=" * 20)
    print("Say: JUNIOR")
    print("Then say what you want")
    print("Say: STOP to end")
    print("")
    print("[IDLE] Listening for 'Junior'...")
    
    while True:
        heard = listen(timeout=10)
        if not heard:
            continue
        
        # Check wake word
        if _is_wake(heard):
            print("[JR] Yo. What do you need?")
            
            # Listen for command
            while True:
                cmd = listen(timeout=8)
                if cmd:
                    if not handle(cmd):
                        break
                else:
                    # Timeout - go back to idle
                    print("[IDLE] Listening for 'Junior'...")
                    break
        
        # Direct stop even without wake
        elif _is_stop(heard):
            print("[JR] Aight. Later.")
            break

if __name__ == '__main__':
    main()
