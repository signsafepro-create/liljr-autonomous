#!/bin/bash
# setup_conversation.sh — Install LilJR Conversation Mode
# Just talk. No typing. Natural back-and-forth.

echo "🎙️ LILJR CONVERSATION SETUP"
echo "============================"
echo "You: Yo junior"
echo "JR:  Yo. What's up?"
echo "You: Open Snapchat"
echo "JR:  Opening Snapchat"
echo "You: Take a pic"
echo "JR:  Got it"
echo ""
echo "No wake word repetition. 60-second conversation window."
echo ""

cd ~/liljr-autonomous 2>/dev/null || cd ~

# Pull latest
git pull origin main 2>/dev/null || echo "Using local files"

# Copy conversation files to home
cp liljr_conversation.py ~/liljr_conversation.py 2>/dev/null
cp liljr_conversation_daemon.py ~/liljr_conversation_daemon.py 2>/dev/null
cp liljr_phone_control.py ~/liljr_phone_control.py 2>/dev/null
cp liljr_relationship.py ~/liljr_relationship.py 2>/dev/null
cp liljr_android_soul.py ~/liljr_android_soul.py 2>/dev/null

echo "✅ Files installed"

# Add aliases
cat >> ~/.bashrc << 'EOF'

# LilJR Conversation Aliases
alias conv='python3 ~/liljr_conversation.py'
alias conv-start='python3 ~/liljr_conversation_daemon.py start'
alias conv-stop='python3 ~/liljr_conversation_daemon.py stop'
alias conv-status='python3 ~/liljr_conversation_daemon.py status'
EOF

echo "✅ Aliases added: conv, conv-start, conv-stop, conv-status"

# Start conversation daemon
echo ""
echo "🚀 Starting conversation daemon..."
python3 ~/liljr_conversation_daemon.py start

# Start server if not running
if ! curl -s --max-time 1 http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "Starting server..."
    nohup python3 ~/server_v8.py > ~/server.log 2>&1 &
    sleep 3
fi

# Notification
termux-notification \
  --title "LilJR Conversation" \
  --content "Just say 'yo junior' and start talking" \
  --priority high

echo ""
echo "=============================="
echo "✅ LILJR CONVERSATION READY"
echo "=============================="
echo ""
echo "HOW TO USE:"
echo "  1. Make sure volume is UP"
echo "  2. Make sure Termux:API has microphone permission"
echo "  3. Say out loud: 'yo junior' or 'hey junior'"
echo "  4. LilJR wakes up and talks back"
echo "  5. Keep talking. No need to repeat wake word."
echo "  6. Say 'quiet' or wait 60 seconds to sleep"
echo ""
echo "EXAMPLES:"
echo "  You: 'yo junior'"
echo "  JR:  'Yo. What's up?'"
echo "  You: 'open Snapchat'"
echo "  JR:  'Opening Snapchat'"
echo "  You: 'take a pic'"
echo "  JR:  'Got it'"
echo "  You: 'show me AAPL stock'"
echo "  JR:  'Opening AAPL chart'"
echo "  You: 'search AI news'"
echo "  JR:  'Searching'"
echo "  You: 'quiet'"
echo "  JR:  'Aight. Holler when you need me.'"
echo ""
echo "QUICK COMMANDS:"
echo "  conv            — Start interactive conversation"
echo "  conv-start      — Start background daemon"
echo "  conv-stop       — Stop daemon"
echo "  conv-status     — Check if running"
echo ""
echo "Say it now: 'yo junior'"
