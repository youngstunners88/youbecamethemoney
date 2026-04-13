#!/bin/bash

# Layer 3 Demo - Simple script for Mr Garcia to see it working

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Layer 3: Learning Engine - Demo for Mr Garcia            ║"
echo "║  Self-improving system proof of concept                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Install dependencies silently if needed
pip install -q flask requests psycopg2-binary 2>/dev/null

# Run the demo skill
echo "🚀 Running learning cycle..."
echo ""

python3 ~/.kimi/skills/layer3-demo/layer3_demo.py

# Show where the report is
echo ""
echo "📂 Opening the visual report..."
echo ""

REPORT="/tmp/layer3_demo_report.html"

if [ -f "$REPORT" ]; then
    echo "✅ Report generated at: $REPORT"
    echo ""
    echo "To view the report:"
    echo "  • Copy this path: $REPORT"
    echo "  • Open in your browser"
    echo ""
    echo "Or, if you have 'open' command:"
    open "$REPORT" 2>/dev/null || echo "  • Run: open $REPORT"
else
    echo "❌ Report not found"
    exit 1
fi
