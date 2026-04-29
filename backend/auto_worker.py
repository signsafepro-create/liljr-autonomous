"""
AUTO WORKER
Runs 24/7 background tasks: build, deploy, trade, monitor
"""
import os
import time
import json
import threading
from datetime import datetime
from typing import Dict, List, Callable

class AutoWorker:
    def __init__(self):
        self.running = False
        self.thread = None
        self.tasks: Dict[str, Dict] = {}
        self.log: List[Dict] = []
        self.interval = int(os.getenv("WORKER_INTERVAL", "60"))  # Default 60 seconds
        self.callbacks: Dict[str, Callable] = {}
    
    def register_task(self, name: str, callback: Callable, interval: int = None):
        """Register a recurring task"""
        self.tasks[name] = {
            "callback": callback,
            "interval": interval or self.interval,
            "last_run": 0,
            "run_count": 0
        }
    
    def start(self) -> Dict:
        """Start the worker loop"""
        if self.running:
            return {"status": "already_running"}
        
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        
        self._log("worker_started", {"interval": self.interval})
        return {"status": "started", "tasks": list(self.tasks.keys())}
    
    def stop(self) -> Dict:
        """Stop the worker"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        self._log("worker_stopped", {})
        return {"status": "stopped"}
    
    def _loop(self):
        """Main worker loop"""
        while self.running:
            current_time = time.time()
            
            for name, task in self.tasks.items():
                if current_time - task["last_run"] >= task["interval"]:
                    try:
                        result = task["callback"]()
                        task["last_run"] = current_time
                        task["run_count"] += 1
                        self._log(f"task_{name}", {"result": str(result)[:100]})
                    except Exception as e:
                        self._log(f"task_{name}_error", {"error": str(e)})
            
            time.sleep(1)  # Check every second
    
    def _log(self, action: str, data: Dict):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "data": data
        }
        self.log.append(entry)
        # Keep log manageable
        if len(self.log) > 1000:
            self.log = self.log[-500:]
    
    def get_status(self) -> Dict:
        return {
            "running": self.running,
            "tasks": {
                name: {
                    "interval": task["interval"],
                    "last_run": task["last_run"],
                    "run_count": task["run_count"]
                }
                for name, task in self.tasks.items()
            },
            "log_count": len(self.log),
            "recent_logs": self.log[-10:]
        }
    
    def get_logs(self, limit: int = 50) -> List[Dict]:
        return self.log[-limit:]

worker = AutoWorker()
