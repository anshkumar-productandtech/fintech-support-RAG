# Build a human review sheet for 10 answers from the rewrite run.
# Run it with:  python src/make_review_sheet.py
#
# Picks 10 answered questions from results/answers_rewrite.csv (seed 7), plus EXTRA_QIDS: 6 customer and
# 4 merchant, at least 4 of them Hinglish. For each, rebuilds the 5 sources the answer
# saw by searching with the question and the saved rewritten query and merging them with
# answer.get_sources(), the same call answer() makes. No Gemini calls.
#
# Writes results/review_sheet.md and results/human_ratings.csv (blank ratings to fill in
# with y or n). A rerun keeps any ratings already in the file and adds blank rows for new qids.
import csv
import random
import re
import sys
from pathlib import Path

import numpy as np

from answer import TOP_K, _connect, _embed_model, cited_numbers, get_sources

ANSWERS = Path("results/answers_rewrite.csv")
SHEET = Path("results/review_sheet.md")
RATINGS = Path("results/human_ratings.csv")
RATING_COLUMNS = ["qid", "faithful", "complete", "language", "note"]

SEED = 7
COUNTS = {"customer": 6, "merchant": 4}
MIN_HINGLISH = 4
# Hand-picked questions reviewed on top of the seeded sample.
EXTRA_QIDS = ["Q01", "Q28", "Q37"]

# A question counts as Hinglish if it has at least one of these Hindi words. Mixed
# questions like "compensation milega?" count. English words such as "me" and "to"
# are left out on purpose.
HINDI_WORDS = {
    "aaj", "aata", "aaya", "aayega", "aane", "ab", "abhi", "baar", "band", "bhej",
    "bol", "bola", "chahiye", "chori", "daala", "dikha", "diya", "din", "ek", "gaya",
    "galat", "galti", "hai", "ho", "hua", "ka", "kaha", "kaise", "kab", "kam", "kar",
    "kare", "karu", "katega", "kat", "ke", "ki", "kitna", "kitne", "kitni", "ko", "kya",
    "kyu", "mera", "mere", "meri", "milega", "nahi", "pa", "paisa", "paise", "raha",
    "rahi", "rakh", "reh", "sakta", "sakte", "se", "tak", "wapas",
}

# Cosine similarity between a question and one stored chunk, the way
# evaluate_answers.py computes top_score.
SCORE_SQL = "SELECT 1 - (embedding <=> %(q)s) FROM chunks WHERE chunk_id = %(chunk_id)s"
SCORE_TOLERANCE = 0.0001  # top_score is saved with 4 decimals


def is_hinglish(question):
    return any(w in HINDI_WORDS for w in re.findall(r"[a-z]+", question.lower()))


def pick(rows):
    """6 customer + 4 merchant answered questions, at least 4 Hinglish, seeded."""
    rng = random.Random(SEED)
    pools = {a: [r for r in rows if r["audience"] == a] for a in COUNTS}
    for a, n in COUNTS.items():
        if len(pools[a]) < n:
            sys.exit(f"Problem: only {len(pools[a])} answered {a} questions, need {n}.")
    # Redraw until the Hinglish minimum holds. The seed makes the result repeatable.
    for _ in range(1000):
        picked = [r for a, n in COUNTS.items() for r in rng.sample(pools[a], n)]
        if sum(is_hinglish(r["question"]) for r in picked) >= MIN_HINGLISH:
            return sorted(picked, key=lambda r: r["qid"])
    sys.exit(f"Problem: couldn't find a sample with {MIN_HINGLISH} Hinglish questions.")


def question_score(conn, question, chunk_id):
    q = next(iter(_embed_model().query_embed([question])))
    q = (q / np.linalg.norm(q)).astype(np.float32)
    row = conn.execute(SCORE_SQL, {"q": q, "chunk_id": chunk_id}).fetchone()
    return float(row[0]) if row else None


def quote(text):
    """Blockquote text so its own headings and tables stay inside the entry."""
    return "\n".join(f"> {line}" if line else ">" for line in text.strip().splitlines())


def existing_ratings():
    """Ratings already in the file, by qid, so a rerun never wipes them."""
    if not RATINGS.exists():
        return {}
    with RATINGS.open(encoding="utf-8") as f:
        return {r["qid"]: r for r in csv.DictReader(f)}


def main():
    if not ANSWERS.exists():
        sys.exit(f"Problem: {ANSWERS} not found. Run: REWRITE=on python src/evaluate_answers.py")
    kept = existing_ratings()

    with ANSWERS.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    modes = {r["mode"] for r in rows}
    if modes != {"rewrite"}:
        sys.exit(f"Problem: expected only rewrite-mode rows, found {sorted(modes)}.")
    answered = [r for r in rows if r["refused"] == "False" and not r["error"]]

    picked = pick(answered)
    by_qid = {r["qid"]: r for r in answered}
    for qid in EXTRA_QIDS:
        if qid not in by_qid:
            sys.exit(f"Problem: {qid} isn't an answered question in {ANSWERS}.")
        if all(r["qid"] != qid for r in picked):
            picked.append(by_qid[qid])
    picked.sort(key=lambda r: r["qid"])
    mismatches = []
    bad_citations = []
    entries = []
    with _connect() as conn:
        for r in picked:
            sources = get_sources(r["question"], r["audience"], r["rewritten_query"])
            if len(sources) != TOP_K:
                sys.exit(f"Problem: {r['qid']} rebuilt {len(sources)} sources, expected {TOP_K}.")
            # Check the rebuild against the saved run.
            score = question_score(conn, r["question"], sources[0]["chunk_id"])
            saved = float(r["top_score"]) if r["top_score"] else None
            cited = cited_numbers(r["answer"])
            ok = saved is not None and score is not None and abs(score - saved) <= SCORE_TOLERANCE
            if not ok:
                mismatches.append(f"{r['qid']}: top_score saved {saved}, rebuilt {score}")
            # A citation past [5] is the model's mistake in the saved answer, not a rebuild
            # problem: it was flagged as citations_valid=False when the answer was made.
            if any(not 1 <= n <= TOP_K for n in cited):
                bad_citations.append(f"{r['qid']}: cites {cited}, only {TOP_K} sources exist")
            entries.append((r, sources, cited))

    hinglish = sum(is_hinglish(r["question"]) for r, _, _ in entries)
    customers = sum(r["audience"] == "customer" for r, _, _ in entries)
    lines = [
        "# Answer review sheet",
        "",
        f"{len(entries)} answered questions from `{ANSWERS}`: {sum(COUNTS.values())} "
        f"picked with seed {SEED}, plus {', '.join(EXTRA_QIDS)} added by hand. "
        f"{customers} customer, {len(entries) - customers} merchant, {hinglish} Hinglish.",
        "Each answer is shown with the 5 sources it was given, rebuilt from the database.",
        f"Rate each one in `{RATINGS}` with y or n:",
        "",
        "- **faithful**: every claim is backed by the source it cites.",
        "- **complete**: it includes every fee, limit, time and condition from the sources "
        "that applies to the question.",
        "- **language**: it replies in the question's language (Hinglish, Hindi or English).",
        "",
    ]
    for r, sources, cited in entries:
        lang = "Hinglish" if is_hinglish(r["question"]) else "English"
        lines += [
            "---",
            "",
            f"## {r['qid']} · {r['audience']} · {lang}",
            "",
            f"**Question:** {r['question']}",
            "",
            f"**Rewritten query:** {r['rewritten_query'] or '(none)'}",
            "",
            f"**Answer** (cites {', '.join(f'[{n}]' for n in cited) or 'nothing'}):",
            "",
            quote(r["answer"]),
            "",
            "### Sources",
            "",
        ]
        for i, s in enumerate(sources, start=1):
            mark = " · cited" if i in cited else ""
            lines += [f"**[{i}] {s['title']}** · `{s['chunk_id']}`{mark}", "", quote(s["text"]), ""]
        missing = [n for n in cited if not 1 <= n <= TOP_K]
        if missing:
            nums = ", ".join(f"[{n}]" for n in missing)
            lines += [f"**Note:** the answer cites {nums}, but only {TOP_K} sources were sent.", ""]

    SHEET.write_text("\n".join(lines), encoding="utf-8")
    with RATINGS.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(RATING_COLUMNS)
        qids = [r["qid"] for r, _, _ in entries]
        # Keep any rated question that is no longer in the sample, rather than drop it.
        qids += [q for q in kept if q not in qids]
        for qid in qids:
            old = kept.get(qid, {})
            w.writerow([qid] + [old.get(c, "") for c in RATING_COLUMNS[1:]])

    print(f"Picked: {', '.join(r['qid'] for r, _, _ in entries)}  ({hinglish} Hinglish)")
    print(f"Saved {SHEET} and {RATINGS}")
    if mismatches:
        print("\nWarning: these may not be the exact sources the answer saw:")
        for m in mismatches:
            print(f"  {m}")
    else:
        print(f"Rebuilt sources match the saved run (top_score checks out for all {len(entries)}).")
    if bad_citations:
        print("\nNote: these saved answers cite sources that don't exist:")
        for m in bad_citations:
            print(f"  {m}")


if __name__ == "__main__":
    main()
