# YBTM API - Integration Phase

Backend API for You Became The Money with Retell voice integration, communication fallback (phone → SMS → email), and lead temperature qualification.

## Quick Start

### 1. Setup

```bash
cd integration
npm install
cp .env.example .env
```

### 2. Configure `.env`

```env
# Database (PostgreSQL required)
DATABASE_URL=postgresql://user:password@localhost:5432/ybtm

# Retell API
RETELL_API_KEY=key_d0ac8de0d3f1643bcff4f12e7ae4

# SMS (Twilio)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890

# Email (SendGrid)
SENDGRID_API_KEY=your_key

# Server
PORT=3000
NODE_ENV=development
```

### 3. Start Server

```bash
npm run dev    # Development with hot reload
npm start      # Production
```

Server runs on `http://localhost:3000`

---

## API Endpoints

### Leads Management

```
GET    /api/leads                      # List all leads
GET    /api/leads/:id                  # Get single lead
GET    /api/leads/:id/calls            # Get call history
GET    /api/leads/:id/interactions     # Get interaction log
POST   /api/leads                      # Create lead
PUT    /api/leads/:id/status           # Update status
PUT    /api/leads/:id/temperature      # Update temperature
POST   /api/leads/:id/initiate-outreach # Start phone→SMS→email
```

### Voice/Retell

```
GET    /api/voice/agent/config         # Get agent config
POST   /api/voice/agent/create         # Create voice agent
GET    /api/voice/calls/:callId        # Get call details
GET    /api/voice/calls/:callId/transcript
POST   /api/voice/webhook/call-ended   # Retell webhook (call completed)
POST   /api/voice/calls/:callId/end    # End active call
```

### Metrics

```
GET    /api/metrics                    # Full dashboard metrics
GET    /api/metrics/temperature        # Leads by temperature
GET    /api/metrics/status             # Leads by status
GET    /api/metrics/service-type       # Leads by service
GET    /api/metrics/calls              # Call performance
```

---

## How It Works

### Communication Fallback Strategy

When initiating outreach to a lead:

1. **Phone Call (Primary)** - Attempt Retell call
   - Voice agent asks qualifying questions
   - Detects lead temperature (cold/luke/warm/hot)
   - 3-second timeout

2. **SMS (Fallback 1)** - If phone fails
   - Sends personalized SMS with CTA
   - Captured in interaction logs

3. **Email (Fallback 2)** - If SMS fails
   - Sends education-focused email
   - Includes free ebook offer
   - Captured in interaction logs

**Usage:**
```bash
POST /api/leads/{leadId}/initiate-outreach
{
  "voiceAgentId": "agent_12345"
}
```

Response:
```json
{
  "success": true,
  "method": "phone",
  "callId": "call_123456",
  "message": "Call initiated to +1234567890"
}
```

### Lead Temperature Scoring

Automatically categorized based on voice call:

- **🔥 HOT** - Ready to hire, asks about next steps
- **🌡️  WARM** - Interested, problem-aware, asking questions  
- **❄️ LUKE** - Curious but uncertain, wants to think
- **❄️❄️ COLD** - Not interested, wrong number

Voice agent's system prompt detects temperature based on keywords and call behavior. Temperature is stored in `leads.lead_temperature` and `calls.temperature_detected`.

---

## Database Schema

### leads table
```sql
id              UUID PRIMARY KEY
source          VARCHAR(20)          -- 'phone', 'sms', 'email', 'retell'
name            VARCHAR(100) NOT NULL
phone           VARCHAR(20)
email           VARCHAR(100)
service_type    VARCHAR(50) NOT NULL -- 'UCC Discharge', 'Securitization Review', etc.
lead_temperature VARCHAR(10)          -- 'cold', 'luke', 'warm', 'hot'
status          VARCHAR(20)           -- 'new', 'qualified', 'consulting', 'retained', 'closed-won', 'closed-lost'
created_at      TIMESTAMP
updated_at      TIMESTAMP
message         TEXT
```

### calls table
```sql
id                  UUID PRIMARY KEY
lead_id             UUID REFERENCES leads(id)
retell_call_id      VARCHAR(100) UNIQUE
call_started_at     TIMESTAMP
call_ended_at       TIMESTAMP
duration_seconds    INTEGER
call_status         VARCHAR(20)      -- 'completed', 'failed', 'no_answer'
temperature_detected VARCHAR(10)     -- detected from transcript
engagement_method   VARCHAR(20)      -- 'phone', 'sms', 'email'
created_at          TIMESTAMP
```

### interaction_logs table
```sql
id              UUID PRIMARY KEY
lead_id         UUID REFERENCES leads(id)
timestamp       TIMESTAMP
platform        VARCHAR(20)      -- 'phone', 'sms', 'email', 'all'
message_type    VARCHAR(20)      -- 'call_initiated', 'message_sent', etc.
message         TEXT
response        TEXT
status          VARCHAR(20)      -- 'success', 'failed'
```

---

## Voice Agent Configuration

Default system prompt embedded in `/src/prompts/voiceAgent.js`:

- Greets professionally: "Good [time], this is [agent] from You Became The Money"
- Asks 3 qualifying questions (2 min)
- Teaches 1 relevant concept (2 min)
- Detects lead temperature (2 min)
- Provides appropriate CTA based on temperature
- Captures name, phone, email at call end
- Includes disclaimers (educational, not legal advice)

Embedded Daniel Garcia framework:
- UCC Articles (3, 8, 9)
- Securitization & trust verification
- Debtor → Creditor mindset
- "From goods to GODS"

---

## Deployment

### Local Development
```bash
npm run dev
```

### Production (Railway/Render)
1. Connect PostgreSQL database
2. Set environment variables (Retell, Twilio, SendGrid)
3. Deploy from Git
4. Configure Retell webhook: `https://yourdomain.com/api/voice/webhook/call-ended`

### VPS (Self-Hosted)
```bash
# Install dependencies
npm install

# Create systemd service
sudo tee /etc/systemd/system/ybtm-api.service > /dev/null <<EOF
[Unit]
Description=YBTM API
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/home/deploy/ybtm/integration
ExecStart=/usr/bin/node src/index.js
Restart=on-failure
Environment="NODE_ENV=production"
EnvironmentFile=/home/deploy/ybtm/integration/.env

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable ybtm-api
sudo systemctl start ybtm-api
sudo systemctl status ybtm-api
```

---

## Testing

### Test lead creation
```bash
curl -X POST http://localhost:3000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "source": "web",
    "name": "John Smith",
    "phone": "+12125551234",
    "email": "john@example.com",
    "serviceType": "UCC Discharge",
    "message": "Interested in your services"
  }'
```

### Test outreach
```bash
curl -X POST http://localhost:3000/api/leads/{leadId}/initiate-outreach \
  -H "Content-Type: application/json" \
  -d '{"voiceAgentId": "agent_12345"}'
```

### Check metrics
```bash
curl http://localhost:3000/api/metrics
```

---

## Architecture

```
integration/
├── src/
│   ├── index.js                      # Server entry point
│   ├── db/
│   │   └── init.js                   # Database schema
│   ├── clients/
│   │   ├── retell.js                 # Retell API wrapper
│   │   ├── sms.js                    # Twilio wrapper
│   │   └── email.js                  # SendGrid wrapper
│   ├── handlers/
│   │   └── communicationFallback.js   # Phone→SMS→Email logic
│   ├── prompts/
│   │   └── voiceAgent.js             # System prompt + config
│   └── routes/
│       ├── leads.js                  # Lead CRUD + outreach
│       ├── voice.js                  # Retell webhooks
│       └── metrics.js                # Dashboard metrics
├── package.json
├── .env.example
└── README.md
```

---

## Next Steps

- [ ] Integrate with Hermes agent for semantic understanding
- [ ] Add Claude API for intelligent transcript analysis
- [ ] Build skill system for case pattern analysis
- [ ] Add calendar integration for consultation scheduling
- [ ] Create admin dashboard for Mr. Garcia

---

**Made with ❤️ for Daniel Garcia & You Became The Money**
