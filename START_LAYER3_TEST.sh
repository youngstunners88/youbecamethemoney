#!/bin/bash

# Layer 3 Testing Interface Startup Script

echo "=================================="
echo "Layer 3: Learning Engine"
echo "Testing Interface Startup"
echo "=================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q flask requests psycopg2-binary 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "⚠️  Some dependencies may not have installed, but that's OK"
fi

echo ""
echo "🚀 Starting Layer 3 Test Interface..."
echo ""
echo "════════════════════════════════════"
echo "Open your browser to:"
echo "👉 http://localhost:5001"
echo "════════════════════════════════════"
echo ""
echo "To stop, press Ctrl+C"
echo ""

# Run the test interface
cd "$(dirname "$0")" || exit
python3 optimization/layer3/test_interface.py
