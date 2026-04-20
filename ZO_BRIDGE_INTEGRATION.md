# ZO_BRIDGE_INTEGRATION.md — Integration with Ramsees

## Overview
The Zo bridge seamlessly integrates with the Garcia-Ramsees command center. This document explains how the 8 tools work together to enable Claude Code to orchestrate the entire system.

---

## Integration Points

### 1. Ramsees Agent → PostgreSQL (hot lead detection)
**Flow:**
```
Ramsees agent monitors PostgreSQL for new leads
  ↓
Query: SELECT * FROM leads WHERE created_at > now() - interval '1 minute'
  ↓
If warmth_score >= 70: Send NTFY notification
  ↓
Additionally: Claude Code can use zo_hermes_chat for priority routing
```

**Tool used:** `zo_postgres()`
- Allows Claude Code to trigger queries on demand
- Verify lead insertion: `zo_postgres("SELECT COUNT(*) FROM leads WHERE warmth_score >= 70")`
- Extract hot leads: `zo_postgres("SELECT * FROM leads WHERE warmth_score >= 70 ORDER BY created_at DESC LIMIT 10")`

---

### 2. Claude Code → Ramsees API (priority messages)
**Flow:**
```
Claude Code detects business logic (high-value client, urgent case)
  ↓
Calls zo_hermes_chat() with priority level
  ↓
Message POSTs to Ramsees API: POST /api/ramsees-message
  ↓
Ramsees validates, enriches with context
  ↓
Routes to NTFY (ntfy.sh) with topic=garcia-ramsees-alerts
  ↓
Garcia receives push notification on phone
```

**Example scenarios:**

a) **Urgent lead escalation:**
```python
zo_hermes_chat("🔥 PRIORITY: Smith Family LLC - $500K real estate dispute, immediate call needed", "high")
```

b) **Case status update:**
```python
zo_hermes_chat("✅ Jones v. State: Motion granted, proceeding to trial phase", "normal")
```

c) **Administrative task:**
```python
zo_hermes_chat("📝 New affidavit required by Friday for Anderson case", "low")
```

---

### 3. Service Lifecycle Management (deploy → health check → logs)
**Deployment workflow:**

```
zo_deploy("ramsees-agent", "2.0.0")
  ↓
Pulls image, updates docker-compose
  ↓
Service restarts
  ↓
zo_health() — verify service is running
  ↓
zo_logs("ramsees-agent", 50) — check for errors in startup
```

**Full example:**
```bash
# Step 1: Deploy new version
result = zo_deploy("ramsees-agent", "2.1.0")
→ {status: "success", version: "2.1.0", deployment: "ramsees-agent"}

# Step 2: Verify deployment
health = zo_health()
→ {status: "success", health_checks: {cpu: "5%", memory: "2.3G", services: 8}}

# Step 3: Check startup logs
logs = zo_logs("ramsees-agent", 100)
→ {status: "success", logs: "2026-04-16 21:45:00 Ramsees v2.1.0 initialized..."}

# Step 4: If errors, restart cleanly
if "error" in logs:
    zo_restart("ramsees-agent")
    → {status: "success", service: "ramsees-agent", restarted: true}
```

---

### 4. Configuration Management (get/set via zo_config)
**Use cases:**

a) **Enable/disable NTFY notifications:**
```bash
zo_config("set", "ntfy_enabled", "true")
```

b) **Adjust lead hotness threshold:**
```bash
zo_config("set", "warmth_threshold", "65")
```

c) **Read current configuration:**
```bash
zo_config("get", "api_port")
→ {status: "success", value: "5000"}
```

---

## Example Workflows

### Workflow 1: New Lead → Priority Alert
**Scenario:** User creates lead in embark.html with warmth=85 (hot client)

```
1. POST /api/leads {name: "Smith", email: "smith@biz.com", warmth: 85}
2. demo-server stores in PostgreSQL
3. Ramsees detects warmth >= 70, sends base NTFY notification
4. Claude Code enhances notification with context:
   
   zo_postgres("SELECT * FROM leads WHERE id = (SELECT MAX(id) FROM leads)")
   → Returns: {name: "Smith", case_type: "Real Estate", value: "$500K"}
   
5. Claude Code sends priority message:
   
   zo_hermes_chat("🔥 HOT: Smith - Real Estate $500K deal, immediate follow-up", "high")
   
6. Garcia receives rich notification on phone with business context
```

---

### Workflow 2: Service Deployment with Verification
**Scenario:** Ramsees agent updated to v2.2.0

```
1. Download new image:
   zo_bash("docker pull ramsees-agent:2.2.0")

2. Deploy and verify:
   zo_deploy("ramsees-agent", "2.2.0")
   → {status: "success"}

3. Check health:
   zo_health()
   → {status: "success", services: 8, memory: "2.4G"}

4. Verify startup logs:
   zo_logs("ramsees-agent", 50)
   → Checks for "initialized successfully" message

5. If all good, notify Garcia:
   zo_hermes_chat("✅ Ramsees agent upgraded to v2.2.0, all systems nominal", "normal")
```

---

### Workflow 3: Incident Response (service down)
**Scenario:** Ramsees agent crashes, alerts Garcia

```
1. Garcia opens command center, investigates:
   zo_health()
   → {cpu: "0%", memory: "0", services: 7} ← ramsees-agent missing!

2. Check logs for error:
   zo_logs("ramsees-agent", 100)
   → "FATAL: Database connection timeout"

3. Verify database is reachable:
   zo_postgres("SELECT 1")
   → Timeout or connection error

4. Restart database:
   zo_bash("systemctl restart postgresql")

5. Give services time to reconnect:
   zo_bash("sleep 5 && systemctl status postgresql")

6. Restart Ramsees:
   zo_restart("ramsees-agent")

7. Verify recovery:
   zo_health()
   → {services: 8} ← back online!

8. Notify success:
   zo_hermes_chat("🔧 Incident resolved: Ramsees restarted after DB recovery", "normal")
```

---

## Integration Checklist

- [ ] **SSH access working** — `zo_bash("whoami")` returns `deploy`
- [ ] **PostgreSQL accessible** — `zo_postgres("SELECT 1")` returns success
- [ ] **Ramsees API responsive** — `zo_hermes_chat("test", "normal")` returns 200
- [ ] **Docker containers running** — `zo_health()` shows all services
- [ ] **Systemd service enabled** — `zo_bash("systemctl status zo-bridge")` shows active
- [ ] **NTFY notifications working** — Receive test notification via `zo_hermes_chat()`
- [ ] **Hot lead detection active** — Create lead with warmth >= 70, receive alert
- [ ] **End-to-end test passed** — Full workflow from embark.html → Garcia's phone

---

## Performance Expectations

| Operation | Latency | Throughput |
|-----------|---------|-----------|
| zo_bash (simple) | 100-300ms | 10 ops/sec |
| zo_postgres (simple query) | 50-150ms | 20 ops/sec |
| zo_hermes_chat (message send) | 200-1000ms | 3 ops/sec |
| zo_health (full check) | 500-2000ms | 1 op/sec |
| zo_deploy (pull + restart) | 30-120s | 0.01 ops/sec |

**Notes:**
- Network latency varies; times above are typical for local/LAN connections
- PostgreSQL queries scale with data size (leads table)
- zo_deploy depends on image size and Docker cache
- Ramsees API latency depends on ngrok tunnel and network conditions

---

## Troubleshooting Integration Issues

### Problem: zo_hermes_chat fails with "Connection refused"
**Solution:**
1. Verify RAMSEES_API URL: `echo $RAMSEES_API`
2. Check ngrok tunnel is running: `curl -I https://detectable-clarita-casuistically.ngrok-free.dev`
3. Verify endpoint exists: `curl -X POST https://.../api/ramsees-message -d '{"message":"test"}'`

### Problem: New leads don't trigger notifications
**Solution:**
1. Verify lead is in PostgreSQL: `zo_postgres("SELECT * FROM leads WHERE id = <last_id>")`
2. Check NTFY_TOPIC env var: `zo_bash("echo $NTFY_TOPIC")` should show `garcia-ramsees-alerts`
3. Test NTFY directly: `curl -d 'test' https://ntfy.sh/garcia-ramsees-alerts`
4. Verify Ramsees is monitoring: `zo_logs("ramsees-agent", 50)` should show "monitoring leads"

### Problem: zo_deploy hangs
**Solution:**
1. Check Docker daemon: `zo_bash("docker ps")` should list containers
2. Monitor disk space: `zo_bash("df -h")` — pull fails if <1GB free
3. Check image pull status: `zo_bash("docker pull ramsees-agent:2.2.0")`
4. Kill hung process if needed: `zo_bash("timeout 10 docker pull ...")`

---

## Security Considerations

### Message Privacy
- zo_hermes_chat POSTs over HTTPS (ngrok tunnel)
- Messages include `source: "zo-bridge"` for audit trail
- No sensitive data (passwords, SSNs) should be included

### Database Audit Trail
- All zo_postgres queries logged to PostgreSQL audit table
- Include timestamp, source, query, result count
- Supports compliance for Garcia's law practice

### SSH Access Restrictions
- zo_bash only runs whitelisted commands (no shell access)
- SSH user `deploy` has no sudo privileges
- Commands timeout at 30 seconds

---

## Monitoring & Alerts

### Daily Health Check (recommended)
```bash
zo_health()  # CPU, memory, disk, services
zo_postgres("SELECT COUNT(*) FROM leads WHERE created_at > now() - interval '1 day'")  # Daily lead volume
zo_logs("ramsees-agent", 20)  # Check for recent errors
```

### Weekly Deep Dive
```bash
zo_bash("df -ih")  # Inode usage
zo_bash("ps aux | grep python")  # Verify Ramsees process
zo_postgres("SELECT AVG(warmth_score) FROM leads WHERE created_at > now() - interval '7 days'")  # Lead quality
```

---

**Integration Version:** 1.0  
**Last Updated:** 2026-04-16  
**Status:** Production-ready
