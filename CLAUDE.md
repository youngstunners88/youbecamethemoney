# You Became The Money

**Project:** AI command center for Daniel Garcia's commercial law practice  
**Stack:** React | PostgreSQL | Hermes Agent | FastMCP | Node.js API  
**Timeline:** 4 weeks (presentation Wednesday)

---

## Workspaces

| Phase | Folder | Purpose | Context |
|-------|--------|---------|---------|
| **Prototype** | `/prototype` | Dashboard MVP, mock API, voice demo | CONTEXT.md |
| **Integration** | `/integration` | Hermes on VPS, real API, first 3 skills | CONTEXT.md |
| **Optimization** | `/optimization` | Voice agent, analytics, hardening, docs | CONTEXT.md |

---

## Routing

| Task | Go to | Read |
|------|-------|------|
| Build dashboard (Days 1-4) | `/prototype` | CONTEXT.md |
| Build Hermes + API (Week 1) | `/integration` | CONTEXT.md |
| Optimize + harden (Weeks 2-4) | `/optimization` | CONTEXT.md |

---

## Reference Files

- **CONTEXT.md** — Project brief, data model, components, skills, success metrics
- **BUILD.md** — Day-by-day task checklist
- **SKILL.md** — Tech stack, FastMCP skills definitions

---

## Key Rules

1. No context bleed between phases
2. Every skill embeds Mr. Garcia's domain knowledge (not generic)
3. Hermes is the orchestrator; dashboard reads from Hermes API
4. All interactions logged to PostgreSQL
5. Self-hosted always (client owns data)

---

## Start Here

When you're ready to build: Point Kimi Code at `/prototype` and say:

> "Per CLAUDE.md, routing to /prototype workspace. Per CONTEXT.md: Build LiveLeads component..."

That's it.
