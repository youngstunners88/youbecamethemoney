# ZO_SETUP.md — Zo Computer Bridge Setup Playbook

## Overview
The Zo Computer is Garcia's infrastructure command center. This guide enables Claude Code to control Zo via the MCP bridge (8 tools: bash, postgres, hermes_chat, deploy, logs, health, restart, config).

**Timeline:** 15 minutes  
**Prerequisites:** SSH access to Zo, Python 3.8+, PostgreSQL client, existing Ramsees setup

---

## Phase 1: Install MCP Bridge

### 1.1 Create ~/.zo/.env (connection config)
```bash
mkdir -p ~/.zo
cat > ~/.zo/.env << 'EOF'
ZO_HOST=zo.garcia-ramsees.local
ZO_PORT=22
ZO_USER=deploy
ZO_DB_HOST=zo.garcia-ramsees.local
ZO_DB_NAME=garcia_ramsees
ZO_DB_USER=postgres
RAMSEES_API=https://detectable-clarita-casuistically.ngrok-free.dev
EOF
```

### 1.2 Verify SSH access to Zo
```bash
ssh -p 22 deploy@zo.garcia-ramsees.local "echo 'Zo access verified'"
```

Expected output: `Zo access verified`

### 1.3 Test PostgreSQL connectivity
```bash
psql -h zo.garcia-ramsees.local -U postgres -d garcia_ramsees -c "SELECT COUNT(*) FROM leads;"
```

---

## Phase 2: Register MCP Server

### 2.1 Register in ~/.mcp.json
Already created at `/home/user/.mcp.json`. Contains:
- Tool definitions (zo_bash, zo_postgres, zo_hermes_chat, etc.)
- Connection env vars from ~/.zo/.env
- Auto-start on Claude Code launch

### 2.2 Restart Claude Code
```bash
# In Claude Code terminal:
/stop
# Close and reopen Claude Code
```

### 2.3 Verify tools are loaded
```bash
# In Claude Code, run:
zo_bash("echo 'bridge working'")
```

Expected output:
```json
{
  "status": "success",
  "output": "bridge working\n",
  "error": "",
  "exit_code": 0
}
```

---

## Phase 3: Test All 8 Tools

### 3.1 zo_bash — Command execution
```bash
zo_bash("uname -a")
```

### 3.2 zo_postgres — Database queries
```bash
zo_postgres("SELECT id, name, warmth_score FROM leads LIMIT 5;")
```

### 3.3 zo_hermes_chat — Message to Ramsees
```bash
zo_hermes_chat("Test message from Zo bridge", "normal")
```

Expected: POST to `{RAMSEES_API}/api/ramsees-message` with status 200

### 3.4 zo_deploy — Service deployment
```bash
zo_deploy("ramsees-agent", "1.2.3")
```

Pulls image, updates docker-compose, restarts service.

### 3.5 zo_logs — View service logs
```bash
zo_logs("ramsees-agent", 100)
```

### 3.6 zo_health — System health check
```bash
zo_health()
```

Returns CPU, memory, disk, running services.

### 3.7 zo_restart — Restart service
```bash
zo_restart("ramsees-agent")
```

### 3.8 zo_config — Manage configuration
```bash
zo_config("get", "api_port")
zo_config("set", "api_port", "5001")
```

---

## Phase 4: Systemd Service (Auto-Start)

### 4.1 Create systemd unit file
```bash
cat > /etc/systemd/system/zo-bridge.service << 'EOF'
[Unit]
Description=Zo Computer MCP Bridge
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/home/user/youbecamethemoney
ExecStart=/usr/bin/python3 mcp-server.py
Restart=always
RestartSec=10
Environment="ZO_HOST=zo.garcia-ramsees.local"
Environment="ZO_PORT=22"
Environment="ZO_USER=deploy"

[Install]
WantedBy=multi-user.target
EOF
```

### 4.2 Enable and start service
```bash
sudo systemctl enable zo-bridge
sudo systemctl start zo-bridge
sudo systemctl status zo-bridge
```

### 4.3 View service logs
```bash
journalctl -u zo-bridge -f
```

---

## Phase 5: Integration with Ramsees

### 5.1 How the bridge works
```
embark.html (new lead)
    ↓
demo-server.py (receives POST)
    ↓
PostgreSQL (stores lead)
    ↓
Ramsees agent (monitors DB)
    ↓
zo_hermes_chat tool (routes priority messages)
    ↓
Ramsees API endpoint
    ↓
NTFY notification → Garcia's phone
```

### 5.2 Example: Hot lead workflow
1. New lead created in embark.html with warmth_score=75
2. Demo-server inserts into PostgreSQL
3. Ramsees detects warmth >= 70
4. Claude Code can now:
   ```bash
   zo_hermes_chat("🔥 HOT LEAD: Smith Family - immediate follow-up recommended", "high")
   ```
5. Message routed to Ramsees → NTFY notification

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `SSH connection refused` | Check Zo host/port in ~/.zo/.env; verify firewall rules |
| `PostgreSQL auth failed` | Verify db_user/db_host; check ~/.pgpass |
| `zo_hermes_chat timeout` | Check RAMSEES_API URL; verify ngrok tunnel is active |
| `Tool not found` | Restart Claude Code; verify ~/.mcp.json registered |
| `Systemd service fails` | Check user permissions; ensure python3 is in PATH |

---

## Quick Reference: 8 Tools

| Tool | Purpose | Example |
|------|---------|---------|
| `zo_bash` | Execute commands | `zo_bash("systemctl status ramsees")` |
| `zo_postgres` | Query database | `zo_postgres("SELECT * FROM leads")` |
| `zo_hermes_chat` | Message Ramsees | `zo_hermes_chat("Sync needed", "high")` |
| `zo_deploy` | Deploy service | `zo_deploy("ramsees-agent", "2.0.0")` |
| `zo_logs` | View logs | `zo_logs("ramsees-agent", 50)` |
| `zo_health` | System status | `zo_health()` |
| `zo_restart` | Restart service | `zo_restart("ramsees-agent")` |
| `zo_config` | Get/set config | `zo_config("get", "port")` |

---

## Files Created

- ✅ `/home/user/youbecamethemoney/mcp-server.py` — 150-line MCP bridge
- ✅ `~/.mcp.json` — MCP registration
- ✅ `/etc/systemd/system/zo-bridge.service` — Auto-start unit (run Phase 4.1)
- ✅ `ZO_SETUP.md` — This file

## Next Steps

1. **Load MCP** → Run Phase 2 (restart Claude Code)
2. **Test bridge** → Run Phase 3 (verify all 8 tools)
3. **Deploy systemd** → Run Phase 4 (auto-start on reboot)
4. **Integration test** → Create lead in embark.html, watch Zo bridge route it

---

**Session:** 8  
**Created:** 2026-04-16  
**Status:** Ready for testing
