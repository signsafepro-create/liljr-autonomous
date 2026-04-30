#!/bin/bash
# tor_bounce.sh — Rotate Tor circuits every 10 minutes for IP anonymity

echo "🧅 LILJR TOR BOUNCER"
echo "===================="

# Check tor
if ! command -v tor >/dev/null 2>&1; then
    echo "Installing tor..."
    pkg install tor -y 2>/dev/null || apt-get install tor -y 2>/dev/null
fi

# Start tor if not running
if ! pgrep -x "tor" > /dev/null 2>&1; then
    echo "Starting tor..."
    tor &
    sleep 5
fi

# Verify tor is working
if curl -s --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip 2>/dev/null | grep -q "IsTor"; then
    echo "✅ Tor is active"
else
    echo "⚠️ Tor may not be routing yet. Waiting..."
    sleep 10
fi

# Bouncer loop
echo "🔄 Rotating circuits every 10 minutes..."
echo "Ctrl+C to stop"
while true; do
    # Signal tor to get new circuit
    killall -HUP tor 2>/dev/null
    echo "[$(date '+%H:%M:%S')] Circuit rotated"
    
    # Show current IP via tor
    IP=$(curl -s --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip 2>/dev/null | grep -o '"IP":"[^"]*"' | cut -d'"' -f4)
    if [ -n "$IP" ]; then
        echo "[$(date '+%H:%M:%S')] Current IP: $IP"
    fi
    
    sleep 600
done
