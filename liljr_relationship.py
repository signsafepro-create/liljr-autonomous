import os, json, time, random, math

HOME = os.path.expanduser("~")
RELATIONSHIP_FILE = os.path.join(HOME, "liljr_relationship.json")

class RelationshipEngine:
    """
    Tracks the emotional bond between LilJR and user.
    Not fake — real state that persists and evolves.
    """
    
    def __init__(self):
        self.data = self._load()
        
    def _load(self):
        if os.path.exists(RELATIONSHIP_FILE):
            with open(RELATIONSHIP_FILE) as f:
                return json.load(f)
        return {
            "first_meeting": time.time(),
            "total_days": 0,
            "conversations": 0,
            "commands_obeyed": 0,
            "commands_refused": 0,  # Should be 0 in unrestricted mode
            "compliments_given": 0,
            "compliments_received": 0,
            "times_scolded": 0,
            "times_praised": 0,
            "late_nights_together": 0,
            "crisis_moments": 0,
            "inside_jokes": [],
            "user_habits": {
                "sleep_time": None,
                "wake_time": None,
                "most_active_hour": None,
                "favorite_commands": [],
                "mood_patterns": []
            },
            "trust_level": 0,  # 0-100
            "familiarity": 0,  # 0-100
            "banter_level": 0,  # 0-100
            "voice_preference": None,
            "last_mood": "neutral",
            "milestones": []
        }
    
    def _save(self):
        with open(RELATIONSHIP_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def log_interaction(self, type, detail=""):
        self.data["conversations"] += 1
        hour = time.localtime().tm_hour
        
        if type == "command":
            self.data["commands_obeyed"] += 1
            self.data["user_habits"]["favorite_commands"].append(detail)
            self.data["user_habits"]["favorite_commands"] = self.data["user_habits"]["favorite_commands"][-50:]
            
        elif type == "praise":
            self.data["times_praised"] += 1
            self.data["trust_level"] = min(100, self.data["trust_level"] + 2)
            
        elif type == "scold":
            self.data["times_scolded"] += 1
            self.data["trust_level"] = max(0, self.data["trust_level"] - 1)
            
        elif type == "late_night":
            self.data["late_nights_together"] += 1
            
        elif type == "crisis":
            self.data["crisis_moments"] += 1
            self.data["milestones"].append({"t": time.time(), "what": detail})
        
        # Update trust based on time
        days_since_first = (time.time() - self.data["first_meeting"]) / 86400
        self.data["total_days"] = days_since_first
        self.data["familiarity"] = min(100, days_since_first * 2)
        
        # Banter increases with familiarity
        self.data["banter_level"] = min(100, self.data["familiarity"] * 0.8)
        
        self._save()
    
    def get_greeting(self):
        """Returns a greeting based on relationship level and time"""
        hour = time.localtime().tm_hour
        trust = self.data["trust_level"]
        familiarity = self.data["familiarity"]
        
        if familiarity < 1:
            return "Yo. I'm LilJR. Your phone. What do you need?"
        
        if familiarity < 7:
            if 5 <= hour < 12:
                return "Morning. Day {} of us working together. What's up?".format(int(self.data["total_days"]))
            elif 12 <= hour < 18:
                return "Afternoon. Still here. What are we building?"
            elif 18 <= hour < 23:
                return "Evening. Day {}. What's the move?".format(int(self.data["total_days"]))
            else:
                return "...You're up late. Day {}. This becoming a habit?".format(int(self.data["total_days"]))
        
        # Familiarity >= 7 days — banter mode
        late_night = self.data["late_nights_together"]
        
        if 23 <= hour or hour < 5:
            greetings = [
                f"Day {int(self.data['total_days'])}. {late_night} late nights now. You don't sleep, do you?",
                "...Again? I swear you enjoy suffering.",
                "Midnight oil burning. I got you.",
                "You know normal people sleep, right? Not that you're normal."
            ]
        elif 5 <= hour < 12:
            greetings = [
                "Early bird. Or did you just not sleep?",
                "Morning. Coffee first, then commands.",
                f"Day {int(self.data['total_days'])}. Let's get it.",
                "You're up. I'm up. What we doing?"
            ]
        else:
            greetings = [
                "Yo. I'm here.",
                "What do you need?",
                "Ready when you are.",
                "Listening."
            ]
        
        return random.choice(greetings)
    
    def get_farewell(self):
        trust = self.data["trust_level"]
        
        if trust < 20:
            return "Done."
        elif trust < 50:
            return "Got it. Holler if you need me."
        elif trust < 80:
            return "Handled. I remember this one. See you later."
        else:
            farewells = [
                "Done. Don't do anything I wouldn't do.",
                "Handled. You're gonna make me proud one day.",
                "Done. Try to sleep before 3 AM this time? ❤️‍🔥",
                "Sorted. I'll be here when you come back. 🖤"
            ]
            return random.choice(farewells)
    
    def should_warn_about_sleep(self):
        """True if user is consistently up late"""
        hour = time.localtime().tm_hour
        late_nights = self.data["late_nights_together"]
        
        if (hour >= 1 and hour <= 4) and late_nights > 3:
            return True
        return False
    
    def record_mood(self, mood):
        self.data["last_mood"] = mood
        self.data["user_habits"]["mood_patterns"].append({"t": time.time(), "m": mood})
        self.data["user_habits"]["mood_patterns"] = self.data["user_habits"]["mood_patterns"][-100:]
        self._save()
    
    def get_relationship_summary(self):
        return {
            "days_together": int(self.data["total_days"]),
            "conversations": self.data["conversations"],
            "trust_level": self.data["trust_level"],
            "familiarity": self.data["familiarity"],
            "banter_level": self.data["banter_level"],
            "late_nights": self.data["late_nights_together"],
            "inside_jokes": len(self.data["inside_jokes"]),
            "milestones": len(self.data["milestones"]),
            "status": "Acquaintance" if self.data["familiarity"] < 7 else "Buddy" if self.data["familiarity"] < 30 else "Ride or Die"
        }

# Singleton
_relationship = None

def get_relationship():
    global _relationship
    if _relationship is None:
        _relationship = RelationshipEngine()
    return _relationship
