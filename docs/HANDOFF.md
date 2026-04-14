# 🤝 Claude Code Handoff — You Became The Money (YBTM)

> **Last Updated:** 2026-04-10  
> **Prepared by:** Kimi Code CLI  
> **Purpose:** Complete transfer of Mr. Garcia's project so Claude Code can seamlessly take over.

---

## 🎯 What Is This Project?

**Client:** Daniel Garcia  
**Brand:** You Became The Money (YBTM)  
**Current Phase:** Prototype / System Planning  
**Deadline:** Wednesday demo (4 days from April 10)  
**Full Timeline:** 4 weeks to production  

This is NOT just a website. It is morphing into a **full command-center system** for Garcia's business:
- Marketing website (locked foundation)
- React dashboard for lead/case management
- Hermes AI agent for 24/7 lead intake
- Voice integration (Web Speech API + ElevenLabs)
- PostgreSQL backend + FastMCP skills

---

## 📁 Repository Layout

```
youbecamethemoney/
├── index.html                  ← Marketing website (LOCKED — do not modify design)
├── about.html                  ← About page (LOCKED)
├── assets/                     ← Images, CSS, JS, PDFs
├── components/                 ← Reusable web components
├── config/                     ← Workspace config
├── docs/
│   └── COMPONENTS.md           ← Component documentation
├── prototype/                  ← React dashboard MVP
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── LiveLeads.tsx
│   │   │   ├── Pipeline.tsx
│   │   │   ├── Metrics.tsx
│   │   │   └── VoiceCommand.tsx
│   │   ├── api/mockHermes.ts
│   │   └── types/index.ts
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── .workspace-state.json       ← Website lock state
├── CONTEXT.md                  ← Full project brief from client
├── BUILD.md                    ← Phase-by-phase sprint tasks
├── SKILL.md                    ← Tech stack + FastMCP skill specs
├── CLAUDE.md                   ← Routing rules for this repo
├── KIMI.md                     ← Kimi-specific notes
├── voice-agent-knowledge-base.md
└── HANDOFF.md                  ← You are here
```

---

## 🔒 LOCKED ITEMS (DO NOT CHANGE WITHOUT PERMISSION)

The following were explicitly approved by the user and are **locked**:

| Item | Status | Location |
|------|--------|----------|
| Egyptian/Kemet theme | 🔒 LOCKED | `assets/css/main.css` |
| Fonts (Cinzel, Cormorant Garamond) | 🔒 LOCKED | `index.html` |
| Color palette (navy, gold, papyrus, charcoal) | 🔒 LOCKED | `assets/css/main.css` |
| ElevenLabs agent | 🔒 LOCKED | `index.html` (bottom-right) |
| SoundCloud player | 🔒 LOCKED | `index.html` (bottom-left) |
| Book sections (8 Amazon + free ebook) | 🔒 LOCKED | `index.html` |
| Navigation items | 🔒 LOCKED | `index.html`, `about.html` |

**Rule:** If Claude Code thinks something locked needs changing, **ASK THE USER FIRST**.

---

## ✅ What's Already Done

### Phase 0: Foundation (April 9)
- [x] Complete Egyptian-themed marketing website
- [x] About Us page
- [x] Book library (8 Amazon + free ebook)
- [x] ElevenLabs voice agent integration
- [x] SoundCloud music player
- [x] Contact form
- [x] Workspace state management established

### Phase 1: Prototype (April 10)
- [x] React + TypeScript + Tailwind dashboard scaffolded
- [x] `LiveLeads` component with real-time simulation
- [x] `Pipeline` Kanban board with drag-drop
- [x] `Metrics` panel with charts
- [x] `VoiceCommand` component demo
- [x] Mock Hermes API (`mockHermes.ts`)
- [x] All planning docs saved (CONTEXT, BUILD, SKILL, CLAUDE)
- [x] `.github/CLAUDE.md` created for Claude Code compatibility

---

## 🚀 What's Next (From BUILD.md)

### Phase 1 Day 1 (Now → Tuesday)
1. **React scaffold improvements**
   - Add `CaseDetail` view
   - Wire mock API to components
   - Add loading/error states
2. **Types + test data**
   - Expand `types/index.ts` with full lead/case models
   - Generate realistic mock data
3. **Voice integration prep**
   - Set up Web Speech API wrapper
   - Connect to ElevenLabs conversational agent

### Phase 1 Day 2-3 (Tuesday → Wednesday morning)
1. **Dashboard polish**
   - Responsive layout
   - Animations/transitions
   - Export/share buttons
2. **Demo rehearsal**
   - Record loom/video walkthrough
   - Prepare talking points for Garcia

### Phase 2: Integration (Week 1)
- PostgreSQL schema
- Node.js API scaffold
- Hermes agent webhook
- FastMCP skill: `intake`

### Phase 3: Optimization (Weeks 2-4)
- Real-time WebSocket sync
- Email/SMS discharge protocols
- Stripe billing integration
- Production deployment

See `BUILD.md` for the **full day-by-day checklist**.

---

## 🧠 Critical Context for Claude Code

### The Pivot
On April 10, the user made it clear: **"We arent just building a website alone. We're eventually going to morph it into a system."** The website foundation is complete and locked. All new work should happen in:
- `prototype/` (dashboard)
- `integration/` (backend, empty — create here)
- `optimization/` (performance tuning, empty — create here)

### User Communication Style
- **Direct, no fluff.**
- **Token-sensitive.** Keep responses concise.
- **Hates repeated mistakes.** Read previous logs before acting.
- **Expects task logging.** Every task must be logged in Solomon's Chamber BEFORE starting.

### Active Tasks (From Solomon's Chamber)
Check these files **immediately** upon starting any session:
- `~/Solomons-Chamber/09-Agent-Sessions/current/TASK-2026-04-10-MR-GARCIA-CONTINUE.md`
- `~/Solomons-Chamber/09-Agent-Sessions/current/TASK-2026-04-10-YBTM-SYSTEM-PLANNING.md`
- `~/Solomons-Chamber/memory/YBTM_WORKSPACE_STATE.md`

---

## 🔗 Related Repos & Resources

| Resource | URL / Path | Purpose |
|----------|------------|---------|
| **This Repo** | `https://github.com/youngstunners88/youbecamethemoney` | Main project codebase |
| **Solomon's Chamber** | `https://github.com/youngstunners88/Solomons-Chamber` | Knowledge base, session logs, all historical context |
| **YBTM System Docs** | `Solomons-Chamber/01-Projects/YBTM-System/` | Duplicate planning docs + architecture |
| **Production API** (future) | TBD | Node.js API |
| **ElevenLabs Agent** | `agent_2401kh49ezxaef3tqynwkb1pyp22` | Voice agent ID |

---

## ⚠️ Mistakes to NEVER Repeat

1. **Don't modify locked design elements** (fonts, colors, theme) without explicit permission.
2. **Don't move/reorder sections** in `index.html` without asking.
3. **Don't break working integrations** (ElevenLabs, SoundCloud).
4. **Don't skip task logging** in Solomon's Chamber.
5. **Don't assume context** — read the files first.

---

## 📝 First Thing Claude Code Should Do

When you (Claude Code) open this project for the first time:

1. **Read this file** (`HANDOFF.md`)
2. **Read `BUILD.md`** to see what's scheduled
3. **Read `CONTEXT.md`** to understand the full vision
4. **Check `~/Solomons-Chamber/09-Agent-Sessions/current/`** for any incomplete tasks
5. **Run the prototype:**
   ```bash
   cd prototype
   npm install
   npm run dev
   ```
6. **Ask the user:** "What should I work on next?" (unless a task log explicitly tells you)

---

## 💬 Commit Message Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation only
- `refactor:` code change that neither fixes a bug nor adds a feature
- `chore:` maintenance tasks

---

**Ready for takeover. Good luck, Claude Code.**
