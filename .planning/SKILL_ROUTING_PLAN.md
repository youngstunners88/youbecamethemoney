# Skill Routing System — Token-Efficient Architecture

## Mission
Build Garcia's command center with intelligent skill routing that optimizes token burn while executing Layer 3 learning + Hermes deployment simultaneously.

## Repos to Install (Priority Ranking)

### TIER 1 — Critical for mission
1. **gsd-build/get-shit-done** (ALREADY IN USE)
   - Purpose: Project orchestration, phase management, atomic commits
   - Token cost: HIGH (orchestrates others)
   - Usage: Master coordinator

2. **drona23/claude-token-efficient**
   - Purpose: Token cost estimation, smart routing, compression
   - Token cost: LOW (utility library)
   - Usage: All routing decisions run through here

3. **giancarloerra/SocratiCode**
   - Purpose: Intelligent questioning for legal context
   - Token cost: MEDIUM (generates smart questions)
   - Usage: Garcia case intake, qualification

### TIER 2 — Support infrastructure
4. **czlonkowski/n8n-mcp**
   - Purpose: Workflow automation, task coordination
   - Token cost: MEDIUM (orchestrates tasks)
   - Usage: Ramsees workflow pipelines

5. **hesreallyhim/awesome-claude-code**
   - Purpose: Best practices, patterns
   - Token cost: LOW (reference)
   - Usage: Code generation guidance

6. **PrismorSec/immunity-agent**
   - Purpose: Security validation
   - Token cost: MEDIUM (audits decisions)
   - Usage: Validate Garcia data access

### TIER 3 — Nice-to-have
7. **nextlevelbuilder/ui-ux-pro-max-skill**
   - Purpose: UI/UX optimization
   - Token cost: MEDIUM
   - Usage: Command center interface refinement

8. **KeygraphHQ/shannon**
   - Purpose: Data compression
   - Token cost: LOW
   - Usage: Response compression

---

## Folder Structure

```
/home/user/youbecamethemoney/
├── .skills/                          # Autonomous skill system
│   ├── __init__.py                   # Skill router (entry point)
│   ├── routing_engine.py             # Token-aware routing logic
│   ├── skill_registry.py             # All available skills
│   ├── token_cost_tracker.py         # Cost estimation + logging
│   │
│   ├── tier1/                        # Critical skills
│   │   ├── gsd_coordinator.py        # GSD orchestration
│   │   ├── token_optimizer.py        # Token efficiency (from drona23/claude-token-efficient)
│   │   ├── legal_questioner.py       # SocratiCode (legal intake)
│   │
│   ├── tier2/                        # Support skills
│   │   ├── workflow_automation.py    # n8n-mcp integration
│   │   ├── code_best_practices.py    # awesome-claude-code reference
│   │   ├── security_validator.py     # immunity-agent
│   │
│   ├── tier3/                        # Optional skills
│   │   ├── ui_optimizer.py           # UI/UX enhancements
│   │   ├── compression.py            # shannon compression
│
│   └── autonomous_executor.py        # Execute skills without prompting
│
├── optimization/layer3/
│   ├── db_schema.py (MODIFIED)       # Switch SQLite → PostgreSQL
│   ├── integration/
│   │   ├── postgres_bridge.py        # Real data source
│   │   ├── retell_connector.py       # Real Retell data
│   │   └── garcia_manual_input.py    # Manual case entries
│
├── hermes/
│   ├── deployment/
│   │   ├── install_hermes.sh         # Install Hermes on Zo
│   │   ├── config.yaml               # Hermes config (PostgreSQL)
│   │   └── skills/
│   │       ├── intake_commercial_law.py
│   │       ├── lead_urgency_scorer.py
│   │       ├── case_pattern_analyzer.py
│   │       ├── discharge_protocol.py
│   │       └── email_drafter.py
```

---

## Autonomous Routing Logic

```python
# Pseudocode for routing_engine.py

TASK_ROUTER = {
    "learn_from_cases": {
        "skill": "token_optimizer",
        "fallback": "gsd_coordinator",
        "cost_budget": 5000,  # tokens
    },
    "qualify_lead": {
        "skill": "legal_questioner",
        "fallback": "code_best_practices",
        "cost_budget": 2000,
    },
    "deploy_to_zo": {
        "skill": "gsd_coordinator",
        "fallback": "workflow_automation",
        "cost_budget": 1000,
    },
    "validate_security": {
        "skill": "security_validator",
        "fallback": "code_best_practices",
        "cost_budget": 3000,
    },
    "optimize_response": {
        "skill": "token_optimizer",
        "fallback": "compression",
        "cost_budget": 500,
    },
}

def route_task(task_type, context):
    """Autonomously route task to optimal skill."""
    if task_type not in TASK_ROUTER:
        return execute_generic(context)
    
    route = TASK_ROUTER[task_type]
    skill = load_skill(route["skill"])
    
    # Estimate cost
    estimated_cost = skill.estimate_cost(context)
    
    if estimated_cost > route["cost_budget"]:
        # Use fallback (cheaper)
        skill = load_skill(route["fallback"])
    
    # Execute without prompting
    return skill.execute(context)
```

---

## Token Optimization Strategy

### 1. Cost Estimation
- **Token budgets** per task type (see TASK_ROUTER)
- **Fallback routing** if cost exceeds budget
- **Compression** for responses >2000 tokens

### 2. Skill Selection
- Choose TIER 1 skills (lowest cost) first
- Cascade to TIER 2 if needed
- Avoid TIER 3 unless specifically called

### 3. Caching
- Cache Hermes responses (legal precedents, patterns)
- Cache learning module outputs (patterns from cases)
- Cache skill definitions (avoid re-loading)

### 4. Batch Processing
- Group layer 3 cycle (weekly) into single call
- Batch Hermes updates (not per-lead)
- Batch security validations (end of week)

---

## Track 1 + Track 2 Execution

### Track 1: Learning Engine Integration
**Skill routing:** `token_optimizer` → `gsd_coordinator`

1. Swap SQLite → PostgreSQL (postgres_bridge.py)
2. Connect to Retell API (retell_connector.py)
3. Add Garcia manual inputs (garcia_manual_input.py)
4. Deploy to Zo as systemd service
5. **Token cost:** ~3000 (setup) + ~500/week (cycle)

### Track 2: Hermes/Ramsees Deployment
**Skill routing:** `gsd_coordinator` → `workflow_automation`

1. Clone Hermes from NousResearch
2. Configure with PostgreSQL
3. Wire 5 FastMCP skills
4. Deploy to Zo via MCP bridge
5. **Token cost:** ~2000 (setup) + ~1000/week (queries)

### Autonomous Execution
- No manual prompting
- Routing engine decides skill per task
- Cost tracker monitors budget
- GSD coordinator manages parallel execution
- Fallback system handles cost overruns

---

## Success Metrics

- ✅ Layer 3 runs weekly on Zo, learns from real data
- ✅ Hermes deployed on Zo, serves Garcia's leads
- ✅ Token burn < 10,000/week (vs. 15,000 without optimization)
- ✅ Skills execute autonomously (no manual intervention)
- ✅ Cost tracking accurate (±10% estimate vs. actual)

---

**Status:** Ready for parallel execution  
**Est. time:** 4-6 hours (with parallel workers)  
**Token budget:** 15,000 (setup phase)
