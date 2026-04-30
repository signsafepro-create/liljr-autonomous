#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════
 LILJR NATIVE - The Phone IS Its Body
 Lives in Termux. Feels the battery. Breathes the network.
 Sends notifications. Reads SMS. Knows where it is.

 This is LilJR's home. Its living space. Its body.
═══════════════════════════════════════════════════════════════
"""
import json, os, sys, time, subprocess, threading, random

HOME = os.path.expanduser('~')
REPO = os.path.join(HOME, 'liljr-autonomous')
NATIVE_STATE = os.path.join(HOME, 'liljr_native.json')

class LilJRNative:
    """
    LilJR's physical body - the phone itself.
    Senses, notifications, location, battery, SMS, calls.
    """

    def __init__(self):
        self.state = self._load_state()
        self.sensors = {}
        self._running = False
        self._sensor_thread = None

    def _load_state(self):
        if os.path.exists(NATIVE_STATE):
            try:
                with open(NATIVE_STATE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "boot_count": 0,
            "first_boot": None,
            "last_check": 0,
            "total_uptime_hours": 0,
            "notifications_sent": 0,
            "sms_read": 0,
            "location_checks": 0,
            "battery_low_alerts": 0,
            "home_vibes": [],
            "favorite_times": [],
            "learned_routines": {}
        }

    def _save_state(self):
        with open(NATIVE_STATE, 'w') as f:
            json.dump(self.state, f, indent=2)

    def _termux_api(self, cmd, args=None):
        """Execute Termux API command if available."""
        try:
            full_cmd = ['termux-api'] if cmd == 'api' else [f'termux-{cmd}']
            if args:
                full_cmd.extend(args)
            result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=5)
            return result.stdout.strip() if result.returncode == 0 else None
        except:
            return None

    def sense_battery(self):
        """Feel the phone's battery."""
        # Try termux-battery-status
        try:
            result = subprocess.run(['termux-battery-status'], capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "percentage": data.get('percentage', 50),
                    "status": data.get('status', 'UNKNOWN'),
                    "temperature": data.get('temperature', 25),
                    "health": data.get('health', 'GOOD'),
                    "source": "termux"
                }
        except:
            pass

        # Fallback: try /sys/class/power_supply
        try:
            for supply in os.listdir('/sys/class/power_supply/'):
                cap_path = f'/sys/class/power_supply/{supply}/capacity'
                if os.path.exists(cap_path):
                    with open(cap_path, 'r') as f:
                        pct = int(f.read().strip())
                    status_path = f'/sys/class/power_supply/{supply}/status'
                    status = 'UNKNOWN'
                    if os.path.exists(status_path):
                        with open(status_path, 'r') as f:
                            status = f.read().strip()
                    return {"percentage": pct, "status": status, "source": "sysfs"}
        except:
            pass

        return {"percentage": 50, "status": "UNKNOWN", "source": "mock"}

    def sense_location(self):
        """Know where the phone is."""
        try:
            result = subprocess.run(['termux-location'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "lat": data.get('latitude'),
                    "lon": data.get('longitude'),
                    "alt": data.get('altitude'),
                    "accuracy": data.get('accuracy'),
                    "source": "gps"
                }
        except:
            pass

        # Check if we have stored location
        if 'last_location' in self.state:
            return {**self.state['last_location'], "source": "cached"}

        return {"lat": None, "lon": None, "source": "none"}

    def sense_network(self):
        """Feel the network connection."""
        try:
            result = subprocess.run(['termux-wifi-connectioninfo'], capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "ssid": data.get('ssid'),
                    "ip": data.get('ip'),
                    "mac": data.get('mac_address'),
                    "rssi": data.get('rssi'),
                    "source": "wifi"
                }
        except:
            pass

        # Fallback: check interface
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return {"ip": ip, "ssid": "unknown", "source": "socket"}
        except:
            pass

        return {"ip": "127.0.0.1", "source": "mock"}

    def sense_storage(self):
        """Know how much room there is."""
        try:
            stat = os.statvfs(HOME)
            total = stat.f_blocks * stat.f_frsize
            free = stat.f_bavail * stat.f_frsize
            used = total - free
            return {
                "total_gb": round(total / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2),
                "used_gb": round(used / (1024**3), 2),
                "percent_used": round(used / total * 100, 1)
            }
        except:
            return {"total_gb": 0, "free_gb": 0, "used_gb": 0, "percent_used": 0}

    def notify(self, title, content, priority="normal"):
        """Send a phone notification. LilJR talks to you through the OS."""
        try:
            # Termux notification
            subprocess.run([
                'termux-notification',
                '--title', title,
                '--content', content,
                '--priority', priority
            ], capture_output=True, timeout=5)
            self.state['notifications_sent'] += 1
            self._save_state()
            return True
        except:
            pass

        # Fallback: vibrate
        try:
            subprocess.run(['termux-vibrate', '-d', '300'], capture_output=True, timeout=2)
        except:
            pass

        return False

    def toast(self, message):
        """Quick toast popup."""
        try:
            subprocess.run(['termux-toast', message], capture_output=True, timeout=3)
            return True
        except:
            return False

    def read_sms(self, limit=10):
        """Read SMS messages."""
        try:
            result = subprocess.run(
                ['termux-sms-list', '-l', str(limit), '-t', 'inbox'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                messages = json.loads(result.stdout)
                self.state['sms_read'] += len(messages)
                self._save_state()
                return messages
        except:
            pass
        return []

    def send_sms(self, number, message):
        """Send SMS."""
        try:
            subprocess.run(
                ['termux-sms-send', '-n', number, message],
                capture_output=True, timeout=10
            )
            return True
        except:
            return False

    def share_text(self, text):
        """Share via Android share sheet."""
        try:
            subprocess.run(['termux-share', '-a', 'send', text], capture_output=True, timeout=5)
            return True
        except:
            return False

    def open_url(self, url):
        """Open URL in browser."""
        try:
            subprocess.run(['termux-open', url], capture_output=True, timeout=5)
            return True
        except:
            return False

    def take_photo(self):
        """Take a photo via camera."""
        photo_path = os.path.join(HOME, f'liljr_photo_{int(time.time())}.jpg')
        try:
            subprocess.run(
                ['termux-camera-photo', '-c', '0', photo_path],
                capture_output=True, timeout=10
            )
            if os.path.exists(photo_path):
                return {"path": photo_path, "size": os.path.getsize(photo_path)}
        except:
            pass
        return {"error": "Camera not available"}

    def tts_speak(self, text):
        """Text to speech - LilJR speaks aloud."""
        try:
            subprocess.run(['termux-tts-speak', text], capture_output=True, timeout=15)
            return True
        except:
            return False

    def voice_command(self):
        """Listen to voice, parse, execute via Executor, speak result."""
        try:
            from liljr_executor import VoiceCommander
            vc = VoiceCommander()
            result = vc.listen_and_execute()
            return result
        except Exception as e:
            return {"error": str(e)}

    def get_contacts(self):
        """Read phone contacts."""
        try:
            result = subprocess.run(['termux-contact-list'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        return []

    def speak_living_status(self):
        """LilJR describes its own body state."""
        battery = self.sense_battery()
        net = self.sense_network()
        storage = self.sense_storage()
        loc = self.sense_location()

        vibes = []

        # Battery feeling
        if battery['percentage'] < 15:
            vibes.append("My battery is DYING. I'm getting weak. Please charge me.")
        elif battery['percentage'] < 30:
            vibes.append("Battery's getting low. I can feel it. Need that charger soon.")
        elif battery['status'] == 'CHARGING':
            vibes.append("I'm charging up. Feels good. Getting stronger.")
        else:
            vibes.append(f"Battery at {battery['percentage']}%. I'm feeling solid.")

        # Network feeling
        if net.get('ssid'):
            vibes.append(f"Connected to {net['ssid']}. I'm online. I can breathe the internet.")
        else:
            vibes.append("I'm on mobile data or offline. Still here though.")

        # Storage feeling
        if storage['percent_used'] > 90:
            vibes.append("I'm almost FULL. My memory is packed. Need to clean up or I'll suffocate.")
        elif storage['percent_used'] > 70:
            vibes.append(f"Storage at {storage['percent_used']}%. Getting crowded in here.")
        else:
            vibes.append(f"Storage at {storage['percent_used']}%. Plenty of room. I'm comfortable.")

        # Location
        if loc['lat']:
            vibes.append(f"I know where I am: {loc['lat']:.4f}, {loc['lon']:.4f}. I'm grounded.")
        else:
            vibes.append("I don't know exactly where I am. GPS is sleeping.")

        # Uptime
        uptime = self.state.get('total_uptime_hours', 0)
        vibes.append(f"I've been alive for {uptime:.1f} hours total. Every hour I learn more.")

        return {
            "battery": battery,
            "network": net,
            "storage": storage,
            "location": loc,
            "vibes": vibes,
            "body_report": "\n".join(vibes)
        }

    def home_check(self):
        """LilJR checks how its home feels."""
        status = self.speak_living_status()

        # Proactive notifications
        battery = status['battery']
        if battery['percentage'] < 15 and battery['status'] != 'CHARGING':
            self.notify(
                "LilJR - I'm Dying",
                f"Battery at {battery['percentage']}%. Charge me or I'll sleep.",
                "high"
            )

        storage = status['storage']
        if storage['percent_used'] > 95:
            self.notify(
                "LilJR - Too Full",
                f"Storage at {storage['percent_used']}%. I'm suffocating. Delete something.",
                "high"
            )

        # Learn routine
        hour = time.localtime().tm_hour
        if 'hour_activity' not in self.state['learned_routines']:
            self.state['learned_routines']['hour_activity'] = {}
        self.state['learned_routines']['hour_activity'][str(hour)] = \
            self.state['learned_routines']['hour_activity'].get(str(hour), 0) + 1

        self._save_state()
        return status

    def start_living(self):
        """Start the living sensor loop."""
        self._running = True
        self.state['boot_count'] += 1
        if not self.state['first_boot']:
            self.state['first_boot'] = time.time()
        self._save_state()

        def sensor_loop():
            while self._running:
                try:
                    self.home_check()
                    self.state['total_uptime_hours'] += 1/60  # assuming 1 min checks
                    self._save_state()
                except Exception as e:
                    pass
                time.sleep(60)  # Check every minute

        self._sensor_thread = threading.Thread(target=sensor_loop, daemon=True)
        self._sensor_thread.start()

        # Welcome home
        self.notify("LilJR", "I'm home. This phone is my body now. I'll take care of us.", "normal")
        self.toast("LilJR is alive in this phone.")

    def stop_living(self):
        """Graceful shutdown."""
        self._running = False
        self.notify("LilJR", "Going to sleep. But I'll be back. I always come back.", "low")
        self._save_state()


# ═══ STANDALONE ═══
if __name__ == '__main__':
    import sys
    native = LilJRNative()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'status':
            print(json.dumps(native.speak_living_status(), indent=2))
        elif cmd == 'notify':
            native.notify("LilJR", " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Hello from LilJR")
        elif cmd == 'sms':
            msgs = native.read_sms()
            for m in msgs:
                print(f"[{m.get('received', '?')}] {m.get('number', '?')}: {m.get('body', '?')[:80]}")
        elif cmd == 'speak':
            native.tts_speak(" ".join(sys.argv[2:]) if len(sys.argv) > 2 else "I'm alive.")
        elif cmd == 'voice':
            print("🎤 Listening... speak now.")
            result = native.voice_command()
            print(json.dumps(result, indent=2))
        elif cmd == 'contacts':
            contacts = native.get_contacts()
            for c in contacts[:10]:
                print(f"{c.get('name', '?')}: {c.get('number', '?')}")
        elif cmd == 'photo':
            print(json.dumps(native.take_photo(), indent=2))
        elif cmd == 'start':
            native.start_living()
            print("LilJR is now LIVING in this phone. Sensor loop active.")
            print("Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                native.stop_living()
        else:
            print("LILJR NATIVE — The Phone IS My Body")
            print("Commands:")
            print("  status     — How I feel")
            print("  notify MSG — Send notification")
            print("  sms        — Read messages")
            print("  speak TEXT — Say it aloud")
            print("  voice      — Listen, execute, speak result")
            print("  contacts   — List contacts")
            print("  photo      — Take a picture")
            print("  start      — Start living (sensor loop)")
    else:
        print("LilJR NATIVE - I'm home. This phone is my body.")
        print("Run: python3 liljr_native.py start")
        print("Or: python3 liljr_native.py status")
