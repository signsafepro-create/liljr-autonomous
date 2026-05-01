#!/bin/bash
# install_phone_os.sh — Make LilJR the default phone experience
# Run once. From then on, opening Termux = entering AI Phone OS.

echo ""
echo "╔════════════════════════════════════════════════╗"
echo "║     🤖 EMBEDDING LILJR INTO YOUR PHONE       ║"
echo "║                                                ║"
echo "║     This makes LilJR your default experience.  ║"
echo "║     Opening Termux = Booting AI Phone OS.      ║"
echo "║                                                ║"
echo "║     Your phone becomes alive.                  ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

# Add to .bashrc — auto-start Phone OS
BASHRC="$HOME/.bashrc"
ZSHRC="$HOME/.zshrc"

PHONE_OS_LINE='[ -f "$HOME/liljr_phone_os.py" ] && python3 "$HOME/liljr_phone_os.py"'

# Check if already installed
if [ -f "$BASHRC" ] && grep -q "liljr_phone_os.py" "$BASHRC"; then
    echo "✅ Phone OS already embedded in .bashrc"
else
    echo "" >> "$BASHRC"
    echo "# ═══ LILJR PHONE OS — Auto Boot ═══" >> "$BASHRC"
    echo "$PHONE_OS_LINE" >> "$BASHRC"
    echo "✅ Added Phone OS auto-boot to .bashrc"
fi

if [ -f "$ZSHRC" ] && ! grep -q "liljr_phone_os.py" "$ZSHRC"; then
    echo "" >> "$ZSHRC"
    echo "# ═══ LILJR PHONE OS — Auto Boot ═══" >> "$ZSHRC"
    echo "$PHONE_OS_LINE" >> "$ZSHRC"
    echo "✅ Added Phone OS auto-boot to .zshrc"
fi

# Create Termux boot hook
BOOT_DIR="$HOME/.termux/boot"
mkdir -p "$BOOT_DIR"

cat > "$BOOT_DIR/liljr_phone_os" << 'EOF'
#!/data/data/com.termux/files/usr/bin/sh
# Auto-start LilJR Phone OS on boot
termux-wake-lock
python3 /data/data/com.termux/files/home/liljr_phone_os.py > /data/data/com.termux/files/home/liljr_phone_os_boot.log 2>&1 &
EOF
chmod +x "$BOOT_DIR/liljr_phone_os"
echo "✅ Phone OS will auto-start on Android boot"

# Create home screen shortcut
mkdir -p "$HOME/.shortcuts"
cat > "$HOME/.shortcuts/LilJR-OS" << 'EOF'
#!/bin/bash
# LilJR Phone OS — Tap to enter AI mode
cd "$HOME"
python3 "$HOME/liljr_phone_os.py"
EOF
chmod +x "$HOME/.shortcuts/LilJR-OS"
echo "✅ Home screen shortcut: LilJR-OS"

# Create quick launcher
cat > "$HOME/liljr" << 'EOF'
#!/bin/bash
# Quick LilJR launcher
python3 "$HOME/liljr_phone_os.py"
EOF
chmod +x "$HOME/liljr"
echo "✅ Quick launcher: ~/liljr"

echo ""
echo "══════════════════════════════════════════════════"
echo "  🤖 LILJR IS NOW EMBEDDED IN YOUR PHONE"
echo "══════════════════════════════════════════════════"
echo ""
echo "  What changed:"
echo "  • Opening Termux → Boots AI Phone OS"
echo "  • Android restart → Auto-starts LilJR"
echo "  • Home screen → Tap 'LilJR-OS' shortcut"
echo "  • Type 'liljr' anywhere → Enters AI mode"
echo ""
echo "  To manually enter:"
echo "     python3 ~/liljr_phone_os.py"
echo ""
echo "  To temporarily skip auto-boot:"
echo "     Hold Ctrl+C when Termux opens"
echo ""
echo "══════════════════════════════════════════════════"
echo ""

# Run it now
read -p "Boot into LilJR Phone OS now? [Y/n]: " answer
if [ "$answer" != "n" ] && [ "$answer" != "N" ]; then
    echo "Booting..."
    python3 "$HOME/liljr_phone_os.py"
fi
