# YBTM Tech Stack & Skills

## Core Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18 + TypeScript + Tailwind CSS |
| Build Tool | Vite |
| State | React hooks (prototype) → Zustand (production) |
| API | REST (fetch) |
| Icons | Inline SVG |
| Fonts | Google Fonts (Cinzel, Inter) |

## FastMCP Skills (Layer 2-3 Moat)

### 1. intake_commercial_law
**Trigger:** New lead mentions UCC, securitization, discharge
**Procedure:**
1. Ask jurisdiction (state)
2. Ask debt type (credit card, mortgage, student loan)
3. Ask if they've filed UCC-1
4. Ask timeline (how old is the debt)
5. Score urgency 1-10

**Output:** Structured intake object + urgency score

### 2. lead_urgency_scorer
**Trigger:** After intake completion
**Inputs:**
- Debt amount
- Days until legal action
- Previous attempts
- Income stability
- Jurisdiction (some states more creditor-friendly)

**Output:** 1-10 urgency score with reasoning

### 3. case_pattern_analyzer
**Trigger:** Weekly batch (Sundays)
**Procedure:**
1. Analyze closed cases (won/lost)
2. Extract patterns (which service types convert best)
3. Update skill memory
4. Report insights to dashboard

**Output:** Weekly insight report

### 4. discharge_protocol
**Trigger:** Lead retained for UCC discharge
**Procedure:**
1. Verify securitization (request PSA)
2. Check trust verification
3. Draft notice of dispute
4. Track response timeline
5. Escalate if no response in 30 days

**Output:** Step-by-step guidance + document drafts

### 5. email_drafter
**Trigger:** Any email need
**Procedure:**
1. Read case context
2. Draft response that:
   - Educates (teaches commercial law concept)
   - Qualifies (asks follow-up question)
   - Sets expectation (timeline, next steps)

**Output:** Draft email + send confirmation

---

## API Endpoints

```
GET  /api/leads              → Lead[]
GET  /api/leads/:id          → Lead
POST /api/leads              → Create lead (from Hermes)
PUT  /api/leads/:id/status   → Update status
GET  /api/cases              → Case[]
GET  /api/metrics            → Metrics
POST /api/voice-command      → { response, action }
GET  /api/interactions       → InteractionLog[]
```

---

## Database Schema

```sql
-- leads
CREATE TABLE leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source VARCHAR(20) NOT NULL,
  name VARCHAR(100) NOT NULL,
  phone VARCHAR(20),
  email VARCHAR(100),
  service_type VARCHAR(50) NOT NULL,
  urgency_score INTEGER CHECK (urgency_score BETWEEN 1 AND 10),
  status VARCHAR(20) DEFAULT 'new',
  timestamp TIMESTAMP DEFAULT NOW(),
  message TEXT
);

-- cases
CREATE TABLE cases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID REFERENCES leads(id),
  service_type VARCHAR(50) NOT NULL,
  value INTEGER,
  intake_date TIMESTAMP,
  close_date TIMESTAMP,
  outcome VARCHAR(10)
);

-- interaction_logs
CREATE TABLE interaction_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  timestamp TIMESTAMP DEFAULT NOW(),
  platform VARCHAR(20) NOT NULL,
  message TEXT NOT NULL,
  hermes_response TEXT NOT NULL,
  lead_id UUID REFERENCES leads(id)
);
```

---

## Future: Hyperspace P2P (Week 5+)

Optional optimization:
- Run Hyperspace node on VPS
- Route routine inferences to P2P (free)
- Claude API as fallback
- Zero cost, potential upside
