# YBTM Voice Integration - Quick Start

## In 5 Minutes

### 1. Start the API
```bash
cd integration
npm install
npm run dev
```

### 2. Create a Lead
```bash
curl -X POST http://localhost:3000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "source": "web",
    "name": "John Smith",
    "phone": "+12125551234",
    "email": "john@example.com",
    "serviceType": "UCC Discharge"
  }'
```

### 3. Trigger Outreach
```bash
curl -X POST http://localhost:3000/api/leads/{leadId}/initiate-outreach \
  -H "Content-Type: application/json" \
  -d '{"voiceAgentId": "agent_12345"}'
```

**Result**: Phone call attempted → SMS fallback → Email fallback (if needed)

### 4. Check Temperature
```bash
curl http://localhost:3000/api/metrics/temperature
# { "hot": 2, "warm": 5, "luke": 3, "cold": 1 }
```

---

## Files Structure

```
youbecamethemoney/
├── integration/                    # Phase 2: API + Retell
│   ├── src/
│   │   ├── index.js               # Server entry point
│   │   ├── clients/               # External API wrappers
│   │   │   ├── retell.js          # Voice calls
│   │   │   ├── sms.js             # Twilio SMS
│   │   │   └── email.js           # SendGrid email
│   │   ├── handlers/
│   │   │   └── communicationFallback.js  # Phone→SMS→Email logic
│   │   ├── prompts/
│   │   │   └── voiceAgent.js      # System prompt + config
│   │   ├── routes/
│   │   │   ├── leads.js           # Lead CRUD + outreach
│   │   │   ├── voice.js           # Retell webhooks
│   │   │   └── metrics.js         # Dashboard data
│   │   └── db/
│   │       └── init.js            # PostgreSQL schema
│   ├── .env.example
│   ├── package.json
│   └── README.md
│
├── optimization/                   # Phase 3: Skills + ML
│   ├── lead_qualifier.py           # Categorical scoring (hot/warm/luke/cold)
│   ├── lead_qualifier_test.py      # Tests
│   └── ...
│
├── prototype/                      # Phase 1: Dashboard
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── LiveLeads.tsx
│   │   │   ├── Pipeline.tsx
│   │   │   ├── Metrics.tsx
│   │   │   ├── VoiceCommand.tsx
│   │   │   └── CaseDetail.tsx
│   │   └── types/
│   └── ...
│
├── IMPLEMENTATION_GUIDE.md         # Full technical docs
├── CONTEXT.md                      # Project requirements
├── SKILL.md                        # Tech stack
├── voice-agent-knowledge-base.md   # Garcia's framework
└── README.md                       # Project overview
```

---

## Temperature Indicators

### 🔥 HOT (Ready to hire)
- "Ready to start"
- "How much does it cost?"
- "When can we do this?"
- Fast speech, excited tone
- **Action**: Immediate consultation with Daniel

### 🌡️ WARM (Interested)
- "Tell me more"
- "That makes sense"
- "Possibly interested"
- Asking follow-up questions
- **Action**: Schedule call in 3 days

### ❄️ LUKE (Curious but uncertain)
- "Maybe"
- "Need to think about it"
- "Could be useful"
- Few questions asked
- **Action**: Send free ebook + nurture

### ❄️❄️ COLD (Not interested)
- "Not interested"
- "No thanks"
- "Stop calling"
- Dismissive tone
- **Action**: 6-month re-engagement sequence

---

## API Reference

### Create Lead
```
POST /api/leads
{
  source: "web|telegram|whatsapp|discord|cli"
  name: string
  phone: string
  email: string
  serviceType: "UCC Discharge" | "Securitization Review" | ...
}
```

### Initiate Outreach
```
POST /api/leads/:id/initiate-outreach
{
  voiceAgentId: "agent_12345"
}

Response:
{
  success: true,
  method: "phone" | "sms" | "email",
  callId: "call_xxx" | "message_id",
  message: "Call initiated to +1234567890"
}
```

### Get Metrics
```
GET /api/metrics
{
  totalLeads: 27,
  conversionRate: 15.4,
  hotLeads: 5,
  warmLeads: 12,
  lukeLeads: 8,
  coldLeads: 2,
  ...
}
```

---

## Environment Setup

```bash
# Copy template
cp integration/.env.example integration/.env

# Edit with real values:
DATABASE_URL=postgresql://user:password@localhost/ybtm
RETELL_API_KEY=key_d0ac8de0d3f1643bcff4f12e7ae4
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...
SENDGRID_API_KEY=SG...
```

---

## Deploy to Production

### Railway
```bash
railway link
railway up
```

### Render
```bash
# Connect repo
# Add env vars in dashboard
# Deploy from Git
```

### Self-hosted VPS
```bash
# Install Node
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PostgreSQL
sudo apt install postgresql

# Clone repo, install, start
git clone ...
cd youbecamethemoney/integration
npm install
npm start
```

---

## Troubleshooting

### API not starting?
```bash
# Check database
psql postgresql://user:pass@localhost/ybtm -c "SELECT 1"

# Check .env
cat integration/.env | grep DATABASE_URL

# Check ports
lsof -i :3000
```

### Phone calls not working?
```bash
# Verify Retell API key
curl -H "Authorization: Bearer key_xxx" https://api.retellai.com/v2/calls

# Check SMS fallback configuration
cat integration/.env | grep TWILIO

# Test SMS directly
npm run test:sms
```

### Webhook not triggering?
```bash
# Verify webhook URL in Retell dashboard
# Should be: https://yourdomain.com/api/voice/webhook/call-ended

# Check logs
npm run dev  # Watch for incoming webhooks

# Test locally
curl -X POST http://localhost:3000/api/voice/webhook/call-ended \
  -H "Content-Type: application/json" \
  -d '{"call_id":"test","call_status":"completed"}'
```

---

## What's Next?

- [ ] Integrate with Hermes agent
- [ ] Use Claude API for transcript analysis
- [ ] Build skills system for case pattern learning
- [ ] Add calendar integration for scheduling
- [ ] Create admin dashboard UI for Mr. Garcia
- [ ] Deploy to production
- [ ] Run first 10 real leads through system

---

**Start**: `cd integration && npm run dev`
**API**: `http://localhost:3000`
**Docs**: See `IMPLEMENTATION_GUIDE.md`

*From goods to GODS* 🚀
