"""
SOCIAL CONNECTOR — Link into any app, text, read, post, reply
SMS, WhatsApp, Telegram, notifications, share to any app
"""
import os
import re
import json
import subprocess
import requests
from typing import Dict, List, Optional

class SocialConnector:
    def __init__(self):
        self.termux_api = self._check_termux_api()
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    
    def _check_termux_api(self) -> bool:
        try:
            subprocess.run(["termux-battery-status"], capture_output=True, timeout=5)
            return True
        except:
            return False
    
    def _run(self, cmd: List[str], timeout: int = 10) -> Dict:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return {"ok": result.returncode == 0, "out": result.stdout, "err": result.stderr}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ═══════════════════════════════════════════════════════════════
    # SMS
    # ═══════════════════════════════════════════════════════════════

    def send_sms(self, number: str, message: str) -> Dict:
        if not self.termux_api:
            return {"status": "error", "message": "termux-api not installed"}
        r = self._run(["termux-sms-send", "-n", number, message])
        return {"status": "sent" if r["ok"] else "failed", "to": number, "message": message[:100]}

    def read_sms(self, limit: int = 20, offset: int = 0) -> List[Dict]:
        if not self.termux_api:
            return []
        r = self._run(["termux-sms-list", "-l", str(limit), "-o", str(offset), "-t", "inbox"])
        if r["ok"] and r["out"]:
            try:
                return json.loads(r["out"])
            except:
                pass
        return []

    def read_sms_conversation(self, number: str, limit: int = 50) -> List[Dict]:
        all_sms = self.read_sms(limit=limit * 2)
        return [msg for msg in all_sms if number in msg.get("number", "")]

    # ═══════════════════════════════════════════════════════════════
    # WHATSAPP
    # ═══════════════════════════════════════════════════════════════

    def whatsapp_send(self, number: str, message: str) -> Dict:
        """Open WhatsApp with pre-filled message. User must tap send."""
        clean_number = re.sub(r"[^0-9+]", "", number)
        if not clean_number.startswith("+"):
            clean_number = "+1" + clean_number  # Default US
        
        # Method 1: Direct WhatsApp intent
        r = self._run([
            "am", "start",
            "-a", "android.intent.action.SEND",
            "-t", "text/plain",
            "-e", "android.intent.extra.TEXT", message,
            "-p", "com.whatsapp"
        ])
        
        if not r["ok"]:
            # Method 2: WhatsApp Web link via browser
            encoded_msg = requests.utils.quote(message)
            r2 = self._run([
                "am", "start",
                "-a", "android.intent.action.VIEW",
                "-d", f"https://wa.me/{clean_number}?text={encoded_msg}"
            ])
            return {"status": "opened_web" if r2["ok"] else "failed", "number": clean_number, "note": "Tap send in WhatsApp"}
        
        return {"status": "opened_app", "number": clean_number, "note": "Tap send in WhatsApp"}

    def whatsapp_open_chat(self, number: str) -> Dict:
        clean_number = re.sub(r"[^0-9+]", "", number)
        r = self._run([
            "am", "start",
            "-a", "android.intent.action.VIEW",
            "-d", f"https://wa.me/{clean_number}"
        ])
        return {"status": "opened" if r["ok"] else "failed", "number": clean_number}

    # ═══════════════════════════════════════════════════════════════
    # TELEGRAM (Bot API)
    # ═══════════════════════════════════════════════════════════════

    def telegram_send(self, message: str, chat_id: str = None) -> Dict:
        token = self.telegram_token
        chat = chat_id or self.telegram_chat_id
        if not token or not chat:
            return {"status": "error", "message": "Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID"}
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            r = requests.post(url, json={"chat_id": chat, "text": message}, timeout=10)
            return {"status": "sent", "response": r.json()}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def telegram_get_updates(self, limit: int = 10) -> List[Dict]:
        if not self.telegram_token:
            return []
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/getUpdates"
            r = requests.get(url, params={"limit": limit}, timeout=10)
            data = r.json()
            return data.get("result", [])
        except:
            return []

    def telegram_reply(self, message: str, reply_to_message_id: int, chat_id: str = None) -> Dict:
        token = self.telegram_token
        chat = chat_id or self.telegram_chat_id
        if not token or not chat:
            return {"status": "error", "message": "Token and chat_id required"}
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            r = requests.post(url, json={
                "chat_id": chat,
                "text": message,
                "reply_to_message_id": reply_to_message_id
            }, timeout=10)
            return {"status": "replied", "response": r.json()}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ═══════════════════════════════════════════════════════════════
    # NOTIFICATIONS
    # ═══════════════════════════════════════════════════════════════

    def read_notifications(self) -> List[Dict]:
        if not self.termux_api:
            return []
        r = self._run(["termux-notification-list"])
        if r["ok"] and r["out"]:
            try:
                return json.loads(r["out"])
            except:
                pass
        return []

    def reply_to_notification(self, id_str: str, reply: str) -> Dict:
        """Reply to a notification (Android 7+). Requires termux-api."""
        if not self.termux_api:
            return {"status": "error", "message": "termux-api required"}
        r = self._run(["termux-notification-reply", "-i", id_str, reply])
        return {"status": "replied" if r["ok"] else "failed", "id": id_str}

    def dismiss_notification(self, id_str: str) -> Dict:
        if not self.termux_api:
            return {"status": "error", "message": "termux-api required"}
        r = self._run(["termux-notification-remove", id_str])
        return {"status": "dismissed" if r["ok"] else "failed"}

    # ═══════════════════════════════════════════════════════════════
    # SHARE TO ANY APP
    # ═══════════════════════════════════════════════════════════════

    def share_text(self, text: str, subject: str = "", app_package: str = None) -> Dict:
        """Share text to any app (opens share sheet or direct to app)"""
        cmd = [
            "am", "start",
            "-a", "android.intent.action.SEND",
            "-t", "text/plain",
            "-e", "android.intent.extra.TEXT", text
        ]
        if subject:
            cmd += ["-e", "android.intent.extra.SUBJECT", subject]
        if app_package:
            cmd += ["-p", app_package]
        r = self._run(cmd)
        return {"status": "shared" if r["ok"] else "failed", "target": app_package or "share_sheet"}

    def share_to_app(self, text: str, app: str) -> Dict:
        """Direct share to known app. app = 'telegram', 'twitter', 'instagram', 'gmail', etc."""
        packages = {
            "telegram": "org.telegram.messenger",
            "twitter": "com.twitter.android",
            "x": "com.twitter.android",
            "instagram": "com.instagram.android",
            "gmail": "com.google.android.gm",
            "facebook": "com.facebook.katana",
            "sms": "com.google.android.apps.messaging",
            "signal": "org.thoughtcrime.securesms",
            "discord": "com.discord"
        }
        pkg = packages.get(app.lower())
        if not pkg:
            return {"status": "error", "message": f"Unknown app '{app}'. Known: {list(packages.keys())}"}
        return self.share_text(text, app_package=pkg)

    def open_app(self, package: str) -> Dict:
        """Launch any app by package name"""
        r = self._run(["monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1"])
        if not r["ok"]:
            r = self._run(["am", "start", "-n", f"{package}/.{package.split('.')[-1]}.MainActivity"])
        return {"status": "launched" if r["ok"] else "failed", "package": package}

    def open_url_in_app(self, url: str, app_package: str = None) -> Dict:
        """Open URL in specific app or default browser"""
        cmd = ["am", "start", "-a", "android.intent.action.VIEW", "-d", url]
        if app_package:
            cmd += ["-p", app_package]
        r = self._run(cmd)
        return {"status": "opened" if r["ok"] else "failed", "url": url, "app": app_package}

    # ═══════════════════════════════════════════════════════════════
    # CLIPBOARD
    # ═══════════════════════════════════════════════════════════════

    def clipboard_get(self) -> Dict:
        if not self.termux_api:
            return {"status": "error", "message": "termux-api required"}
        r = self._run(["termux-clipboard-get"])
        return {"status": "ok", "content": r["out"]} if r["ok"] else {"status": "error", "message": r["err"]}

    def clipboard_set(self, text: str) -> Dict:
        if not self.termux_api:
            return {"status": "error", "message": "termux-api required"}
        r = self._run(["termux-clipboard-set", text])
        return {"status": "set"} if r["ok"] else {"status": "error", "message": r["err"]}

    # ═══════════════════════════════════════════════════════════════
    # CONTACTS
    # ═══════════════════════════════════════════════════════════════

    def get_contacts(self) -> List[Dict]:
        if not self.termux_api:
            return []
        r = self._run(["termux-contact-list"])
        if r["ok"] and r["out"]:
            try:
                return json.loads(r["out"])
            except:
                pass
        return []

    def find_contact(self, name: str) -> List[Dict]:
        contacts = self.get_contacts()
        name_lower = name.lower()
        return [c for c in contacts if name_lower in c.get("name", "").lower()]

    # ═══════════════════════════════════════════════════════════════
    # CALL LOGS
    # ═══════════════════════════════════════════════════════════════

    def get_call_log(self, limit: int = 50) -> List[Dict]:
        if not self.termux_api:
            return []
        r = self._run(["termux-telephony-call-log", "-l", str(limit)])
        if r["ok"] and r["out"]:
            try:
                return json.loads(r["out"])
            except:
                pass
        return []

    # ═══════════════════════════════════════════════════════════════
    # EMAIL (via share to Gmail)
    # ═══════════════════════════════════════════════════════════════

    def email_send(self, to: str, subject: str, body: str) -> Dict:
        """Opens Gmail with pre-filled email. User taps send."""
        r = self._run([
            "am", "start",
            "-a", "android.intent.action.SENDTO",
            "-d", f"mailto:{to}?subject={requests.utils.quote(subject)}&body={requests.utils.quote(body)}"
        ])
        return {"status": "opened" if r["ok"] else "failed", "to": to, "note": "Tap send in Gmail"}

    # ═══════════════════════════════════════════════════════════════
    # SOCIAL POSTING
    # ═══════════════════════════════════════════════════════════════

    def post_to_social(self, text: str, platform: str) -> Dict:
        """Post to social platform. Opens app with pre-filled text."""
        platforms = {
            "twitter": "com.twitter.android",
            "x": "com.twitter.android",
            "instagram": "com.instagram.android",
            "facebook": "com.facebook.katana",
            "linkedin": "com.linkedin.android",
            "tiktok": "com.zhiliaoapp.musically",
            "reddit": "com.reddit.frontpage"
        }
        pkg = platforms.get(platform.lower())
        if not pkg:
            return {"status": "error", "message": f"Platform '{platform}' not supported. Use: {list(platforms.keys())}"}
        return self.share_text(text, app_package=pkg)

    def post_with_image(self, text: str, image_path: str, platform: str) -> Dict:
        """Share image + text to platform"""
        platforms = {
            "instagram": "com.instagram.android",
            "twitter": "com.twitter.android",
            "facebook": "com.facebook.katana",
            "whatsapp": "com.whatsapp"
        }
        pkg = platforms.get(platform.lower())
        if not pkg:
            return {"status": "error", "message": f"Platform not supported"}
        
        cmd = [
            "am", "start",
            "-a", "android.intent.action.SEND",
            "-t", "image/*",
            "-e", "android.intent.extra.STREAM", f"file://{image_path}",
            "-e", "android.intent.extra.TEXT", text
        ]
        r = self._run(cmd)
        return {"status": "shared" if r["ok"] else "failed", "platform": platform}

    # ═══════════════════════════════════════════════════════════════
    # BATCH / AUTOMATED
    # ═══════════════════════════════════════════════════════════════

    def mass_text(self, numbers: List[str], message: str) -> List[Dict]:
        """Send same text to multiple numbers"""
        results = []
        for num in numbers:
            results.append(self.send_sms(num, message))
        return results

    def auto_reply_sms(self, keyword: str, reply: str) -> Dict:
        """Check recent SMS and auto-reply if keyword found"""
        messages = self.read_sms(limit=10)
        sent = 0
        for msg in messages:
            if keyword.lower() in msg.get("body", "").lower():
                number = msg.get("number", "")
                if number:
                    self.send_sms(number, reply)
                    sent += 1
        return {"status": "done", "replies_sent": sent, "keyword": keyword}

    def broadcast(self, message: str, channels: List[str]) -> Dict:
        """Broadcast to multiple channels: sms, telegram, whatsapp"""
        results = {}
        for ch in channels:
            if ch == "telegram":
                results["telegram"] = self.telegram_send(message)
            elif ch == "whatsapp":
                # WhatsApp needs a number, skip or use default
                results["whatsapp"] = {"status": "skipped", "message": "WhatsApp requires target number"}
        return {"status": "broadcast_done", "results": results}

social = SocialConnector()
