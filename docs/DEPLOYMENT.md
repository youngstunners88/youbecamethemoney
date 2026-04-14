# YBTM Deployment Guide

**Last Updated:** Apr 14, 2026  
**System:** You Became The Money — Command Center for Daniel Garcia

---

## Quick Reference

| Service | Port | Command |
|---------|------|---------|
| React Dashboard | 5173 (dev) | `cd prototype && npm run dev` |
| Interview API | 8090 | `python3 integration/src/lemonslice/interview_api.py` |
| Integration API | 3000 | `cd integration && npm run dev` |
| PostgreSQL | 5432 | (systemd or Docker) |

---

## 1. Deploy Dashboard to Vercel (Wednesday Demo)

```bash
cd prototype
npm install
npm run build        # verify 0 errors
npx vercel --prod    # follow prompts, link to youngstunners88
```

Set framework to **Vite**. The `vercel.json` already handles SPA routing.

Once deployed, share the Vercel URL with Mr. Garcia — the demo is live.

---

## 2. Run Locally (Development)

```bash
# Dashboard
cd prototype
npm install
npm run dev          # http://localhost:5173

# Interview portal API (separate terminal)
cd youbecamethemoney
pip3 install fastapi uvicorn anthropic psycopg2-binary
python3 integration/src/lemonslice/interview_api.py
# http://localhost:8090/portal
```

---

## 3. Database Setup (Phase 2 — Integration Week)

### Prerequisites
- PostgreSQL 14+
- `psql` CLI

### Create database
```bash
createdb ybtm
psql ybtm < database/migrations/001_client_interviews.sql
psql ybtm < database/migrations/002_skills_audit.sql
```

### Environment variables
Create `.env` in project root:
```
DATABASE_URL=postgresql://user:password@localhost:5432/ybtm
ANTHROPIC_API_KEY=sk-ant-...
RETELL_API_KEY=key_...
PORT=3000
```

---

## 4. Integration API (Phase 2)

```bash
cd integration
npm install
cp .env.example .env   # fill in DATABASE_URL, ANTHROPIC_API_KEY, RETELL_API_KEY
npm run dev            # http://localhost:3000
```

**Key endpoints:**
```
POST /api/leads                    — create lead
POST /api/leads/:id/initiate-outreach  — trigger Margarita call
POST /api/interview/submit         — submit Lemonslice interview
GET  /api/metrics                  — dashboard metrics
```

---

## 5. Skills (Phase 2)

```bash
cd optimization/skills
pip3 install -r requirements.txt   # anthropic, psycopg2-binary, pytest

# Run all tests
pytest tests/ -v                   # 42 tests, 42 pass

# Run individual skill
python3 interview_analyzer.py      # interactive test
python3 hall_of_fame_curator.py    # interactive test
```

---

## 6. Lemonslice Interview Portal

```bash
# Start interview server
python3 integration/src/lemonslice/interview_api.py

# Open in browser
open http://localhost:8090/portal

# Share with leads (production)
https://your-domain.com:8090/portal?lead_id=UUID
```

The portal runs standalone — no database required for demo. It submits to `interview_analyzer` which updates warmth scores and feeds the **Warmth** tab in the dashboard.

---

## 7. VPS Deployment (Phase 2 — Production)

```bash
# On client VPS (Ubuntu 22.04)
sudo apt update && sudo apt install -y nodejs npm python3-pip postgresql nginx

# Clone repo
git clone https://github.com/youngstunners88/youbecamethemoney.git
cd youbecamethemoney

# Database
sudo -u postgres createdb ybtm
psql ybtm < database/migrations/001_client_interviews.sql
psql ybtm < database/migrations/002_skills_audit.sql

# Integration API as service
sudo cp integration/ybtm-api.service /etc/systemd/system/
sudo systemctl enable ybtm-api && sudo systemctl start ybtm-api

# Interview API as service
sudo cp integration/ybtm-interview.service /etc/systemd/system/
sudo systemctl enable ybtm-interview && sudo systemctl start ybtm-interview

# Dashboard (Nginx serves dist/)
cd prototype && npm run build
sudo cp -r dist/* /var/www/html/
```

---

## 8. Environment Checklist

Before going live, verify:

- [ ] `ANTHROPIC_API_KEY` set (skills fall back to rule-based if missing, but Claude is better)
- [ ] `RETELL_API_KEY` set (Margarita voice agent)
- [ ] `DATABASE_URL` points to live PostgreSQL
- [ ] Both migrations run successfully
- [ ] `npm run build` passes with 0 errors
- [ ] Vercel deployment live (or Nginx serving dist/)
- [ ] Interview portal reachable at `:8090/portal`
- [ ] Voice commands work in Chrome (microphone permission)

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Dashboard blank on Vercel | Check `vercel.json` has `"rewrites"` for SPA |
| Interview API 500 | Check `DATABASE_URL` + run migrations |
| Voice tab no mic | Use Chrome or Edge, allow microphone |
| Skills tests fail | `pip3 install anthropic psycopg2-binary pytest` |
| Warmth tab empty | Start interview API + submit a portal interview |
