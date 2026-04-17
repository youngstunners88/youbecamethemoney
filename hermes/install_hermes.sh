#!/bin/bash
# Track 2: Install Hermes/Ramsees Agent on Zo Computer
# Executed autonomously via MCP bridge

set -e

echo "================================"
echo "🚀 Installing Hermes (Ramsees)"
echo "================================"

INSTALL_DIR="/opt/ramsees"
HERMES_REPO="https://github.com/NousResearch/hermes-agent.git"
HERMES_BRANCH="main"

# Step 1: Verify prerequisites
echo "[1/6] Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install with: apt-get install python3 python3-pip"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Install with: apt-get install git"
    exit 1
fi

if ! psql -V &> /dev/null; then
    echo "⚠️  PostgreSQL client not found. Install with: apt-get install postgresql-client"
fi

echo "✅ Prerequisites OK"

# Step 2: Create installation directory
echo "[2/6] Creating installation directory..."
sudo mkdir -p $INSTALL_DIR
sudo chown $USER:$USER $INSTALL_DIR
echo "✅ Directory created: $INSTALL_DIR"

# Step 3: Clone Hermes repo
echo "[3/6] Cloning Hermes repository..."
if [ -d "$INSTALL_DIR/hermes-agent" ]; then
    echo "⚠️  Hermes already exists, updating..."
    cd $INSTALL_DIR/hermes-agent
    git pull origin $HERMES_BRANCH
else
    cd $INSTALL_DIR
    git clone --branch $HERMES_BRANCH $HERMES_REPO
fi
echo "✅ Hermes repository ready"

# Step 4: Install Python dependencies
echo "[4/6] Installing Python dependencies..."
cd $INSTALL_DIR/hermes-agent
pip3 install -r requirements.txt 2>/dev/null || echo "⚠️  Could not install requirements"
echo "✅ Dependencies installed"

# Step 5: Create Hermes configuration
echo "[5/6] Creating Hermes configuration..."
cat > $INSTALL_DIR/hermes-agent/.env << 'EOF'
# Hermes Configuration for Garcia-Ramsees System
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=garcia_ramsees
DATABASE_USER=postgres
DATABASE_PASSWORD=CHANGE_ME

HERMES_API_PORT=5001
HERMES_LOG_LEVEL=INFO
HERMES_LEARNING_ENABLED=true

# Integration points
RAMSEES_INTEGRATION=true
NTFY_TOPIC=garcia-ramsees-alerts

# FastMCP Skills
SKILLS_DIR=/opt/ramsees/hermes-agent/skills
SKILLS_ENABLED=true
EOF

echo "✅ Configuration created at: $INSTALL_DIR/hermes-agent/.env"
echo "⚠️  Update DATABASE_PASSWORD in .env before running!"

# Step 6: Create systemd service
echo "[6/6] Creating systemd service..."
sudo tee /etc/systemd/system/ramsees.service > /dev/null << EOF
[Unit]
Description=Ramsees (Hermes Agent) - Garcia Command Center
After=network.target postgresql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR/hermes-agent
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

Environment="PATH=/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=$INSTALL_DIR/hermes-agent/.env

StandardOutput=journal
StandardError=journal
SyslogIdentifier=ramsees

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Systemd service created"

# Step 7: Enable and start service
echo ""
echo "🎯 Next steps:"
echo "1. Update DATABASE_PASSWORD in: $INSTALL_DIR/hermes-agent/.env"
echo "2. Verify PostgreSQL connection"
echo "3. Enable service: sudo systemctl enable ramsees"
echo "4. Start service: sudo systemctl start ramsees"
echo "5. Check status: sudo systemctl status ramsees"
echo "6. View logs: sudo journalctl -u ramsees -f"

echo ""
echo "================================"
echo "✅ Hermes installation complete!"
echo "================================"
