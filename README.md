# LilJR Autonomous Control v4.0

**100% Phone Control + Web Automation + Stock Trading + 24/7 Autonomous Worker**

## What's Included

### 📱 Phone Control (`phone_control.py`)
- Launch any Android app by package name
- Open URLs in browser
- Send SMS, make calls
- Read notifications, clipboard, contacts
- Take photos, screenshots
- GPS location
- Simulate taps, swipes, key presses
- Control brightness, volume
- Vibrations
- Requires Termux:API (`pkg install termux-api`)

### 🌐 Browser Automation (`browser_agent.py`)
- Fetch and parse any webpage
- Login to websites
- Scrape specific elements (CSS/XPath)
- Click elements, type in fields
- Form submission
- Session/cookie persistence
- Selenium headless support

### 💰 Stock Trading (`trading_engine.py`)
- Alpaca API integration (paper trading = free)
- Buy/Sell market and limit orders
- Live price monitoring
- Watchlist management
- Portfolio value calculation
- Trade history
- Auto-trading strategies (momentum, dip-buy, scalp)
- Fallback to yfinance for price data

### 🛡️ Risk Manager (`risk_manager.py`)
- Daily loss limits
- Max position size
- Max positions count
- Trade logging
- PnL tracking

### ⚙️ Auto Worker (`auto_worker.py`)
- 24/7 background task loop
- Register custom recurring tasks
- Price monitoring every 5 minutes
- Brain pulse every minute
- Activity logging

### 🤖 Unified Server (`server.py`)
- All modules wired together
- REST API for every function
- WebSocket for live data
- Phone control endpoints
- Trading endpoints with risk checks
- Browser automation endpoints
- Worker control endpoints

## API Endpoints

### Phone Control
- `POST /api/phone/launch_app` — Launch app
- `POST /api/phone/launch_url` — Open URL
- `POST /api/phone/send_sms` — Send SMS
- `POST /api/phone/call` — Make call
- `GET /api/phone/battery` — Battery status
- `GET /api/phone/apps` — List installed apps
- `POST /api/phone/tap` — Tap screen
- `POST /api/phone/swipe` — Swipe screen
- `POST /api/phone/key` — Press key
- `GET /api/phone/screenshot` — Take screenshot
- `GET /api/phone/location` — GPS location
- `GET/POST /api/phone/clipboard` — Read/set clipboard

### Browser
- `POST /api/browser/fetch` — Fetch page
- `POST /api/browser/login` — Login
- `POST /api/browser/scrape` — Scrape element
- `POST /api/browser/click` — Click element
- `POST /api/browser/type` — Type in field

### Trading
- `GET /api/trading/account` — Account info
- `GET /api/trading/positions` — Current positions
- `GET /api/trading/price/{symbol}` — Get price
- `POST /api/trading/buy` — Buy stock
- `POST /api/trading/sell` — Sell stock
- `GET /api/trading/watchlist` — Watchlist
- `GET /api/trading/prices` — All prices
- `GET /api/trading/orders` — Order history
- `GET /api/trading/history` — Trade history
- `GET /api/trading/portfolio` — Portfolio value
- `POST /api/trading/auto` — Enable/disable auto-trade

### Worker
- `POST /api/worker/start` — Start worker
- `POST /api/worker/stop` — Stop worker
- `GET /api/worker/status` — Worker status
- `GET /api/worker/logs` — Activity logs

### WebSocket `/ws`
- Real-time price feeds
- Execute trades via websocket
- Phone control via websocket
- Live status updates

## Setup

```bash
# 1. Clone
git clone https://github.com/signsafepro-create/liljr-autonomous.git
cd liljr-autonomous/backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set trading API keys (optional)
export ALPACA_API_KEY="your_key"
export ALPACA_SECRET_KEY="your_secret"

# 4. Start server
python server.py
```

## Phone Setup (Termux)

```bash
# Install Termux:API
pkg install termux-api

# Grant permissions in Android settings
# Then test:
termux-battery-status
```

## Frontend

Add `AutonomousDashboard.js` to your LilJR app screens. It provides:
- Command center (type commands like `buy AAPL 5`)
- Auto-trade toggle
- Live command log
- System status

## Trading Setup

1. Create free Alpaca account at https://alpaca.markets
2. Get API keys from dashboard
3. Set environment variables
4. Paper trading is free and unlimited

## Safety

Risk manager enforces:
- Max $100 daily loss (configurable)
- Max $1000 per position
- Max 5 open positions
- All trades logged

## 100% Control Commands

```
# Phone
launch com.whatsapp
url https://google.com
tap 500 800
swipe 100 500 700 500
key HOME
screenshot

# Trading
buy AAPL 5
sell TSLA 2

# Browser
fetch https://example.com
login https://site.com user pass
scrape https://site.com .price
```
