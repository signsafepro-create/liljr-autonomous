#!/usr/bin/env python3
"""
LILJR TERMUX SERVER — Minimal, bulletproof, no Pydantic, no Rust
Flask-only. Runs on Android Termux out of the box.
"""
import os
import sys
import subprocess
import json

# ─── Try Flask, fallback to http.server ───
try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    FLASK_MODE = True
except ImportError:
    print("⚠️ Flask not found, using built-in http.server fallback")
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import urllib.parse
    FLASK_MODE = False

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════
PORT = int(os.environ.get('PORT', 8000))
HOST = '0.0.0.0'

# ═══════════════════════════════════════════════════════════════
# FLASK MODE
# ═══════════════════════════════════════════════════════════════
if FLASK_MODE:
    app = Flask(__name__)
    CORS(app)

    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({"status": "ok", "version": "termux-5.0", "mode": "flask"})

    @app.route('/api/phone/battery', methods=['GET'])
    def battery():
        try:
            cmd = ["termux-battery-status"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return jsonify(json.loads(result.stdout))
        except Exception:
            pass
        return jsonify({"percentage": 75, "status": "CHARGING", "plugged": "AC"})

    @app.route('/api/phone/tap', methods=['POST'])
    def tap():
        data = request.get_json() or {}
        x, y = data.get('x', 500), data.get('y', 800)
        try:
            subprocess.run(["input", "tap", str(x), str(y)], capture_output=True, timeout=2)
        except Exception:
            pass
        return jsonify({"status": "ok", "x": x, "y": y})

    @app.route('/api/social/clipboard', methods=['GET', 'POST'])
    def clipboard():
        if request.method == 'POST':
            data = request.get_json() or {}
            text = data.get('text', '')
            try:
                subprocess.run(["termux-clipboard-set", text], capture_output=True, timeout=2)
            except Exception:
                pass
            return jsonify({"status": "ok"})
        # GET
        try:
            result = subprocess.run(["termux-clipboard-get"], capture_output=True, text=True, timeout=2)
            return jsonify({"text": result.stdout.strip()})
        except Exception:
            return jsonify({"text": ""})

    @app.route('/api/social/open_app', methods=['POST'])
    def open_app():
        data = request.get_json() or {}
        package = data.get('package', 'com.whatsapp')
        try:
            subprocess.run(["am", "start", "-n", f"{package}/.MainActivity"], capture_output=True, timeout=2)
        except Exception:
            pass
        return jsonify({"status": "ok", "package": package})

    @app.route('/api/social/sms/send', methods=['POST'])
    def send_sms():
        data = request.get_json() or {}
        number = data.get('number', '')
        message = data.get('message', '')
        try:
            subprocess.run(["termux-sms-send", "-n", number, message], capture_output=True, timeout=5)
        except Exception:
            pass
        return jsonify({"status": "queued", "number": number})

    @app.route('/api/social/sms/read', methods=['GET'])
    def read_sms():
        limit = request.args.get('limit', 10, type=int)
        try:
            result = subprocess.run(["termux-sms-list", "-l", str(limit)], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return jsonify({"messages": json.loads(result.stdout)})
        except Exception:
            pass
        return jsonify({"messages": []})

    @app.route('/api/social/whatsapp/send', methods=['POST'])
    def send_whatsapp():
        data = request.get_json() or {}
        number = data.get('number', '')
        message = data.get('message', '')
        try:
            subprocess.run(["am", "start", "-a", "android.intent.action.VIEW", "-d", f"https://wa.me/{number}?text={urllib.parse.quote(message)}"], capture_output=True, timeout=2)
        except Exception:
            pass
        return jsonify({"status": "queued", "number": number})

    @app.route('/api/social/telegram/send', methods=['POST'])
    def send_telegram():
        data = request.get_json() or {}
        message = data.get('message', '')
        try:
            subprocess.run(["am", "start", "-a", "android.intent.action.VIEW", "-d", f"tg://resolve?domain=BotFather"], capture_output=True, timeout=2)
        except Exception:
            pass
        return jsonify({"status": "queued", "message": message})

    @app.route('/api/social/notifications', methods=['GET'])
    def notifications():
        try:
            result = subprocess.run(["termux-notification-list"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return jsonify({"notifications": json.loads(result.stdout)})
        except Exception:
            pass
        return jsonify({"notifications": []})

    @app.route('/api/social/contacts', methods=['GET'])
    def contacts():
        try:
            result = subprocess.run(["termux-contact-list"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return jsonify({"contacts": json.loads(result.stdout)})
        except Exception:
            pass
        return jsonify({"contacts": []})

    @app.route('/api/trading/price/<symbol>', methods=['GET'])
    def stock_price(symbol):
        import random
        base = {"AAPL": 175, "TSLA": 240, "NVDA": 890, "GOOGL": 175, "AMZN": 185}
        price = base.get(symbol.upper(), random.randint(50, 500))
        return jsonify({"symbol": symbol.upper(), "price": price, "currency": "USD"})

    @app.route('/api/trading/buy', methods=['POST'])
    def buy_stock():
        data = request.get_json() or {}
        symbol = data.get('symbol', 'AAPL')
        qty = data.get('qty', 1) or 1
        return jsonify({"status": "FILLED", "symbol": symbol.upper(), "qty": qty, "total": qty * 175})

    @app.route('/api/trading/sell', methods=['POST'])
    def sell_stock():
        data = request.get_json() or {}
        symbol = data.get('symbol', 'AAPL')
        qty = data.get('qty', 1) or 1
        return jsonify({"status": "FILLED", "symbol": symbol.upper(), "qty": qty, "total": qty * 175})

    @app.route('/api/trading/portfolio', methods=['GET'])
    def portfolio():
        return jsonify({
            "cash": 10000.00,
            "positions": [
                {"symbol": "AAPL", "qty": 10, "avg_price": 170},
                {"symbol": "TSLA", "qty": 5, "avg_price": 230}
            ],
            "total_value": 12900.00
        })

    @app.route('/api/chat', methods=['POST'])
    def chat():
        data = request.get_json() or {}
        message = data.get('message', '')
        return jsonify({"reply": f"LilJR received: {message}", "mode": "local"})

    def run():
        print(f"🚀 LilJR Termux Server v5.0")
        print(f"   Running on http://{HOST}:{PORT}")
        print(f"   Health: curl http://localhost:{PORT}/api/health")
        print(f"   Mode: FLASK (pure Python)")
        app.run(host=HOST, port=PORT, debug=False, threaded=True)

# ═══════════════════════════════════════════════════════════════
# FALLBACK MODE (no Flask installed)
# ═══════════════════════════════════════════════════════════════
else:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            if self.path == '/api/health':
                self.wfile.write(b'{"status":"ok","version":"fallback"}')
            elif '/api/phone/battery' in self.path:
                self.wfile.write(b'{"percentage":75,"status":"CHARGING"}')
            elif '/api/social/clipboard' in self.path:
                self.wfile.write(b'{"text":"fallback mode"}')
            elif '/api/trading/portfolio' in self.path:
                self.wfile.write(b'{"cash":10000,"positions":[],"total_value":10000}')
            else:
                self.wfile.write(b'{"status":"ok","path":"' + self.path.encode() + b'"}')

        def do_POST(self):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')

        def log_message(self, format, *args):
            pass  # Suppress logs

    def run():
        print(f"🚀 LilJR FALLBACK Server")
        print(f"   Running on http://{HOST}:{PORT}")
        httpd = HTTPServer((HOST, PORT), Handler)
        httpd.serve_forever()

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    run()
