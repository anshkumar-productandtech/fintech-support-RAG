# Compare two answer runs side by side.
# Run it with:  python src/compare_runs.py results/answers_chunks.csv results/answers_rewrite.csv
# With no arguments it compares results/answers_chunks.csv and results/answers_articles.csv.
# Both files are written by src/evaluate_answers.py. The first file is the baseline.
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from evaluate_answers import LONG_ANSWER, mean, p95

DEFAULT_RUNS = [Path("results/answers_chunks.csv"), Path("results/answers_articles.csv")]
USAGE = "Usage: python src/compare_runs.py BASELINE.csv OTHER.csv"


def label(path):
    """Short run name from the file name: answers_rewrite.csv -> rewrite."""
    return path.stem.removeprefix("answers_")


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
    if len(sys.argv) == 1:
        paths = DEFAULT_RUNS
    elif len(sys.argv) == 3:
        paths = [Path(a) for a in sys.argv[1:]]
    else:
        sys.exit(USAGE)
    a_name, b_name = (label(p) for p in paths)
    if a_name == b_name:
        a_name, b_name = str(paths[0]), str(paths[1])
    a, b = (load(p) for p in paths)
    w = max(12, len(a_name), len(b_name))

    print("=== Summary ===")
    print(f"{'':20} {a_name:>{w}} {b_name:>{w}}")
    for (lbl, x), (_, y) in zip(summary(a), summary(b)):
        print(f"{lbl:20} {x:>{w}} {y:>{w}}")

    qids = sorted(set(a) | set(b))
    changed = [q for q in qids if result(a.get(q)) != result(b.get(q))]
    print(f"\n=== Refused changed between runs: {len(changed)} ===")
    for q in changed:
        row = a.get(q) or b.get(q)
        print(f"{q}  {a_name}: {result(a.get(q)):8}  {b_name}: {result(b.get(q)):8}  {row['question']}")

    regressions = [
        q for q in qids
        if q in a and q in b and a[q]["answerable"]
        and result(a[q]) == "answered" and result(b[q]) == "refused"
    ]
    print(f"\n=== Regressions (answerable, answered in {a_name}, refused in {b_name}): {len(regressions)} ===")
    if not regressions:
        print("None.")
    for q in regressions:
        print(f"{q}  {a[q]['question']}")


if __name__ == "__main__":
    main()
