# You Became The Money - CONTEXT.md

**Project:** Command center system for Daniel Garcia's commercial law practice  
**Timeline:** 4 weeks to production  
**Deadline:** Wednesday presentation (prototype)  
**Model:** $3,500 setup + $1,200/month recurring

---

## What This Project Is

An AI-powered operations system with three layers:
1. **Hermes Agent** — 24/7 lead intake (Telegram, WhatsApp, Discord, CLI)
2. **React Dashboard** — Real-time visibility (leads, pipeline, metrics, voice commands)
3. **FastMCP Skills** — Custom commercial law tools (not commoditized, specific to Mr. Garcia's practice)

Layer 1 (commoditized) → Layer 2 (workflow automation) → Layer 3 (learns from data).

---

## Tech Stack

| Component | Tech |
|-----------|------|
| Frontend | React + TypeScript + Tailwind |
| AI Brain | Hermes Agent (open-source) |
| Backend | Node.js API (Express) |
| Database | PostgreSQL |
| LLM | Claude API + Nous Hermes 4 |
| Voice | Web Speech API + ElevenLabs |
| Skills | FastMCP (Python) |
| Hosting | Client VPS (self-hosted) |

---

## Workspaces

**🟠 Prototype (Days 1-4):**  
React dashboard, mock Hermes API, voice command demo. Deliverable: Live demo for Wednesday.

**🟡 Integration (Week 1):**  
Hermes on VPS, PostgreSQL, Node.js API bridge, first 3 FastMCP skills. Deliverable: End-to-end intake flow.

**🟢 Optimization (Weeks 2-4):**  
Voice agent, advanced analytics, automation, security hardening. Deliverable: Production-ready system.

---

## Data Model

```
Lead: id, source, name, phone, email, serviceType, urgencyScore (1-10), status, timestamp
Case: id, leadId, serviceType, value, intakeDate, closeDate, outcome
Skill: name, trigger, procedure, effectiveness, createdDate
InteractionLog: timestamp, platform, message, hermesResponse, leadId
```

---

## Dashboard Components

1. **LiveLeads** — Card stream, filter by urgency + service type
2. **Pipeline** — Kanban (new → qualified → consulting → retained → closed)
3. **Metrics** — Conversion %, avg case value, intake→consult time, pipeline value
4. **VoiceCommand** — Mic button → text → Hermes API → response
5. **CaseDetail** — Single case interaction timeline
6. **SkillsManager** — View + audit Hermes-created skills (future)

---

## Custom FastMCP Skills (Layer 2-3 Moat)

Non-commoditized. Embed Mr. Garcia's domain knowledge:

1. **intake_commercial_law** — Ask the right questions (UCC articles, securitization, jurisdiction)
2. **lead_urgency_scorer** — Score 1-10 based on case specifics + past outcomes
3. **case_pattern_analyzer** — Extract learnings from closed cases, update memory
4. **discharge_protocol** — Step-by-step guidance (securitization → trust verification → notice)
5. **email_drafter** — Context-aware responses that teach + qualify

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Wednesday | Dashboard renders, voice works, Mr. Garcia says yes |
| Week 1 | Real lead (WhatsApp) → Hermes qualifies → dashboard shows it |
| Week 4 | 10+ real leads processed, Mr. Garcia running autonomously |

---

## Naming Conventions

- Components: `LiveLeads.tsx`, `Pipeline.tsx`, `VoiceCommand.tsx`
- API endpoints: `/api/leads`, `/api/metrics`, `/api/pipeline`, `/api/voice-command`
- Skills: `intake_commercial_law.py`, `lead_urgency_scorer.py`, `case_pattern_analyzer.py`
- Database: PostgreSQL, tables: leads, cases, interaction_logs
- Deployments: Dashboard on Vercel, Hermes on client VPS (systemd service)

---

## When Prompting Kimi Code

**Example tight prompt:**
> "Per CONTEXT.md Workspace: Prototype, Component: LiveLeads. Build React component showing test leads (15 diverse examples), filter by urgencyScore + serviceType. Tailwind styling, 200 LOC, simulate real-time (new lead every 10s). Target: 1.5 hours."

**Avoid:**
> "I need a dashboard component that shows leads as cards..."

---

## Key Rules

1. **No context bleed between workspaces.** Prototype stays prototype until Wednesday. Then integration begins.
2. **FastMCP skills are not generic.** Every skill must embed Mr. Garcia's legal framework.
3. **Hermes is the orchestrator.** Dashboard reads FROM Hermes via API, not the other way around.
4. **All interactions logged.** Every lead, every case, every Hermes decision goes to PostgreSQL.
5. **Self-hosted always.** Client owns VPS, owns data, owns system.

---

## What Good Work Looks Like

✅ **Prototype:** Dashboard looks polished, feels like a real product, voice demo works (even if mock).  
✅ **Integration:** Real lead flows from Telegram → Hermes qualifies → dashboard shows it, logged in DB.  
✅ **Production:** Mr. Garcia checks dashboard daily, Hermes handles 80% of intake, conversion metrics visible.

---

## Constraints

- **Token efficiency:** Reference SKILL_COMPRESSED.md + BUILD_COMPRESSED.md to avoid repeating architecture.
- **4-day deadline for prototype:** Fast iteration, MVP mindset.
- **4-week deadline for production:** Full feature set, security, documentation.
- **Recurring revenue model:** $1,200/month means you're invested in optimization long-term.

---

## Future Roadmap (Week 5+)

**Hyperspace P2P Integration:** Optional. Run Hyperspace node on VPS. Route routine inferences (lead scoring, summaries) to P2P network (free), Claude API as fallback. Zero cost, potential upside. Not critical to core build—add later as optimization.

---

## Adjust As You Go

This CONTEXT.md is a living document. As you move through the sprint:
- Add specifics about Mr. Garcia's business rules (which service types convert best, etc.)
- Refine skill definitions based on real case data
- Update success metrics weekly
- Edit this file after each phase to reflect what you've learned
