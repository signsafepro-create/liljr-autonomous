#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# TERMUX SETUP — Pure Python (no Rust, no pydantic-core)
# Run: cd ~ && bash setup_termux.sh
# ═══════════════════════════════════════════════════════════════

echo "🚀 LilJR Termux Setup (Pure Python)"
echo "===================================="

# MUST cd home first — old directory gets deleted
cd ~ || exit 1

# 1. Remove old repo
echo "Removing old repo..."
rm -rf liljr-autonomous

# 2. Clone fresh
echo "Cloning..."
git clone https://github.com/signsafepro-create/liljr-autonomous.git

# 3. Install deps — PURE PYTHON ONLY (no Rust compilation)
echo "Installing pure-Python deps..."
cd ~/liljr-autonomous/backend

# Use pre-built wheels only, no compilation
pip install \
  fastapi==0.95.2 \
  uvicorn==0.22.0 \
  requests==2.31.0 \
  python-dotenv==1.0.0 \
  flask==3.0.0 \
  flask-cors==4.0.0 \
  --no-deps 2>&1 | tail -5

# Install starlette and pydantic v1 separately (pure Python)
pip install \
  starlette==0.27.0 \
  pydantic==1.10.13 \
  typing-extensions==4.6.0 \
  anyio==3.7.0 \
  idna==3.4 \
  sniffio==1.3.0 \
  click==8.1.0 \
  h11==0.14.0 \
  markupsafe==2.1.0 \
  jinja2==3.1.0 \
  werkzeug==2.3.0 \
  itsdangerous==2.1.0 \
  certifi==2023.0 \
  charset-normalizer==3.1.0 \
  urllib3==2.0.0 \
  2>&1 | tail -5

echo ""
echo "✅ Setup complete"
echo ""
echo "Start server:"
echo "  cd ~/liljr-autonomous/backend && python server.py"
echo ""
echo "Or use lj:"
echo "  bash ~/lj start"
