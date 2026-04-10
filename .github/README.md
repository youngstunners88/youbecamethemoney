# GitHub Repository Guide

## For Claude Code Users

When opening this project in Claude Code:

1. **Read CLAUDE.md first** - It contains workspace routing rules
2. **Check current phase** - Look at BUILD.md for status
3. **Navigate to correct workspace** - prototype/ integration/ or optimization/

## Repository Structure

```
youbecamethemoney/
├── CLAUDE.md              ← START HERE
├── CONTEXT.md             ← Project brief
├── BUILD.md               ← Task checklist
├── SKILL.md               ← Tech specs
├── README.md              ← This file (general overview)
├── prototype/             ← Phase 1 (React dashboard)
│   ├── src/
│   ├── dist/              ← Production build
│   └── package.json
├── integration/           ← Phase 2 (API, Hermes, DB)
└── optimization/          ← Phase 3 (Production hardening)
```

## Phase Status

🟠 **Prototype** - 85% complete  
🟡 **Integration** - Not started  
🟢 **Optimization** - Not started

## Quick Commands

```bash
# Run prototype dashboard
cd prototype && npm run dev

# Build for production
cd prototype && npm run build

# Test (when available)
npm test
```

## Key Files for AI Agents

| File | Purpose |
|------|---------|
| CLAUDE.md | Routing, workspace structure, rules |
| CONTEXT.md | Requirements, data model, success metrics |
| BUILD.md | Day-by-day task checklist |
| SKILL.md | FastMCP skill templates, API specs |

---

*This repository is configured for seamless handoff between Kimi Code and Claude Code.*
