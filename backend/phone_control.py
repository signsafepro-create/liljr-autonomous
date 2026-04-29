"""
PHONE CONTROL MODULE
Full Android device control via Termux:API + ADB
Launch apps, simulate taps, send SMS, make calls, read notifications
"""
import subprocess
import json
import os
from typing import Dict, List, Optional

class PhoneController:
    def __init__(self):
        self.termux_api = self._check_termux_api()
        self.installed_apps = self._get_installed_apps()
    
    def _check_termux_api(self) -> bool:
        """Check if termux-api is installed"""
        try:
            subprocess.run(["termux-battery-status"], capture_output=True, timeout=5)
            return True
        except:
            return False
    
    def _get_installed_apps(self) -> List[str]:
        """Get list of installed packages"""
        try:
            result = subprocess.run(
                ["pm", "list", "packages"],
                capture_output=True, text=True, timeout=10
            )
            packages = [line.replace("package:", "") for line in result.stdout.strip().split("\n") if line]
            return packages
        except:
            return []
    
    def launch_app(self, package_name: str) -> Dict:
        """Launch any app by package name"""
        try:
            subprocess.run(
                ["am", "start", "-n", f"{package_name}/.{package_name.split('.')[-1]}.MainActivity"],
                capture_output=True, timeout=10
            )
            return {"status": "launched", "app": package_name}
        except Exception as e:
            # Try alternative launch
            try:
                subprocess.run(
                    ["am", "start", "-a", "android.intent.action.MAIN", "-n", package_name],
                    capture_output=True, timeout=10
                )
                return {"status": "launched", "app": package_name, "method": "intent"}
            except Exception as e2:
                return {"status": "error", "message": str(e2), "app": package_name}
    
    def launch_url(self, url: str) -> Dict:
        """Open URL in browser"""
        try:
            subprocess.run(
                ["am", "start", "-a", "android.intent.action.VIEW", "-d", url],
                capture_output=True, timeout=10
            )
            return {"status": "opened", "url": url}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def send_sms(self, number: str, message: str) -> Dict:
        """Send SMS via termux-api"""
        if not self.termux_api:
            return {"status": "error", "message": "termux-api not installed. Run: pkg install termux-api"}
        try:
            subprocess.run(
                ["termux-sms-send", "-n", number, message],
                capture_output=True, timeout=10
            )
            return {"status": "sent", "to": number, "message": message[:50]}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def make_call(self, number: str) -> Dict:
        """Make phone call"""
        try:
            subprocess.run(
                ["am", "start", "-a", "android.intent.action.CALL", "-d", f"tel:{number}"],
                capture_output=True, timeout=10
            )
            return {"status": "calling", "number": number}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_battery(self) -> Dict:
        """Get battery status"""
        if not self.termux_api:
            return {"status": "unavailable", "message": "termux-api required"}
        try:
            result = subprocess.run(
                ["termux-battery-status"],
                capture_output=True, text=True, timeout=5
            )
            return json.loads(result.stdout)
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_contacts(self) -> List[Dict]:
        """Get contacts via termux-api"""
        if not self.termux_api:
            return []
        try:
            result = subprocess.run(
                ["termux-contact-list"],
                capture_output=True, text=True, timeout=10
            )
            return json.loads(result.stdout)
        except:
            return []
    
    def read_notifications(self) -> List[Dict]:
        """Read recent notifications"""
        if not self.termux_api:
            return []
        try:
            result = subprocess.run(
                ["termux-notification-list"],
                capture_output=True, text=True, timeout=10
            )
            return json.loads(result.stdout)
        except:
            return []
    
    def vibrate(self, duration_ms: int = 500) -> Dict:
        """Vibrate phone"""
        if not self.termux_api:
            return {"status": "error", "message": "termux-api required"}
        try:
            subprocess.run(
                ["termux-vibrate", "-d", str(duration_ms)],
                capture_output=True, timeout=5
            )
            return {"status": "vibrated", "duration": duration_ms}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def take_photo(self, camera_id: int = 0) -> Dict:
        """Take photo via termux-api"""
        if not self.termux_api:
            return {"status": "error", "message": "termux-api required"}
        try:
            filename = f"/sdcard/DCIM/liljr_capture_{int(time.time())}.jpg"
            subprocess.run(
                ["termux-camera-photo", "-c", str(camera_id), filename],
                capture_output=True, timeout=15
            )
            return {"status": "captured", "file": filename}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_location(self) -> Dict:
        """Get GPS location"""
        if not self.termux_api:
            return {"status": "error", "message": "termux-api required"}
        try:
            result = subprocess.run(
                ["termux-location"],
                capture_output=True, text=True, timeout=30
            )
            return json.loads(result.stdout)
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def simulate_tap(self, x: int, y: int) -> Dict:
        """Simulate tap at coordinates (requires root or adb)"""
        try:
            subprocess.run(
                ["input", "tap", str(x), str(y)],
                capture_output=True, timeout=5
            )
            return {"status": "tapped", "x": x, "y": y}
        except Exception as e:
            return {"status": "error", "message": str(e), "note": "May require root access"}
    
    def simulate_swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> Dict:
        """Simulate swipe"""
        try:
            subprocess.run(
                ["input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)],
                capture_output=True, timeout=5
            )
            return {"status": "swiped", "from": [x1,y1], "to": [x2,y2]}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def type_text(self, text: str) -> Dict:
        """Type text (requires root)"""
        try:
            subprocess.run(
                ["input", "text", text.replace(" ", "%s")],
                capture_output=True, timeout=5
            )
            return {"status": "typed", "text": text[:50]}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def press_key(self, keycode: str) -> Dict:
        """Press key (HOME, BACK, RECENT, etc)"""
        keycodes = {
            "HOME": "3", "BACK": "4", "RECENT": "187",
            "POWER": "26", "VOLUME_UP": "24", "VOLUME_DOWN": "25",
            "ENTER": "66", "TAB": "61"
        }
        code = keycodes.get(keycode.upper(), keycode)
        try:
            subprocess.run(
                ["input", "keyevent", str(code)],
                capture_output=True, timeout=5
            )
            return {"status": "pressed", "key": keycode}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def screenshot(self) -> Dict:
        """Take screenshot"""
        try:
            filename = f"/sdcard/Pictures/liljr_screenshot_{int(time.time())}.png"
            subprocess.run(
                ["screencap", filename],
                capture_output=True, timeout=10
            )
            return {"status": "captured", "file": filename}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def set_brightness(self, level: int) -> Dict:
        """Set screen brightness 0-255"""
        try:
            subprocess.run(
                ["settings", "put", "system", "screen_brightness", str(level)],
                capture_output=True, timeout=5
            )
            return {"status": "set", "brightness": level}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def set_volume(self, stream: str, level: int) -> Dict:
        """Set volume (music, alarm, notification, ring)"""
        streams = {"music": "3", "alarm": "4", "notification": "5", "ring": "2"}
        stream_code = streams.get(stream.lower(), "3")
        try:
            subprocess.run(
                ["cmd", "media", "volume", stream.lower(), "set", str(level)],
                capture_output=True, timeout=5
            )
            return {"status": "set", "stream": stream, "level": level}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_clipboard(self) -> Dict:
        """Read clipboard"""
        if not self.termux_api:
            return {"status": "error", "message": "termux-api required"}
        try:
            result = subprocess.run(
                ["termux-clipboard-get"],
                capture_output=True, text=True, timeout=5
            )
            return {"status": "ok", "content": result.stdout}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def set_clipboard(self, text: str) -> Dict:
        """Set clipboard"""
        if not self.termux_api:
            return {"status": "error", "message": "termux-api required"}
        try:
            subprocess.run(
                ["termux-clipboard-set", text],
                capture_output=True, timeout=5
            )
            return {"status": "set", "text": text[:50]}
        except Exception as e:
            return {"status": "error", "message": str(e)}

phone = PhoneController()
