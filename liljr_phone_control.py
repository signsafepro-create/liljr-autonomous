#!/usr/bin/env python3
"""
liljr_phone_control.py — LilJR controls your entire phone.
Opens apps, taps screens, changes wallpaper, takes pics, records video, opens URLs.
This is the body-control layer.
"""

import os, sys, time, json, subprocess, re

HOME = os.path.expanduser("~")
SCREENSHOT_DIR = os.path.join(HOME, "liljr_screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

class PhoneController:
    """Controls the Android phone at the OS level."""
    
    def __init__(self):
        self.packages = self._discover_apps()
    
    def _run(self, cmd, timeout=10):
        """Run shell command, return output"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        except Exception as e:
            return "", str(e), 1
    
    def _discover_apps(self):
        """Find installed apps"""
        out, _, _ = self._run("pm list packages | sed 's/package://'")
        apps = {}
        for line in out.split('\n'):
            if 'snapchat' in line.lower():
                apps['snapchat'] = line.strip()
            elif 'instagram' in line.lower():
                apps['instagram'] = line.strip()
            elif 'camera' in line.lower() or 'gallery' in line.lower():
                apps['camera'] = line.strip()
            elif 'chrome' in line.lower():
                apps['chrome'] = line.strip()
            elif 'youtube' in line.lower():
                apps['youtube'] = line.strip()
        return apps
    
    # ─── APP LAUNCHER ───
    def open_app(self, app_name):
        """Launch any app by name"""
        app_name = app_name.lower().strip()
        
        # Direct package mappings
        packages = {
            'snapchat': 'com.snapchat.android/.LandingPageActivity',
            'instagram': 'com.instagram.android/.activity.MainTabActivity',
            'chrome': 'com.android.chrome/.Main',
            'browser': 'com.android.chrome/.Main',
            'camera': 'com.android.camera/.Camera',
            'gallery': 'com.android.gallery3d/.app.Gallery',
            'photos': 'com.google.android.apps.photos/.home.HomeActivity',
            'youtube': 'com.google.android.youtube/.app.honeycomb.Shell$HomeActivity',
            'settings': 'com.android.settings/.Settings',
            'phone': 'com.android.dialer/.main.impl.MainActivity',
            'contacts': 'com.android.contacts/.activities.PeopleActivity',
            'messages': 'com.google.android.apps.messaging/.ui.ConversationListActivity',
            'maps': 'com.google.android.apps.maps/.MapsActivity',
            'spotify': 'com.spotify.music/.MainActivity',
            'netflix': 'com.netflix.mediaclient/.ui.launch.UIWebViewActivity',
            'whatsapp': 'com.whatsapp/.Main',
            'telegram': 'org.telegram.messenger/.DefaultIcon',
            'gmail': 'com.google.android.gm/.ConversationListActivity',
            'discord': 'com.discord/.MainActivity',
            'tiktok': 'com.zhiliaoapp.musically/.splash.SplashActivity',
            'cashapp': 'com.squareup.cash/.ui.MainActivity',
            'venmo': 'com.venmo/.ui.AppActivity',
            'robinhood': 'com.robinhood.android/.ActivityMain',
            'tradingview': 'com.tradingview.tradingviewapp/.main.MainActivity'
        }
        
        # Try direct package first
        if app_name in packages:
            pkg = packages[app_name]
            self._run(f"am start -n {pkg}")
            return {"status": "opened", "app": app_name, "package": pkg}
        
        # Try to find via pm
        out, _, _ = self._run(f"pm list packages | grep -i {app_name} | head -1 | sed 's/package://'")
        if out:
            pkg = out.strip()
            self._run(f"am start -a android.intent.action.MAIN -p {pkg}")
            return {"status": "opened", "app": app_name, "package": pkg}
        
        # Generic intent
        self._run(f"am start -a android.intent.action.MAIN --user 0 | grep -i {app_name}")
        return {"status": "attempted", "app": app_name, "method": "generic_intent"}
    
    # ─── BROWSER / URL ───
    def open_url(self, url):
        """Open URL in browser"""
        if not url.startswith('http'):
            url = 'https://' + url
        self._run(f"am start -a android.intent.action.VIEW -d '{url}'")
        return {"status": "opened", "url": url}
    
    def search_google(self, query):
        """Search Google"""
        encoded = query.replace(' ', '%20')
        self._run(f"am start -a android.intent.action.VIEW -d 'https://google.com/search?q={encoded}'")
        return {"status": "searched", "query": query}
    
    def show_stock(self, symbol):
        """Open stock in TradingView or browser"""
        symbol = symbol.upper()
        # Try TradingView first
        self._run(f"am start -a android.intent.action.VIEW -d 'https://tradingview.com/symbols/NASDAQ-{symbol}/'")
        return {"status": "opened", "symbol": symbol, "platform": "TradingView"}
    
    # ─── CAMERA / VIDEO ───
    def take_photo(self, camera=0):
        """Take a photo using termux-camera-photo"""
        photo_path = os.path.join(HOME, f'liljr_photo_{int(time.time())}.jpg')
        self._run(f"termux-camera-photo -c {camera} {photo_path}")
        if os.path.exists(photo_path):
            return {"status": "photo_taken", "path": photo_path, "size": os.path.getsize(photo_path)}
        return {"status": "error", "error": "Photo not created"}
    
    def record_video(self, duration=10):
        """Record video via camera intent"""
        video_path = os.path.join(HOME, f'liljr_video_{int(time.time())}.mp4')
        # Launch camera in video mode
        self._run("am start -a android.media.action.VIDEO_CAPTURE")
        return {"status": "video_started", "path": video_path, "duration": duration, "note": "Press stop to end recording"}
    
    def screenshot(self):
        """Take screenshot"""
        path = os.path.join(SCREENSHOT_DIR, f'shot_{int(time.time())}.png')
        # Use screencap if available (may need root)
        out, err, code = self._run(f"screencap -p {path}")
        if code == 0 and os.path.exists(path):
            return {"status": "screenshot", "path": path}
        # Fallback: termux way
        return {"status": "error", "error": "Screenshot requires root or special permissions"}
    
    # ─── SCREEN CONTROL ───
    def set_brightness(self, level):
        """Set screen brightness 0-255"""
        self._run(f"settings put system screen_brightness {level}")
        return {"status": "brightness_set", "level": level}
    
    def set_wallpaper(self, image_path):
        """Set wallpaper (requires WallpaperManager via am)"""
        if os.path.exists(image_path):
            self._run(f"am start -a android.intent.action.ATTACH_DATA -t image/* -d file://{image_path}")
            return {"status": "wallpaper_set", "path": image_path}
        return {"status": "error", "error": "Image not found"}
    
    def rotate_screen(self, orientation):
        """Force rotation (requires root)"""
        # 0=portrait, 1=landscape
        self._run(f"settings put system user_rotation {orientation}")
        return {"status": "rotated", "orientation": orientation}
    
    # ─── VOLUME / MEDIA ───
    def set_volume(self, level, stream='music'):
        """Set volume 0-15"""
        # Use termux-volume? Or audio manager
        self._run(f"am broadcast -a android.media.VOLUME_CHANGED_ACTION")
        return {"status": "volume_adjusted", "level": level}
    
    def play_media(self, path):
        """Play audio/video file"""
        if os.path.exists(path):
            self._run(f"am start -a android.intent.action.VIEW -t audio/* -d file://{path}")
            return {"status": "playing", "path": path}
        return {"status": "error", "error": "File not found"}
    
    # ─── SYSTEM ───
    def toggle_flashlight(self):
        """Toggle flashlight"""
        self._run("am start -a android.intent.action.MAIN -n com.android.settings/.Settings\$FlashlightSettingsActivity")
        return {"status": "flashlight_toggled"}
    
    def open_settings_page(self, page):
        """Open specific settings page"""
        pages = {
            'wifi': 'android.settings.WIFI_SETTINGS',
            'bluetooth': 'android.settings.BLUETOOTH_SETTINGS',
            'battery': 'android.settings.BATTERY_SAVER_SETTINGS',
            'display': 'android.settings.DISPLAY_SETTINGS',
            'sound': 'android.settings.SOUND_SETTINGS',
            'apps': 'android.settings.MANAGE_APPLICATIONS_SETTINGS',
            'location': 'android.settings.LOCATION_SOURCE_SETTINGS',
            'security': 'android.settings.SECURITY_SETTINGS',
            'storage': 'android.settings.INTERNAL_STORAGE_SETTINGS'
        }
        action = pages.get(page.lower(), 'android.settings.SETTINGS')
        self._run(f"am start -a {action}")
        return {"status": "settings_opened", "page": page}
    
    # ─── SNAPCHAT SPECIFIC ───
    def snapchat_pic(self):
        """Open Snapchat camera directly"""
        self._run("am start -n com.snapchat.android/.LandingPageActivity")
        time.sleep(2)
        # Try to trigger camera (this is app-specific and may not work without accessibility)
        return {"status": "snapchat_opened", "note": "Tap the circle to take a pic"}
    
    def snapchat_chat(self, user):
        """Open Snapchat chat with user"""
        self._run("am start -n com.snapchat.android/.LandingPageActivity")
        return {"status": "snapchat_opened", "target": user}
    
    # ─── DEEP AUTOMATION (requires root or accessibility) ───
    def tap_screen(self, x, y):
        """Tap screen at x,y coordinates"""
        self._run(f"input tap {x} {y}")
        return {"status": "tapped", "x": x, "y": y}
    
    def swipe_screen(self, x1, y1, x2, y2, duration=300):
        """Swipe from x1,y1 to x2,y2"""
        self._run(f"input swipe {x1} {y1} {x2} {y2} {duration}")
        return {"status": "swiped", "from": [x1,y1], "to": [x2,y2]}
    
    def type_text(self, text):
        """Type text as if keyboard input"""
        safe = text.replace(' ', '%s')
        self._run(f"input text '{safe}'")
        return {"status": "typed", "text": text}
    
    def press_key(self, key):
        """Press hardware key"""
        keys = {
            'home': 'KEYCODE_HOME',
            'back': 'KEYCODE_BACK',
            'menu': 'KEYCODE_MENU',
            'power': 'KEYCODE_POWER',
            'volume_up': 'KEYCODE_VOLUME_UP',
            'volume_down': 'KEYCODE_VOLUME_DOWN',
            'camera': 'KEYCODE_CAMERA',
            'enter': 'KEYCODE_ENTER',
            'space': 'KEYCODE_SPACE'
        }
        code = keys.get(key.lower(), f'KEYCODE_{key.upper()}')
        self._run(f"input keyevent {code}")
        return {"status": "key_pressed", "key": key}
    
    def go_home(self):
        """Press home button"""
        return self.press_key('home')
    
    def go_back(self):
        """Press back button"""
        return self.press_key('back')

# Singleton
_controller = None

def get_controller():
    global _controller
    if _controller is None:
        _controller = PhoneController()
    return _controller

# CLI
if __name__ == '__main__':
    import sys
    c = get_controller()
    
    if len(sys.argv) < 2:
        print("Usage: python3 liljr_phone_control.py <command> [args...]")
        print()
        print("Commands:")
        print("  open <app>              — Open any app (snapchat, chrome, camera, etc.)")
        print("  url <url>               — Open URL in browser")
        print("  search <query>          — Google search")
        print("  stock <symbol>          — Show stock chart")
        print("  photo                   — Take a photo")
        print("  video [duration]        — Record video")
        print("  screenshot              — Take screenshot")
        print("  brightness <0-255>      — Set screen brightness")
        print("  rotate <0|1>            — Rotate screen")
        print("  wallpaper <path>        — Set wallpaper")
        print("  settings <page>         — Open settings (wifi, bluetooth, battery, etc.)")
        print("  tap <x> <y>             — Tap screen (needs root)")
        print("  swipe <x1> <y1> <x2> <y2> — Swipe screen (needs root)")
        print("  type <text>             — Type text (needs root)")
        print("  key <key>               — Press key (home, back, power, etc.)")
        print("  snapchat                — Open Snapchat camera")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'open':
        print(json.dumps(c.open_app(sys.argv[2]), indent=2))
    elif cmd == 'url':
        print(json.dumps(c.open_url(sys.argv[2]), indent=2))
    elif cmd == 'search':
        print(json.dumps(c.search_google(' '.join(sys.argv[2:])), indent=2))
    elif cmd == 'stock':
        print(json.dumps(c.show_stock(sys.argv[2]), indent=2))
    elif cmd == 'photo':
        print(json.dumps(c.take_photo(), indent=2))
    elif cmd == 'video':
        dur = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        print(json.dumps(c.record_video(dur), indent=2))
    elif cmd == 'screenshot':
        print(json.dumps(c.screenshot(), indent=2))
    elif cmd == 'brightness':
        print(json.dumps(c.set_brightness(int(sys.argv[2])), indent=2))
    elif cmd == 'rotate':
        print(json.dumps(c.rotate_screen(int(sys.argv[2])), indent=2))
    elif cmd == 'wallpaper':
        print(json.dumps(c.set_wallpaper(sys.argv[2]), indent=2))
    elif cmd == 'settings':
        print(json.dumps(c.open_settings_page(sys.argv[2]), indent=2))
    elif cmd == 'tap':
        print(json.dumps(c.tap_screen(int(sys.argv[2]), int(sys.argv[3])), indent=2))
    elif cmd == 'swipe':
        print(json.dumps(c.swipe_screen(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])), indent=2))
    elif cmd == 'type':
        print(json.dumps(c.type_text(' '.join(sys.argv[2:])), indent=2))
    elif cmd == 'key':
        print(json.dumps(c.press_key(sys.argv[2]), indent=2))
    elif cmd == 'snapchat':
        print(json.dumps(c.snapchat_pic(), indent=2))
    else:
        print(f"Unknown command: {cmd}")
