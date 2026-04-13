# YBTM Build Checklist

## Phase 1: Prototype (Days 1-4) — Deadline: Wednesday

### Day 1: Foundation
- [x] React + TypeScript + Tailwind setup
- [x] Project structure (src/components, src/api, src/types)
- [x] Mock Hermes API with 15 diverse leads
- [x] TypeScript interfaces (Lead, Case, Metrics, etc.)

### Day 2: Core Components
- [x] LiveLeads component (filter by service, urgency, real-time sim)
- [x] Pipeline Kanban (drag-drop, 6 columns)
- [x] Metrics panel (4 KPIs, distribution chart)

### Day 3: Voice & Polish
- [x] VoiceCommand component (mic demo, quick commands)
- [x] Egyptian/Kemet theme styling
- [x] Responsive layout
- [x] Production build

### Day 4: Demo Prep (Claude Code sealed it)
- [x] CaseDetail component — pipeline progress, interaction log, case notes
- [x] Real Web Speech API (Chrome/Edge mic, interim results, visual waveform)
- [x] Smart Hermes responses (urgency, pipeline value, consult schedule, UCC, Trust)
- [x] Lead click-through from LiveLeads + Pipeline → CaseDetail
- [x] Loading skeleton states
- [x] vercel.json SPA routing config
- [x] Production build passing (37 modules, 175KB JS)
- [ ] Deploy to Vercel (run: cd prototype && npx vercel --prod)
- [ ] Record demo video (optional)

**Deliverable:** Live dashboard demo for Wednesday

---

## Phase 2: Integration (Week 1)

### Tasks
- [ ] Set up VPS (client-owned)
- [ ] PostgreSQL database
- [ ] Node.js API bridge
- [ ] Deploy Hermes agent
- [ ] First 3 FastMCP skills:
  - [ ] intake_commercial_law
  - [ ] lead_urgency_scorer
  - [ ] email_drafter
- [ ] End-to-end test: Telegram → Hermes → Dashboard

**Deliverable:** Real lead flows through system

---

## Phase 3: Optimization (Weeks 2-4)

### Week 2: Voice & Analytics
- [ ] Real voice recognition (Web Speech API)
- [ ] Advanced metrics (cohort analysis, forecasting)
- [ ] Case pattern analyzer skill
- [ ] Discharge protocol skill

### Week 3: Automation
- [ ] Auto-follow-up sequences
- [ ] Smart lead routing
- [ ] Calendar integration
- [ ] Document generation

### Week 4: Hardening
- [ ] Security audit
- [ ] Load testing
- [ ] Documentation
- [ ] Handoff to Mr. Garcia

**Deliverable:** Production-ready system

---

## Current Status

**Phase:** Prototype  
**Progress:** 98%  
**Next:** Deploy to Vercel (`cd prototype && npx vercel --prod`) — then it's demo-ready for Mr. Garcia.
