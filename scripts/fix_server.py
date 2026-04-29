#!/usr/bin/env python3
"""
LILJR SERVER FIXER — Fixes buy/sell crash when qty is null
Run: python fix_server.py ~/liljr-autonomous/backend/server_termux.py
"""
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "server_termux.py"

try:
    f = open(path, 'r').read()
except FileNotFoundError:
    print(f"❌ File not found: {path}")
    sys.exit(1)

# Fix buy_stock
old_buy = """    @app.route('/api/trading/buy', methods=['POST'])
    def buy_stock():
        data = request.get_json() or {}
        symbol = data.get('symbol', 'AAPL')
        qty = data.get('qty', 1)
        return jsonify({"status": "FILLED", "symbol": symbol.upper(), "qty": qty, "total": qty * 175})"""

new_buy = """    @app.route('/api/trading/buy', methods=['POST'])
    def buy_stock():
        data = request.get_json() or {}
        symbol = data.get('symbol', 'AAPL')
        qty = data.get('qty') or 1
        return jsonify({"status": "FILLED", "symbol": symbol.upper(), "qty": qty, "total": qty * 175})"""

f = f.replace(old_buy, new_buy)

# Fix sell_stock
old_sell = """    @app.route('/api/trading/sell', methods=['POST'])
    def sell_stock():
        data = request.get_json() or {}
        symbol = data.get('symbol', 'AAPL')
        qty = data.get('qty', 1)
        return jsonify({"status": "FILLED", "symbol": symbol.upper(), "qty": qty, "total": qty * 175})"""

new_sell = """    @app.route('/api/trading/sell', methods=['POST'])
    def sell_stock():
        data = request.get_json() or {}
        symbol = data.get('symbol', 'AAPL')
        qty = data.get('qty') or 1
        return jsonify({"status": "FILLED", "symbol": symbol.upper(), "qty": qty, "total": qty * 175})"""

f = f.replace(old_sell, new_sell)

open(path, 'w').write(f)
print(f"✅ Fixed {path}")
print("Restart server: bash ~/lj stop && bash ~/lj start")
