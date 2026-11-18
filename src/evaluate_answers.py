# Run every test question through answer() and measure refusals, citations, length,
# cost, speed and the top search score.
# Run it with:  python src/evaluate_answers.py
#           or:  SOURCES=articles python src/evaluate_answers.py
# Saves one row per question to results/answers_<mode>.csv, where <mode> is the
# source mode answer() reports (chunks or articles).
import csv
import math
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector

import answer as answer_module
from answer import _embed_model, answer

QUESTIONS = Path("tests/questions.csv")
RESULTS_DIR = Path("results")
WAIT_SECONDS = 7  # Gemini free tier: 10 requests per minute
LONG_ANSWER = 120  # words

FIELDS = [
    "qid", "mode", "answerable", "topic", "audience", "question", "refused", "top_score",
    "cited", "citations_valid", "words", "input_tokens", "output_tokens",
    "cost_usd", "seconds", "error", "answer",
]

SCORE_SQL = "SELECT 1 - (embedding <=> %(q)s) FROM chunks WHERE chunk_id = %(chunk_id)s"


def top_score(conn, question, sources):
    """Cosine similarity between the question and the top chunk answer() used."""
    if not sources:
        return None
    q = next(iter(_embed_model().query_embed([question])))
    q = (q / np.linalg.norm(q)).astype(np.float32)
    row = conn.execute(SCORE_SQL, {"q": q, "chunk_id": sources[0]["chunk_id"]}).fetchone()
    return float(row[0]) if row else None


def p95(values):
    """95th percentile by the nearest-rank method."""
    ordered = sorted(values)
    return ordered[math.ceil(0.95 * len(ordered)) - 1]


def mean(values):
    return sum(values) / len(values) if values else float("nan")


def main():
    if not QUESTIONS.exists():
        sys.exit(f"Problem: {QUESTIONS} not found.")
    with QUESTIONS.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    load_dotenv()
    url = os.environ.get("DATABASE_URL")
    if not url:
        sys.exit("Problem: DATABASE_URL is not set. Add it to the .env file.")
    try:
        conn = psycopg.connect(url)
    except psycopg.OperationalError as e:
        sys.exit(f"Problem: could not connect to the database. Is it running?\n{e}")
    register_vector(conn)

    RESULTS_DIR.mkdir(exist_ok=True)
    results = []
    # The output file is named after the mode answer() reports, so it is opened
    # after the first successful answer. Rows that fail before then wait in `pending`.
    mode, out, writer, pending = None, None, None, []

    def write(record):
        writer.writerow({
            **record,
            "mode": mode,
            "cited": ";".join(map(str, record.get("cited", []))),
            "top_score": f"{record['top_score']:.4f}" if record.get("top_score") is not None else "",
            "cost_usd": f"{record['cost_usd']:.6f}" if "cost_usd" in record else "",
            "seconds": f"{record['seconds']:.2f}" if "seconds" in record else "",
        })

    def open_output(m):
        nonlocal mode, out, writer
        mode = m
        out = output_path(mode).open("w", newline="", encoding="utf-8")
        writer = csv.DictWriter(out, fieldnames=FIELDS)
        writer.writeheader()
        for r in pending:
            write(r)

    with conn:
        for i, row in enumerate(rows, start=1):
            if i > 1:
                time.sleep(WAIT_SECONDS)
            record = {
                "qid": row["qid"],
                "answerable": row["answerable"] == "yes",
                "topic": row["topic"],
                "audience": row["audience"],
                "question": row["question"],
            }
            try:
                r = answer(row["question"], row["audience"])
            except Exception as e:  # keep going; one failure shouldn't lose the run
                # Only the error type and message; never the request or its headers.
                record.update(error=f"{type(e).__name__}: {e}", refused=None, answer="")
                print(f"{i}/{len(rows)} {row['qid']} ERROR {type(e).__name__}")
            else:
                if mode is None:
                    open_output(r["mode"])
                record.update(
                    refused=r["refused"],
                    top_score=top_score(conn, row["question"], r["sources"]),
                    cited=r["cited"],
                    citations_valid=not r["invalid_citations"],
                    words=len(r["text"].split()),
                    input_tokens=r["input_tokens"],
                    output_tokens=r["output_tokens"],
                    cost_usd=r["cost_usd"],
                    seconds=r["seconds"],
                    error="",
                    answer=r["text"],
                )
                status = "refused" if r["refused"] else "answered"
                print(f"{i}/{len(rows)} {row['qid']} {status} {r['seconds']:.1f}s")

            results.append(record)
            if writer is None:
                pending.append(record)
            else:
                write(record)
                out.flush()

    if writer is None:  # every question failed, so answer() never reported a mode
        open_output(answer_module.SOURCES)
    out.close()
    report(results, output_path(mode))


def output_path(mode):
    return RESULTS_DIR / f"answers_{mode}.csv"


def report(results, output):
    ok = [r for r in results if not r.get("error")]
    failed = [r for r in results if r.get("error")]
    answerable = [r for r in ok if r["answerable"]]
    unanswerable = [r for r in ok if not r["answerable"]]
    answered = [r for r in ok if not r["refused"]]

    print("\n=== Results ===")
    if failed:
        print(f"Errors: {len(failed)} questions failed: {', '.join(r['qid'] for r in failed)}")

    total_unans = sum(1 for r in results if not r["answerable"])
    total_ans = sum(1 for r in results if r["answerable"])

    correct = [r for r in unanswerable if r["refused"]]
    leaked = [r for r in unanswerable if not r["refused"]]
    print(f"\nCorrect refusals: {len(correct)} of {total_unans}")
    for r in leaked:
        print(f"  answered: {r['qid']}  {r['question']}")

    wrong = [r for r in answerable if r["refused"]]
    print(f"\nWrong refusals: {len(wrong)} of {total_ans}")
    for r in wrong:
        print(f"  {r['qid']}  {r['question']}")

    no_cite = [r for r in answered if not r["cited"]]
    bad_cite = [r for r in answered if not r["citations_valid"]]
    print(f"\nAnswers with no citation: {len(no_cite)}"
          + (f"  ({', '.join(r['qid'] for r in no_cite)})" if no_cite else ""))
    print(f"Answers citing a source that doesn't exist: {len(bad_cite)}"
          + (f"  ({', '.join(r['qid'] for r in bad_cite)})" if bad_cite else ""))

    words = [r["words"] for r in answered]
    long = [r for r in answered if r["words"] > LONG_ANSWER]
    print(f"\nAverage words (answers, not refusals): {mean(words):.0f}")
    print(f"Over {LONG_ANSWER} words: {len(long)}"
          + (f"  ({', '.join(r['qid'] for r in long)})" if long else ""))

    costs = [r["cost_usd"] for r in ok]
    secs = [r["seconds"] for r in ok]
    if ok:
        print(f"\nTotal cost: ${sum(costs):.6f}")
        print(f"Average cost per answer: ${mean(costs):.6f}")
        print(f"Seconds: average {mean(secs):.1f}, p95 {p95(secs):.1f}")

    ans_scores = [r["top_score"] for r in answerable if r.get("top_score") is not None]
    unans_scores = [r["top_score"] for r in unanswerable if r.get("top_score") is not None]
    print("\nTop search score:")
    print(f"  average answerable:   {mean(ans_scores):.3f}")
    print(f"  average unanswerable: {mean(unans_scores):.3f}")
    if ans_scores and unans_scores:
        low = min((r for r in answerable if r.get("top_score") is not None), key=lambda r: r["top_score"])
        high = max((r for r in unanswerable if r.get("top_score") is not None), key=lambda r: r["top_score"])
        print(f"  lowest answerable:    {low['top_score']:.3f}  ({low['qid']})")
        print(f"  highest unanswerable: {high['top_score']:.3f}  ({high['qid']})")

    print(f"\nSaved {len(results)} rows to {output}")


if __name__ == "__main__":
    main()
