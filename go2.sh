#!/bin/bash
# go2.sh — ONE COMMAND. Kill everything. Start fresh. Just talk.

echo "🔪 Killing all LilJR processes..."
pkill -9 -f "python.*liljr" 2>/dev/null
pkill -9 -f "termux-speech" 2>/dev/null
pkill -9 -f "termux-tts" 2>/dev/null
sleep 2

echo "📥 Pulling latest..."
cd ~/liljr-autonomous
git pull origin main 2>/dev/null

echo "📋 Copying files..."
cp liljr_conversational.py ~/liljr_conversational.py
cp liljr_fullvoice.py ~/liljr_fullvoice.py
cp liljr_phone_control.py ~/liljr_phone_control.py 2>/dev/null
cp server_v8.py ~/server_v8.py 2>/dev/null

echo "🚀 Starting server..."
python3 ~/server_v8.py > ~/server.log 2>&1 &
sleep 5

echo "⚡ Starting LilJR..."
echo ""
echo "SAY: 'yo junior' to wake up"
echo "SAY: 'that's enough' to stop"
echo ""

python3 ~/liljr_conversational.py
