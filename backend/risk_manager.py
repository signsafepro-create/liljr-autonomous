"""
RISK MANAGEMENT
Prevents catastrophic losses, enforces limits
"""
import os
from typing import Dict, Optional
from datetime import datetime

class RiskManager:
    def __init__(self):
        self.max_daily_loss = float(os.getenv("MAX_DAILY_LOSS", "100.00"))  # $100 max daily loss
        self.max_position_size = float(os.getenv("MAX_POSITION_SIZE", "1000.00"))  # $1000 per position
        self.max_positions = int(os.getenv("MAX_POSITIONS", "5"))  # Max 5 open positions
        self.daily_trades = 0
        self.daily_loss = 0.0
        self.daily_profit = 0.0
        self.last_reset = datetime.utcnow().date()
        self.trade_log: list = []
    
    def _check_reset(self):
        today = datetime.utcnow().date()
        if today != self.last_reset:
            self.daily_trades = 0
            self.daily_loss = 0.0
            self.daily_profit = 0.0
            self.last_reset = today
    
    def can_trade(self, action: str, symbol: str, amount: float) -> Dict:
        self._check_reset()
        
        checks = []
        
        # Check daily loss limit
        if self.daily_loss >= self.max_daily_loss:
            checks.append({"rule": "daily_loss_limit", "passed": False, "message": f"Daily loss limit reached: ${self.daily_loss}"})
        
        # Check position size
        if amount > self.max_position_size:
            checks.append({"rule": "position_size", "passed": False, "message": f"Position ${amount} exceeds max ${self.max_position_size}"})
        
        # All checks must pass
        failed = [c for c in checks if not c["passed"]]
        
        if failed:
            return {
                "allowed": False,
                "reasons": failed,
                "suggestion": "Wait for conditions to improve or adjust risk settings"
            }
        
        return {"allowed": True, "checks": checks}
    
    def record_trade(self, action: str, symbol: str, amount: float, result: float):
        self._check_reset()
        self.daily_trades += 1
        if result < 0:
            self.daily_loss += abs(result)
        else:
            self.daily_profit += result
        
        self.trade_log.append({
            "time": datetime.utcnow().isoformat(),
            "action": action,
            "symbol": symbol,
            "amount": amount,
            "result": result
        })
    
    def get_status(self) -> Dict:
        self._check_reset()
        return {
            "daily_trades": self.daily_trades,
            "daily_loss": round(self.daily_loss, 2),
            "daily_profit": round(self.daily_profit, 2),
            "net_pnl": round(self.daily_profit - self.daily_loss, 2),
            "max_daily_loss": self.max_daily_loss,
            "max_position_size": self.max_position_size,
            "max_positions": self.max_positions,
            "last_reset": str(self.last_reset)
        }
    
    def get_trade_log(self) -> list:
        return self.trade_log[-50:]  # Last 50 trades

risk = RiskManager()
