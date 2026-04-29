"""
TRADING ENGINE
Stock trading via Alpaca API (free, no commission)
Supports: buy, sell, market orders, limit orders
Live price monitoring, auto-trading strategies
"""
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests

class TradingEngine:
    def __init__(self):
        self.api_key = os.getenv("ALPACA_API_KEY", "")
        self.secret = os.getenv("ALPACA_SECRET_KEY", "")
        self.base_url = "https://paper-api.alpaca.markets"  # Paper trading (free)
        self.data_url = "https://data.alpaca.markets"
        self.positions: Dict[str, Dict] = {}
        self.orders: List[Dict] = []
        self.watchlist: List[str] = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA", "META"]
        self.trade_history: List[Dict] = []
        self.auto_trade_enabled = False
        self.strategies = {
            "momentum": self._momentum_strategy,
            "dip_buy": self._dip_buy_strategy,
            "scalp": self._scalp_strategy
        }
    
    def _headers(self) -> Dict:
        return {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.secret,
            "Content-Type": "application/json"
        }
    
    def is_configured(self) -> bool:
        return bool(self.api_key and self.secret)
    
    def get_account(self) -> Dict:
        """Get account info"""
        if not self.is_configured():
            return {"status": "error", "message": "Alpaca API keys not set"}
        try:
            resp = requests.get(f"{self.base_url}/v2/account", headers=self._headers(), timeout=10)
            return resp.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_positions(self) -> List[Dict]:
        """Get current positions"""
        if not self.is_configured():
            return []
        try:
            resp = requests.get(f"{self.base_url}/v2/positions", headers=self._headers(), timeout=10)
            data = resp.json()
            self.positions = {p["symbol"]: p for p in data}
            return data
        except Exception as e:
            return []
    
    def get_price(self, symbol: str) -> Dict:
        """Get current price"""
        try:
            # Use free yfinance as fallback if no Alpaca keys
            if not self.is_configured():
                return self._yfinance_price(symbol)
            resp = requests.get(
                f"{self.data_url}/v2/stocks/{symbol}/quotes/latest",
                headers=self._headers(), timeout=10
            )
            return resp.json()
        except Exception as e:
            return self._yfinance_price(symbol)
    
    def _yfinance_price(self, symbol: str) -> Dict:
        """Fallback price via yfinance"""
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            return {
                "symbol": symbol,
                "price": info.get("lastPrice", 0),
                "change": info.get("lastPrice", 0) - info.get("open", 0),
                "source": "yfinance"
            }
        except:
            # Mock price for testing
            mock_prices = {
                "AAPL": 185.50, "GOOGL": 140.20, "MSFT": 380.00,
                "TSLA": 240.00, "AMZN": 170.00, "NVDA": 880.00, "META": 500.00
            }
            return {
                "symbol": symbol,
                "price": mock_prices.get(symbol, 100.00),
                "source": "mock",
                "note": "Set ALPACA_API_KEY for real data"
            }
    
    def buy(self, symbol: str, qty: float = 1.0, order_type: str = "market", 
            limit_price: Optional[float] = None) -> Dict:
        """Buy stock"""
        if not self.is_configured():
            return {"status": "error", "message": "Alpaca API not configured"}
        try:
            order = {
                "symbol": symbol.upper(),
                "qty": str(qty),
                "side": "buy",
                "type": order_type,
                "time_in_force": "day"
            }
            if order_type == "limit" and limit_price:
                order["limit_price"] = str(limit_price)
            
            resp = requests.post(
                f"{self.base_url}/v2/orders",
                headers=self._headers(),
                json=order,
                timeout=10
            )
            result = resp.json()
            self.orders.append(result)
            self.trade_history.append({
                "time": datetime.utcnow().isoformat(),
                "action": "BUY",
                "symbol": symbol,
                "qty": qty,
                "status": result.get("status", "pending")
            })
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def sell(self, symbol: str, qty: Optional[float] = None, order_type: str = "market") -> Dict:
        """Sell stock"""
        if not self.is_configured():
            return {"status": "error", "message": "Alpaca API not configured"}
        try:
            order = {
                "symbol": symbol.upper(),
                "side": "sell",
                "type": order_type,
                "time_in_force": "day"
            }
            if qty:
                order["qty"] = str(qty)
            else:
                order["side"] = "sell"  # Sell all
            
            resp = requests.post(
                f"{self.base_url}/v2/orders",
                headers=self._headers(),
                json=order,
                timeout=10
            )
            result = resp.json()
            self.trade_history.append({
                "time": datetime.utcnow().isoformat(),
                "action": "SELL",
                "symbol": symbol,
                "qty": qty,
                "status": result.get("status", "pending")
            })
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_orders(self, status: str = "all") -> List[Dict]:
        """Get order history"""
        if not self.is_configured():
            return self.trade_history
        try:
            resp = requests.get(
                f"{self.base_url}/v2/orders",
                headers=self._headers(),
                params={"status": status},
                timeout=10
            )
            return resp.json()
        except:
            return self.trade_history
    
    def watch_prices(self) -> Dict:
        """Get prices for all watched symbols"""
        prices = {}
        for symbol in self.watchlist:
            prices[symbol] = self.get_price(symbol)
            time.sleep(0.5)  # Rate limit
        return prices
    
    def add_to_watchlist(self, symbol: str) -> Dict:
        """Add symbol to watchlist"""
        symbol = symbol.upper()
        if symbol not in self.watchlist:
            self.watchlist.append(symbol)
        return {"watchlist": self.watchlist}
    
    def remove_from_watchlist(self, symbol: str) -> Dict:
        """Remove symbol from watchlist"""
        symbol = symbol.upper()
        if symbol in self.watchlist:
            self.watchlist.remove(symbol)
        return {"watchlist": self.watchlist}
    
    def enable_auto_trade(self, strategy: str = "momentum", params: Dict = None) -> Dict:
        """Enable automated trading"""
        self.auto_trade_enabled = True
        return {
            "status": "enabled",
            "strategy": strategy,
            "watchlist": self.watchlist,
            "params": params or {}
        }
    
    def disable_auto_trade(self) -> Dict:
        """Disable automated trading"""
        self.auto_trade_enabled = False
        return {"status": "disabled"}
    
    def _momentum_strategy(self, symbol: str, price_data: Dict) -> Optional[str]:
        """Buy when price is rising"""
        # Simplified - real implementation would use technical indicators
        return None
    
    def _dip_buy_strategy(self, symbol: str, price_data: Dict) -> Optional[str]:
        """Buy on dips"""
        return None
    
    def _scalp_strategy(self, symbol: str, price_data: Dict) -> Optional[str]:
        """Quick in-and-out trades"""
        return None
    
    def run_auto_trade_cycle(self) -> List[Dict]:
        """One cycle of auto-trading"""
        if not self.auto_trade_enabled:
            return []
        
        actions = []
        prices = self.watch_prices()
        
        for symbol, price_info in prices.items():
            # Simple mock logic for now
            price = price_info.get("price", 0)
            if price > 0 and random.random() < 0.1:  # 10% chance to trade
                # Mock trade decision
                action = random.choice(["buy", "sell"])
                actions.append({
                    "symbol": symbol,
                    "action": action,
                    "price": price,
                    "time": datetime.utcnow().isoformat(),
                    "note": "Auto-trade (mock)"
                })
        
        return actions
    
    def get_trade_history(self) -> List[Dict]:
        return self.trade_history
    
    def get_portfolio_value(self) -> Dict:
        """Calculate total portfolio value"""
        positions = self.get_positions()
        total = 0.0
        for pos in positions:
            total += float(pos.get("market_value", 0))
        
        account = self.get_account()
        cash = float(account.get("cash", 0)) if isinstance(account, dict) else 0
        
        return {
            "positions_value": total,
            "cash": cash,
            "total": total + cash,
            "positions_count": len(positions)
        }

trader = TradingEngine()
