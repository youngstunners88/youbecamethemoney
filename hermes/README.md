# Ramsees Gateway — Command Center Agent Front Door

**What it is:** The Ramsees persona — a commercial-law specialist built on the
NousResearch Hermes-3 foundation (https://github.com/NousResearch/hermes-agent)
— exposed through an HTTP gateway that lives **inside the command center**
(`detectable-clarita-casuistically.ngrok-free.dev`), not on Zo.

**Why here, not on Zo:** Mr. Garcia's clients hit the command center first.
Putting the agent gateway on the same host cuts a network hop, keeps
conversation logs in the same Postgres that feeds the dashboard, and lets
Retell AI post webhooks to a stable URL instead of chasing Zo's tunnel.

## Files

| Path | Purpose |
|------|---------|
| `ramsees_gateway.py`            | HTTP server + Ramsees persona + Hermes upstream proxy |
| `install_hermes.sh`             | Legacy: installs the NousResearch Hermes model on Zo (optional upstream) |
| `skills/*.py`                   | The 5 FastMCP skills Ramsees calls into |
| `../database/migrations/003_…`  | `ramsees_conversations` table + `retell_calls` view |

## Endpoints

Base URL (local dev): `http://localhost:8787`
Production: bolted onto the existing command-center ngrok tunnel.

| Method | Path                         | What it does |
|--------|------------------------------|--------------|
| POST   | `/api/ramsees/chat`          | Plain text or JSON → Ramsees reply. Handles bare sentences. |
| POST   | `/api/ramsees/retell`        | Retell AI webhook (`call_ended`, `call_analyzed`). Triages + notifies. |
| POST   | `/api/ramsees/embark`        | embark.html posts the Nefertari transcript here after intake. |
| GET    | `/api/ramsees/health`        | Liveness, upstream, model. |
| GET    | `/api/ramsees/history`       | Last 50 turns (JSON). |

## Persona

Ramsees is a role applied to NousResearch Hermes — not a custom model.
The full system prompt lives in `ramsees_gateway.py::RAMSEES_SYSTEM_PROMPT`.
Short version: Egyptian gravitas, decisive, specializes in SBLC / UCC /
securitization / trust instruments, never invents case law, logs everything.

The fallback path (`_fallback_response`) kicks in when the upstream Hermes
endpoint is unreachable — so the command center never returns a 500 just
because `kofi.zo.space/hermes` is down.

## Running locally

```bash
export HERMES_UPSTREAM="https://kofi.zo.space/hermes"
export HERMES_API_KEY="<if your upstream requires one>"
export RAMSEES_PG_DSN="postgresql://postgres@localhost:5432/garcia_ramsees"
export NTFY_TOPIC="garcia-ramsees-alerts"

psql -d garcia_ramsees -f ../database/migrations/003_ramsees_conversations.sql

python3 ramsees_gateway.py
# listening on :8787
```

## Retell AI wiring

In the Retell dashboard, set the webhook URL to:

```
https://detectable-clarita-casuistically.ngrok-free.dev/api/ramsees/retell
```

Events Ramsees cares about:

- `call_ended` — fires when the call terminates with a transcript
- `call_analyzed` — fires later with Retell's own analysis

Each event is stored as a turn in `ramsees_conversations` (channel=`retell`,
`meta.call_id` preserved) and summarized by Ramsees into a warmth + next-action
line. High-warmth calls trigger an NTFY push to `garcia-ramsees-alerts`.

Query today's calls from Postgres:

```sql
SELECT * FROM retell_calls WHERE started_at::date = CURRENT_DATE;
```

## embark.html wiring

The existing `embark.html` already saves Nefertari's 9-question interview to
`localStorage`. On completion, POST the same payload to
`/api/ramsees/embark` and Ramsees will warmth-score, classify, and push a
notification to Mr. Garcia — all in one round-trip.

## Why Ramsees stopped responding well to plain text

The old setup pointed the UI directly at `kofi.zo.space/hermes`, which is the
raw OpenAI-compatible Hermes endpoint. That endpoint expects a full `messages`
array. When the voice UI sent a bare transcript string, Hermes either 400'd
or produced a cold generic reply.

The gateway fixes this by always wrapping user input in the Ramsees system
prompt + the last 12 turns of context, so plain text always gets a
persona-consistent response.
