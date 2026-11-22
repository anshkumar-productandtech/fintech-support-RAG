# A small web app for the support copilot: one page, one API call.
# Run it with:  .venv/bin/uvicorn app:app --app-dir src --host 0.0.0.0 --port 8080
#
# The app only calls answer() and reshapes its result for the page.
# It never logs the question text, IP addresses or any API key.
import logging
import os
import sys
import threading
import time
from collections import deque
from datetime import datetime, timezone
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

# Limits, checked before any Gemini call. Both are in memory, so they reset on restart.
VISITOR_LIMIT = 8  # questions per visitor (IP address)...
VISITOR_WINDOW = 10 * 60  # ...per 10 minutes
DAILY_ANSWER_CAP = int(os.getenv("DAILY_ANSWER_CAP", "100"))  # everyone, per UTC day
VISITOR_LIMIT_REASON = "visitor_limit"
DAILY_CAP_REASON = "daily_cap"

log = logging.getLogger("copilot")
# uvicorn's access log prints each visitor's IP address, so it's switched off.
logging.getLogger("uvicorn.access").disabled = True
app = FastAPI(
    title="Kuberix Support Copilot", docs_url=None, redoc_url=None, openapi_url=None
)

_limits_lock = threading.Lock()
_visitor_times = {}  # IP -> deque of time.monotonic() of their recent questions
_daily = {"day": None, "count": 0}  # answers started on this UTC date


def client_ip(request):
    """The visitor's IP, from the first of these that is set:

    True-Client-IP, CF-Connecting-IP, the last entry of X-Forwarded-For (the one our
    own proxy appended; earlier entries can be set by the visitor), the direct peer.
    """
    for header in ("true-client-ip", "cf-connecting-ip"):
        value = request.headers.get(header, "").strip()
        if value:
            return value
    last = request.headers.get("x-forwarded-for", "").split(",")[-1].strip()
    if last:
        return last
    return request.client.host if request.client else "unknown"


def check_limits(ip):
    """Count one question for this IP and for today, or raise 429 if over a limit.

    A rejected question doesn't count against either limit.
    """
    now = time.monotonic()
    today = datetime.now(timezone.utc).date()
    with _limits_lock:
        # Forget visitors whose questions are all older than the window.
        for old_ip in [k for k, t in _visitor_times.items() if now - t[-1] >= VISITOR_WINDOW]:
            del _visitor_times[old_ip]
        times = _visitor_times.setdefault(ip, deque())
        while times and now - times[0] >= VISITOR_WINDOW:
            times.popleft()
        if len(times) >= VISITOR_LIMIT:
            retry_after = int(VISITOR_WINDOW - (now - times[0])) + 1
            log.info("rate limited reason=%s", VISITOR_LIMIT_REASON)
            raise HTTPException(
                429, {"reason": VISITOR_LIMIT_REASON}, {"Retry-After": str(retry_after)}
            )

        if _daily["day"] != today:
            _daily["day"], _daily["count"] = today, 0
        if _daily["count"] >= DAILY_ANSWER_CAP:
            if not times:
                del _visitor_times[ip]
            log.info("rate limited reason=%s", DAILY_CAP_REASON)
            raise HTTPException(429, {"reason": DAILY_CAP_REASON})

        times.append(now)
        _daily["count"] += 1


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
