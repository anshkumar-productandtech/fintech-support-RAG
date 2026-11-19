# Compare the Ragas judge's ratings with the human ratings.
# Run it with:  python src/compare_judge.py
#
# Reads results/human_ratings.csv and results/judge_ratings.csv. For each check
# (faithful, complete, language) prints how often the judge agrees with the human, as
# X of N, and lists every disagreement with the judge's reason. Faithfulness counts as
# y at 1.0 and n below 1.0. A qid is left out of a check when either side has no rating.
import csv
import sys
from pathlib import Path

HUMAN = Path("results/human_ratings.csv")
JUDGE = Path("results/judge_ratings.csv")
CHECKS = ["faithful", "complete", "language"]


def load(path):
    if not path.exists():
        sys.exit(f"Problem: {path} not found.")
    with path.open(encoding="utf-8") as f:
        return {r["qid"]: r for r in csv.DictReader(f)}


def judge_rating(row, check):
    """The judge's (y/n, reason) for a check, or (None, None) if it has none."""
    if check == "faithful":
        score = (row.get("faithfulness") or "").strip()
        if not score:
            return None, None
        value = float(score)
        claims = (row.get("unsupported_claims") or "").strip()
        reason = f"score {value:.3f}" + (f"; unsupported: {claims}" if claims else "")
        return ("y" if value >= 1.0 else "n"), reason
    value = (row.get(check) or "").strip().lower()
    return (value or None), (row.get(f"{check}_reason") or "").strip()


def main():
    human, judge = load(HUMAN), load(JUDGE)
    for check in CHECKS:
        agree, compared, disagreements, skipped = 0, 0, [], []
        for qid, h in human.items():
            mine = (h.get(check) or "").strip().lower()
            theirs, reason = judge_rating(judge[qid], check) if qid in judge else (None, None)
            if not mine or not theirs:
                skipped.append(qid)
                continue
            compared += 1
            if mine == theirs:
                agree += 1
            else:
                disagreements.append((qid, mine, theirs, reason, (h.get("note") or "").strip()))

        print(f"\n{check}: {agree} of {compared} agree")
        if skipped:
            print(f"  not compared (a rating is missing): {', '.join(skipped)}")
        for qid, mine, theirs, reason, note in disagreements:
            print(f"  {qid}  you: {mine}  judge: {theirs}")
            if note:
                print(f"       your note: {note}")
            print(f"       judge's reason: {reason}")


if __name__ == "__main__":
    main()
