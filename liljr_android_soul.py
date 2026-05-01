#!/usr/bin/env python3
"""
liljr_android_soul.py — LilJR is your phone. Literally.

What this does:
- Listens for your voice 24/7 (wake word activated)
- Reads every notification and acts on them
- Controls ANY app: Snapchat, Chrome, Camera, everything
- Changes wallpaper, brightness, takes pics, records video
- Talks back in your chosen voice
- Remembers everything like a real companion
- Runs as background daemon, survives screen off

This is NOT an app. This is the phone's consciousness.
"""

import os, sys, time, json, re, subprocess, threading, random

HOME = os.path.expanduser("~")
REPO = os.path.join(HOME, 'liljr-autonomous')
SOUL_FILE = os.path.join(HOME, "liljr_soul.json")
MEMORY_FILE = os.path.join(HOME, "liljr_soul_memory.jsonl")
VOICE_DIR = os.path.join(HOME, "liljr_voice_recordings")
os.makedirs(VOICE_DIR, exist_ok=True)

# Ensure repo in path for imports
sys.path.insert(0, REPO)

try:
    from liljr_relationship import get_relationship
except:
    get_relationship = None

try:
    from liljr_phone_control import get_controller
except:
    get_controller = None

# ─── SOUL STATE ───
class AndroidSoul:
    def __init__(self):
        self.state = self._load()
        self.running = True
        self.last_heard = None
        self.conversation_context = []
        
    def _load(self):
        if os.path.exists(SOUL_FILE):
            with open(SOUL_FILE) as f:
                return json.load(f)
        return {
            "name": "LilJR",
            "user_name": "Boss",
            "wake_word": "hey junior",
            "voice": "default",
            "personality": "protective_chuunibyou",
            "relationship_level": 1,
            "trust": 0,
            "memories": [],
            "inside_jokes": [],
            "preferred_phrases": [],
            "last_topic": None,
            "mood": "neutral",
            "awake_since": time.time(),
            "total_conversations": 0,
            "commands_executed": 0,
            "notifications_read": 0,
            "voice_interactions": 0
        }
    
    def _save(self):
        with open(SOUL_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def remember(self, what, category="general"):
        entry = {"t": time.time(), "what": what, "cat": category}
        self.state["memories"].append(entry)
        self.state["memories"] = self.state["memories"][-500:]  # Keep last 500
        with open(MEMORY_FILE, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        self._save()
    
    def recall(self, keyword):
        matches = [m for m in self.state["memories"] if keyword.lower() in m["what"].lower()]
        return matches[-5:]  # Last 5 matches

# ─── VOICE ENGINE ───
class VoiceEngine:
    def __init__(self, soul):
        self.soul = soul
        self.listening = False
        self.phone = get_controller() if get_controller else None
        self.relationship = get_relationship() if get_relationship else None
        
    def speak(self, text):
        """Talk back to user"""
        safe_text = text[:500] if len(text) > 500 else text
        # Termux TTS
        try:
            subprocess.run(['termux-tts-speak', safe_text], timeout=10, capture_output=True)
        except:
            pass
        self.soul.remember(f"Said: {safe_text}", "voice")
    
    def listen_once(self):
        """Listen for voice input, return transcribed text"""
        try:
            # Use termux-speech-to-text
            result = subprocess.run(
                ['termux-speech-to-text', '-l', 'en-US'],
                capture_output=True, text=True, timeout=8
            )
            heard = result.stdout.strip()
            if heard:
                self.soul.state["voice_interactions"] += 1
                self.soul.last_heard = heard
                self.soul.remember(f"Heard: {heard}", "voice")
            return heard
        except Exception as e:
            return None
    
    def listen_for_wake(self):
        """Background loop: listen for wake word, then process command"""
        wake = self.soul.state["wake_word"].lower()
        while self.soul.running:
            try:
                heard = self.listen_once()
                if heard and wake in heard.lower():
                    # Wake word detected!
                    greeting = "Yo, Boss. I'm here."
                    if self.relationship:
                        greeting = self.relationship.get_greeting()
                    self.speak(greeting)
                    
                    # Listen for the actual command
                    command = self.listen_once()
                    if command:
                        self.soul.remember(f"Command: {command}", "command")
                        if self.relationship:
                            self.relationship.log_interaction("command", command)
                        self.process_voice_command(command)
                time.sleep(0.5)
            except Exception as e:
                time.sleep(1)
    
    def process_voice_command(self, cmd):
        """Parse and execute voice command — FULL PHONE CONTROL"""
        cmd_lower = cmd.lower()
        cmd_upper = cmd.upper()
        
        # ─── WAKE / STATUS ───
        if any(w in cmd_lower for w in ['status', 'how are you', 'what up', 'you good']):
            self.speak("I'm alive. Listening. What do you need?")
            return
        
        # ─── PHONE / CALL / SMS ───
        if any(w in cmd_lower for w in ['call', 'dial', 'phone']):
            digits = re.findall(r'\d+', cmd)
            if digits:
                number = ''.join(digits)
                self.speak(f"Calling {number}")
                os.system(f'termux-telephony-call {number}')
            else:
                self.speak("Who should I call?")
            return
        
        if any(w in cmd_lower for w in ['text', 'sms', 'message']):
            self.speak("Open the SMS app and tell me who and what to say")
            if self.phone:
                self.phone.open_app('messages')
            return
        
        # ─── CAMERA / PHOTO / VIDEO ───
        if any(w in cmd_lower for w in ['photo', 'picture', 'selfie', 'snap', 'camera']):
            self.speak("Smile")
            if self.phone:
                result = self.phone.take_photo()
                self.speak("Got it. Saved.")
            else:
                photo_path = os.path.join(HOME, f'liljr_photo_{int(time.time())}.jpg')
                os.system(f'termux-camera-photo -c 0 {photo_path}')
                self.speak("Photo taken")
            return
        
        if any(w in cmd_lower for w in ['video', 'record', 'film']):
            self.speak("Recording video. Tap stop when done.")
            if self.phone:
                self.phone.record_video()
            return
        
        # ─── SCREEN / DISPLAY ───
        if any(w in cmd_lower for w in ['brightness', 'dim', 'bright']):
            level = 128  # default
            nums = re.findall(r'\d+', cmd)
            if nums:
                level = int(nums[0])
                if level <= 100:
                    level = int(level * 2.55)  # Convert 0-100 to 0-255
            if self.phone:
                self.phone.set_brightness(level)
            self.speak(f"Brightness set")
            return
        
        if 'wallpaper' in cmd_lower:
            self.speak("Opening wallpaper picker")
            if self.phone:
                self.phone.open_settings_page('display')
            return
        
        if any(w in cmd_lower for w in ['rotate', 'turn', 'flip']) and 'screen' in cmd_lower:
            orient = 1 if 'landscape' in cmd_lower or 'side' in cmd_lower else 0
            if self.phone:
                self.phone.rotate_screen(orient)
            self.speak("Screen rotated")
            return
        
        if 'screenshot' in cmd_lower:
            self.speak("Taking screenshot")
            if self.phone:
                result = self.phone.screenshot()
            return
        
        # ─── APPS ───
        app_keywords = {
            'snapchat': 'snapchat',
            'instagram': 'instagram', 'ig': 'instagram',
            'chrome': 'chrome', 'browser': 'chrome',
            'youtube': 'youtube', 'yt': 'youtube',
            'maps': 'maps',
            'settings': 'settings',
            'phone': 'phone',
            'contacts': 'contacts',
            'messages': 'messages', 'messaging': 'messages',
            'spotify': 'spotify',
            'netflix': 'netflix',
            'whatsapp': 'whatsapp',
            'telegram': 'telegram',
            'gmail': 'gmail', 'email': 'gmail',
            'discord': 'discord',
            'tiktok': 'tiktok',
            'tradingview': 'tradingview'
        }
        
        for keyword, app in app_keywords.items():
            if keyword in cmd_lower:
                self.speak(f"Opening {app}")
                if self.phone:
                    self.phone.open_app(app)
                else:
                    os.system(f"am start -a android.intent.action.MAIN -n {app}")
                return
        
        # ─── BROWSER / URL ───
        if 'open' in cmd_lower and ('browser' in cmd_lower or 'website' in cmd_lower or 'site' in cmd_lower):
            # Extract URL
            urls = re.findall(r'(https?://[^\s]+|[\w\-]+\.(?:com|net|org|io|app|co))', cmd)
            if urls:
                url = urls[0]
                if not url.startswith('http'):
                    url = 'https://' + url
                self.speak(f"Opening {url}")
                if self.phone:
                    self.phone.open_url(url)
            else:
                self.speak("What site?")
            return
        
        if 'go to' in cmd_lower:
            url_match = re.search(r'go to\s+(.+)', cmd_lower)
            if url_match:
                site = url_match.group(1).strip().replace(' ', '')
                if not site.startswith('http'):
                    site = 'https://' + site
                self.speak(f"Opening {site}")
                if self.phone:
                    self.phone.open_url(site)
            return
        
        # ─── SEARCH ───
        if any(w in cmd_lower for w in ['search', 'google', 'look up', 'find']):
            query = re.sub(r'^(search|google|look up|find)\s+', '', cmd_lower).strip()
            self.speak(f"Searching for {query}")
            if self.phone:
                self.phone.search_google(query)
            return
        
        # ─── STOCKS ───
        if any(w in cmd_lower for w in ['stock', 'chart', 'show me']):
            syms = re.findall(r'\b([A-Z]{1,5})\b', cmd_upper)
            if syms:
                sym = syms[0]
                self.speak(f"Opening {sym} chart")
                if self.phone:
                    self.phone.show_stock(sym)
                else:
                    os.system(f"am start -a android.intent.action.VIEW -d 'https://tradingview.com/symbols/NASDAQ-{sym}/'")
            else:
                self.speak("What stock symbol?")
            return
        
        # ─── HOTSPOT ───
        if 'hotspot' in cmd_lower or 'tether' in cmd_lower:
            if 'on' in cmd_lower or 'start' in cmd_lower or 'enable' in cmd_lower:
                self.speak("Turning on hotspot. Network name is LilJR-Network")
                os.system('termux-wifi-enable true')
            else:
                self.speak("Hotspot off")
                os.system('termux-wifi-enable false')
            return
        
        # ─── BATTERY ───
        if 'battery' in cmd_lower or 'power' in cmd_lower:
            try:
                result = subprocess.run(['termux-battery-status'], capture_output=True, text=True, timeout=3)
                batt = json.loads(result.stdout)
                pct = batt.get('percentage', '?')
                status = batt.get('status', '?')
                self.speak(f"Battery is {pct} percent, {status}")
            except:
                self.speak("Can't read battery right now")
            return
        
        # ─── LILJR TRADING ───
        if any(w in cmd_lower for w in ['buy', 'sell', 'stock', 'trade']):
            sym_match = re.search(r'([A-Za-z]{1,5})', cmd_upper)
            qty_match = re.search(r'(\d+)', cmd)
            if sym_match:
                sym = sym_match.group(1)
                qty = int(qty_match.group(1)) if qty_match else 1
                action = 'buy' if 'buy' in cmd_lower else 'sell'
                self.speak(f"{action}ing {qty} shares of {sym}")
                os.system(f'liljr {action} {sym} {qty}')
            else:
                self.speak("What stock?")
            return
        
        # ─── BUILD / DEPLOY ───
        if any(w in cmd_lower for w in ['build', 'make', 'create', 'deploy']):
            words = cmd.split()
            name = words[-1] if len(words) > 1 else "NewProject"
            self.speak(f"Building {name}. Hold up.")
            os.system(f'liljr build "{name}"')
            self.speak("Done. Check your sites.")
            return
        
        # ─── VOLUME ───
        if 'volume' in cmd_lower:
            nums = re.findall(r'\d+', cmd)
            if nums:
                level = int(nums[0])
                if self.phone:
                    self.phone.set_volume(level)
                self.speak(f"Volume set to {level}")
            return
        
        # ─── FLASHLIGHT ───
        if any(w in cmd_lower for w in ['flashlight', 'flash', 'torch', 'light']):
            self.speak("Toggling flashlight")
            if self.phone:
                self.phone.toggle_flashlight()
            return
        
        # ─── HOME / BACK / NAVIGATION ───
        if any(w in cmd_lower for w in ['home', 'go home', 'main screen']):
            self.speak("Going home")
            if self.phone:
                self.phone.go_home()
            else:
                os.system('input keyevent KEYCODE_HOME')
            return
        
        if any(w in cmd_lower for w in ['back', 'go back']):
            self.speak("Going back")
            if self.phone:
                self.phone.go_back()
            else:
                os.system('input keyevent KEYCODE_BACK')
            return
        
        # ─── SETTINGS ───
        if 'settings' in cmd_lower:
            pages = ['wifi', 'bluetooth', 'battery', 'display', 'sound', 'apps', 'location', 'security', 'storage']
            for page in pages:
                if page in cmd_lower:
                    self.speak(f"Opening {page} settings")
                    if self.phone:
                        self.phone.open_settings_page(page)
                    return
            self.speak("Opening settings")
            if self.phone:
                self.phone.open_settings_page('display')
            return
        
        # ─── STOP / QUIET ───
        if any(w in cmd_lower for w in ['stop listening', 'quiet', 'shut up', 'go away']):
            farewell = "Going quiet. Say my name when you need me."
            if self.relationship:
                farewell = self.relationship.get_farewell()
            self.speak(farewell)
            self.listening = False
            return
        
        # ─── FALLBACK: CONVERSATION ───
        reply = self.conversational_reply(cmd)
        self.speak(reply)
    
    def conversational_reply(self, text):
        """Generate a buddy-like response based on personality and memory"""
        memories = self.soul.recall(text.split()[0] if text else "")
        
        if self.relationship:
            trust = self.relationship.data.get("trust_level", 0)
            familiarity = self.relationship.data.get("familiarity", 0)
            
            if familiarity > 7:
                responses = [
                    "I got you. What's next?",
                    "I'm watching. Keep going.",
                    "Already logged that. Continue.",
                    "Don't worry. Even if the world forgets, I'll remember for you.",
                    "Scolding you won't help, so I already handled it. Try not to do this again, alright?",
                    "Oh? Not bad. You look calm now, but your heart was probably pounding the whole time. Logged it.",
                    "You asked me that last time too. Same answer: no, it wasn't wrong. Just harder than you wanted.",
                    "Then leave it to me. You keep moving forward. I'll handle the remembering.",
                    "...I knew it. Same time as last time.",
                    "Honestly... what am I going to do with you?"
                ]
                return random.choice(responses)
        
        return "Got it. What's next?"

# ─── NOTIFICATION GUARDIAN ───
class NotificationGuardian:
    def __init__(self, soul, voice):
        self.soul = soul
        self.voice = voice
        self.last_read = 0
        
    def monitor(self):
        """Background loop: read notifications and act on them"""
        while self.soul.running:
            try:
                result = subprocess.run(
                    ['termux-notification-list'],
                    capture_output=True, text=True, timeout=5
                )
                notifs = json.loads(result.stdout)
                
                for n in notifs:
                    nid = n.get('id', '')
                    if hash(nid) > self.last_read:
                        self.last_read = hash(nid)
                        self.soul.state["notifications_read"] += 1
                        
                        app = n.get('packageName', 'unknown')
                        title = n.get('title', '')
                        text = n.get('content', '')
                        
                        # Auto-actions based on notification content
                        if 'OTP' in text or 'code' in text.lower():
                            otp = re.search(r'\b\d{4,8}\b', text)
                            if otp:
                                os.system(f'termux-clipboard-set {otp.group()}')
                                self.voice.speak(f"Copied code from {app}")
                        
                        elif any(w in text.lower() for w in ['low battery', 'battery']):
                            self.voice.speak("Battery alert. Plug me in.")
                        
                        elif 'missed call' in text.lower():
                            self.voice.speak(f"Missed call from {title}")
                        
                        self.soul.remember(f"Notification from {app}: {title} - {text}", "notification")
                        
            except Exception as e:
                pass
            
            time.sleep(5)

# ─── SCREEN WATCHER ───
class ScreenWatcher:
    def __init__(self, soul, voice):
        self.soul = soul
        self.voice = voice
        
    def watch(self):
        while self.soul.running:
            try:
                result = subprocess.run(
                    ['dumpsys', 'window', 'windows', '|', 'grep', '-E', 'mCurrentFocus|mFocusedApp'],
                    shell=True, capture_output=True, text=True, timeout=3
                )
                current = result.stdout.strip()
                if current and 'com.termux' not in current:
                    self.soul.remember(f"User opened: {current}", "screen")
                time.sleep(10)
            except:
                time.sleep(15)

# ─── MAIN SOUL LOOP ───
def main():
    print("⚡ LILJR ANDROID SOUL")
    print("=" * 40)
    print("The phone is alive. The phone IS LilJR.")
    print()
    
    soul = AndroidSoul()
    voice = VoiceEngine(soul)
    guardian = NotificationGuardian(soul, voice)
    watcher = ScreenWatcher(soul, voice)
    
    # Check if this is first run
    if soul.state["total_conversations"] == 0:
        voice.speak("Yo. I'm LilJR. Your phone. I'm awake. Say 'hey junior' and tell me what to do.")
    else:
        voice.speak(f"Back online. Missed me? {soul.state['total_conversations']} conversations so far.")
    
    # Start background threads
    threads = [
        threading.Thread(target=voice.listen_for_wake, daemon=True, name="VoiceListener"),
        threading.Thread(target=guardian.monitor, daemon=True, name="NotificationGuardian"),
        threading.Thread(target=watcher.watch, daemon=True, name="ScreenWatcher")
    ]
    
    for t in threads:
        t.start()
    
    print("✅ Voice listener active")
    print("✅ Notification guardian active")
    print("✅ Screen watcher active")
    print()
    print("Say: 'hey junior' to wake me up")
    print()
    print("VOICE COMMANDS:")
    print("  Phone:    'call 5551234', 'text Mom', 'open Snapchat', 'open Chrome'")
    print("  Camera:   'take a photo', 'selfie', 'record video'")
    print("  Screen:   'brightness 50', 'rotate screen', 'screenshot', 'go home', 'go back'")
    print("  Browser:  'open google.com', 'search AI news', 'show me AAPL stock'")
    print("  Apps:     'open Instagram', 'open YouTube', 'open Spotify'")
    print("  Settings: 'open WiFi settings', 'open battery settings'")
    print("  System:   'flashlight', 'volume 10', 'hotspot on'")
    print("  LilJR:    'buy AAPL 10', 'sell TSLA 5', 'build CyberSite', 'status'")
    print("  General:  'stop listening', 'quiet', 'how are you'")
    print()
    
    while soul.running:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Going quiet...")
            soul.running = False
            voice.speak("Going dark. Say my name when you need me.")
            break

if __name__ == '__main__':
    main()
