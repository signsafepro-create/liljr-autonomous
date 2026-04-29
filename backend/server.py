"""
LILJR AUTONOMOUS CONTROL SERVER v4.0
All modules fused: Phone + Browser + Trading + Worker + Risk
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from phone_control import phone
from browser_agent import browser
from trading_engine import trader
from risk_manager import risk
from auto_worker import worker
from social_connector import social

app = FastAPI(title="LilJR Autonomous Control", version="4.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ═══════════════════════════════════════════════════════════════
# CORE ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "4.0.0", "mode": "AUTONOMOUS"}

@app.get("/api/status")
def status():
    return {
        "phone": {"api_available": phone.termux_api, "apps": len(phone.installed_apps)},
        "trading": {"configured": trader.is_configured(), "watchlist": trader.watchlist},
        "risk": risk.get_status(),
        "worker": worker.get_status(),
        "social": {"termux_api": social.termux_api, "telegram_configured": bool(social.telegram_token)}
    }

# ═══════════════════════════════════════════════════════════════
# PHONE CONTROL ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.post("/api/phone/launch_app")
async def launch_app(request: Request):
    data = await request.json()
    return phone.launch_app(data.get("package", ""))

@app.post("/api/phone/launch_url")
async def launch_url(request: Request):
    data = await request.json()
    return phone.launch_url(data.get("url", ""))

@app.post("/api/phone/send_sms")
async def send_sms(request: Request):
    data = await request.json()
    return phone.send_sms(data.get("number", ""), data.get("message", ""))

@app.post("/api/phone/call")
async def make_call(request: Request):
    data = await request.json()
    return phone.make_call(data.get("number", ""))

@app.get("/api/phone/battery")
def get_battery():
    return phone.get_battery()

@app.get("/api/phone/apps")
def get_apps():
    return {"apps": phone.installed_apps[:100]}  # First 100

@app.post("/api/phone/tap")
async def tap(request: Request):
    data = await request.json()
    return phone.simulate_tap(data.get("x", 0), data.get("y", 0))

@app.post("/api/phone/swipe")
async def swipe(request: Request):
    data = await request.json()
    return phone.simulate_swipe(
        data.get("x1", 0), data.get("y1", 0),
        data.get("x2", 0), data.get("y2", 0),
        data.get("duration", 300)
    )

@app.post("/api/phone/key")
async def press_key(request: Request):
    data = await request.json()
    return phone.press_key(data.get("key", "HOME"))

@app.get("/api/phone/screenshot")
def screenshot():
    return phone.screenshot()

@app.get("/api/phone/location")
def location():
    return phone.get_location()

@app.get("/api/phone/clipboard")
def get_clipboard():
    return phone.get_clipboard()

@app.post("/api/phone/clipboard")
async def set_clipboard(request: Request):
    data = await request.json()
    return phone.set_clipboard(data.get("text", ""))

# ═══════════════════════════════════════════════════════════════
# BROWSER AUTOMATION ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.post("/api/browser/fetch")
async def browser_fetch(request: Request):
    data = await request.json()
    return browser.fetch_page(data.get("url", ""))

@app.post("/api/browser/login")
async def browser_login(request: Request):
    data = await request.json()
    return browser.login(
        data.get("url", ""),
        data.get("username", ""),
        data.get("password", ""),
        data.get("user_field", "username"),
        data.get("pass_field", "password")
    )

@app.post("/api/browser/scrape")
async def browser_scrape(request: Request):
    data = await request.json()
    return browser.scrape_element(
        data.get("url", ""),
        data.get("selector", ""),
        data.get("by", "css")
    )

@app.post("/api/browser/click")
async def browser_click(request: Request):
    data = await request.json()
    return browser.click_element(data.get("url", ""), data.get("selector", ""))

@app.post("/api/browser/type")
async def browser_type(request: Request):
    data = await request.json()
    return browser.type_in_field(
        data.get("url", ""),
        data.get("selector", ""),
        data.get("text", ""),
        data.get("submit", False)
    )

# ═══════════════════════════════════════════════════════════════
# TRADING ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.get("/api/trading/account")
def trading_account():
    return trader.get_account()

@app.get("/api/trading/positions")
def trading_positions():
    return trader.get_positions()

@app.get("/api/trading/price/{symbol}")
def trading_price(symbol: str):
    return trader.get_price(symbol.upper())

@app.post("/api/trading/buy")
async def trading_buy(request: Request):
    data = await request.json()
    symbol = data.get("symbol", "").upper()
    qty = float(data.get("qty", 1))
    
    # Risk check
    price_info = trader.get_price(symbol)
    price = price_info.get("price", 0)
    amount = price * qty
    
    risk_check = risk.can_trade("buy", symbol, amount)
    if not risk_check["allowed"]:
        return {"status": "blocked", "reason": risk_check}
    
    result = trader.buy(symbol, qty)
    if result.get("status") not in ["error", "blocked"]:
        risk.record_trade("buy", symbol, amount, 0)  # PnL unknown yet
    return result

@app.post("/api/trading/sell")
async def trading_sell(request: Request):
    data = await request.json()
    symbol = data.get("symbol", "").upper()
    qty = data.get("qty")
    if qty:
        qty = float(qty)
    return trader.sell(symbol, qty)

@app.get("/api/trading/watchlist")
def trading_watchlist():
    return {"watchlist": trader.watchlist}

@app.post("/api/trading/watchlist")
async def modify_watchlist(request: Request):
    data = await request.json()
    action = data.get("action", "add")
    symbol = data.get("symbol", "").upper()
    if action == "add":
        return trader.add_to_watchlist(symbol)
    return trader.remove_from_watchlist(symbol)

@app.get("/api/trading/prices")
def trading_prices():
    return trader.watch_prices()

@app.get("/api/trading/orders")
def trading_orders():
    return trader.get_orders()

@app.get("/api/trading/history")
def trading_history():
    return trader.get_trade_history()

@app.get("/api/trading/portfolio")
def trading_portfolio():
    return trader.get_portfolio_value()

@app.post("/api/trading/auto")
async def trading_auto(request: Request):
    data = await request.json()
    enabled = data.get("enabled", False)
    strategy = data.get("strategy", "momentum")
    if enabled:
        return trader.enable_auto_trade(strategy, data.get("params", {}))
    return trader.disable_auto_trade()

# ═══════════════════════════════════════════════════════════════
# RISK MANAGEMENT ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.get("/api/risk/status")
def risk_status():
    return risk.get_status()

@app.get("/api/risk/log")
def risk_log():
    return {"trades": risk.get_trade_log()}

# ═══════════════════════════════════════════════════════════════
# WORKER ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.post("/api/worker/start")
def worker_start():
    # Register default tasks
    if not worker.tasks:
        worker.register_task("price_monitor", lambda: trader.watch_prices(), interval=300)
        worker.register_task("brain_pulse", lambda: {"pulse": "ok"}, interval=60)
    return worker.start()

@app.post("/api/worker/stop")
def worker_stop():
    return worker.stop()

@app.get("/api/worker/status")
def worker_status():
    return worker.get_status()

@app.get("/api/worker/logs")
def worker_logs():
    return {"logs": worker.get_logs(50)}

# ═══════════════════════════════════════════════════════════════
# SOCIAL CONNECTOR — Text, WhatsApp, Telegram, Notifications
# ═══════════════════════════════════════════════════════════════

@app.post("/api/social/sms/send")
async def social_sms_send(request: Request):
    data = await request.json()
    return social.send_sms(data.get("number", ""), data.get("message", ""))

@app.get("/api/social/sms/read")
def social_sms_read(limit: int = 20):
    return {"messages": social.read_sms(limit)}

@app.get("/api/social/sms/conversation/{number}")
def social_sms_conversation(number: str, limit: int = 50):
    return {"messages": social.read_sms_conversation(number, limit)}

@app.post("/api/social/whatsapp/send")
async def social_whatsapp_send(request: Request):
    data = await request.json()
    return social.whatsapp_send(data.get("number", ""), data.get("message", ""))

@app.post("/api/social/whatsapp/open")
async def social_whatsapp_open(request: Request):
    data = await request.json()
    return social.whatsapp_open_chat(data.get("number", ""))

@app.post("/api/social/telegram/send")
async def social_telegram_send(request: Request):
    data = await request.json()
    return social.telegram_send(data.get("message", ""), data.get("chat_id"))

@app.get("/api/social/telegram/updates")
def social_telegram_updates(limit: int = 10):
    return {"updates": social.telegram_get_updates(limit)}

@app.post("/api/social/telegram/reply")
async def social_telegram_reply(request: Request):
    data = await request.json()
    return social.telegram_reply(data.get("message", ""), data.get("reply_to"), data.get("chat_id"))

@app.get("/api/social/notifications")
def social_notifications():
    return {"notifications": social.read_notifications()}

@app.post("/api/social/notification/reply")
async def social_notification_reply(request: Request):
    data = await request.json()
    return social.reply_to_notification(data.get("id", ""), data.get("reply", ""))

@app.post("/api/social/share")
async def social_share(request: Request):
    data = await request.json()
    return social.share_text(data.get("text", ""), data.get("subject", ""), data.get("app"))

@app.post("/api/social/share/app")
async def social_share_app(request: Request):
    data = await request.json()
    return social.share_to_app(data.get("text", ""), data.get("app", ""))

@app.post("/api/social/post")
async def social_post(request: Request):
    data = await request.json()
    return social.post_to_social(data.get("text", ""), data.get("platform", ""))

@app.post("/api/social/open_app")
async def social_open_app(request: Request):
    data = await request.json()
    return social.open_app(data.get("package", ""))

@app.post("/api/social/open_url")
async def social_open_url(request: Request):
    data = await request.json()
    return social.open_url_in_app(data.get("url", ""), data.get("app"))

@app.get("/api/social/clipboard")
def social_clipboard_get():
    return social.clipboard_get()

@app.post("/api/social/clipboard")
async def social_clipboard_set(request: Request):
    data = await request.json()
    return social.clipboard_set(data.get("text", ""))

@app.get("/api/social/contacts")
def social_contacts():
    return {"contacts": social.get_contacts()}

@app.get("/api/social/contacts/search")
def social_contacts_search(name: str):
    return {"contacts": social.find_contact(name)}

@app.get("/api/social/calls")
def social_calls(limit: int = 50):
    return {"calls": social.get_call_log(limit)}

@app.post("/api/social/email")
async def social_email(request: Request):
    data = await request.json()
    return social.email_send(data.get("to", ""), data.get("subject", ""), data.get("body", ""))

@app.post("/api/social/mass_text")
async def social_mass_text(request: Request):
    data = await request.json()
    return social.mass_text(data.get("numbers", []), data.get("message", ""))

@app.post("/api/social/auto_reply")
async def social_auto_reply(request: Request):
    data = await request.json()
    return social.auto_reply_sms(data.get("keyword", ""), data.get("reply", ""))

@app.post("/api/social/broadcast")
async def social_broadcast(request: Request):
    data = await request.json()
    return social.broadcast(data.get("message", ""), data.get("channels", []))

# ═══════════════════════════════════════════════════════════════
# WEBSOCKET — Live Data Feed
# ═══════════════════════════════════════════════════════════════

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            msg = __import__('json').loads(data)
            
            if msg.get("type") == "price":
                symbol = msg.get("symbol", "AAPL")
                price = trader.get_price(symbol)
                await websocket.send_json({"type": "price", "data": price})
            
            elif msg.get("type") == "trade":
                # Execute trade via websocket
                symbol = msg.get("symbol", "").upper()
                action = msg.get("action", "buy")
                qty = float(msg.get("qty", 1))
                if action == "buy":
                    result = trader.buy(symbol, qty)
                else:
                    result = trader.sell(symbol, qty)
                await websocket.send_json({"type": "trade_result", "data": result})
            
            elif msg.get("type") == "phone":
                action = msg.get("action", "")
                if action == "screenshot":
                    result = phone.screenshot()
                elif action == "battery":
                    result = phone.get_battery()
                elif action == "tap":
                    result = phone.simulate_tap(msg.get("x", 0), msg.get("y", 0))
                else:
                    result = {"status": "unknown_action"}
                await websocket.send_json({"type": "phone_result", "data": result})
            
            elif msg.get("type") == "status":
                await websocket.send_json({
                    "type": "status",
                    "data": {
                        "trading": trader.get_portfolio_value(),
                        "risk": risk.get_status(),
                        "worker": worker.get_status()
                    }
                })
            
            else:
                await websocket.send_json({"type": "echo", "data": msg})
                
    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    print(f"🤖 LilJR Autonomous Control v4.0 on port {port}")
    print(f"📱 Phone control: {phone.termux_api}")
    print(f"💬 Social connector: SMS, WhatsApp, Telegram, notifications")
    print(f"💰 Trading: {'LIVE' if trader.is_configured() else 'MOCK (set ALPACA_API_KEY)'}")
    uvicorn.run(app, host="0.0.0.0", port=port)
