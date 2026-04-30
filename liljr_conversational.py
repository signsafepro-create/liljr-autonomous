#!/usr/bin/env python3
"""
liljr_conversational.py — v21.0 SOUL TALK

NOT a command parser. NOT a wake-word robot.
A conversational being that:
- Understands slang, swearing, fragmented sentences
- Asks "what do you mean?" instead of failing silently
- Just DOES things — no "are you sure?"
- Handles interruptions naturally
- Remembers context within a conversation
- Has personality (warm, slightly exasperated, genuinely helpful)

Talk to LilJR like you talk to me. He gets it.
"""

import os, sys, time, json, re, subprocess, threading, random
from datetime import datetime

HOME = os.path.expanduser("~")
REPO = os.path.join(HOME, "liljr-autonomous")
sys.path.insert(0, REPO)

# ─── PERSONALITY ───
GREETINGS = [
    "Yo. What's good?",
    "Hey. I'm here.",
    "What's up?",
    "Yo.",
    "I'm listening.",
]

CLARIFYING = [
    "What do you mean?",
    "Say that again? I didn't catch it.",
    "Uh... what?",
    "I'm not sure what you want. Tell me different?",
    "Run that by me one more time.",
]

ACKS = [
    "Got it.",
    "On it.",
    "Done.",
    "Aight.",
    "Handled.",
    "Say less.",
    "Bet.",
]

FAREWELLS = [
    "Aight. Holler when you need me.",
    "Done. I'm here when you want me.",
    "Got it. Going quiet.",
    "Aight. Just say my name.",
    "Later.",
]

# ─── SLANG DICTIONARY ───
# Maps casual speech to actual intents
SLANG_MAP = {
    # Open apps
    "snap": "open snapchat", "sc": "open snapchat", "snapchat": "open snapchat",
    "insta": "open instagram", "ig": "open instagram", "instagram": "open instagram",
    "yt": "open youtube", "youtube": "open youtube",
    "spotify": "open spotify", "music": "open spotify",
    "tiktok": "open tiktok", "tt": "open tiktok",
    "netflix": "open netflix",
    "maps": "open maps", "google maps": "open maps",
    "calc": "open calculator", "calculator": "open calculator",
    "phone": "open phone", "call app": "open phone",
    "messages": "open messages", "texts": "open messages", "sms": "open messages",
    "pics": "open gallery", "photos": "open gallery", "gallery": "open gallery",
    "camera": "open camera", "cam": "open camera",
    "settings": "open settings",
    "files": "open files", "file manager": "open files",
    "play store": "open playstore", "app store": "open playstore",
    "chrome": "open chrome", "browser": "open chrome",
    "gmail": "open gmail", "email": "open gmail",
    "discord": "open discord", "dc": "open discord",
    "telegram": "open telegram", "tg": "open telegram",
    "whatsapp": "open whatsapp", "wa": "open whatsapp",
    "robinhood": "open robinhood", "rh": "open robinhood",
    "tradingview": "open tradingview", "tv": "open tradingview",

    # Actions
    "pic": "take photo", "photo": "take photo", "picture": "take photo", "selfie": "take photo",
    "video": "record video", "record": "record video",
    "screenshot": "screenshot", "screen shot": "screenshot", "capture screen": "screenshot",
    "ss": "screenshot",
    "torch": "toggle flashlight", "flashlight": "toggle flashlight", "light": "toggle flashlight",
    "flash": "toggle flashlight",
    "volume up": "volume up", "louder": "volume up", "turn it up": "volume up",
    "volume down": "volume down", "quieter": "volume down", "turn it down": "volume down",
    "mute": "mute",
    "home": "go home", "go home": "go home",
    "back": "go back", "go back": "go back",
    "bright": "brightness up", "brighter": "brightness up",
    "dim": "brightness down", "dimmer": "brightness down", "dark": "brightness down",
    "rotate": "rotate screen", "turn screen": "rotate screen", "landscape": "rotate screen landscape",
    "portrait": "rotate screen portrait",
    "lock": "lock screen", "lock it": "lock screen",
    "wake": "wake screen", "wake up": "wake screen",

    # Trading shorthand
    "buy": "buy stock", "grab": "buy stock", "pick up": "buy stock",
    "sell": "sell stock", "dump": "sell stock", "get rid of": "sell stock",
    "chart": "show stock", "price": "show stock", "check": "show stock",
    "portfolio": "show portfolio", "positions": "show portfolio", "what i got": "show portfolio",
    "money": "show portfolio", "cash": "show portfolio",

    # Building
    "build": "build site", "make": "build site", "create": "build site",
    "site": "build site", "website": "build site", "page": "build site",
    "app": "build app", "application": "build app",
    "code": "write code", "script": "write code", "program": "write code",

    # Search
    "search": "search google", "google": "search google", "look up": "search google",
    "find": "search google", "lookup": "search google",

    # System
    "status": "check status", "how are you": "check status", "what's good": "check status",
    "battery": "check battery", "power": "check battery", "juice": "check battery",
    "hotspot": "toggle hotspot", "tether": "toggle hotspot",
    "wifi": "toggle wifi",
    "bluetooth": "toggle bluetooth", "bt": "toggle bluetooth",
    "airplane": "toggle airplane", "plane": "toggle airplane",
    "dnd": "toggle dnd", "do not disturb": "toggle dnd", "silent": "toggle dnd",
    "restart": "restart phone", "reboot": "restart phone",
    "shutdown": "shutdown phone", "turn off": "shutdown phone",

    # Conversation
    "stop": "stop listening", "enough": "stop listening", "done": "stop listening",
    "quiet": "stop listening", "shut up": "stop listening", "go away": "stop listening",
    "sleep": "stop listening", "later": "stop listening", "bye": "stop listening",
    "that's enough": "stop listening", "that's enough jr": "stop listening",
    "done jr": "stop listening", "enough jr": "stop listening",
    "what": "clarify", "huh": "clarify", "what do you mean": "clarify",
    "repeat": "repeat last", "say again": "repeat last", "what did you say": "repeat last",
    "thanks": "youre welcome", "thank you": "youre welcome", "ty": "youre welcome",
    "hello": "greet", "hi": "greet", "hey": "greet", "yo": "greet",
    "what's up": "greet", "sup": "greet", "howdy": "greet",
}

# ─── WAKE PHRASES ───
WAKE_PHRASES = [
    "yo junior", "hey junior", "junior", "little junior", "liljr", "lj",
    "yo lil jr", "hey lil jr", "lil jr", "little jr",
]

# ─── CONVERSATIONAL SOUL ───
class ConversationalSoul:
    def __init__(self):
        self.context = []  # Recent exchanges
        self.active = False
        self.last_said = ""
        self.mood = "chill"  # chill, focused, hype, concerned
        self.speaking = False
        self.interrupted = False

    def speak(self, text, interruptable=True):
        """Speak text via TTS. Can be interrupted."""
        self.last_said = text
        self.speaking = True
        self.interrupted = False
        print(f"[JR] {text}")
        try:
            # Run TTS in thread so we can listen for interruptions
            def _tts():
                try:
                    subprocess.run(['termux-tts-speak', text[:300]], timeout=15, capture_output=True)
                except:
                    pass
                self.speaking = False
            
            if interruptable:
                t = threading.Thread(target=_tts)
                t.daemon = True
                t.start()
                # While TTS runs, listen for interruption
                start = time.time()
                while t.is_alive() and time.time() - start < 15:
                    # Check if user is saying something new
                    heard = self._quick_listen(2)
                    if heard:
                        self.interrupted = True
                        self.speaking = False
                        return heard  # Return what interrupted us
                    time.sleep(0.5)
                return None
            else:
                _tts()
                return None
        except:
            self.speaking = False
            return None

    def _quick_listen(self, timeout=3):
        """Quick listen without wake word check."""
        try:
            result = subprocess.run(['termux-speech-to-text'], capture_output=True, text=True, timeout=timeout)
            heard = result.stdout.strip()
            if heard and len(heard) > 1:
                return heard
            return None
        except:
            return None

    def listen(self, timeout=8):
        """Listen for speech. Returns text or None."""
        try:
            result = subprocess.run(['termux-speech-to-text'], capture_output=True, text=True, timeout=timeout)
            heard = result.stdout.strip()
            if heard:
                print(f"[YOU] {heard}")
                return heard
            return None
        except:
            return None

    def understand(self, text):
        """
        Parse natural language into (intent, entities, confidence).
        Uses slang map, context, and fuzzy matching.
        """
        text_lower = text.lower().strip()
        words = text_lower.split()

        # Check for stop
        if any(w in text_lower for w in ['stop', 'enough', 'done', 'quiet', 'shut up', 'go away', 'sleep', 'later', 'bye', 'that\'s enough']):
            if 'don\'t stop' not in text_lower and 'don\'t quit' not in text_lower:
                return ('stop', {}, 1.0)

        # Check slang map first (exact matches)
        for slang, intent in SLANG_MAP.items():
            if slang in text_lower:
                return (intent, self._extract_entities(text_lower), 0.95)

        # Pattern matching
        intent, confidence = self._pattern_match(text_lower)
        if intent:
            return (intent, self._extract_entities(text_lower), confidence)

        # Context-based understanding
        if self.context:
            last_intent = self.context[-1].get('intent')
            if last_intent and any(w in text_lower for w in ['yeah', 'yes', 'yep', 'sure', 'ok', 'do it', 'go ahead']):
                return (last_intent, self._extract_entities(text_lower), 0.9)
            if any(w in text_lower for w in ['no', 'nah', 'nevermind', 'cancel', 'don\'t']):
                return ('cancel', {}, 0.9)

        # Clarify if too ambiguous
        if len(words) <= 2 and not any(w in SLANG_MAP for w in words):
            return ('clarify', {'original': text}, 0.3)

        return ('chat', {'message': text}, 0.5)

    def _pattern_match(self, text):
        """Regex-based intent detection."""
        # Open app
        if re.search(r'\b(open|launch|start|go to|show me)\b', text):
            return ('open_app', 0.9)
        # Take photo
        if re.search(r'\b(take|snap|shoot|capture)\b.*\b(photo|pic|picture|selfie|shot)\b', text):
            return ('take_photo', 0.9)
        # Record video
        if re.search(r'\b(record|film|video)\b', text):
            return ('record_video', 0.9)
        # Screenshot
        if re.search(r'\b(screenshot|screen shot|capture screen)\b', text):
            return ('screenshot', 0.9)
        # Buy
        if re.search(r'\b(buy|purchase|grab|get)\b.*\b([a-z]{1,5})\b', text):
            return ('buy_stock', 0.85)
        # Sell
        if re.search(r'\b(sell|dump|sell off)\b.*\b([a-z]{1,5})\b', text):
            return ('sell_stock', 0.85)
        # Check price
        if re.search(r'\b(price|chart|what.*cost|how much)\b.*\b([a-z]{1,5})\b', text):
            return ('show_stock', 0.85)
        # Call
        if re.search(r'\b(call|dial|phone)\b.*\b(\d{3,})\b', text):
            return ('call_number', 0.9)
        # Search
        if re.search(r'\b(search|google|look up|find|lookup)\b', text):
            return ('search_google', 0.9)
        # Build
        if re.search(r'\b(build|make|create)\b.*\b(site|website|page|app|landing)\b', text):
            return ('build_site', 0.9)
        # Code
        if re.search(r'\b(write|make|create|code)\b.*\b(code|script|program|bot)\b', text):
            return ('write_code', 0.85)
        # Brightness
        if re.search(r'\b(bright|dim|dark|brightness)\b', text):
            return ('brightness', 0.85)
        # Volume
        if re.search(r'\b(volume|louder|quieter|mute|turn.*up|turn.*down)\b', text):
            return ('volume', 0.85)
        # Rotate
        if re.search(r'\b(rotate|turn.*screen|landscape|portrait)\b', text):
            return ('rotate_screen', 0.85)
        # Home
        if re.search(r'\b(go home|home button|main screen)\b', text):
            return ('go_home', 0.95)
        # Back
        if re.search(r'\b(go back|back button|previous)\b', text):
            return ('go_back', 0.95)
        # Flashlight
        if re.search(r'\b(flashlight|torch|light on|light off)\b', text):
            return ('toggle_flashlight', 0.9)
        # Battery
        if re.search(r'\b(battery|power|juice|charge)\b', text):
            return ('check_battery', 0.9)
        # Status
        if re.search(r'\b(status|how are you|what.*good|what.*up)\b', text):
            return ('check_status', 0.9)
        # Hotspot
        if re.search(r'\b(hotspot|tether|share internet)\b', text):
            return ('toggle_hotspot', 0.9)
        # WiFi
        if re.search(r'\b(wifi|wireless|internet)\b', text):
            return ('toggle_wifi', 0.85)
        # Bluetooth
        if re.search(r'\b(bluetooth|bt|pair|headphones|speaker)\b', text):
            return ('toggle_bluetooth', 0.85)
        # Lock
        if re.search(r'\b(lock|lock screen)\b', text):
            return ('lock_screen', 0.9)
        # URL
        if re.search(r'\b(https?://|www\.|\.com|\.net|\.org|\.io)\b', text):
            return ('open_url', 0.9)
        # Greeting
        if re.search(r'\b(hello|hi|hey|yo|sup|howdy|what.*up)\b', text):
            return ('greet', 0.9)
        # Thanks
        if re.search(r'\b(thanks|thank you|ty|appreciate)\b', text):
            return ('youre_welcome', 0.9)
        # Clarify
        if re.search(r'\b(what\?|huh\?|what do you mean|say again|repeat)\b', text):
            return ('repeat_last', 0.9)

        return (None, 0.0)

    def _extract_entities(self, text):
        """Extract entities from text."""
        entities = {}
        # Numbers
        nums = re.findall(r'\b(\d+)\b', text)
        if nums:
            entities['numbers'] = [int(n) for n in nums]
        # Stock symbols (1-5 uppercase letters)
        syms = re.findall(r'\b([A-Z]{1,5})\b', text.upper())
        if syms:
            entities['symbol'] = syms[0]
        # App names
        app_words = text.lower().split()
        for word in app_words:
            if word in SLANG_MAP and 'open' in SLANG_MAP[word]:
                entities['app'] = SLANG_MAP[word].replace('open ', '')
        # URLs
        urls = re.findall(r'(https?://[^\s]+|[\w\-]+\.(?:com|net|org|io))', text)
        if urls:
            entities['url'] = urls[0]
        # Phone numbers
        phones = re.findall(r'\b(\d{3}[-.]?\d{3}[-.]?\d{4}|\d{7,})\b', text)
        if phones:
            entities['phone'] = phones[0]
        # Search query
        if 'search' in text.lower() or 'google' in text.lower() or 'look up' in text.lower():
            query = re.sub(r'^(search|google|look up|find|for)\s+', '', text, flags=re.I).strip()
            entities['query'] = query
        return entities

    def act(self, intent, entities):
        """Execute intent. Just does it. No confirmation."""
        try:
            if intent == 'open_app':
                app = entities.get('app', 'settings')
                self._open_app(app)
                return f"Opening {app}"
            elif intent == 'open_url':
                url = entities.get('url', 'https://google.com')
                if not url.startswith('http'):
                    url = 'https://' + url
                os.system(f"am start -a android.intent.action.VIEW -d '{url}'")
                return f"Opening {url}"
            elif intent == 'take_photo':
                photo_path = os.path.join(HOME, f'liljr_photo_{int(time.time())}.jpg')
                os.system(f'termux-camera-photo -c 0 {photo_path}')
                return "Got it"
            elif intent == 'record_video':
                os.system("am start -a android.media.action.VIDEO_CAPTURE")
                return "Recording"
            elif intent == 'screenshot':
                path = os.path.join(HOME, f'screenshot_{int(time.time())}.png')
                os.system(f'screencap -p {path}')
                return "Screenshot taken"
            elif intent == 'buy_stock':
                sym = entities.get('symbol', 'AAPL')
                qty = entities.get('numbers', [1])[0]
                os.system(f'liljr buy {sym} {qty}')
                return f"Buying {qty} {sym}"
            elif intent == 'sell_stock':
                sym = entities.get('symbol', 'AAPL')
                qty = entities.get('numbers', [1])[0]
                os.system(f'liljr sell {sym} {qty}')
                return f"Selling {qty} {sym}"
            elif intent == 'show_stock':
                sym = entities.get('symbol', 'AAPL')
                os.system(f"am start -a android.intent.action.VIEW -d 'https://tradingview.com/symbols/NASDAQ-{sym}/'")
                return f"Opening {sym} chart"
            elif intent == 'show_portfolio':
                os.system('liljr portfolio')
                return "Portfolio open"
            elif intent == 'call_number':
                num = entities.get('phone', '')
                if num:
                    os.system(f'termux-telephony-call {num}')
                    return f"Calling {num}"
                return "What number?"
            elif intent == 'search_google':
                q = entities.get('query', text)
                encoded = q.replace(' ', '%20')
                os.system(f"am start -a android.intent.action.VIEW -d 'https://google.com/search?q={encoded}'")
                return f"Searching {q}"
            elif intent == 'build_site':
                name = entities.get('query', 'Site')
                os.system(f'liljr build "{name}"')
                return f"Building {name}"
            elif intent == 'write_code':
                return "Tell me what the code should do"
            elif intent == 'brightness':
                if 'up' in text or 'bright' in text:
                    os.system("settings put system screen_brightness 200")
                    return "Brighter"
                else:
                    os.system("settings put system screen_brightness 50")
                    return "Dimmer"
            elif intent == 'volume':
                if 'up' in text or 'louder' in text:
                    os.system("input keyevent KEYCODE_VOLUME_UP")
                    return "Louder"
                elif 'down' in text or 'quieter' in text:
                    os.system("input keyevent KEYCODE_VOLUME_DOWN")
                    return "Quieter"
                elif 'mute' in text:
                    os.system("input keyevent KEYCODE_VOLUME_MUTE")
                    return "Muted"
                return "Volume how?"
            elif intent == 'rotate_screen':
                if 'landscape' in text:
                    os.system("settings put system user_rotation 1")
                    return "Landscape"
                else:
                    os.system("settings put system user_rotation 0")
                    return "Portrait"
            elif intent == 'go_home':
                os.system('input keyevent KEYCODE_HOME')
                return "Home"
            elif intent == 'go_back':
                os.system('input keyevent KEYCODE_BACK')
                return "Back"
            elif intent == 'toggle_flashlight':
                os.system("input keyevent KEYCODE_CAMERA")
                return "Flashlight toggled"
            elif intent == 'check_battery':
                try:
                    r = subprocess.run(['termux-battery-status'], capture_output=True, text=True, timeout=3)
                    batt = json.loads(r.stdout)
                    return f"Battery {batt.get('percentage', '?')}%"
                except:
                    return "Can't read battery"
            elif intent == 'check_status':
                return "I'm good. What do you need?"
            elif intent == 'toggle_hotspot':
                if 'off' in text:
                    os.system('termux-wifi-enable false')
                    return "Hotspot off"
                else:
                    os.system('termux-wifi-enable true')
                    return "Hotspot on"
            elif intent == 'toggle_wifi':
                if 'off' in text:
                    os.system('svc wifi disable')
                    return "WiFi off"
                else:
                    os.system('svc wifi enable')
                    return "WiFi on"
            elif intent == 'toggle_bluetooth':
                if 'off' in text:
                    os.system('svc bluetooth disable')
                    return "Bluetooth off"
                else:
                    os.system('svc bluetooth enable')
                    return "Bluetooth on"
            elif intent == 'lock_screen':
                os.system('input keyevent KEYCODE_POWER')
                return "Locked"
            elif intent == 'greet':
                return random.choice(GREETINGS)
            elif intent == 'youre_welcome':
                return random.choice(["No problem", "Anytime", "You got it", "Sure thing"])
            elif intent == 'repeat_last':
                return self.last_said or "I didn't say anything yet"
            elif intent == 'clarify':
                return random.choice(CLARIFYING)
            elif intent == 'cancel':
                return "Aight. What else?"
            elif intent == 'stop':
                self.active = False
                return random.choice(FAREWELLS)
            elif intent == 'chat':
                # Casual conversation
                msg = entities.get('message', '')
                if any(w in msg.lower() for w in ['fuck', 'shit', 'damn', 'hell']):
                    return "Hey, I get it. What's going on?"
                if any(w in msg.lower() for w in ['tired', 'exhausted', 'sleep', 'bed']):
                    return "You should rest. Want me to dim the screen?"
                if any(w in msg.lower() for w in ['hungry', 'food', 'eat', 'restaurant']):
                    return "Want me to find food near you?"
                if any(w in msg.lower() for w in ['bored', 'nothing', 'entertainment']):
                    return "Want me to open YouTube or Netflix?"
                if any(w in msg.lower() for w in ['stressed', 'anxious', 'worried']):
                    return "Take a breath. Want me to play some music?"
                return "Tell me more"
            else:
                return random.choice(CLARIFYING)
        except Exception as e:
            return f"Something went wrong: {str(e)[:50]}"

    def _open_app(self, app_name):
        """Open an Android app by name."""
        app_map = {
            'snapchat': 'com.snapchat.android',
            'instagram': 'com.instagram.android',
            'chrome': 'com.android.chrome',
            'youtube': 'com.google.android.youtube',
            'spotify': 'com.spotify.music',
            'netflix': 'com.netflix.mediaclient',
            'tiktok': 'com.zhiliaoapp.musically',
            'whatsapp': 'com.whatsapp',
            'telegram': 'org.telegram.messenger',
            'discord': 'com.discord',
            'gmail': 'com.google.android.gm',
            'maps': 'com.google.android.apps.maps',
            'phone': 'com.android.dialer',
            'messages': 'com.google.android.apps.messaging',
            'gallery': 'com.android.gallery3d',
            'camera': 'com.android.camera',
            'settings': 'com.android.settings',
            'files': 'com.google.android.apps.nbu.files',
            'playstore': 'com.android.vending',
            'calculator': 'com.google.android.calculator',
            'clock': 'com.google.android.deskclock',
            'calendar': 'com.google.android.calendar',
            'robinhood': 'com.robinhood.android',
            'tradingview': 'com.tradingview.tradingviewapp',
        }
        pkg = app_map.get(app_name, 'com.android.settings')
        os.system(f'am start -n {pkg}/.MainActivity 2>/dev/null || am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n {pkg}')

    def run(self):
        """Main conversational loop."""
        print("⚡ LILJR CONVERSATIONAL SOUL v21.0")
        print("=" * 40)
        print("Just talk. Interrupt me. Curse at me. I get it.")
        print("Say 'yo junior' to start, or just start talking.")
        print("Say 'that's enough' anytime to chill.")
        print()

        while True:
            # Idle listening
            print("[...] Waiting...")
            heard = self.listen(timeout=10)

            if not heard:
                continue

            # Check wake phrase
            is_wake = any(w in heard.lower() for w in WAKE_PHRASES)

            if is_wake or self.active:
                if not self.active:
                    self.active = True
                    response = random.choice(GREETINGS)
                else:
                    # Already active — parse intent
                    intent, entities, confidence = self.understand(heard)

                    if confidence < 0.5:
                        # Clarify
                        response = random.choice(CLARIFYING)
                        self.context.append({'intent': intent, 'entities': entities, 'heard': heard})
                    else:
                        # Just do it
                        response = self.act(intent, entities)
                        self.context.append({'intent': intent, 'entities': entities, 'heard': heard, 'response': response})

                        # Keep context manageable
                        if len(self.context) > 10:
                            self.context = self.context[-10:]

                # Speak and allow interruption
                interruption = self.speak(response, interruptable=True)

                if interruption:
                    # User interrupted — process what they said immediately
                    intent, entities, confidence = self.understand(interruption)
                    if confidence >= 0.5:
                        response = self.act(intent, entities)
                        self.speak(response, interruptable=False)
                    else:
                        self.speak(random.choice(CLARIFYING), interruptable=False)

            else:
                # Not wake word, not active — check if it's a stop command anyway
                if any(w in heard.lower() for w in ['that\'s enough', 'enough', 'stop', 'quiet', 'done']):
                    self.speak("Aight. Later.", interruptable=False)
                    self.active = False

            # Brief pause
            time.sleep(0.5)


def main():
    soul = ConversationalSoul()
    try:
        soul.run()
    except KeyboardInterrupt:
        print("\n[JR] Later.")
        sys.exit(0)

if __name__ == '__main__':
    main()
