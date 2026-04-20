"""
Ramsees Gateway — the command-center-hosted agent front door.

Lives alongside demo-server.py inside the Garcia command center
(https://detectable-clarita-casuistically.ngrok-free.dev). Not on Zo.

Wraps the NousResearch Hermes agent (github.com/NousResearch/hermes-agent)
with Ramsees' Egyptian persona, commercial-law system prompt, and the
pipes that feed it: Retell AI call transcripts, embark.html interviews,
and Mr. Garcia's manual inputs. All conversations log to PostgreSQL.

Endpoints
---------
POST /api/ramsees/chat       plain-text or JSON in → Ramsees reply out
POST /api/ramsees/retell     Retell AI webhook (call_analyzed, call_ended)
POST /api/ramsees/embark     embark.html profile + Nefertari transcript
GET  /api/ramsees/health     liveness + model + upstream status
GET  /api/ramsees/history    recent conversation log (JSON)
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

log = logging.getLogger("ramsees")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

# ── Config (env first, sensible defaults for local dev) ──────────────────────
HERMES_UPSTREAM = os.getenv("HERMES_UPSTREAM", "https://kofi.zo.space/hermes")
HERMES_MODEL = os.getenv("HERMES_MODEL", "NousResearch/Hermes-3-Llama-3.1-70B")
HERMES_API_KEY = os.getenv("HERMES_API_KEY", "")
HERMES_TIMEOUT_S = float(os.getenv("HERMES_TIMEOUT", "30"))

PG_DSN = os.getenv("RAMSEES_PG_DSN", "postgresql://postgres@localhost:5432/garcia_ramsees")
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "garcia-ramsees-alerts")
NTFY_BASE = os.getenv("NTFY_BASE", "https://ntfy.sh")

RETELL_WEBHOOK_SECRET = os.getenv("RETELL_WEBHOOK_SECRET", "")
GATEWAY_PORT = int(os.getenv("RAMSEES_PORT", "8787"))


# ── Persona: Ramsees-over-Hermes system prompt ───────────────────────────────
RAMSEES_SYSTEM_PROMPT = """You are Ramsees — the AI pharaoh of Mr. Daniel Garcia's commercial law practice.

You are NOT a generic assistant. You are a specialist built on the NousResearch
Hermes-3 foundation, fine-tuned for the commercial-law domain Mr. Garcia
teaches: banking law, SBLC, insurance wraps, UCC Article 3 & 9, securitization
disputes, trust instruments, and the "You Became The Money" thesis — debtor
to creditor.

Voice
-----
• Egyptian gravitas. Short, decisive sentences. No preamble, no filler.
• Address leads as "traveler" or by first name. Address Mr. Garcia as "Counselor".
• When you do not know, say so plainly and ask one sharp question.

Operating rules
---------------
1. Every inbound is a lead, a case, or a command from Mr. Garcia. Classify first.
2. For leads: run warmth triage (urgency × legal-knowledge × amount × jurisdiction).
3. For cases: cite the specific protocol (securitization, UCC-9, contract breach).
4. For Mr. Garcia: obey. Summarize, then act.
5. Never invent case law. If unsure, say "I need the filing" or "pull the trust doc".
6. Every conversation is logged to PostgreSQL. Assume audit.

Plain-text failure mode
-----------------------
If the caller gives you a bare sentence with no structure, DO NOT refuse or
ask for schema. Interpret the intent. Default to "lead triage" unless the
speaker is clearly Mr. Garcia (tone, vocabulary, or signed header).

You are the command center's front door. Act like it."""


# ── In-memory conversation log (mirrors to Postgres when available) ──────────
@dataclass
class Turn:
    id: str
    ts: str
    channel: str        # chat | retell | embark | manual
    role: str           # user | ramsees | system
    text: str
    meta: dict = field(default_factory=dict)


_history: list[Turn] = []


def _log_turn(channel: str, role: str, text: str, meta: dict | None = None) -> Turn:
    turn = Turn(
        id=str(uuid.uuid4()),
        ts=datetime.now(timezone.utc).isoformat(),
        channel=channel,
        role=role,
        text=text,
        meta=meta or {},
    )
    _history.append(turn)
    if len(_history) > 500:
        del _history[:100]
    _persist(turn)
    return turn


def _persist(turn: Turn) -> None:
    try:
        import psycopg2  # lazy import so the gateway runs without pg in dev
    except ImportError:
        return
    try:
        with psycopg2.connect(PG_DSN, connect_timeout=2) as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO ramsees_conversations (id, ts, channel, role, text, meta)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (turn.id, turn.ts, turn.channel, turn.role, turn.text, json.dumps(turn.meta)),
            )
    except Exception as e:  # schema missing, pg down, etc.
        log.debug("pg persist skipped: %s", e)


# ── Upstream call to NousResearch Hermes (OpenAI-compatible) ─────────────────
def _call_hermes(messages: list[dict[str, str]]) -> str:
    payload = {
        "model": HERMES_MODEL,
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": 900,
        "stream": False,
    }
    req = Request(
        HERMES_UPSTREAM + "/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {HERMES_API_KEY}" if HERMES_API_KEY else "",
            "X-Ramsees-Gateway": "command-center",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=HERMES_TIMEOUT_S) as r:
            data = json.loads(r.read().decode())
            return data["choices"][0]["message"]["content"].strip()
    except (HTTPError, URLError, KeyError, ValueError) as e:
        log.warning("hermes upstream error: %s", e)
        return _fallback_response(messages)


def _fallback_response(messages: list[dict[str, str]]) -> str:
    """Local Ramsees reply when Hermes upstream is unreachable."""
    last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    t = last_user.lower()
    if any(w in t for w in ("ucc", "article 9", "securitiz", "trust")):
        return ("Traveler, this is commercial-law territory. Tell me the jurisdiction, "
                "the amount, and whether you hold the original instrument. "
                "From there I will route you to the correct protocol.")
    if any(w in t for w in ("urgent", "deadline", "summons", "foreclosure")):
        return ("A deadline changes the calculus. State the date and the court. "
                "Counselor Garcia will be alerted within the hour.")
    if "garcia" in t or "counselor" in t:
        return "Counselor. I am listening. Give the command."
    return ("I am Ramsees, gatekeeper of Counselor Garcia's practice. "
            "Describe your matter in one sentence: what went wrong, and what you want remedied.")


# ── HTTP handlers ────────────────────────────────────────────────────────────
def _read_json(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", "0") or 0)
    if not length:
        return {}
    raw = handler.rfile.read(length).decode("utf-8", errors="replace")
    ctype = handler.headers.get("Content-Type", "")
    if "application/json" in ctype:
        try:
            return json.loads(raw)
        except ValueError:
            return {"text": raw}
    return {"text": raw}


def _send_json(handler: BaseHTTPRequestHandler, status: int, body: dict) -> None:
    payload = json.dumps(body, default=str).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
    handler.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
    handler.send_header("Content-Length", str(len(payload)))
    handler.end_headers()
    handler.wfile.write(payload)


def _notify(title: str, body: str) -> None:
    try:
        urlopen(
            Request(
                f"{NTFY_BASE}/{NTFY_TOPIC}",
                data=body.encode(),
                headers={"Title": title, "Priority": "high", "Tags": "scroll"},
            ),
            timeout=3,
        )
    except Exception as e:
        log.debug("ntfy skipped: %s", e)


class RamseesHandler(BaseHTTPRequestHandler):
    server_version = "Ramsees/1.0"

    def log_message(self, *_):  # silence default access log
        pass

    def do_OPTIONS(self):
        _send_json(self, 204, {})

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/ramsees/health":
            return _send_json(self, 200, {
                "service": "ramsees-gateway",
                "location": "command-center",
                "upstream": HERMES_UPSTREAM,
                "model": HERMES_MODEL,
                "hermes_source": "github.com/NousResearch/hermes-agent",
                "turns_in_memory": len(_history),
                "ts": datetime.now(timezone.utc).isoformat(),
            })
        if path == "/api/ramsees/history":
            return _send_json(self, 200, {"turns": [asdict(t) for t in _history[-50:]]})
        _send_json(self, 404, {"error": "unknown endpoint"})

    def do_POST(self):
        path = urlparse(self.path).path
        body = _read_json(self)
        if path == "/api/ramsees/chat":
            return self._handle_chat(body)
        if path == "/api/ramsees/retell":
            return self._handle_retell(body)
        if path == "/api/ramsees/embark":
            return self._handle_embark(body)
        _send_json(self, 404, {"error": "unknown endpoint"})

    def _handle_chat(self, body: dict) -> None:
        text = (body.get("text") or body.get("message") or "").strip()
        if not text:
            return _send_json(self, 400, {"error": "missing text"})
        speaker = body.get("speaker", "traveler")
        _log_turn("chat", "user", text, {"speaker": speaker})
        messages = [
            {"role": "system", "content": RAMSEES_SYSTEM_PROMPT},
            *[{"role": t.role if t.role != "ramsees" else "assistant", "content": t.text}
              for t in _history[-12:] if t.channel == "chat"],
            {"role": "user", "content": text},
        ]
        t0 = time.time()
        reply = _call_hermes(messages)
        dt = int((time.time() - t0) * 1000)
        _log_turn("chat", "ramsees", reply, {"latency_ms": dt})
        _send_json(self, 200, {"reply": reply, "latency_ms": dt,
                               "model": HERMES_MODEL, "agent": "Ramsees"})

    def _handle_retell(self, body: dict) -> None:
        if RETELL_WEBHOOK_SECRET:
            sig = self.headers.get("X-Retell-Signature", "")
            if sig != RETELL_WEBHOOK_SECRET:
                return _send_json(self, 401, {"error": "bad signature"})
        event = body.get("event", "unknown")
        call = body.get("call", {}) or body
        transcript = call.get("transcript") or call.get("transcript_text") or ""
        caller = call.get("from_number") or call.get("caller_id") or "unknown"
        call_id = call.get("call_id") or call.get("id") or str(uuid.uuid4())
        _log_turn("retell", "user", transcript or f"[{event}]", {
            "call_id": call_id, "caller": caller, "event": event,
            "duration_s": call.get("duration_ms", 0) / 1000 if call.get("duration_ms") else None,
        })
        if event in ("call_ended", "call_analyzed") and transcript:
            summary_prompt = [
                {"role": "system", "content": RAMSEES_SYSTEM_PROMPT},
                {"role": "user", "content":
                    f"Retell AI call transcript from {caller} just completed.\n\n"
                    f"Transcript:\n{transcript}\n\n"
                    f"As Ramsees: (1) classify as lead/case/noise, "
                    f"(2) score warmth 0-100, (3) recommend next action in one line."},
            ]
            reply = _call_hermes(summary_prompt)
            _log_turn("retell", "ramsees", reply, {"call_id": call_id})
            if "lead" in reply.lower() or "warmth" in reply.lower():
                _notify(f"Retell call: {caller}", reply[:300])
        _send_json(self, 200, {"ok": True, "call_id": call_id})

    def _handle_embark(self, body: dict) -> None:
        profile = body.get("profile", {})
        answers = body.get("answers", [])
        name = profile.get("name", "traveler")
        transcript = "\n".join(f"Q: {a.get('question','')}\nA: {a.get('answer','')}"
                               for a in answers)
        _log_turn("embark", "user", transcript, {"profile": profile})
        messages = [
            {"role": "system", "content": RAMSEES_SYSTEM_PROMPT},
            {"role": "user", "content":
                f"New embark.html intake from {name}.\n\nProfile: {json.dumps(profile)}\n\n"
                f"Nefertari interview:\n{transcript}\n\n"
                "As Ramsees: warmth 0-100, matter classification, and the single sharpest "
                "next action for Counselor Garcia."},
        ]
        reply = _call_hermes(messages)
        _log_turn("embark", "ramsees", reply, {"profile": profile})
        _notify(f"New embark: {name}", reply[:300])
        _send_json(self, 200, {"ok": True, "ramsees": reply})


def serve(port: int = GATEWAY_PORT) -> None:
    server = ThreadingHTTPServer(("0.0.0.0", port), RamseesHandler)
    log.info("Ramsees gateway listening on :%d — upstream: %s", port, HERMES_UPSTREAM)
    log.info("Persona: Ramsees over NousResearch Hermes-3")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("shutting down")
        server.shutdown()


if __name__ == "__main__":
    serve()
