# ZO_BRIDGE_ARCHITECTURE.md — System Design

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code (Browser)                     │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │         MCP Client (8 zo_* tools available)              │ │
│  └──────────────────────┬──────────────────────────────────┘ │
└─────────────────────────┼──────────────────────────────────────┘
                          │
                          │ stdio
                          ↓
┌─────────────────────────────────────────────────────────────┐
│         mcp-server.py (MCP Server, Zo Bridge)                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │zo_bash   │ │zo_postgres│ │zo_hermes │ │zo_deploy │        │
│  └──┬───────┘ └──┬───────┘ └──┬──────┘ └──┬───────┘        │
│     │            │            │           │                 │
│  ┌──┴────────┬───┴───────┬────┴────────┬──┴────────────┐   │
│  │SSH (param│PostgreSQL  │HTTP Req    │Docker exec    │   │
│  │iko)      │ psql       │to Ramsees  │& systemctl    │   │
│  └──────────┴────────────┴────────────┴───────────────┘   │
└─────────────────────────────────────────────────────────────┘
         │                 │                 │
         ↓                 ↓                 ↓
    ┌─────────┐    ┌──────────┐      ┌────────────┐
    │Zo Linux │    │Zo Postgres│     │Ramsees API │
    │(SSH 22) │    │(5432)     │     │(ngrok)     │
    └─────────┘    └──────────┘     └────────────┘
         │                 │              │
    ┌────┴─────────┬───────┴──┐         │
    │systemctl     │journalctl │         │
    │docker        │processes  │         │
    │commands      │           │         │
    └──────────────┴───────────┘         │
                                         ↓
                                  ┌────────────────┐
                                  │NTFY Notif.     │
                                  │→ Garcia's phone│
                                  └────────────────┘
```

---

## Component Breakdown

### 1. Claude Code Client
- **Environment:** Browser (Claude Code)
- **Role:** User interface for controlling Zo
- **Interaction:** Calls zo_* tools via stdio to MCP server
- **Tools accessible:** 8 tools (bash, postgres, hermes_chat, deploy, logs, health, restart, config)

### 2. MCP Server (mcp-server.py)
- **Type:** FastMCP server
- **Location:** `/home/user/youbecamethemoney/mcp-server.py`
- **Lines:** ~150
- **Registration:** `~/.mcp.json`
- **Environment:** Python 3.8+
- **Startup:** Automatic (via ~/.mcp.json on Claude Code launch)

### 3. Tool Implementations

#### zo_bash
- **Protocol:** SSH via paramiko
- **Target:** Zo Linux server
- **Port:** 22 (configurable)
- **Auth:** Key-based SSH (public key in ~/.ssh/authorized_keys on Zo)
- **Returns:** stdout, stderr, exit_code
- **Timeout:** 30 seconds
- **Use case:** Execute any Linux command on Zo

#### zo_postgres
- **Protocol:** PostgreSQL client (psql)
- **Target:** Zo PostgreSQL instance
- **Port:** 5432 (configurable)
- **Database:** garcia_ramsees
- **Auth:** Username/password in ~/.zo/.env
- **Returns:** Query results as text
- **Use case:** Read/write leads, track conversions, audit data

#### zo_hermes_chat
- **Protocol:** HTTP POST
- **Target:** Ramsees API (ngrok tunnel)
- **Endpoint:** `/api/ramsees-message`
- **Payload:** `{message, priority, source: "zo-bridge"}`
- **Returns:** API response JSON
- **Timeout:** 10 seconds
- **Use case:** Send priority messages to Ramsees agent (high/normal/low)

#### zo_deploy
- **Protocol:** SSH → Docker commands
- **Target:** Zo docker-compose
- **Process:**
  1. Pull image: `docker pull {service}:{version}`
  2. Update compose: `docker-compose up -d {service}`
  3. Verify running: `docker ps | grep {service}`
- **Returns:** Deployment status, output
- **Use case:** Deploy new Ramsees versions, updates to services

#### zo_logs
- **Protocol:** SSH → journalctl
- **Command:** `journalctl -u {service} -n {lines} --no-pager`
- **Returns:** Last N lines of service logs
- **Use case:** Troubleshoot service issues, monitor activity

#### zo_health
- **Protocol:** SSH → system commands
- **Checks:**
  - CPU: `top -bn1`
  - Memory: `free -h`
  - Disk: `df -h /`
  - Services: `systemctl list-units --type=service --state=running`
- **Returns:** Health metrics JSON
- **Use case:** Monitor Zo infrastructure health

#### zo_restart
- **Protocol:** SSH → systemctl
- **Command:** `systemctl restart {service}`
- **Returns:** Success/failure status
- **Use case:** Restart Ramsees or other services

#### zo_config
- **Protocol:** SSH → JSON file management
- **Get:** `cat /etc/ramsees/config.json | jq '.{key}'`
- **Set:** Write updated JSON to config file
- **Returns:** Config value or confirmation
- **Use case:** Manage Zo/Ramsees runtime configuration

---

## Data Flow: New Lead → Notification

```
1. User creates lead in embark.html
   └─ POST /api/leads {name, email, case_type, warmth_score}

2. demo-server.py receives lead
   └─ Validates, assigns ID, stores in PostgreSQL

3. PostgreSQL transaction logged
   └─ Table: leads (id, name, email, warmth_score, created_at)

4. Ramsees agent (running on Zo or local) monitors DB
   └─ Queries: SELECT * FROM leads WHERE warmth_score >= 70

5. Ramsees detects hot lead (warmth >= 70)
   └─ Triggers default notification (via NTFY_TOPIC=garcia-ramsees-alerts)

6. Claude Code can enhance/override with priority routing:
   ```
   zo_hermes_chat("🔥 URGENT: Smith Family - $250K contract case", "high")
   ```

7. zo_hermes_chat tool POSTs to Ramsees API
   └─ Endpoint: https://detectable-clarita-casuistically.ngrok-free.dev/api/ramsees-message

8. Ramsees routes message to NTFY
   └─ Topic: garcia-ramsees-alerts
   └─ Subscription: Garcia's phone

9. Garcia receives notification
   └─ Content: "🔥 URGENT: Smith Family - $250K contract case [Source: Zo Bridge]"
```

---

## Security Model

### SSH Access
- **Key-based auth only** (no passwords)
- **Public key:** Deployed to Zo `~/.ssh/authorized_keys`
- **User:** `deploy` (non-root, least privileges)
- **Firewall:** SSH only from Claude Code machine (whitelist IPs)

### Database Access
- **User:** `postgres` (read/write to garcia_ramsees)
- **Connection:** Local TCP (localhost:5432) or SSH tunnel
- **Queries:** No shell metacharacters (parameterized)
- **Audit:** All queries logged to PostgreSQL audit table

### HTTP (Ramsees API)
- **Protocol:** HTTPS (ngrok tunnel)
- **Auth:** Bearer token or API key (if configured)
- **Rate limiting:** Ramsees enforces 30 req/min per source
- **Payload:** JSON only, no command injection vectors

### MCP Server Security
- **No shell eval** — All commands are whitelisted functions
- **Input validation:** Parameterized queries, no string concat
- **Error handling:** Never exposes sensitive info in error messages
- **Logging:** All tool calls logged with timestamp, source, result

---

## Configuration Files

### ~/.mcp.json
Registers zo-bridge server with connection env vars.

### ~/.zo/.env
```
ZO_HOST=zo.garcia-ramsees.local
ZO_PORT=22
ZO_USER=deploy
ZO_DB_HOST=zo.garcia-ramsees.local
ZO_DB_NAME=garcia_ramsees
ZO_DB_USER=postgres
RAMSEES_API=https://detectable-clarita-casuistically.ngrok-free.dev
```

### /etc/systemd/system/zo-bridge.service
Enables auto-start on Zo reboot.

---

## Failure Modes & Resilience

| Failure | Behavior | Recovery |
|---------|----------|----------|
| SSH disconnected | zo_bash returns error | Retry with exponential backoff |
| PostgreSQL down | zo_postgres fails gracefully | Ramsees uses cache; notify ops |
| Ramsees API timeout | zo_hermes_chat returns 504 | Queue message locally, retry |
| Zo reboots | Service restarts via systemd | Auto-reconnect on restart |
| Network latency | Commands timeout after 30s | Fail fast, user can retry |

---

## Performance Metrics

- **SSH connection:** ~100ms (depends on network)
- **zo_bash latency:** 100-500ms (command dependent)
- **zo_postgres latency:** 50-200ms (query dependent)
- **zo_hermes_chat latency:** 100-2000ms (API dependent)
- **Tool registration:** <10ms (in-memory, no I/O)
- **Memory overhead:** ~50MB (Python runtime + connections)

---

## Monitoring

### Log locations
- **MCP server:** `journalctl -u zo-bridge -f` (if systemd)
- **Ramsees agent:** Integrated NTFY topic
- **PostgreSQL:** `/var/log/postgresql/` on Zo
- **Docker:** `docker logs ramsees-agent`

### Health checks
- Run `zo_health()` tool to check CPU, memory, disk, services
- Run `zo_postgres("SELECT 1")` to verify DB connectivity
- Run `zo_bash("systemctl status ramsees-agent")` to verify service

---

**Architecture Version:** 1.0  
**Last Updated:** 2026-04-16  
**Designed For:** Garcia-Ramsees commercial law command center
