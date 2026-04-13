# Layer 3: Learning Engine Architecture

**Status**: Design Phase (Implementation follows)  
**Purpose**: System that improves itself without human intervention  
**Constraint**: Local computation, minimal API calls, scheduled execution

---

## System Philosophy

**Not**: "Let's automate more"  
**Yes**: "Let's learn from what works, then do more of it"

Every week:
1. Collect data from last 7 days
2. Extract patterns (3 modules analyze independently)
3. Generate insights (local computation only)
4. Push insights → Hermes (system prompt injection)
5. Measure impact
6. Repeat

---

## Folder Structure

```
optimization/
├── layer3/
│   ├── __init__.py
│   ├── README.md
│   ├── config.py                      # Constants, thresholds
│   ├── db_schema.py                   # SQLite for insights
│   │
│   ├── data_layer/
│   │   ├── __init__.py
│   │   ├── collector.py               # Pulls from Retell API, PostgreSQL
│   │   ├── cleaner.py                 # Formats transcripts, timestamps
│   │   └── models.py                  # Pydantic schemas (structured data)
│   │
│   ├── learning_modules/
│   │   ├── __init__.py
│   │   ├── conversion_predictor.py    # "Will this lead close?"
│   │   ├── optimal_timing.py          # "Best time to call?"
│   │   ├── script_optimizer.py        # "Better script phrases?"
│   │   └── quality_scorer.py          # Agent performance grading
│   │
│   ├── feedback_loop/
│   │   ├── __init__.py
│   │   ├── insight_engine.py          # Combines all 3 modules
│   │   ├── action_mapper.py           # Insights → Hermes actions
│   │   └── hermes_api.py              # Send decisions to Hermes
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── insights_db.py             # SQLite: patterns learned
│   │   ├── cache.py                   # Local cache (60 min TTL)
│   │   └── schemas.sql                # DB schema
│   │
│   └── run.py                         # Entry point (scheduler calls this)
```

---

## Data Collection Layer

### What We Capture
```
Per Call:
├── call_id (unique)
├── lead_id
├── timestamp (start)
├── duration_seconds
├── lead_temperature (hot/warm/luke/cold)
├── lead_source (web/telegram/sms/organic)
├── service_type (UCC/Securitization/etc)
├── transcript (full dialogue)
├── outcome (completed/failed/no_answer)
├── agent_sentiment (extracted from words)
└── prospect_sentiment (extracted from words)

Per Lead Outcome:
├── lead_id
├── status_before (new/qualified/consulting)
├── status_after (consulting/retained/closed-won/closed-lost)
├── case_value (if won)
├── days_to_close
└── service_type
```

### Schema (SQLite)

```sql
-- Layer 3 Learning Database (separate from production)

CREATE TABLE call_records (
  id TEXT PRIMARY KEY,
  lead_id TEXT,
  timestamp DATETIME,
  duration_seconds INT,
  lead_temperature VARCHAR(10),
  lead_source VARCHAR(20),
  service_type VARCHAR(50),
  transcript TEXT,
  outcome VARCHAR(20),          -- completed, failed, no_answer
  agent_sentiment_score FLOAT,  -- 0-1
  prospect_sentiment_score FLOAT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE lead_outcomes (
  id TEXT PRIMARY KEY,
  lead_id TEXT,
  lead_temp_at_call VARCHAR(10),
  status_before VARCHAR(20),
  status_after VARCHAR(20),
  case_value DECIMAL(10,2),
  days_to_close INT,
  service_type VARCHAR(50),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE learned_patterns (
  id TEXT PRIMARY KEY,
  module VARCHAR(30),           -- conversion_predictor, optimal_timing, script_optimizer
  pattern_type VARCHAR(50),     -- e.g., "best_call_time", "high_close_phrase"
  pattern_data JSON,
  confidence FLOAT,             -- 0-1
  samples_count INT,            -- how many data points informed this
  created_at DATETIME,
  last_updated DATETIME
);

CREATE TABLE improvement_log (
  id TEXT PRIMARY KEY,
  week_number INT,
  module VARCHAR(30),
  insight TEXT,
  action_taken TEXT,            -- What Hermes did differently
  impact_metric FLOAT,          -- % improvement
  created_at DATETIME
);
```

---

## Learning Modules (Core)

### Module 1: conversion_predictor.py

**Purpose**: Predict if a lead will close based on call patterns

**Inputs**:
```python
class PredictionRequest:
    lead_temperature: str          # hot, warm, luke, cold
    service_type: str              # UCC Discharge, etc
    call_duration: int             # seconds
    source: str                    # web, sms, organic
    agent_sentiment: float         # 0-1 (extracted from transcript)
    prospect_sentiment: float      # 0-1
    previous_conversions: int      # How many leads with same profile closed?
```

**Output**:
```python
class ConversionPrediction:
    close_probability: float       # 0-1 (e.g., 0.78 = 78% likely to close)
    confidence: float              # 0-1 (how sure are we?)
    reason: str                    # "High temp + long call + happy sentiment"
    recommended_action: str        # "Schedule immediately", "Nurture", "Archive"
```

**Algorithm** (Naive Bayes over historical data):
```
close_prob = P(closed | hot_temp, long_call, high_sentiment)
           = P(closed AND hot) / P(hot)

Update weekly with new closed cases.
```

**Example**: 
- 142 past hot leads with long calls (>8min) → 89 closed
- → P(close | hot + long) = 89/142 = 63% base rate
- Adjustments: positive sentiment +15%, weekday calls +8%
- Final: 0.63 × 1.15 × 1.08 = 0.78 probability

---

### Module 2: optimal_timing.py

**Purpose**: Identify best time to call each lead type

**Inputs**:
```python
class TimingAnalysis:
    lead_source: str              # web, organic, sms
    service_type: str             # UCC Discharge, etc
    lead_temperature: str         # hot, warm, luke, cold
    prospect_timezone: str        # America/New_York, etc
```

**Output**:
```python
class OptimalTiming:
    best_hour: int                # 0-23 (e.g., 9 = 9am)
    best_day: str                 # Monday, Tuesday, etc
    success_rate_at_time: float   # 0-1 (e.g., 0.82)
    worst_hour: int               # Avoid this
    samples: int                  # How many calls informed this
```

**Algorithm** (Empirical time binning):
```
For each hour (0-23):
  success_rate[hour] = completed_calls[hour] / total_calls[hour]
  
For each day (Mon-Sun):
  success_rate[day] = completed_calls[day] / total_calls[day]

Best = highest success_rate
Worst = lowest success_rate
```

**Example**:
```
Hot leads (UCC Discharge) called at 9-11am: 87% success
Hot leads called at 6-8pm: 43% success
→ Recommendation: Schedule all hot UCC calls 9-11am
```

---

### Module 3: script_optimizer.py

**Purpose**: Find phrases that work, suggest improvements

**Inputs**:
```python
class ScriptAnalysis:
    call_outcomes: List[dict]     # [{transcript, outcome, sentiment}, ...]
    service_type: str
    agent_name: str               # "Margarita"
```

**Output**:
```python
class ScriptInsights:
    high_performing_phrases: List[str]    # Phrases in 80%+ close rate calls
    low_performing_phrases: List[str]     # Phrases in <30% close rate calls
    recommended_changes: List[str]        # Specific improvements
    new_system_prompt: str                # Updated agent instruction
    impact_estimate: float                # Expected close rate ↑ from changes
```

**Algorithm** (Phrase-outcome correlation):
```
For each unique phrase in transcripts:
  close_rate = calls_with_phrase_that_closed / total_calls_with_phrase
  
If close_rate > 0.75:
  Add to "high_performing"
  
If close_rate < 0.35:
  Add to "low_performing" (remove or replace)
```

**Example**:
```
High-performing phrases:
- "What's your current situation with debt?" → 84% close
- "The force of nature is with you" → 79% close
- "UCC Article 3 gives you leverage" → 81% close

Low-performing phrases:
- "Is this a good time?" → 18% close (too timid)
- "I'm sure you're busy" → 22% close (assumes rejection)

Recommendation:
Replace "Is this a good time?" with "Let me show you how UCC works"
Remove "I'm sure you're busy"
```

---

## Feedback Loop Engine

### Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    WEEKLY CYCLE (Sunday 2am)                 │
└──────────────────────────────────────────────────────────────┘

1. DATA COLLECTION (Run once/week)
   ├─ Pull last 7 days of call data from Retell API
   ├─ Pull lead outcomes from PostgreSQL
   └─ Store in Layer3 SQLite (insights_db.db)

2. LEARNING MODULES (Run in parallel)
   ├─ conversion_predictor.py
   │  └─ Output: "Hot + long calls + sentiment = 78% close"
   ├─ optimal_timing.py
   │  └─ Output: "Best time: 9-11am weekdays"
   └─ script_optimizer.py
      └─ Output: "Replace X phrase with Y phrase"

3. INSIGHT ENGINE (Combine results)
   ├─ Rank insights by confidence × impact
   ├─ Filter contradictions
   └─ Generate 3-5 actionable changes

4. ACTION MAPPER (Convert → Hermes commands)
   ├─ Insight: "Hot leads have 78% close at 9-11am"
   │  Action: "Prioritize hot leads in 9-11am slot"
   │
   ├─ Insight: "Phrase 'Is this a good time?' = 18% close"
   │  Action: "Update Margarita system prompt (remove phrase)"
   │
   └─ Insight: "Web-sourced leads close faster than SMS"
       Action: "Route web leads to senior agent Margarita"

5. HERMES API (Push decisions)
   ├─ POST /hermes/update-prompt
   │  {"agent": "margarita", "new_instructions": "..."}
   │
   ├─ POST /hermes/update-routing
   │  {"rule": "hot_leads", "schedule_window": "9-11am"}
   │
   └─ POST /hermes/update-parameters
       {"lead_scoring": "conversion_predictor_v3"}

6. MEASUREMENT (Track impact)
   ├─ Next 7 days: Measure close rate
   ├─ Compare vs baseline
   └─ Store in improvement_log table

7. FEEDBACK (Close loop)
   └─ "New script boosted close rate 6% week-over-week"
```

---

## Hermes Integration

### When Layer 3 Calls Hermes (NOT every call)

**Rule: Only act if confidence > 75% AND sample_size > 30**

| When | What | Frequency |
|------|------|-----------|
| Weekly (Sunday 2am) | Major improvements | Scheduled |
| After 100 calls | Recalibrate scoring | Triggered |
| If metric drops 10% | Emergency adjustment | Alert-based |
| Never | Per-call micro-adjustments | Don't do this |

### Example: Margarita Gets Smarter

**Week 1 (Baseline)**:
```
Margarita System Prompt v1.0:
"You are a professional intake specialist. Ask about their situation, 
teach about UCC, detect temperature, provide CTA based on interest."
→ Close rate: 18.5%
```

**Week 2 (After Layer 3 Analysis)**:
```
Margarita System Prompt v1.1:
"You are a professional intake specialist. 
[NEW] Start with: 'What's your current situation with debt?'
[NEW] When they show interest, say: 'The force of nature is with you'
[NEW] For hot prospects, immediately offer: 'Schedule with Daniel this week?'
[REMOVE] Stop asking 'Is this a good time?'
[REMOVE] Stop saying 'I'm sure you're busy'"
→ Close rate: 21.2% (+2.7%)
```

**Week 3 (After Timing Optimization)**:
```
Lead Router updated:
[NEW] Hot leads: Prioritize 9-11am calls (87% success window)
[NEW] Warm leads: 1-3pm follow-ups (best for nurturing)
[NEW] Cold leads: Batch email campaigns (avoid expensive calls)
→ Close rate: 24.1% (+2.9%)
→ Cost per lead: Down 18%
```

---

## Efficiency Strategy (Critical)

### API Usage Limits

**Per Week**:
- Retell API: 1 call (pull last 7 days data) ✓
- PostgreSQL: 1 query (pull outcomes) ✓
- Browser tools: 0 (unnecessary) ✓
- Claude API: 0 (use local ML) ✓

**Total cost impact**: ~$0.02/week (just the data pulls)

### Computation Strategy

**Real-Time** (NOT DONE):
- No per-call ML inference
- No transcript analysis during call

**Scheduled Weekly** (DONE ONCE):
- Batch analysis of 7 days data
- All 3 learning modules run in 2-3 minutes
- Store insights (reuse entire week)

**Cached** (DONE ONCE):
- Last 7 days patterns cached for 1 week
- Insight score cached
- Routing rules cached
- No recomputation until next Sunday

### Example Costs

```
Monday-Saturday (6 days):
- 0 API calls for learning
- 0 ML inference
- Cost: $0

Sunday 2am (1 day):
- 1 Retell API call: $0.001 (if charged)
- 1 PostgreSQL query: $0
- Local ML computation: $0 (runs in 2 min on server)
- Send 3 prompts to Hermes: $0 (internal API)
- Cost: ~$0.001

Weekly total: $0.001 (negligible)
```

---

## Example: Full Loop (Lead → Learning → Improvement)

### Day 1: Lead Arrives
```
Lead: John (web source, UCC Discharge interested)
Margarita calls Monday 2pm → Failed to answer
→ SMS fallback sent
```

### Day 2: Lead Calls Back
```
Tuesday 10am: John calls back
Margarita: "What's your current situation?"
John: "I have a securitization issue..."
Margarita: "The force of nature is with you. Would you like to..."
Result: RETAINED (John books consultation)
Call logged to insights_db.db
```

### Day 7: Layer 3 Analysis Runs
```
Week's data: 147 calls analyzed
- 32 hot temperature
- 89 hot leads → 71 retained (80% close!)
- 71 calls at 9-11am → 68 completed (96% success)
- 71 calls at 6pm → 52 completed (73% success)

conversion_predictor output:
{
  "high_probability_signals": [
    "hot_temp + 9-11am = 96%",
    "phrase 'force of nature' = 84% close",
    "UCC service type = 81% close"
  ]
}

script_optimizer output:
{
  "high_performers": [
    "What's your current situation? → 84% close",
    "The force of nature is with you → 79%"
  ],
  "low_performers": [
    "Is this a good time? → 18% close (REMOVE)"
  ]
}

optimal_timing output:
{
  "best_window": "9-11am weekdays",
  "success_rate": 0.96,
  "avoid_window": "5-7pm",
  "success_rate": 0.63
}
```

### Day 7 Evening: Hermes Gets Updated
```
Insight Engine combines:
- "Hot leads at 9-11am = 96% success" → Priority action
- "Remove 'Is this a good time?'" → Script change
- "Web-sourced leads = fastest close" → Routing change

Actions taken:
1. Update Margarita prompt (remove timid phrases)
2. Route hot leads to 9-11am window
3. Promote web leads to priority queue

Result: Next week's close rate jumps 2.7%
```

### Week 2: John's Lead Closes
```
Daniel does consultation
John becomes client (case value: $3,200)
Lead marked closed-won
→ Feeds back into learned_patterns
→ Confirms "9-11am hot = high value clients"
```

---

## System Improves Over Time

| Week | Close Rate | Avg Call Time | Quality | Cost/Lead | How |
|------|-----------|--------------|---------|-----------|-----|
| 1 | 18.5% | Manual | Varies | $12 | Baseline |
| 2 | 21.2% | 6m42s | Better | $11 | Script v1.1 |
| 3 | 24.1% | 6m15s | Improved | $9.80 | Timing optimization |
| 4 | 26.8% | 5m50s | Refined | $8.20 | Routing optimization |
| 5 | 28.3% | 5m30s | Excellent | $7.10 | Combined learning |
| 8 | 35.2% | 4m20s | Outstanding | $4.50 | 8 weeks of compounding |
| 12 | 42.1% | 3m50s | Expert-level | $2.80 | 3 months of improvement |

**Each week improves the system**:
- Better script → More closures
- Smarter timing → Fewer wasted calls
- Refined routing → Right person, right time
- Cost drops → Margins improve
- Quality rises → Reputation improves

---

## Key Principles

1. **Simplicity**: 3 learning modules, not 30
2. **Leverage**: Analyze past data, improve future behavior
3. **Compounding**: Each improvement builds on last
4. **Efficiency**: 1 API call/week, local ML
5. **Actionability**: Every insight → Hermes action
6. **Measurement**: Track impact, prove it works

---

## Browser Tools Strategy

### When to Use browser-use (Cloud)
- Rare: Only when pulling external data not in our system
- Example: "Get competitor pricing from website"
- Frequency: 0-1x per month (if at all)

### When to Use chrome-devtools-mcp (Local)
- Never needed initially
- Possible later: Automate Retell dashboard pulls
- Only if API calls not available

### When to Avoid Both
- 99% of Layer 3 operations
- All ML/learning happens locally
- All Hermes communication is API-to-API

---

**Next: Implementation** (Code skeletons + full working example)
