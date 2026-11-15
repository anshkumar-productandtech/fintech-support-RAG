# Check the test questions in tests/questions.csv for mistakes.
# Run it with:  python src/check_tests.py
import csv
import sys
from collections import Counter
from pathlib import Path

QUESTIONS = Path("tests/questions.csv")
ARTICLES = Path("help-center")
COLUMNS = ["qid", "question", "audience", "expected_id", "answerable", "topic"]
AUDIENCES = ["customer", "merchant"]


def article_ids():
    # Read the id: line from the front matter of every article.
    ids = set()
    for path in sorted(ARTICLES.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        if not raw.startswith("---"):
            continue
        header = raw.split("---", 2)[1]
        for line in header.splitlines():
            if line.startswith("id:"):
                ids.add(line.split(":", 1)[1].strip())
    return ids


def main():
    ids = article_ids()
    problems = []

    with QUESTIONS.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != COLUMNS:
            sys.exit(f"Problem: columns are {reader.fieldnames}, expected {COLUMNS}")
        rows = list(reader)

    seen = set()
    for line, row in enumerate(rows, start=2):  # line 1 is the header
        qid = row["qid"].strip()
        where = f"line {line} ({qid or 'no qid'})"
        expected = row["expected_id"].strip()

        if not qid:
            problems.append(f"{where}: qid is empty")
        elif qid in seen:
            problems.append(f"{where}: qid is a duplicate")
        seen.add(qid)

        if row["audience"] not in AUDIENCES:
            problems.append(f"{where}: audience is '{row['audience']}', expected customer or merchant")

        if row["answerable"] == "yes":
            if not expected:
                problems.append(f"{where}: answerable but expected_id is empty")
            elif expected not in ids:
                problems.append(f"{where}: expected_id '{expected}' is not an article id")
        elif row["answerable"] == "no":
            if expected:
                problems.append(f"{where}: unanswerable but expected_id is '{expected}'")
        else:
            problems.append(f"{where}: answerable is '{row['answerable']}', expected yes or no")

    for problem in problems:
        print("Problem:", problem)
    if problems:
        print()

    answerable = [r for r in rows if r["answerable"] == "yes"]
    by_audience = Counter(r["audience"] for r in answerable)
    covered = {r["expected_id"].strip() for r in answerable} & ids

    print("Total questions:", len(rows))
    print("Answerable:", len(answerable))
    print("Not answerable:", sum(1 for r in rows if r["answerable"] == "no"))
    for audience in AUDIENCES:
        print(f"Answerable, {audience}:", by_audience[audience])
    print(f"Articles covered: {len(covered)} of {len(ids)}")

    if problems:
        sys.exit(f"{len(problems)} problem(s) found.")
    print("OK")


if __name__ == "__main__":
    main()
