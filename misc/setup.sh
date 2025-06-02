#!/bin/bash

# Fenrir Discord Bot Setup Script
# This script helps set up the Discord bot environment

set -e

echo "🐺 Fenrir Discord Bot Setup Script"
echo "=================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if we're in the right directory
if [ ! -f "bot.py" ]; then
    echo "❌ Please run this script from the /home/nl/Projects/DiscordBot/Claude-Bot directory"
    exit 1
fi

echo "✅ Found bot.py - in correct directory"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your Discord bot token"
    echo "⚠️  Set ENABLE_HOMELAB=true when you want homelab features"
else
    echo "✅ .env file already exists"
fi

# Create logs directory
if [ ! -d "logs" ]; then
    echo "📁 Creating logs directory..."
    mkdir logs
else
    echo "✅ Logs directory already exists"
fi

echo ""
echo "🎉 Fenrir setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Discord bot token"
echo "2. Fenrir will start with homelab module DISABLED by default"
echo "3. To enable homelab features later:"
echo "   - Set ENABLE_HOMELAB=true in .env"
echo "   - Deploy the homelab API server"
echo "   - Restart Fenrir"
echo "4. Run Fenrir with: python bot.py"
echo ""
echo "For more information, see README.md"