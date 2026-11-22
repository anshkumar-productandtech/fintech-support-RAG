# A small web app for the support copilot: one page, one API call.
# Run it with:  .venv/bin/uvicorn app:app --app-dir src --host 0.0.0.0 --port 8080
#
# The app only calls answer() and reshapes its result for the page.
# It never logs the question text, IP addresses or any API key.
import hashlib
import logging
import os
import random
import sys
import time
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent))
from answer import _connect, answer  # noqa: E402

MAX_QUESTION_CHARS = 500
INDEX_HTML = Path(__file__).resolve().parent.parent / "static" / "index.html"
NO_HEADING = "Introduction"  # a chunk from the text before an article's first "## "

# Limits, checked before any Gemini call. They're kept in Postgres (tables made by
# scripts/create_usage_tables.py), because Vercel runs many short-lived copies of the app.
VISITOR_LIMIT = 8  # questions per visitor (IP address)...
VISITOR_WINDOW = 10 * 60  # ...per 10-minute window, in seconds
DAILY_ANSWER_CAP = int(os.getenv("DAILY_ANSWER_CAP", "100"))  # everyone, per UTC day
VISITOR_LIMIT_REASON = "visitor_limit"
DAILY_CAP_REASON = "daily_cap"
CLEANUP_CHANCE = 0.05  # share of questions that also delete visitor rows over a day old

# Each statement adds one, unless the row is already at its limit: then the WHERE
# fails, nothing changes and no row comes back. Atomic, so copies running at the same
# time can't both take the last place.
VISITOR_SQL = """
    INSERT INTO usage_visitor AS v (ip_hash, window_start, count)
    VALUES (%(ip_hash)s, date_bin(make_interval(secs => %(window)s), now(), 'epoch'), 1)
    ON CONFLICT (ip_hash, window_start)
        DO UPDATE SET count = v.count + 1 WHERE v.count < %(limit)s
    RETURNING count
"""
DAILY_SQL = """
    INSERT INTO usage_daily AS d (day, answers)
    VALUES ((now() AT TIME ZONE 'UTC')::date, 1)
    ON CONFLICT (day)
        DO UPDATE SET answers = d.answers + 1 WHERE d.answers < %(cap)s
    RETURNING answers
"""
CLEANUP_SQL = "DELETE FROM usage_visitor WHERE window_start < now() - interval '1 day'"

log = logging.getLogger("copilot")
# uvicorn's access log prints each visitor's IP address, so it's switched off.
logging.getLogger("uvicorn.access").disabled = True
app = FastAPI(
    title="Kuberix Support Copilot", docs_url=None, redoc_url=None, openapi_url=None
)


def client_ip(request):
    """The visitor's IP, from the first of these that is set:

    x-vercel-forwarded-for, x-real-ip, the first entry of x-forwarded-for, the direct
    peer. Vercel sets all three headers itself and overwrites x-forwarded-for, so
    visitors can't fake them. Headers like True-Client-IP aren't used: on Vercel they
    come from the visitor.
    """
    for header in ("x-vercel-forwarded-for", "x-real-ip", "x-forwarded-for"):
        first = request.headers.get(header, "").split(",")[0].strip()
        if first:
            return first
    return request.client.host if request.client else "unknown"


def ip_hash(ip):
    """sha256(IP_HASH_SALT + ip) as hex. Raises 503 if IP_HASH_SALT is unset."""
    salt = os.getenv("IP_HASH_SALT")
    if not salt:
        log.error("IP_HASH_SALT is not set, so no questions are accepted")
        raise HTTPException(503, "The copilot isn't available right now.")
    return hashlib.sha256((salt + ip).encode()).hexdigest()


def check_limits(ip):
    """Count one question for this visitor and for today, or raise 429 if over a limit.

    Both counts are in one transaction: a rejected question counts against neither.
    Raises 503 if the limits can't be checked, so Gemini is never called unchecked.
    """
    hashed = ip_hash(ip)
    try:
        with _connect() as conn:
            with conn.transaction():
                params = {"ip_hash": hashed, "window": VISITOR_WINDOW, "limit": VISITOR_LIMIT}
                if conn.execute(VISITOR_SQL, params).fetchone() is None:
                    log.info("rate limited reason=%s", VISITOR_LIMIT_REASON)
                    retry_after = VISITOR_WINDOW - int(time.time()) % VISITOR_WINDOW
                    raise HTTPException(
                        429, {"reason": VISITOR_LIMIT_REASON}, {"Retry-After": str(retry_after)}
                    )
                over_cap = (
                    DAILY_ANSWER_CAP < 1
                    or conn.execute(DAILY_SQL, {"cap": DAILY_ANSWER_CAP}).fetchone() is None
                )
                if over_cap:  # raising here rolls back the visitor's count too
                    log.info("rate limited reason=%s", DAILY_CAP_REASON)
                    raise HTTPException(429, {"reason": DAILY_CAP_REASON})
            if random.random() < CLEANUP_CHANCE:
                conn.execute(CLEANUP_SQL)
    except HTTPException:
        raise
    except Exception as e:
        log.error("limit check failed: %s", type(e).__name__)
        raise HTTPException(503, "The copilot isn't available right now.")


class AnswerRequest(BaseModel):
    question: str
    audience: Literal["customer", "merchant"]


def section_heading(source):
    """The chunk's "## " heading, or Introduction if it has none."""
    for line in source["text"].splitlines():
        if line.startswith("## "):
            return line[3:].strip()
    return NO_HEADING


@app.get("/health")
def health():
    try:
        with _connect() as conn:
            conn.execute("SELECT count(*) FROM chunks").fetchone()
    except Exception as e:
        log.error("health check failed: %s", type(e).__name__)
        return JSONResponse({"ok": False, "db": False}, status_code=503)
    return {"ok": True, "db": True}


@app.get("/")
def index():
    return FileResponse(INDEX_HTML)


# A plain def, not async: answer() blocks, so FastAPI runs it in a worker thread.
@app.post("/api/answer")
def api_answer(req: AnswerRequest, request: Request):
    question = req.question.strip()
    if not question:
        raise HTTPException(400, "Question is empty.")
    if len(question) > MAX_QUESTION_CHARS:
        raise HTTPException(400, f"Question is over {MAX_QUESTION_CHARS} characters.")
    check_limits(client_ip(request))

    try:
        result = answer(question, req.audience)
    except Exception as e:
        # Only the error type: messages and tracebacks can include the prompt.
        log.error("answer() failed: %s", type(e).__name__)
        raise HTTPException(502, "The copilot couldn't draft a reply. Try again.")

    log.info(
        "answered audience=%s refused=%s needs_review=%s seconds=%.1f",
        req.audience, result["refused"], result["needs_review"], result["seconds"],
    )
    # A flagged answer is never sent: the page shows a hand-off instead.
    reply = "" if result["needs_review"] else result["text"]
    return {
        "reply": reply,
        "refused": result["refused"],
        "safety_answer": result["safety_answer"],
        "sources": [
            {
                "number": i,
                "chunk_id": s["chunk_id"],
                "title": s["title"],
                "section": section_heading(s),
            }
            for i, s in enumerate(result["sources"], start=1)
        ],
        "needs_review": result["needs_review"],
        "review_reasons": result["review_reasons"],
        "seconds": round(result["seconds"], 1),
        "cost": result["cost_usd"],
    }
