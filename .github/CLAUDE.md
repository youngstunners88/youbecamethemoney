# You Became The Money - Claude Code Guide

**Project:** AI command center for Daniel Garcia's commercial law practice  
**Stack:** React | PostgreSQL | Hermes Agent | FastMCP | Node.js API  
**Timeline:** 4 weeks (presentation Wednesday)

---

## START HERE - READ THIS FIRST

Before doing ANY work, read these files in order:
1. **CLAUDE.md** (this file) - Routing and workspace structure
2. **CONTEXT.md** - Project brief, data model, components
3. **BUILD.md** - Day-by-day task checklist
4. **SKILL.md** - Tech stack, FastMCP skills definitions

---

## Workspace Structure

```
youbecamethemoney/
├── CLAUDE.md          ← You are here (routing rules)
├── CONTEXT.md         ← Project brief, data model, success metrics
├── BUILD.md           ← Day-by-day checklist
├── SKILL.md           ← Tech stack, FastMCP skills
├── prototype/         ← Phase 1: Dashboard MVP (CURRENT - Days 1-4)
├── integration/       ← Phase 2: Hermes + API (Week 1)
├── optimization/      ← Phase 3: Production (Weeks 2-4)
├── index.html         ← Marketing website (separate)
└── about.html         ← About page (separate)
```

---

## Workspace Routing Rules

| Task | Go to | Read |
|------|-------|------|
| Build dashboard components | `/prototype` | CONTEXT.md |
| Set up Hermes agent | `/integration` | CONTEXT.md |
| Build API bridge | `/integration` | CONTEXT.md |
| Create FastMCP skills | `/integration` or `/optimization` | SKILL.md |
| Add voice recognition | `/optimization` | CONTEXT.md |
| Security hardening | `/optimization` | CONTEXT.md |

---

## Current Phase

**🟠 PROTOTYPE (Days 1-4)** - Deadline: Wednesday

### Status: 85% Complete
- ✅ React + TypeScript + Tailwind setup
- ✅ LiveLeads component (filters, real-time sim)
- ✅ Pipeline Kanban (drag-drop)
- ✅ Metrics panel (KPIs, charts)
- ✅ VoiceCommand component (demo)
- ✅ Mock Hermes API
- ✅ Production build
- ⏳ Deploy to Vercel

### Quick Start:
```bash
cd prototype
npm run dev
# http://localhost:3000
```

---

## Key Rules (DO NOT BREAK)

1. **No context bleed** - Stay in your workspace phase
2. **Hermes orchestrates** - Dashboard reads FROM Hermes API
3. **Skills embed domain knowledge** - Not generic; specific to commercial law
4. **Log everything** - All interactions go to PostgreSQL
5. **Self-hosted** - Client owns VPS, data, system

---

## Common Tasks

### Adding a Dashboard Component
```bash
cd prototype/src/components
# Create ComponentName.tsx
# Add route in App.tsx
# Update types if needed
```

### Creating a FastMCP Skill
1. Go to `/integration/skills/` (create if doesn't exist)
2. Create `{skill_name}.py`
3. Follow SKILL.md template
4. Test with mock data first

### Deploying Prototype
```bash
cd prototype
npm run build
# Deploy dist/ folder to Vercel/Netlify
```

---

## File Reference

| File | Purpose | When to Read |
|------|---------|--------------|
| CLAUDE.md | Routing, workspace rules | Every session |
| CONTEXT.md | Project requirements | When building features |
| BUILD.md | Task checklist | Daily planning |
| SKILL.md | Tech specs, skill templates | When implementing skills |

---

## Contact

**Client:** Daniel Garcia  
**Project:** You Became The Money  
**Model:** $3,500 setup + $1,200/month recurring

---

*Last updated: 2026-04-10*
