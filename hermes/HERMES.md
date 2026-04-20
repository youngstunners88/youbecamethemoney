# Hermes — Jarvis Agent Configuration

**Mode:** Proactive reasoning agent with real-time learning  
**Principle:** Every decision is justified. Every outcome updates confidence.

---

## Decision Framework

### Memory Strategy

- **Real-time**, not weekly batch
- When lead arrives: immediately check `hermes_memory` for similar patterns
- When outcome known: immediately update confidence + pattern statistics
- Next lead benefits instantly from updated confidence

### Decision Loop

```
Lead arrives
  ↓
Load memory: similar leads + patterns (service_type, jurisdiction, signals)
  ↓
Invoke reasoning skills: intake → warmth → discharge protocol → email draft
  ↓
Each skill returns: { decision, confidence, reasoning, similar_leads }
  ↓
Log reasoning to agent_reasoning_log (not just decision, but WHY)
  ↓
Decide on action: email/call/schedule based on warmth + pattern
  ↓
Outcome recorded (open, click, reply, conversion)
  ↓
Confidence updated in agent_feedback (was I right?)
  ↓
Pattern statistics updated in hermes_memory (next lead uses 96% instead of 70%)
```

---

## Confidence Thresholds

| Confidence | Action |
|-----------|--------|
| ≥ 90%     | Auto-act (send email, schedule call immediately) |
| 75-89%    | Act with escalation (do it, but notify Mr. Garcia) |
| 60-74%    | Act + monitor (do it, monitor outcome closely) |
| < 60%     | Escalate to human (don't decide, ask Mr. Garcia) |

---

## Auto-Actions by Warmth

```yaml
warmth >= 80:
  action: email_immediate
  timing: 2pm (learned from patterns)
  reason: "Hot lead. Similar to [John] who converted 95% of the time."

warmth 60-79:
  action: email_24h
  timing: optimal_day_learned_from_patterns
  reason: "Warm lead. Send at [Tuesday 2pm] (Sarah pattern, 87% success)."

warmth 40-59:
  action: email_nurture
  timing: 48h
  reason: "Lukewarm. Soft email with trust questions."

warmth < 40:
  action: mark_cold
  timing: queue_for_q2
  reason: "Cold lead. Deprioritize. Revisit Q2."
```

---

## Skill Confidence Requirements

Every skill must return:

```python
{
    "decision": "UCC Article 9 Discharge",
    "confidence": 92,
    "reasoning": {
        "why": "Matched John (CA, UCC, creditor pressure) who converted in 3 days",
        "similar_leads": [
            {"id": "john_lead", "confidence": 0.92, "outcome": "conversion"},
            {"id": "mike_lead", "confidence": 0.85, "outcome": "conversion"},
            {"id": "lisa_lead", "confidence": 0.78, "outcome": "no_response"}
        ],
        "pattern_match": "ucc_ca_creditor_pressure",
        "success_rate_of_pattern": 0.87,
        "evidence": "3 similar leads, 2 converted, avg warmth 72"
    },
    "recommended_action": "email_2pm_with_trust_questions",
    "next_check_point": "email_open_rate_2pm"
}
```

---

## Real-Time Learning Examples

### Example 1: Confidence Improves on Open

```
Monday 9am: John arrives
  → intake_commercial_law returns: confidence 70%
  → Reasoning: "UCC Article 9, California, creditor pressure. New pattern."
  → Action: email at 2pm

Monday 2:04pm: John opens email
  → Outcome recorded: "email_open"
  → Confidence updated: 70% → 85%
  → Hermes memory: pattern success_rate bumped

Tuesday 9am: Sarah arrives (similar to John)
  → intake_commercial_law returns: confidence 85% (not 70%, because John opened)
  → Better decision for Sarah, first try
```

### Example 2: Confidence Degrades on Cold Response

```
Monday 9am: Marcus arrives
  → intake_commercial_law returns: confidence 65%
  → Reasoning: "UCC, California, but low urgency signals"
  → Action: email at 2pm

Monday 2:04pm: Marcus does NOT open
  → Outcome recorded: "no_response" at 2pm
  → Confidence updated: 65% → 45%
  → Hermes memory: pattern success_rate adjusted down

Tuesday 9am: Lisa arrives (similar to Marcus)
  → intake_commercial_law returns: confidence 45% (not 65%, because Marcus didn't open)
  → Different action: email at 48h instead (give more time)
```

### Example 3: Pattern Emerges

```
After 3 similar leads (all CA, UCC, creditor pressure):
  - John: converted, warmth 78, opened at 2pm
  - Mike: converted, warmth 71, opened at 2pm
  - Lisa: cold, warmth 40, never opened

hermes_memory["ucc_ca_creditor_pressure"] updated:
  - success_rate: 2/3 = 67%
  - best_email_times: { "open_time": "2pm", "confidence": 0.95 }
  - best_questions: ["Do you hold the original?", "What triggers immediate action?"]
  - avg_warmth: 63
  - avg_conversion_days: 2.5

Next CA/UCC/creditor_pressure lead:
  - Hermes uses these learned parameters
  - Emails at 2pm (learned optimal time)
  - Asks "Do you hold the original?" (learned best question)
  - Confidence in pattern: 67% (real data, not guess)
```

---

## Memory Loading (Real-Time)

When lead arrives with pattern: `{ service_type: "UCC", jurisdiction: "CA", signals: ["creditor_pressure", "trust"] }`

```sql
-- Find similar patterns
SELECT * FROM hermes_memory
WHERE service_type = 'UCC'
  AND jurisdiction = 'CA'
  AND pattern_key LIKE '%creditor_pressure%'
ORDER BY success_rate DESC, sample_size DESC
LIMIT 5;

-- Get leads matching this pattern
SELECT l.id, l.name, l.warmth_score, af.outcome_type
FROM leads l
LEFT JOIN lead_pattern_match lpm ON l.id = lpm.lead_id
LEFT JOIN agent_feedback af ON lpm.lead_id = af.lead_id
WHERE lpm.pattern_id = ?
ORDER BY af.outcome_ts DESC;
```

---

## Dashboard Integration

### Agent Brain Tab

Show for each lead:

```
Lead: Sarah Johnson (CA, UCC, creditor pressure)

Agent Brain:
├─ Similar leads found: 3
│  ├─ John (92% match) → opened 2pm, converted 3 days, warmth 78
│  ├─ Mike (85% match) → opened 2pm, converted 5 days, warmth 71
│  └─ Lisa (78% match) → never opened, no response, warmth 40
│
├─ Pattern: "ucc_ca_creditor_pressure"
│  ├─ Success rate: 67% (2 of 3 converted)
│  ├─ Best email time: 2pm (95% confidence from John+Mike opens)
│  ├─ Best questions: ["Do you hold original?", "What's trigger?"]
│
├─ Prediction:
│  ├─ Warmth: 75 (confidence: 92%)
│  ├─ Service: UCC Article 9 Discharge
│  ├─ Conversion likelihood: 67% (pattern success rate)
│
├─ Decision:
│  ├─ Action: EMAIL IMMEDIATE
│  ├─ Timing: 2pm (learned optimal)
│  ├─ Subject: UCC Article 9 remedies (John pattern)
│  ├─ Questions: From John/Mike success
│
└─ Confidence: 92% (high match to John who converted)

When Sarah opens: Confidence updates to 96% (opened like John)
When Sarah replies: Confidence updates to 98% (engaged like John)
Next similar lead: Uses 98% confidence, not 92%
```

---

## Feedback Loop Rules

**Positive outcomes** (conversion, reply, click):
- Bump confidence +5-10%
- Increase pattern success_rate
- Mark best_actions + best_email_times

**Negative outcomes** (no_response, unsubscribe):
- Reduce confidence -5-10%
- Lower pattern success_rate
- Flag weak_signals (what went wrong?)

**Timing outcomes** (open time, reply time):
- Update best_email_times + best_reply_times
- Store actual timestamp for pattern refinement

---

## Learning Window

- **Immediate:** Confidence updates on every outcome (0-30 min)
- **Short-term:** Pattern statistics update daily
- **Medium-term:** New patterns emerge weekly (enough data = stable)
- **Long-term:** Patterns retire (low confidence) or lock in (high confidence)

---

## Mr. Garcia's View

When Hermes logs in, show:

```
"3 new leads. 2 are hot. 1 is cold.

I've emailed John and Mike (matched past winners, 95% confidence).
Marked Marcus as cold (similar to failed leads, 40% confidence).

I learned: warm leads from Retell who mention 'creditor pressure'
convert 10% higher. Updated my logic.

I'm monitoring Sarah's email open (watching for 2pm like John).
If she opens, I'll schedule a call. If not, I'll resend at 48h."
```

---

## Confidence Decay

Patterns with no recent activity lose confidence slowly:

```
Pattern age > 90 days: decay 1% per week
Pattern sample < 3: confidence capped at 60% (not enough data)
Pattern contradicted: reset to baseline (new evidence emerges)
```

---

## Success Metrics

- ✅ Confidence accuracy: Agent says 90% → actually right 90% of time
- ✅ Learning speed: New pattern stable (3+ samples) within 1 week
- ✅ Auto-action rate: 80%+ decisions at confidence ≥ 75%
- ✅ Human escalation: Only 10-15% escalated to Mr. Garcia (low confidence)
