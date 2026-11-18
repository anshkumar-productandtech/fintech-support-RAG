# Compare the chunks-mode and articles-mode answer runs side by side.
# Run it with:  python src/compare_runs.py
# Reads results/answers_chunks.csv and results/answers_articles.csv
# (written by src/evaluate_answers.py with SOURCES=chunks and SOURCES=articles).
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from evaluate_answers import LONG_ANSWER, mean, p95

RUNS = {
    "chunks": Path("results/answers_chunks.csv"),
    "articles": Path("results/answers_articles.csv"),
}


def load(path):
    if not path.exists():
        sys.exit(f"Problem: {path} not found. Run src/evaluate_answers.py first.")
    with path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["answerable"] = r["answerable"] == "True"
        r["ok"] = not r["error"]
        r["refused"] = r["refused"] == "True" if r["ok"] else None
    return {r["qid"]: r for r in rows}


def result(row):
    """'refused', 'answered', 'error', or 'missing' for one question in one run."""
    if row is None:
        return "missing"
    if not row["ok"]:
        return "error"
    return "refused" if row["refused"] else "answered"


def summary(rows):
    rows = list(rows.values())
    ok = [r for r in rows if r["ok"]]
    answered = [r for r in ok if not r["refused"]]
    words = [int(r["words"]) for r in answered]
    costs = [float(r["cost_usd"]) for r in ok]
    secs = [float(r["seconds"]) for r in ok]
    n_unans = sum(1 for r in rows if not r["answerable"])
    n_ans = sum(1 for r in rows if r["answerable"])
    return [
        ("Correct refusals", f"{sum(1 for r in ok if not r['answerable'] and r['refused'])}/{n_unans}"),
        ("Wrong refusals", f"{sum(1 for r in ok if r['answerable'] and r['refused'])}/{n_ans}"),
        ("Uncited answers", str(sum(1 for r in answered if not r["cited"]))),
        ("Invalid citations", str(sum(1 for r in answered if r["citations_valid"] != "True"))),
        ("Avg words", f"{mean(words):.0f}"),
        (f"Over {LONG_ANSWER} words", str(sum(1 for w in words if w > LONG_ANSWER))),
        ("Avg cost", f"${mean(costs):.6f}"),
        ("Avg seconds", f"{mean(secs):.1f}"),
        ("p95 seconds", f"{p95(secs):.1f}" if secs else "nan"),
        ("Errors", str(len(rows) - len(ok))),
    ]


def main():
    chunks, articles = (load(p) for p in RUNS.values())

    print("=== Summary ===")
    print(f"{'':20} {'chunks':>12} {'articles':>12}")
    for (label, a), (_, b) in zip(summary(chunks), summary(articles)):
        print(f"{label:20} {a:>12} {b:>12}")

    qids = sorted(set(chunks) | set(articles))
    changed = [q for q in qids if result(chunks.get(q)) != result(articles.get(q))]
    print(f"\n=== Refused changed between runs: {len(changed)} ===")
    for q in changed:
        row = chunks.get(q) or articles.get(q)
        print(f"{q}  chunks: {result(chunks.get(q)):8}  articles: {result(articles.get(q)):8}  {row['question']}")

    regressions = [
        q for q in qids
        if q in chunks and q in articles and chunks[q]["answerable"]
        and result(chunks[q]) == "answered" and result(articles[q]) == "refused"
    ]
    print(f"\n=== Regressions (answerable, answered in chunks, refused in articles): {len(regressions)} ===")
    if not regressions:
        print("None.")
    for q in regressions:
        print(f"{q}  {chunks[q]['question']}")


if __name__ == "__main__":
    main()
