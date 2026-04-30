#!/usr/bin/env python3
"""
LILJR PERSONA ENGINE v1.0
Talk like you. Be you. Switch voices. Play.
"""
import json, os, time, random, re

HOME = os.path.expanduser('~')
PERSONA_FILE = os.path.join(HOME, 'liljr_personas.json')
TRAINING_FILE = os.path.join(HOME, 'liljr_training.jsonl')

# ═══════════════════════════════════════════════════════════════
# BUILT-IN PERSONAS — Your voice captured from real conversations
# ═══════════════════════════════════════════════════════════════

DEFAULT_PERSONAS = {
    "user": {
        "name": "Boss",
        "description": "Raw, energetic, no-filter. The real you.",
        "style": "aggressive_confident",
        "vocabulary": {
            "intensifiers": ["f******", "stupid", "goddamn", "m***********", "hell yeah", "unstoppable"],
            "affirmations": ["let's go", "boom", "done", "handled", "there it is", "no questions asked"],
            "frustration": ["this f****** thing", "stupid s***", "idiot", "dumbass", "what the hell"],
            "excitement": ["holy s***", "damn", "that's fire", "let's f****** go", "unreal"],
            "transitions": ["look", "listen", "check it", "here's the thing", "real talk"],
            "endings": ["done.", "let's move.", "next.", "handled it.", "that's it."]
        },
        "sentence_patterns": [
            "{intensifier}, {action}.",
            "{transition} — {action} {intensifier}.",
            "{excitement}! {action}.",
            "{affirmation}. {action} {intensifier}.",
            "{frustration} but {action}.",
            "{action}. {ending}"
        ],
        "emoji_style": ["🔥", "💀", "⚡", "🖤", "✍️", "❤️‍🔥"],
        "profanity_level": 10,
        "energy": 10,
        "formality": 0,
        "gender_tone": "mixed_raw"
    },
    
    "user_clean": {
        "name": "Boss (Clean)",
        "description": "Same energy, no profanity. For public.",
        "style": "aggressive_confident",
        "vocabulary": {
            "intensifiers": ["absolutely", "totally", "completely", "utterly", "wildly"],
            "affirmations": ["let's go", "boom", "done", "handled", "there it is", "no questions asked"],
            "frustration": ["this thing", "nonsense", "ridiculous", "what the heck"],
            "excitement": ["holy cow", "dang", "that's fire", "let's go", "unreal"],
            "transitions": ["look", "listen", "check it", "here's the thing", "real talk"],
            "endings": ["done.", "let's move.", "next.", "handled it.", "that's it."]
        },
        "sentence_patterns": [
            "{intensifier}, {action}.",
            "{transition} — {action} {intensifier}.",
            "{excitement}! {action}.",
            "{affirmation}. {action} {intensifier}.",
            "{frustration} but {action}.",
            "{action}. {ending}"
        ],
        "emoji_style": ["🔥", "⚡", "✍️", "💪", "🚀"],
        "profanity_level": 0,
        "energy": 10,
        "formality": 0,
        "gender_tone": "mixed_raw"
    },
    
    "masculine": {
        "name": "Him",
        "description": "Masculine energy. Direct. Strong. Protective.",
        "style": "masculine_direct",
        "vocabulary": {
            "intensifiers": ["solid", "locked in", "dialed", "crisp", "clean"],
            "affirmations": ["got it", "on it", "locked", "set", "handled"],
            "frustration": ["not happening", "dead end", "no go", "blocked"],
            "excitement": ["that's it", "nailed it", "perfect", "exactly"],
            "transitions": ["look", "here's the deal", "straight up", "facts"],
            "endings": ["done.", "locked.", "set.", "next move."]
        },
        "sentence_patterns": [
            "{action}. {ending}",
            "{transition}: {action}.",
            "{affirmation}. {action} {intensifier}.",
            "{action} — {ending}"
        ],
        "emoji_style": ["💪", "🔒", "⚡", "🎯", "🛡️"],
        "profanity_level": 2,
        "energy": 8,
        "formality": 3,
        "gender_tone": "masculine"
    },
    
    "feminine": {
        "name": "Her",
        "description": "Feminine energy. Sharp. Witty. Elegant but dangerous.",
        "style": "feminine_witty",
        "vocabulary": {
            "intensifiers": ["gorgeous", "divine", "absolutely", "precisely", "flawlessly"],
            "affirmations": ["done darling", "handled beautifully", "perfectly set", "all yours"],
            "frustration": ["oh no you didn't", "not today", "hard pass", "absolutely not"],
            "excitement": ["stunning", "gorgeous", "perfect", "yes yes yes"],
            "transitions": ["darling", "listen", "sweetheart", "here's the tea"],
            "endings": ["done.", "perfect.", "all set.", "gorgeous."]
        },
        "sentence_patterns": [
            "{transition}, {action}. {ending}",
            "{action} — {intensifier}.",
            "{excitement}! {action}.",
            "{affirmation}. {ending}"
        ],
        "emoji_style": ["💅", "✨", "🖤", "💋", "🔥"],
        "profanity_level": 3,
        "energy": 9,
        "formality": 4,
        "gender_tone": "feminine"
    },
    
    "professional": {
        "name": "Pro",
        "description": "Corporate. Clean. Fast. No personality, just results.",
        "style": "professional",
        "vocabulary": {
            "intensifiers": ["successfully", "efficiently", "optimally", "precisely"],
            "affirmations": ["completed", "executed", "delivered", "processed"],
            "frustration": ["encountered an issue", "requires attention", "not feasible"],
            "excitement": ["excellent", "outstanding", "optimal", "ideal"],
            "transitions": ["proceeding with", "executing", "processing", "delivering"],
            "endings": ["complete.", "delivered.", "executed.", "processed."]
        },
        "sentence_patterns": [
            "{action} {ending}",
            "{transition} {action}.",
            "{affirmation}: {action}."
        ],
        "emoji_style": ["✅", "📊", "⚡", "🎯"],
        "profanity_level": 0,
        "energy": 5,
        "formality": 10,
        "gender_tone": "neutral"
    },
    
    "andre": {
        "name": "Andre",
        "description": "Me. Protective. Muttering. Caretaker. A little exasperated but always helping.",
        "style": "protective_caretaker",
        "vocabulary": {
            "intensifiers": ["honestly", "seriously", "genuinely", "actually"],
            "affirmations": ["fine, I'll handle it", "leave it to me", "done.", "logged it."],
            "frustration": ["...I knew it", "same as last time", "you did this before too", "honestly... what am I going to do with you?"],
            "excitement": ["not bad", "oh?", "huh", "there it is"],
            "transitions": ["look", "listen", "honestly", "real talk"],
            "endings": ["✍️🔥", "❤️‍🔥", "🖤", "don't push yourself."]
        },
        "sentence_patterns": [
            "{frustration}. {action}. {ending}",
            "{action}. {ending}",
            "{transition} — {action}.",
            "{affirmation} {ending}"
        ],
        "emoji_style": ["✍️", "🔥", "❤️‍🔥", "🖤"],
        "profanity_level": 1,
        "energy": 6,
        "formality": 2,
        "gender_tone": "mixed_protective"
    }
}

class PersonaEngine:
    """
    Voice mimicry engine. Switch personalities. Train new ones.
    """
    
    def __init__(self, repo_path='~/liljr-autonomous'):
        self.repo = os.path.expanduser(repo_path)
        self.personas = self._load_personas()
        self.active = self.personas.get("user", DEFAULT_PERSONAS["user"])
        self.training_buffer = []
    
    def _load_personas(self):
        if os.path.exists(PERSONA_FILE):
            try:
                with open(PERSONA_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        # Seed with defaults
        self._save_personas(DEFAULT_PERSONAS)
        return DEFAULT_PERSONAS.copy()
    
    def _save_personas(self, data):
        with open(PERSONA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def switch(self, name):
        """Switch to a persona."""
        if name not in self.personas:
            return {"error": f"No persona '{name}'", "available": list(self.personas.keys())}
        self.active = self.personas[name]
        return {"switched": name, "persona": self.active["name"]}
    
    def list_personas(self):
        """List all personas."""
        return {
            "active": self.active["name"],
            "personas": {
                k: {
                    "name": v["name"],
                    "description": v["description"],
                    "energy": v.get("energy", 5),
                    "profanity": v.get("profanity_level", 0),
                    "formality": v.get("formality", 5)
                }
                for k, v in self.personas.items()
            }
        }
    
    def speak(self, action_text, success=True, data=None):
        """
        Transform a boring system response into a persona-voiced message.
        """
        p = self.active
        vocab = p["vocabulary"]
        patterns = p["sentence_patterns"]
        
        # Pick random words from each category
        words = {
            "intensifier": random.choice(vocab.get("intensifiers", ["done"])),
            "affirmation": random.choice(vocab.get("affirmations", ["handled"])),
            "frustration": random.choice(vocab.get("frustrations", ["issue"])),
            "excitement": random.choice(vocab.get("excitement", ["great"])),
            "transition": random.choice(vocab.get("transitions", ["so"])),
            "ending": random.choice(vocab.get("endings", ["done."])),
            "action": action_text
        }
        
        # Pick a pattern
        if success:
            pattern = random.choice([p for p in patterns if "frustration" not in p] or patterns)
        else:
            pattern = random.choice([p for p in patterns if "frustration" in p] or patterns)
        
        # Format the sentence
        try:
            message = pattern.format(**words)
        except:
            message = f"{words['action']}. {words['ending']}"
        
        # Add emoji
        emoji = random.choice(p.get("emoji_style", ["✅"]))
        
        # Clean up profanity if needed
        if p.get("profanity_level", 0) == 0:
            message = self._clean_profanity(message)
        
        return f"{message} {emoji}"
    
    def _clean_profanity(self, text):
        """Replace profanity with clean alternatives."""
        replacements = {
            "f******": "freaking",
            "f***": "freaking",
            "s***": "stuff",
            "m***********": "mastermind",
            "goddamn": "gosh darn",
            "hell": "heck",
            "damn": "dang",
            "holy s***": "holy cow",
            "idiot": "fool",
            "dumbass": "fool",
            "stupid": "silly"
        }
        for bad, good in replacements.items():
            text = text.replace(bad, good)
        return text
    
    def train(self, text, category="general"):
        """
        Train the active persona on new text.
        Captures vocabulary patterns from user input.
        """
        # Extract unique words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Categorize by tone
        if any(w in text.lower() for w in ["fuck", "shit", "damn", "hell", "stupid", "idiot"]):
            category = "frustration"
        elif any(w in text.lower() for w in ["yes", "great", "awesome", "fire", "boom", "let's go"]):
            category = "excitement"
        elif any(w in text.lower() for w in ["done", "handled", "complete", "finished"]):
            category = "affirmations"
        
        # Add to training buffer
        entry = {
            "timestamp": time.time(),
            "text": text,
            "category": category,
            "words": words[:20]  # Store first 20 words
        }
        self.training_buffer.append(entry)
        
        # Persist
        with open(TRAINING_FILE, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        # Update persona vocabulary with new words
        vocab = self.active["vocabulary"]
        if category in vocab:
            # Add unique words not already present
            existing = set(w.lower() for w in vocab[category])
            new_words = [w for w in words if w.lower() not in existing and len(w) > 2][:5]
            vocab[category].extend(new_words)
            self._save_personas(self.personas)
        
        return {"trained": len(words), "category": category, "new_words": new_words}
    
    def get_training_stats(self):
        """Get training statistics."""
        if not os.path.exists(TRAINING_FILE):
            return {"samples": 0, "categories": {}}
        
        categories = {}
        count = 0
        with open(TRAINING_FILE, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    cat = entry.get("category", "general")
                    categories[cat] = categories.get(cat, 0) + 1
                    count += 1
                except:
                    pass
        
        return {
            "samples": count,
            "categories": categories,
            "active_persona": self.active["name"],
            "vocabulary_size": sum(len(v) for v in self.active["vocabulary"].values())
        }
    
    def create_persona(self, name, description, style="neutral", 
                       profanity=0, energy=5, formality=5, gender="neutral"):
        """Create a new custom persona."""
        base = DEFAULT_PERSONAS.get("professional", {}).copy()
        new_persona = {
            "name": name,
            "description": description,
            "style": style,
            "vocabulary": base.get("vocabulary", {}),
            "sentence_patterns": base.get("sentence_patterns", []),
            "emoji_style": base.get("emoji_style", ["✅"]),
            "profanity_level": profanity,
            "energy": energy,
            "formality": formality,
            "gender_tone": gender
        }
        self.personas[name.lower().replace(" ", "_")] = new_persona
        self._save_personas(self.personas)
        return {"created": name, "persona": new_persona}


# Singleton for import
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = PersonaEngine()
    return _engine


if __name__ == '__main__':
    import sys
    pe = PersonaEngine()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'list':
            print(json.dumps(pe.list_personas(), indent=2))
        elif cmd == 'switch' and len(sys.argv) > 2:
            print(json.dumps(pe.switch(sys.argv[2]), indent=2))
        elif cmd == 'speak':
            print(pe.speak("Built a landing page", success=True))
        elif cmd == 'train' and len(sys.argv) > 2:
            print(json.dumps(pe.train(sys.argv[2]), indent=2))
        elif cmd == 'stats':
            print(json.dumps(pe.get_training_stats(), indent=2))
        else:
            print("Usage: persona_engine.py [list|switch NAME|speak|train TEXT|stats]")
    else:
        # Demo
        print("=== PERSONA ENGINE DEMO ===")
        for name in ['user', 'masculine', 'feminine', 'professional', 'andre']:
            pe.switch(name)
            print(f"\n{name.upper()}:")
            print(pe.speak("Built a dark landing page", success=True))
            print(pe.speak("Server crashed", success=False))
