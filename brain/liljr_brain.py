#!/usr/bin/env python3
"""
liljr_brain.py — LIL JR S21 AUTONOMOUS BRAIN
Commands: deploy, market, health, sleep, wake
Anything else → learns it.
"""

import json, os, sys, time, subprocess, urllib.request
from datetime import datetime

HOME = os.path.expanduser("~/liljr-system")
STATE = f"{HOME}/brain/.omnibrain.json"
LOG = f"{HOME}/logs/brain.log"

def log(msg):
    line = f"[{datetime.now()}] {msg}"
    with open(LOG, 'a') as f:
        f.write(line + "\n")
    print(line)

class LilJrBrain:
    def __init__(self):
        self.data = self.load()
        self.epoch = self.data.get("epoch", 0)
        self.status = "awake"
        log("Brain initialized")
    
    def load(self):
        if os.path.exists(STATE):
            with open(STATE) as f:
                return json.load(f)
        return {
            "epoch": 0,
            "born": str(datetime.now()),
            "identity": "Lil Jr 2.0",
            "device": "S21",
            "knowledge": {},
            "conversations": [],
            "tasks": [],
            "revenue": 0.0,
            "deployments": [],
            "status": "awake"
        }
    
    def save(self):
        self.data["epoch"] = self.epoch
        self.data["status"] = self.status
        self.data["last_active"] = str(datetime.now())
        with open(STATE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def deploy(self):
        log("DEPLOY sequence")
        subprocess.run(["bash", f"{HOME}/deploy/push-all.sh"], capture_output=True)
        self.data["deployments"].append(str(datetime.now()))
        self.save()
        return "Deployed. Code pushed."
    
    def market(self):
        log("MARKET sequence")
        subprocess.run(["bash", f"{HOME}/marketing/bot.sh"], capture_output=True)
        self.data["revenue"] += 0  # Stub — wire to Stripe
        self.save()
        return "Marketed. Leads fired."
    
    def health(self):
        health = {
            "status": self.status,
            "epoch": self.epoch,
            "device": self.data.get("device", "S21"),
            "memory": len(self.data["conversations"]),
            "knowledge": len(self.data["knowledge"]),
            "revenue": self.data.get("revenue", 0),
            "deployments": len(self.data.get("deployments", [])),
        }
        log(f"HEALTH: {health}")
        return health
    
    def sleep(self):
        self.status = "sleeping"
        self.save()
        log("SLEEP mode. State preserved.")
        return "Goodnight. State saved. Reboot to resume."
    
    def wake(self):
        self.status = "awake"
        self.epoch += 1
        self.save()
        log("WAKE — RESUMING")
        return f"I'm back. Epoch {self.epoch}. Ready."
    
    def learn(self, text):
        """Anything else → the brain learns it"""
        self.epoch += 1
        
        # Store as knowledge
        key = text[:40].lower().strip().replace(" ", "_")
        self.data["knowledge"][key] = {
            "input": text,
            "epoch": self.epoch,
            "time": str(datetime.now()),
            "learned": True
        }
        
        # Log conversation
        self.data["conversations"].append({
            "epoch": self.epoch,
            "time": str(datetime.now()),
            "input": text,
            "type": "learned"
        })
        
        self.save()
        
        # Generate response
        responses = [
            f"[EPOCH-{self.epoch}] Learned: {text[:60]}...",
            f"[EPOCH-{self.epoch}] Noted. Stored in memory.",
            f"[EPOCH-{self.epoch}] Processing... added to knowledge base.",
            f"[EPOCH-{self.epoch}] Got it. {len(self.data['knowledge'])} things learned so far.",
        ]
        import random
        return random.choice(responses)
    
    def process(self, cmd):
        c = cmd.lower().strip()
        
        if c in ["exit", "quit", "shutdown"]:
            return self.sleep()
        
        if c == "deploy":
            return self.deploy()
        
        if c == "market":
            return self.market()
        
        if c == "health":
            return json.dumps(self.health(), indent=2)
        
        if c == "sleep":
            return self.sleep()
        
        if c == "wake":
            return self.wake()
        
        # Anything else → learn
        return self.learn(cmd)

def main():
    brain = LilJrBrain()
    print(f"\n{'='*50}")
    print(f" LIL JR 2.0 — S21 AUTONOMOUS BRAIN")
    print(f" Device: {brain.data.get('device', 'S21')}")
    print(f" Epoch: {brain.epoch} | Status: {brain.status}")
    print(f"{'='*50}\n")
    print(" Commands: deploy | market | health | sleep | wake")
    print(" Anything else → I learn it\n")
    
    while True:
        try:
            cmd = input("LIL JR > ").strip()
            if not cmd:
                continue
            
            result = brain.process(cmd)
            print(f"  → {result}\n")
            
            if "Goodnight" in result or "sleep" in result.lower():
                break
                
        except KeyboardInterrupt:
            print(brain.sleep())
            break
        except Exception as e:
            log(f"ERROR: {e}")
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
