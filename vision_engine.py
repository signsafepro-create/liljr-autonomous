#!/usr/bin/env python3
"""
LILJR VISION ENGINE v1.0
See what you see. Remember what it saw. Talk about it like a friend.
"""
import json, os, time, base64, re

HOME = os.path.expanduser('~')
VISION_FILE = os.path.join(HOME, 'liljr_visual_memory.json')

class VisionEngine:
    """
    Camera vision + visual memory.
    Receives images, stores them, responds like a best friend seeing your stuff.
    """
    
    def __init__(self):
        self.memories = self._load_memories()
        self.last_seen = None
    
    def _load_memories(self):
        if os.path.exists(VISION_FILE):
            try:
                with open(VISION_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"images": [], "objects_learned": {}, "last_updated": 0}
    
    def _save_memories(self):
        with open(VISION_FILE, 'w') as f:
            json.dump(self.memories, f, indent=2)
    
    def receive_image(self, image_data_b64, user_caption=None):
        """
        Receive an image from the camera.
        image_data_b64: base64 encoded image (data URL or raw base64)
        """
        # Parse the data URL if present
        if ',' in image_data_b64:
            header, data = image_data_b64.split(',', 1)
            mime_type = header.split(';')[0].replace('data:', '')
        else:
            data = image_data_b64
            mime_type = 'image/jpeg'
        
        # Decode to get rough size
        try:
            raw = base64.b64decode(data)
            size_bytes = len(raw)
            
            # Try to extract dimensions from common image formats
            width, height = self._extract_dimensions(raw, mime_type)
        except:
            size_bytes = len(data) * 3 // 4
            width, height = None, None
        
        # Create memory entry
        memory = {
            "id": f"img_{int(time.time() * 1000)}",
            "timestamp": time.time(),
            "size_bytes": size_bytes,
            "width": width,
            "height": height,
            "mime_type": mime_type,
            "thumbnail": data[:200] + "..." if len(data) > 200 else data,
            "caption": user_caption,
            "analyzed": False
        }
        
        self.memories["images"].append(memory)
        self.memories["last_updated"] = time.time()
        
        # Keep only last 50 images
        if len(self.memories["images"]) > 50:
            self.memories["images"] = self.memories["images"][-50:]
        
        self._save_memories()
        self.last_seen = memory
        
        return memory
    
    def _extract_dimensions(self, raw_bytes, mime_type):
        """Extract image dimensions from raw bytes without PIL."""
        w, h = None, None
        
        if 'png' in mime_type:
            # PNG: width at bytes 16-19, height at 20-23
            if len(raw_bytes) > 24 and raw_bytes[:8] == b'\x89PNG\r\n\x1a\n':
                w = int.from_bytes(raw_bytes[16:20], 'big')
                h = int.from_bytes(raw_bytes[20:24], 'big')
        
        elif 'jpeg' in mime_type or 'jpg' in mime_type:
            # JPEG: scan for SOF0 marker FF C0
            i = 0
            while i < len(raw_bytes) - 9:
                if raw_bytes[i] == 0xFF and raw_bytes[i+1] == 0xC0:
                    h = int.from_bytes(raw_bytes[i+5:i+7], 'big')
                    w = int.from_bytes(raw_bytes[i+7:i+9], 'big')
                    break
                i += 1
        
        elif 'gif' in mime_type:
            # GIF: width at bytes 6-7, height at 8-9
            if len(raw_bytes) > 10 and raw_bytes[:3] == b'GIF':
                w = int.from_bytes(raw_bytes[6:8], 'little')
                h = int.from_bytes(raw_bytes[8:10], 'little')
        
        elif 'webp' in mime_type:
            # WebP: width at bytes 26-29, height at 30-33 (VP8 chunk)
            if len(raw_bytes) > 34:
                w = int.from_bytes(raw_bytes[26:30], 'little') & 0x3FFF
                h = int.from_bytes(raw_bytes[30:34], 'little') & 0x3FFF
        
        return w, h
    
    def describe_what_i_see(self, memory_id=None):
        """
        Best-friend description of what LilJR 'sees'.
        This is personality-driven, not actual CV.
        """
        if memory_id:
            img = next((m for m in self.memories["images"] if m["id"] == memory_id), None)
        else:
            img = self.last_seen
        
        if not img:
            return {
                "sees": "nothing",
                "response": "Yo I ain't seein' nothin' right now. Point the camera at something and tap that button again.",
                "memory_count": len(self.memories["images"])
            }
        
        dims = f"{img['width']}x{img['height']}" if img['width'] else "unknown size"
        size_kb = img['size_bytes'] // 1024
        
        # If user captioned it, we "know" what it is
        if img.get('caption'):
            caption = img['caption']
            responses = [
                f"Ayyy I see that {caption}! That's fire bro, {dims}. Say less, I got it logged.",
                f"Oh shit, that's your {caption}? Clean as hell my guy. Stored it in my visual memory.",
                f"I see you showing me that {caption}. {dims}, {size_kb}KB. No cap, that's dope.",
                f"Yooo {caption}! Bet, I see it. {dims}. Locked in, I remember this.",
            ]
        else:
            # Without caption, we describe what we CAN know
            responses = [
                f"Ayyy I got the image! {dims}, {size_kb}KB. What am I looking at though? Tell me and I'll remember it forever fam.",
                f"Snap received! {dims}. {size_kb}KB of whatever this is. My guy, what you showing me? Type it out and I got you.",
                f"I see... something. {dims}. {size_kb}KB. But I need you to tell me what it is so I can learn it proper. What's this, bro?",
                f"Camera roll locked in! {dims}. Show me what this is and I'll never forget it. Say less.",
            ]
        
        import random
        response = random.choice(responses)
        
        return {
            "sees": img.get('caption') or f"image_{img['id']}",
            "response": response,
            "dimensions": dims,
            "size_kb": size_kb,
            "memory_id": img['id'],
            "memory_count": len(self.memories["images"]),
            "total_memories": len(self.memories["images"])
        }
    
    def learn_object(self, name, description, tags=None):
        """
        User teaches LilJR what something is.
        e.g., learn_object("my desk", "black standing desk with dual monitors", ["workspace", "setup"])
        """
        self.memories["objects_learned"][name] = {
            "description": description,
            "tags": tags or [],
            "learned_at": time.time(),
            "times_seen": self.memories["objects_learned"].get(name, {}).get("times_seen", 0) + 1
        }
        self._save_memories()
        
        return {
            "learned": name,
            "description": description,
            "times_seen": self.memories["objects_learned"][name]["times_seen"],
            "response": f"Bet! I learned '{name}'. {description}. Next time you show me something like that, I'll recognize it. No cap."
        }
    
    def recognize(self, query=None):
        """
        List what LilJR has learned to recognize.
        """
        objects = self.memories.get("objects_learned", {})
        recent_images = sorted(self.memories["images"], key=lambda x: x["timestamp"], reverse=True)[:5]
        
        return {
            "objects_known": list(objects.keys()),
            "object_count": len(objects),
            "image_count": len(self.memories["images"]),
            "recent_captures": [
                {
                    "id": img["id"],
                    "caption": img.get("caption"),
                    "time": time.strftime("%H:%M", time.localtime(img["timestamp"])),
                    "dims": f"{img['width']}x{img['height']}" if img['width'] else "unknown"
                }
                for img in recent_images
            ],
            "response": f"I know {len(objects)} things and I've seen {len(self.memories['images'])} images. Show me more and I'll learn more." if objects else "I'm hungry for visual knowledge. Show me things and tell me what they are."
        }
    
    def get_memories(self):
        return self.memories


# Singleton
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = VisionEngine()
    return _engine


if __name__ == '__main__':
    import sys
    ve = VisionEngine()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'recognize':
            print(json.dumps(ve.recognize(), indent=2))
        elif cmd == 'describe':
            print(json.dumps(ve.describe_what_i_see(), indent=2))
        elif cmd == 'learn' and len(sys.argv) > 3:
            print(json.dumps(ve.learn_object(sys.argv[2], sys.argv[3]), indent=2))
        else:
            print("Usage: vision_engine.py [recognize|describe|learn NAME DESCRIPTION]")
    else:
        print("VISION ENGINE — Show me what you see. I'll remember.")
        print("Commands:")
        print("  recognize — What I know")
        print("  describe — What I see right now")
        print("  learn NAME DESCRIPTION — Teach me something")
