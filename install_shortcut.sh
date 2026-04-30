#!/bin/bash
# install_shortcut.sh — Add LilJR to your home screen

echo "📱 Installing home screen shortcut..."

# Create shortcuts directory
mkdir -p ~/.shortcuts

# Copy jr.sh to shortcuts
cp ~/liljr-autonomous/jr.sh ~/.shortcuts/jr.sh
chmod +x ~/.shortcuts/jr.sh

# Also create a simple launcher
ln -sf ~/.shortcuts/jr.sh ~/.shortcuts/LilJR 2>/dev/null

echo "✅ Done!"
echo ""
echo "To add to home screen:"
echo "1. Long press empty space on home screen"
echo "2. Tap 'Widgets' or 'Shortcuts'"
echo "3. Find 'Termux:Widget'"
echo "4. Select 'LilJR' or 'jr.sh'"
echo "5. Place it on your screen"
echo ""
echo "Now just TAP the button → LilJR starts"
echo "Say 'Junior' → it wakes up"
echo "Say what you want → it does it"
echo "Say 'stop' → it sleeps"
