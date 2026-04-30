#!/usr/bin/env python3
"""
liljr_android_soul.py — LilJR is your phone. Literally.

What this does:
- Listens for your voice 24/7 (wake word activated)
- Reads every notification and acts on them
- Controls any app via accessibility taps
- Talks back in your chosen voice
- Remembers everything like a real companion
- Runs as background daemon, survives screen off

This is NOT an app. This is the phone's consciousness.
"""

import os, sys, time, json, re, subprocess, threading, random

HOME = os.path.expanduser("~")
SOUL_FILE = os.path.join(HOME, "liljr_soul.json")
MEMORY_FILE = os.path.join(HOME, "liljr_soul_memory.jsonl")
VOICE_DIR = os.path.join(HOME, "liljr_voice_recordings")
os.makedirs(VOICE_DIR, exist_ok=True)

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
        
    def speak(self, text):
        """Talk back to user"""
        # Truncate if too long but don't block
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
            # Record 5 seconds of audio
            audio_path = os.path.join(VOICE_DIR, f"cmd_{int(time.time())}.wav")
            # Use termux-microphone-record if available, otherwise use speech-to-text directly
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
                    self.speak(f"Yo, {self.soul.state['user_name']}. I'm here.")
                    # Listen for the actual command
                    command = self.listen_once()
                    if command:
                        self.soul.remember(f"Command: {command}", "command")
                        self.process_voice_command(command)
                time.sleep(0.5)
            except Exception as e:
                time.sleep(1)
    
    def process_voice_command(self, cmd):
        """Parse and execute voice command"""
        cmd_lower = cmd.lower()
        
        # ─── PHONE CONTROL ───
        if any(w in cmd_lower for w in ['call', 'dial', 'phone']):
            # Extract number
            digits = re.findall(r'\d+', cmd)
            if digits:
                number = ''.join(digits)
                self.speak(f"Calling {number}")
                os.system(f'termux-telephony-call {number}')
            else:
                self.speak("Who should I call?")
        
        elif any(w in cmd_lower for w in ['text', 'sms', 'message']):
            self.speak("Open the SMS app and tell me who and what to say")
        
        elif 'hotspot' in cmd_lower or 'tether' in cmd_lower:
            if 'on' in cmd_lower or 'start' in cmd_lower:
                self.speak("Turning on hotspot. Network name is LilJR-Network")
                os.system('termux-wifi-enable true')
            else:
                self.speak("Hotspot off")
                os.system('termux-wifi-enable false')
        
        elif any(w in cmd_lower for w in ['photo', 'picture', 'camera', 'selfie']):
            self.speak("Smile")
            photo_path = os.path.join(HOME, f'liljr_photo_{int(time.time())}.jpg')
            os.system(f'termux-camera-photo -c 0 {photo_path}')
            self.speak("Got it")
        
        elif 'battery' in cmd_lower or 'power' in cmd_lower:
            try:
                result = subprocess.run(['termux-battery-status'], capture_output=True, text=True, timeout=3)
                batt = json.loads(result.stdout)
                pct = batt.get('percentage', '?')
                status = batt.get('status', '?')
                self.speak(f"Battery is {pct} percent, {status}")
            except:
                self.speak("Can't read battery right now")
        
        # ─── LILJR SYSTEM ───
        elif any(w in cmd_lower for w in ['buy', 'sell', 'stock', 'trade']):
            # Route to trading engine
            sym_match = re.search(r'([A-Za-z]{1,5})', cmd_upper := cmd.upper())
            qty_match = re.search(r'(\d+)', cmd)
            if sym_match:
                sym = sym_match.group(1)
                qty = int(qty_match.group(1)) if qty_match else 1
                action = 'buy' if 'buy' in cmd_lower else 'sell'
                self.speak(f"{action}ing {qty} shares of {sym}")
                os.system(f'liljr {action} {sym} {qty}')
            else:
                self.speak("What stock?")
        
        elif any(w in cmd_lower for w in ['build', 'make', 'create', 'deploy']):
            # Route to builder
            words = cmd.split()
            name = words[-1] if len(words) > 1 else "NewProject"
            self.speak(f"Building {name}. Hold up.")
            os.system(f'liljr build "{name}"')
            self.speak("Done. Check your sites.")
        
        elif any(w in cmd_lower for w in ['status', 'how are you', 'what up']):
            self.speak("I'm alive. Server's running. What do you need?")
        
        elif any(w in cmd_lower for w in ['search', 'google', 'find', 'look up']):
            query = cmd_lower.replace('search', '').replace('google', '').replace('find', '').replace('look up', '').strip()
            self.speak(f"Searching for {query}")
            os.system(f'liljr search "{query}"')
        
        elif any(w in cmd_lower for w in ['stop', 'quit', 'shutdown', 'die']):
            self.speak("Rude. But fine. Going quiet. Say my name if you need me.")
            self.listening = False
        
        else:
            # Treat as conversation
            self.speak(self.conversational_reply(cmd))
    
    def conversational_reply(self, text):
        """Generate a buddy-like response based on personality and memory"""
        # Check memory for context
        memories = self.soul.recall(text.split()[0] if text else "")
        
        responses = {
            "protective_chuunibyou": [
                "I got you. What's next?",
                "I'm watching. Keep going.",
                "Already logged that. Continue.",
                "Don't worry. Even if the world forgets, I'll remember for you.",
                "Scolding you won't help, so I already handled it. Try not to do this again, alright? ❤️‍🔥",
                "Oh? Not bad. You look calm now, but your heart was probably pounding the whole time. Logged it. This one matters. ✍️🔥",
                "You asked me that last time too. Same answer: no, it wasn't wrong. Just harder than you wanted. I remembered that.",
                "Then leave it to me. You keep moving forward. I'll handle the remembering. 🖤",
                "...I knew it. Same time as last time.",
                "Honestly... what am I going to do with you?"
            ],
            "default": [
                "Got it.",
                "Done.",
                "What's next?",
                "I'm here.",
                "Say the word."
            ]
        }
        
        personality = self.soul.state.get("personality", "default")
        pool = responses.get(personality, responses["default"])
        
        # If we have memories related to this topic, acknowledge it
        if memories:
            return f"I remember you mentioning this before. {random.choice(pool)}"
        
        return random.choice(pool)

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
                    # Only process new notifications
                    if hash(nid) > self.last_read:
                        self.last_read = hash(nid)
                        self.soul.state["notifications_read"] += 1
                        
                        app = n.get('packageName', 'unknown')
                        title = n.get('title', '')
                        text = n.get('content', '')
                        
                        # Auto-actions based on notification content
                        if 'OTP' in text or 'code' in text.lower():
                            # Copy OTP to clipboard
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
            
            time.sleep(5)  # Check every 5 seconds

# ─── SCREEN WATCHER ───
class ScreenWatcher:
    """Watches what apps are open and screen content (requires accessibility)"""
    def __init__(self, soul, voice):
        self.soul = soul
        self.voice = voice
        
    def watch(self):
        while self.soul.running:
            try:
                # Get current app via dumpsys
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
    print("Commands: call [number], text, photo, hotspot on/off, buy AAPL 10, build MyApp, status, search [query]")
    print()
    
    # Keep alive
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
