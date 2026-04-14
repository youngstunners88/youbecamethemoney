# YBTM Voice Agent Implementation Guide

**Status**: ✅ Complete
**Date**: April 13, 2026
**API Key**: key_d0ac8de0d3f1643bcff4f12e7ae4

---

## What We Built

A complete voice-first lead qualification system for Daniel Garcia's You Became The Money practice.

### Core Components

#### 1. **Retell API Integration** ✅
- Voice call orchestration
- Inbound/outbound call handling
- Transcription capture
- Webhook integration for call completion

**Location**: `integration/src/clients/retell.js`

#### 2. **Communication Fallback Strategy** ✅
- Phone call first (3-second timeout)
- SMS fallback via Twilio
- Email fallback via SendGrid
- All interactions logged in PostgreSQL

**Location**: `integration/src/handlers/communicationFallback.js`

**Flow**:
```
Lead created
    ↓
POST /api/leads/:id/initiate-outreach
    ↓
Try: Retell phone call
    ├─ Success? → Call initiated (temperature detected after)
    └─ Timeout (3s)? → Try SMS
        ├─ Success? → SMS sent
        └─ Failed? → Try Email
            ├─ Success? → Email sent
            └─ Failed? → Log as unreachable
```

#### 3. **Categorical Lead Scoring** ✅
Four-tier temperature system:
- **🔥 HOT**: Ready to hire, asks pricing, wants next steps
- **🌡️ WARM**: Interested, problem-aware, asking questions
- **❄️ LUKE**: Curious but hesitant, wants to think
- **❄️❄️ COLD**: Not interested, wrong number

Automatically detected from voice call transcript using keyword analysis + decision-readiness scoring.

**Location**: `optimization/lead_qualifier.py`

#### 4. **Voice Agent Configuration** ✅
System prompt for Retell that:
- Opens with professional greeting
- Asks 3 qualifying questions (2 min)
- Teaches 1 relevant concept (2 min)
- Detects temperature signals (2 min)
- Provides appropriate CTA
- Captures contact info at close
- Embeds Daniel Garcia's framework

**Location**: `integration/src/prompts/voiceAgent.js`

#### 5. **Database Schema** ✅
PostgreSQL schema with:
- **leads** table: Core lead info + temperature
- **calls** table: Retell call records + detected temperature
- **interaction_logs** table: All touchpoints (phone/SMS/email)
- **cases** table: Outcome tracking

**Deployed**: `integration/src/db/init.js`

---

## API Endpoints

### Lead Management
```bash
# Create a lead
POST /api/leads
{
  "source": "web|telegram|whatsapp|discord|cli",
  "name": "John Smith",
  "phone": "+12125551234",
  "email": "john@example.com",
  "serviceType": "UCC Discharge",
  "message": "Interested in your services"
}

# Get all leads (with filters)
GET /api/leads?status=new&temperature=hot&limit=50

# Get single lead
GET /api/leads/:leadId

# Update lead temperature
PUT /api/leads/:leadId/temperature
{ "temperature": "warm" }

# Initiate multi-channel outreach
POST /api/leads/:leadId/initiate-outreach
{ "voiceAgentId": "agent_12345" }
# Response: { method: "phone|sms|email", success: true }

# Get lead's call history
GET /api/leads/:leadId/calls

# Get lead's interaction log
GET /api/leads/:leadId/interactions
```

### Voice/Retell Management
```bash
# Get voice agent config
GET /api/voice/agent/config

# Create voice agent (custom)
POST /api/voice/agent/create
{
  "name": "Custom Agent",
  "systemPrompt": "Your custom prompt...",
  "voiceId": "professional"
}

# Get call transcript
GET /api/voice/calls/:callId/transcript

# Webhook (Retell → your API)
POST /api/voice/webhook/call-ended
# Retell sends: { call_id, user_id, call_status, transcript, duration_seconds }
```

### Metrics/Dashboard
```bash
# Full metrics
GET /api/metrics
# Returns: { totalLeads, conversionRate, hotLeads, warmLeads, etc. }

# By temperature
GET /api/metrics/temperature
# Returns: { hot: 5, warm: 12, luke: 8, cold: 2 }

# By status
GET /api/metrics/status
# Returns: { new: 15, qualified: 8, consulting: 3, retained: 1 }

# Call performance
GET /api/metrics/calls
# Returns: { total_calls, completed, failed, avg_duration, hot_leads, ... }
```

---

## Quick Start

### 1. Setup Database

```bash
# Create PostgreSQL database
createdb ybtm

# Run migrations (auto on first server start)
npm run dev
# Server creates tables automatically
```

### 2. Configure Environment

```bash
cd integration
cp .env.example .env

# Edit .env with:
DATABASE_URL=postgresql://user:password@localhost:5432/ybtm
RETELL_API_KEY=key_d0ac8de0d3f1643bcff4f12e7ae4
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
SENDGRID_API_KEY=your_key
```

### 3. Start Server

```bash
npm install
npm run dev
```

Server runs on `http://localhost:3000`

### 4. Test Flow

```bash
# Create test lead
curl -X POST http://localhost:3000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "source": "web",
    "name": "Test User",
    "phone": "+12125551234",
    "email": "test@example.com",
    "serviceType": "UCC Discharge"
  }'

# Copy the returned lead ID

# Initiate outreach (will try phone → SMS → email)
curl -X POST http://localhost:3000/api/leads/{leadId}/initiate-outreach \
  -H "Content-Type: application/json" \
  -d '{"voiceAgentId": "agent_12345"}'

# Check metrics
curl http://localhost:3000/api/metrics
```

---

## How Lead Temperature Works

### Detection Method

**During voice call:**
1. Agent follows system prompt
2. Asks qualifying questions
3. Captures responses
4. Call transcribed by Retell
5. Keywords analyzed for temperature indicators

**After call:**
1. Webhook received: `/api/voice/webhook/call-ended`
2. Transcript analyzed
3. Temperature categorized:
   - **HOT keywords**: ready, hire, next steps, how much, yes, when can
   - **WARM keywords**: interested, tell me more, makes sense, possibly
   - **LUKE keywords**: maybe, could be, not sure, i guess
   - **COLD keywords**: not interested, no thanks, stop, wrong number

4. Temperature stored in `leads.lead_temperature` + `calls.temperature_detected`

**Scoring:**
```
avg_score = (engagement + problem_awareness + decision_readiness) / 3

if avg_score >= 8: HOT
elif avg_score >= 6: WARM
elif avg_score >= 4: LUKE
else: COLD

# Overrides if cold keywords present
if cold_keywords > 2: COLD
```

### Dashboard Display

Prototype shows leads as cards with:
- Lead name + source
- Temperature badge (color-coded)
- Service type
- Urgency score → Temperature
- Last contact
- Quick action button

---

## Communication Fallback Details

### Phone to SMS (3-second timeout)

```javascript
// Attempt Retell call
const callPromise = retellClient.initiateCall(phone, agentId, metadata);

// 3-second timeout
const timeout = new Promise((_, reject) => {
  setTimeout(() => reject(new Error('Phone call timeout')), 3000);
});

try {
  const result = await Promise.race([callPromise, timeout]);
  // Call initiated successfully
} catch (err) {
  // Fall back to SMS
  await smsClient.sendSMS(phone, smsMessage);
}
```

### SMS Template

```
Hi John! Daniel Garcia from You Became The Money here. 🚀 
We have an exclusive opportunity to discuss your commercial law needs. 
Reply STOP to opt out, or tell us more about your situation.
```

### Email Template (Warm Lead)

```
Subject: Let's Schedule Your Consultation - Daniel Garcia

Hi John,

Thanks for taking our call today. Based on our conversation, 
I think we might be a great fit for your situation.

Here's what I'd like to do: 
Schedule a 15-minute consultation with Daniel Garcia 
so he can understand your case and share specific strategies.

[Calendar Link]

From goods to GODS - let's get you there.
```

---

## Admin Dashboard Integration

### For Prototype (React)

Update `LiveLeads.tsx` to use real API:

```tsx
// OLD: Mock data
const leads = mockLeads;

// NEW: Fetch from API
const [leads, setLeads] = useState([]);

useEffect(() => {
  fetch('/api/leads?status=new')
    .then(r => r.json())
    .then(leads => setLeads(leads));
}, []);
```

### Temperature Badge Component

```tsx
const getTempColor = (temp: string) => {
  const colors = {
    hot: 'bg-red-600',
    warm: 'bg-orange-500',
    luke: 'bg-blue-400',
    cold: 'bg-gray-400'
  };
  return colors[temp] || 'bg-gray-300';
};

<span className={`px-3 py-1 rounded text-white text-sm ${getTempColor(lead.lead_temperature)}`}>
  {lead.lead_temperature?.toUpperCase() || 'UNQUALIFIED'}
</span>
```

---

## Advanced: Claude API Integration

For smarter transcript analysis:

```python
# In lead_qualifier.py
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("CLAUDE_API_KEY"))

def analyze_transcript_with_claude(transcript: str) -> dict:
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system="""You are an expert at analyzing sales call transcripts. 
        Classify the lead temperature as: hot, warm, luke, or cold.
        Return JSON with: temperature, confidence, reasoning, recommended_action""",
        messages=[
            {"role": "user", "content": f"Transcript: {transcript}"}
        ]
    )
    return json.loads(message.content[0].text)
```

---

## Deployment Checklist

- [ ] PostgreSQL database created
- [ ] Environment variables configured (.env)
- [ ] Retell API key verified
- [ ] SMS gateway (Twilio) configured (optional but recommended)
- [ ] Email gateway (SendGrid) configured (optional but recommended)
- [ ] Node.js dependencies installed (`npm install`)
- [ ] Database schema initialized (auto on first run)
- [ ] Voice agent created and ID obtained
- [ ] Retell webhook configured: `https://yourdomain.com/api/voice/webhook/call-ended`
- [ ] Frontend connected to API endpoints
- [ ] Test call completed end-to-end
- [ ] Metrics dashboard displaying data

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│             React Dashboard (Prototype)                 │
│  - LiveLeads: Real-time lead cards                      │
│  - Pipeline: Kanban board by status                     │
│  - Metrics: Dashboard with temperature breakdown       │
│  - VoiceCommand: Voice interaction                      │
└──────────────────────┬──────────────────────────────────┘
                       │ REST API
                       ▼
┌─────────────────────────────────────────────────────────┐
│             Node.js API (Integration)                   │
├─────────────────────────────────────────────────────────┤
│ Routes:                                                 │
│  - /api/leads          (CRUD + outreach initiation)    │
│  - /api/voice          (Retell webhooks)               │
│  - /api/metrics        (Dashboard data)                │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
    ┌────────┐    ┌────────┐    ┌────────┐
    │ Retell │    │Database│    │Fallback│
    │ Voice  │    │(PG)    │    │Handler │
    └────────┘    └────────┘    └────────┘
        │
   ┌────┴─────────────────┐
   ▼                      ▼
 Phone              SMS/Email
(3s timeout)       (If no answer)
```

---

## Key Features Implemented

| Feature | Status | Location |
|---------|--------|----------|
| Retell voice integration | ✅ | `integration/src/clients/retell.js` |
| Phone→SMS→Email fallback | ✅ | `integration/src/handlers/communicationFallback.js` |
| Categorical scoring | ✅ | `optimization/lead_qualifier.py` |
| Voice agent system prompt | ✅ | `integration/src/prompts/voiceAgent.js` |
| PostgreSQL schema | ✅ | `integration/src/db/init.js` |
| Lead CRUD API | ✅ | `integration/src/routes/leads.js` |
| Voice webhook handling | ✅ | `integration/src/routes/voice.js` |
| Metrics API | ✅ | `integration/src/routes/metrics.js` |
| Garcia knowledge base | ✅ | `youbecamethemoney/voice-agent-knowledge-base.md` |
| SMS client (Twilio) | ✅ | `integration/src/clients/sms.js` |
| Email client (SendGrid) | ✅ | `integration/src/clients/email.js` |

---

## Next Steps

1. **Test end-to-end**: Make a call to your phone, verify transcript captured
2. **Deploy to staging**: Railway or Render
3. **Connect Hermes**: Integrate with Hermes agent for semantic understanding
4. **Add Claude API**: Use Claude to analyze transcripts for even smarter qualification
5. **Build admin UI**: Create dedicated dashboard for Mr. Garcia

---

## Support

For issues:
1. Check `.env` configuration
2. Verify database connection: `pg_isready -h localhost`
3. Check server logs: `npm run dev`
4. Test Retell API: `curl https://api.retellai.com/v2/calls`

---

**Built with ❤️ for Daniel Garcia & You Became The Money**
*From goods to GODS - let's scale this together.*
