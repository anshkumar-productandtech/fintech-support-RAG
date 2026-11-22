# A small web app for the support copilot: one page, one API call.
# Run it with:  .venv/bin/uvicorn app:app --app-dir src --host 0.0.0.0 --port 8080
#
# The app only calls answer() and reshapes its result for the page.
# It never logs the question text or any API key.
import logging
import sys
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent))
from answer import answer  # noqa: E402

MAX_QUESTION_CHARS = 500
INDEX_HTML = Path(__file__).resolve().parent.parent / "static" / "index.html"
NO_HEADING = "Introduction"  # a chunk from the text before an article's first "## "

log = logging.getLogger("copilot")
app = FastAPI(title="Kuberix Support Copilot", docs_url=None, redoc_url=None)


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
    return {"ok": True}


@app.get("/")
def index():
    return FileResponse(INDEX_HTML)


# A plain def, not async: answer() blocks, so FastAPI runs it in a worker thread.
@app.post("/api/answer")
def api_answer(req: AnswerRequest):
    question = req.question.strip()
    if not question:
        raise HTTPException(400, "Question is empty.")
    if len(question) > MAX_QUESTION_CHARS:
        raise HTTPException(400, f"Question is over {MAX_QUESTION_CHARS} characters.")

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
    return {
        "reply": result["text"],
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
