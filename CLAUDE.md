# You Became The Money

**Project:** AI command center for Daniel Garcia's commercial law practice  
**Stack:** React | PostgreSQL | Hermes Agent (Jarvis Mode) | FastMCP | Node.js API  
**Architecture:** Proactive reasoning agent + real-time learning (not reactive dashboard)

---

## Core Design (Jarvis Mode)

**Old Model:** Dashboard + logging  
**New Model:** Agent reasoning + real-time learning + confidence scoring

| Aspect | Old | New |
|--------|-----|-----|
| Memory | Weekly batch | Real-time, every interaction |
| Learning | Pattern reports | Confidence updates immediately |
| Hermes | Responds | Anticipates + decides |
| Skills | Log decisions | Justify + learn from outcomes |
| Dashboard | Shows data | Shows agent reasoning |

---

## Key Files

- **HERMES.md** — Agent decision framework (confidence thresholds, auto-actions, memory strategy)
- **CONTEXT.md** — Data model, skills, success metrics
- **database/migrations/004_agent_reasoning.sql** — Agent brain schema (reasoning_log, feedback, hermes_memory)
- **hermes/skills/*.py** — All 5 skills now return: { decision, confidence, reasoning, similar_leads }

---

## Key Rules (Jarvis Mode)

1. **Every decision must be justified** — Not "Lead is hot" but "Lead is hot because: matched John (CA, UCC, creditor pressure) who converted 95% of the time"
2. **Confidence is currency** — Confidence < 60% → escalate to human. Confidence ≥ 90% → auto-act.
3. **Learn from every outcome** — Lead opens email → confidence updates immediately → next lead benefits
4. **Real-time memory** — No weekly batch. When lead arrives, instantly check hermes_memory for similar patterns.
5. **All interactions logged** — Every skill call, every reasoning, every outcome goes to agent_reasoning_log + agent_feedback

---

## Workflow (Jarvis Mode)

```
Lead arrives
  ↓
Load hermes_memory: find similar leads (service_type, jurisdiction, signals)
  ↓
Invoke all 5 skills in parallel:
  - intake_commercial_law: returns fit_score + confidence
  - lead_urgency_scorer: returns urgency + recommended timing
  - case_pattern_analyzer: returns pattern match + success rate
  - discharge_protocol: returns protocol + estimated timeline
  - email_drafter: returns draft + predicted open rate
  ↓
Log reasoning to agent_reasoning_log (confidence, why, similar_leads)
  ↓
Decide: auto-act (confidence ≥ 90%) or escalate (confidence < 60%)
  ↓
Outcome recorded (open, click, reply, conversion)
  ↓
Confidence updated in agent_feedback
  ↓
hermes_memory updated (success_rate, best_timing, best_questions)
  ↓
Next similar lead uses 95% confidence instead of 70%
```

---

## Success = Jarvis Behavior

When Mr. Garcia logs in, Hermes says:

> "3 new leads. 2 are hot (matching past winners, 95% confidence).
> I'm emailing them now (best time based on John pattern).
> 1 is cold. Marked for Q2.
> 
> I learned: warm leads from Retell who mention 'trust'
> convert 10% higher. Updated my logic for next lead."

---

## Start Here

Read **HERMES.md** first (decision framework).  
Then read **CONTEXT.md** (data model, skills).  
Then check **database/migrations/004_agent_reasoning.sql** (schema).

