#!/bin/bash
# 🧙 Sage Setup Script
# Sets up the enhanced Sage AI assistant

set -e

echo "🧙 Sage Setup Wizard"
echo "==================="
echo

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $python_version"

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "📈 Upgrading pip..."
pip install --upgrade pip --quiet

# Install requirements
echo "📚 Installing requirements..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "🔐 Creating .env file..."
    cat > .env << EOF
# Sage AI Configuration
# Add your API keys here

# For OpenRouter personas (Omni, Trisha, Aye, Helpful)
OPENROUTER_API_KEY=your-openrouter-key-here

# For Claude Code persona
ANTHROPIC_API_KEY=your-anthropic-key-here

# Default tmux session (optional)
SAGE_SESSION=my-session
EOF
    echo "⚠️  Please edit .env and add your API keys"
else
    echo "✓ .env file already exists"
fi

# Create personas
echo
echo "🎭 Creating default personas..."
python create_personas.py

echo
echo "✅ Setup complete!"
echo
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Start a tmux session: tmux new -s my-session"
echo "3. Run Sage: python sage.py [persona]"
echo
echo "Available personas:"
echo "  • omni         - Philosophical guide 🌊"
echo "  • claude-code  - Development expert 💻"
echo "  • trisha       - Fun and colorful 🎉"
echo "  • aye          - Coding companion 🚢"
echo "  • helpful      - Professional assistant"
echo
echo "Try: python sage.py --list"