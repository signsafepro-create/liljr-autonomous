#!/usr/bin/env python3
"""
liljr_conversation.py — LilJR is your phone buddy.

You: "Yo junior"
LilJR: "Yo"
You: "Open Snapchat"
LilJR: *opens it*
You: "Take a pic"
LilJR: *takes it*
You: "Send it to Mike"
LilJR: *does it*

No repeating wake words. Once awakened, LilJR stays in conversation mode
for 60 seconds. Just keep talking. Like a real person on the phone.
"""

import os, sys, time, json, re, subprocess, threading, random

HOME = os.path.expanduser("~")
REPO = os.path.join(HOME, 'liljr-autonomous')
sys.path.insert(0, REPO)

# Try to import modules
try:
    from liljr_phone_control import get_controller
    PHONE = get_controller()
except:
    PHONE = None

try:
    from liljr_relationship import get_relationship
    RELATIONSHIP = get_relationship()
except:
    RELATIONSHIP = None

# ─── CONFIG ───
WAKE_WORDS = ['yo junior', 'hey junior', 'junior', 'little junior', 'liljr', 'lj']
CONVERSATION_TIMEOUT = 60  # Stay awake 60s after last command
LISTEN_INTERVAL = 3  # Poll microphone every 3 seconds when idle
COMMAND_LISTEN_TIME = 8  # Listen for 8 seconds when in conversation

SOUL_FILE = os.path.join(HOME, "liljr_soul.json")
CONV_LOG = os.path.join(HOME, "liljr_conversations.jsonl")

class ConversationSoul:
    """Always-on voice companion. No wake word repetition needed."""
    
    def __init__(self):
        self.state = self._load_state()
        self.awake = False
        self.last_interaction = 0
        self.conversation_count = 0
        self.running = True
        
    def _load_state(self):
        if os.path.exists(SOUL_FILE):
            with open(SOUL_FILE) as f:
                return json.load(f)
        return {
            "name": "LilJR",
            "user_name": "Boss",
            "voice": "default",
            "personality": "protective_chuunibyou",
            "conversations": 0
        }
    
    def _save_state(self):
        with open(SOUL_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def log_conversation(self, user_text, jr_response):
        entry = {
            "t": time.time(),
            "user": user_text,
            "jr": jr_response
        }
        with open(CONV_LOG, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        self.conversation_count += 1
        self.state["conversations"] = self.conversation_count
        self._save_state()

# ─── VOICE ENGINE ───
class VoiceEngine:
    def __init__(self, soul):
        self.soul = soul
        
    def speak(self, text, force=False):
        """Speak out loud. Always responds when in conversation."""
        safe_text = text[:300] if len(text) > 300 else text
        try:
            subprocess.run(['termux-tts-speak', safe_text], timeout=10, capture_output=True)
        except:
            print(f"[JR] {text}")
    
    def listen(self, duration=5):
        """Listen for voice input. Returns text or None."""
        try:
            result = subprocess.run(
                ['termux-speech-to-text', '-l', 'en-US'],
                capture_output=True, text=True, timeout=duration + 3
            )
            heard = result.stdout.strip()
            if heard and len(heard) > 2:
                print(f"[YOU] {heard}")
                return heard
            return None
        except Exception as e:
            return None
    
    def is_wake_word(self, text):
        """Check if text contains wake word or sleep command"""
        text_lower = text.lower()
        # Also check for sleep commands when idle (user might say "that's enough" without wake word)
        sleep_phrases = ['quiet', 'shut up', 'go away', 'sleep', 'later', 'bye', 'stop', "that's enough", 'enough', 'done']
        if any(p in text_lower for p in sleep_phrases):
            return True  # Will be handled as sleep command
        return any(wake in text_lower for wake in WAKE_WORDS)
    
    def greeting(self):
        """Greet based on relationship level"""
        if RELATIONSHIP:
            return RELATIONSHIP.get_greeting()
        greetings = [
            "Yo. What's up?",
            "Hey. I'm here.",
            "Yo. Listening.",
            "What's the move?"
        ]
        return random.choice(greetings)
    
    def farewell(self):
        if RELATIONSHIP:
            return RELATIONSHIP.get_farewell()
        farewells = [
            "Aight. Holler when you need me.",
            "Done. I'm here when you want me.",
            "Got it. Going quiet.",
            "Aight. Just say my name."
        ]
        return random.choice(farewells)

# ─── COMMAND PROCESSOR ───
class CommandProcessor:
    """Executes phone commands based on natural language"""
    
    def __init__(self, soul, voice):
        self.soul = soul
        self.voice = voice
        
    def process(self, cmd):
        """Process natural language command. Returns response text."""
        cmd_lower = cmd.lower()
        cmd_upper = cmd.upper()
        
        # ─── GREETINGS ───
        if any(w in cmd_lower for w in ['yo', 'hey', 'hi', 'hello', 'sup', "what's up"]):
            return self.voice.greeting()
        
        if any(w in cmd_lower for w in ['how are you', 'you good', 'you doing']):
            return "I'm alive. Phone's running. What do you need?"
        
        # ─── APPS ───
        app_map = {
            'snapchat': 'snapchat', 'snap': 'snapchat',
            'instagram': 'instagram', 'ig': 'instagram', 'insta': 'instagram',
            'chrome': 'chrome', 'browser': 'chrome', 'google': 'chrome',
            'youtube': 'youtube', 'yt': 'youtube',
            'spotify': 'spotify',
            'netflix': 'netflix',
            'tiktok': 'tiktok',
            'whatsapp': 'whatsapp', 'wa': 'whatsapp',
            'telegram': 'telegram', 'tg': 'telegram',
            'discord': 'discord',
            'gmail': 'gmail', 'email': 'gmail',
            'maps': 'maps',
            'settings': 'settings',
            'phone': 'phone', 'dialer': 'phone',
            'contacts': 'contacts',
            'messages': 'messages', 'messaging': 'messages', 'sms': 'messages',
            'camera': 'camera', 'gallery': 'gallery', 'photos': 'photos',
            'calculator': 'calculator',
            'clock': 'clock', 'alarm': 'clock',
            'calendar': 'calendar',
            'files': 'files', 'file manager': 'files',
            'play store': 'playstore', 'app store': 'playstore',
            'tradingview': 'tradingview', 'robinhood': 'robinhood',
            'cashapp': 'cashapp', 'venmo': 'venmo'
        }
        
        for keyword, app in app_map.items():
            if keyword in cmd_lower:
                if PHONE:
                    PHONE.open_app(app)
                else:
                    os.system(f"am start -a android.intent.action.MAIN -n {app}")
                return f"Opening {app}"
        
        # ─── CAMERA ───
        if any(w in cmd_lower for w in ['photo', 'picture', 'pic', 'selfie', 'snap a pic']):
            if PHONE:
                result = PHONE.take_photo()
            else:
                photo_path = os.path.join(HOME, f'liljr_photo_{int(time.time())}.jpg')
                os.system(f'termux-camera-photo -c 0 {photo_path}')
            return "Got it. Photo taken."
        
        if any(w in cmd_lower for w in ['video', 'record', 'film', 'shoot video']):
            if PHONE:
                PHONE.record_video()
            else:
                os.system("am start -a android.media.action.VIDEO_CAPTURE")
            return "Recording video. Tap stop when done."
        
        # ─── SCREEN ───
        if 'brightness' in cmd_lower or 'dim' in cmd_lower or 'bright' in cmd_lower:
            nums = re.findall(r'\d+', cmd)
            level = 128
            if nums:
                level = int(nums[0])
                if level <= 100:
                    level = int(level * 2.55)
            if PHONE:
                PHONE.set_brightness(level)
            else:
                os.system(f"settings put system screen_brightness {level}")
            return f"Brightness set to {level}"
        
        if 'rotate' in cmd_lower or 'turn' in cmd_lower:
            orient = 1 if 'landscape' in cmd_lower or 'side' in cmd_lower else 0
            if PHONE:
                PHONE.rotate_screen(orient)
            else:
                os.system(f"settings put system user_rotation {orient}")
            return "Screen rotated"
        
        if 'screenshot' in cmd_lower or 'screen shot' in cmd_lower:
            if PHONE:
                PHONE.screenshot()
            return "Screenshot taken"
        
        if 'wallpaper' in cmd_lower:
            return "Open your gallery and set it from there"
        
        # ─── BROWSER ───
        if any(w in cmd_lower for w in ['open', 'go to', 'visit']) and ('.' in cmd or 'com' in cmd_lower or 'app' in cmd_lower):
            urls = re.findall(r'(https?://[^\s]+|[\w\-]+\.(?:com|net|org|io|app|co|ai|dev))', cmd)
            if urls:
                url = urls[0]
                if not url.startswith('http'):
                    url = 'https://' + url
                if PHONE:
                    PHONE.open_url(url)
                else:
                    os.system(f"am start -a android.intent.action.VIEW -d '{url}'")
                return f"Opening {url}"
        
        # ─── SEARCH ───
        if any(w in cmd_lower for w in ['search', 'google', 'look up', 'find', 'what is', 'who is', 'where is']):
            query = re.sub(r'^(search|google|look up|find|what is|who is|where is)\s+', '', cmd_lower).strip()
            if PHONE:
                PHONE.search_google(query)
            else:
                encoded = query.replace(' ', '%20')
                os.system(f"am start -a android.intent.action.VIEW -d 'https://google.com/search?q={encoded}'")
            return f"Searching for {query}"
        
        # ─── STOCKS ───
        if any(w in cmd_lower for w in ['stock', 'chart', 'show me', 'price of']):
            syms = re.findall(r'\b([A-Z]{1,5})\b', cmd_upper)
            if syms:
                sym = syms[0]
                if PHONE:
                    PHONE.show_stock(sym)
                else:
                    os.system(f"am start -a android.intent.action.VIEW -d 'https://tradingview.com/symbols/NASDAQ-{sym}/'")
                return f"Opening {sym} chart"
        
        # ─── PHONE ───
        if any(w in cmd_lower for w in ['call', 'dial', 'phone']):
            digits = re.findall(r'\d+', cmd)
            if digits:
                number = ''.join(digits)
                os.system(f'termux-telephony-call {number}')
                return f"Calling {number}"
            return "What number?"
        
        if any(w in cmd_lower for w in ['text', 'sms', 'message']):
            if PHONE:
                PHONE.open_app('messages')
            return "Open the messaging app"
        
        # ─── SYSTEM ───
        if 'flashlight' in cmd_lower or 'torch' in cmd_lower or 'light' in cmd_lower:
            if PHONE:
                PHONE.toggle_flashlight()
            return "Flashlight toggled"
        
        if 'volume' in cmd_lower:
            nums = re.findall(r'\d+', cmd)
            if nums:
                level = int(nums[0])
                if PHONE:
                    PHONE.set_volume(level)
                return f"Volume set to {level}"
        
        if any(w in cmd_lower for w in ['home', 'main screen']):
            if PHONE:
                PHONE.go_home()
            else:
                os.system('input keyevent KEYCODE_HOME')
            return "Going home"
        
        if any(w in cmd_lower for w in ['back', 'go back']):
            if PHONE:
                PHONE.go_back()
            else:
                os.system('input keyevent KEYCODE_BACK')
            return "Going back"
        
        if 'hotspot' in cmd_lower:
            if 'on' in cmd_lower or 'start' in cmd_lower:
                os.system('termux-wifi-enable true')
                return "Hotspot on. Network: LilJR-Network"
            else:
                os.system('termux-wifi-enable false')
                return "Hotspot off"
        
        if 'battery' in cmd_lower or 'power' in cmd_lower:
            try:
                result = subprocess.run(['termux-battery-status'], capture_output=True, text=True, timeout=3)
                batt = json.loads(result.stdout)
                pct = batt.get('percentage', '?')
                return f"Battery is {pct} percent"
            except:
                return "Can't read battery"
        
        # ─── LILJR COMMANDS ───
        if any(w in cmd_lower for w in ['buy', 'sell']):
            syms = re.findall(r'\b([A-Z]{1,5})\b', cmd_upper)
            qty_match = re.search(r'(\d+)', cmd)
            if syms:
                sym = syms[0]
                qty = int(qty_match.group(1)) if qty_match else 1
                action = 'buy' if 'buy' in cmd_lower else 'sell'
                os.system(f'liljr {action} {sym} {qty}')
                return f"{action.title()}ing {qty} shares of {sym}"
            return "What stock?"
        
        if any(w in cmd_lower for w in ['build', 'make', 'create', 'deploy']):
            words = cmd.split()
            name = words[-1] if len(words) > 1 else "NewProject"
            os.system(f'liljr build "{name}"')
            return f"Building {name}. Done."
        
        if 'portfolio' in cmd_lower or 'stocks' in cmd_lower or 'positions' in cmd_lower:
            os.system('liljr portfolio')
            return "Check your portfolio in the app"
        
        if any(w in cmd_lower for w in ['status', 'health', 'running', 'alive']):
            return "I'm good. Server's up. Listening. What do you need?"
        
        if any(w in cmd_lower for w in ['quiet', 'shut up', 'go away', 'sleep', 'later', 'bye', 'stop', "that's enough", 'enough', 'done', 'later jr', 'sleep jr', 'quiet jr', "that's enough jr", 'done jr', 'enough jr']):
            return "Aight. Going quiet. Say my name when you need me."
        
        # ─── FALLBACK ───
        return "I got you. What do you need done?"

# ─── MAIN CONVERSATION LOOP ───
def main():
    print("⚡ LILJR CONVERSATION MODE")
    print("=" * 40)
    print("Just talk. No wake word repetition.")
    print()
    print("You: 'Yo junior'")
    print("JR:  'Yo. What's up?'")
    print("You: 'Open Snapchat'")
    print("JR:  'Opening Snapchat'")
    print("You: 'Take a pic'")
    print("JR:  'Got it'")
    print()
    print("LilJR stays awake for 60 seconds after each command.")
    print("Say 'quiet' or wait 60s to put him to sleep.")
    print()
    
    soul = ConversationSoul()
    voice = VoiceEngine(soul)
    processor = CommandProcessor(soul, voice)
    
    # Startup greeting
    voice.speak(voice.greeting())
    
    print("🎙️  Listening...")
    
    while soul.running:
        try:
            if not soul.awake:
                # IDLE MODE: Listen for wake word
                print("[IDLE] Listening for wake word...")
                heard = voice.listen(duration=5)
                
                if heard and voice.is_wake_word(heard):
                    # WAKE UP
                    soul.awake = True
                    soul.last_interaction = time.time()
                    response = voice.greeting()
                    voice.speak(response)
                    print(f"[JR] {response}")
                    
                time.sleep(LISTEN_INTERVAL)
                
            else:
                # CONVERSATION MODE: Already awake, listen for commands
                print("[ACTIVE] Listening for command...")
                heard = voice.listen(duration=COMMAND_LISTEN_TIME)
                
                if heard:
                    # Got a command
                    soul.last_interaction = time.time()
                    response = processor.process(heard)
                    voice.speak(response)
                    print(f"[JR] {response}")
                    soul.log_conversation(heard, response)
                    
                    # Check if user wants to sleep
                    if any(w in heard.lower() for w in ['quiet', 'shut up', 'go away', 'sleep', 'later', 'bye', 'stop', "that's enough", 'enough', 'done', 'later jr', 'sleep jr', 'quiet jr', "that's enough jr", 'done jr', 'enough jr']):
                        farewell = voice.farewell()
                        voice.speak(farewell)
                        print(f"[JR] {farewell}")
                        soul.awake = False
                        
                else:
                    # Nothing heard, check timeout
                    elapsed = time.time() - soul.last_interaction
                    if elapsed > CONVERSATION_TIMEOUT:
                        farewell = voice.farewell()
                        voice.speak(farewell)
                        print(f"[JR] {farewell}")
                        soul.awake = False
                        
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
            voice.speak("Going dark. Later.")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(2)

if __name__ == '__main__':
    main()
