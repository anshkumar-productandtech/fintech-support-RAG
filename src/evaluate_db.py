# Measure how well the Postgres search finds the right article for each test question.
# Run it with:  python src/evaluate_db.py
#          or:  python src/evaluate_db.py filter   (only search the question's own audience)
import csv
import os
import sys
from pathlib import Path

QUESTIONS = Path("tests/questions.csv")
MODEL = "BAAI/bge-small-en-v1.5"
TOP_K = 5

if len(sys.argv) > 2 or (len(sys.argv) == 2 and sys.argv[1] != "filter"):
    sys.exit("Usage: python src/evaluate_db.py [filter]")
use_filter = len(sys.argv) == 2

if not QUESTIONS.exists():
    sys.exit(f"Problem: {QUESTIONS} not found.")

# Imported after the argument check so a usage mistake fails fast and clean.
import numpy as np
import psycopg
from dotenv import load_dotenv
from fastembed import TextEmbedding
from pgvector.psycopg import register_vector

load_dotenv()
url = os.environ.get("DATABASE_URL")
if not url:
    sys.exit("Problem: DATABASE_URL is not set. Add it to the .env file.")

with QUESTIONS.open(encoding="utf-8", newline="") as f:
    questions = [row for row in csv.DictReader(f) if row["answerable"].strip() == "yes"]
if not questions:
    sys.exit(f"Problem: no answerable questions in {QUESTIONS}.")

model = TextEmbedding(MODEL)
q = np.array(list(model.query_embed([row["question"] for row in questions])), dtype=np.float32)
q = q / np.linalg.norm(q, axis=1, keepdims=True)

# When audience is NULL the filter lets every row through.
SQL = """
    SELECT doc_id, chunk_id
    FROM chunks
    WHERE %(audience)s::text IS NULL OR audience = %(audience)s
    ORDER BY embedding <=> %(q)s
"""

try:
    conn = psycopg.connect(url, prepare_threshold=None)
except psycopg.OperationalError as e:
    sys.exit(f"Problem: could not connect to the database. Is it running?\n{e}")

results = []
with conn:
    register_vector(conn)
    for row, vec in zip(questions, q):
        params = {"q": vec, "audience": row["audience"] if use_filter else None}
        try:
            ranked = conn.execute(SQL, params).fetchall()
        except psycopg.errors.UndefinedTable:
            sys.exit("Problem: the chunks table does not exist. Run: python src/load_db.py")

        doc_ids = [doc_id for doc_id, _ in ranked]
        if row["expected_id"] in doc_ids:
            rank = doc_ids.index(row["expected_id"]) + 1
        else:
            rank = len(ranked) + 1
        results.append({
            "qid": row["qid"],
            "topic": row["topic"],
            "expected_id": row["expected_id"],
            "rank": rank,
            "hit": rank <= TOP_K,
            "top_result": ranked[0][1] if ranked else "",
            "question": row["question"],
        })

total = len(results)
hits = sum(r["hit"] for r in results)
firsts = sum(r["rank"] == 1 for r in results)
mrr = sum(1 / r["rank"] for r in results) / total

print(f"Postgres search, {'filtered by audience' if use_filter else 'no filter'}, questions: {total}")
print(f"Hit rate (rank <= {TOP_K}): {hits}/{total} ({hits / total:.0%})")
print(f"Ranked 1st: {firsts}/{total}")
print(f"MRR: {mrr:.3f}")

misses = [r for r in results if not r["hit"]]
print(f"\nMisses ({len(misses)}):")
for r in misses:
    print(f"  {r['qid']}  rank {r['rank']}  expected {r['expected_id']}  top {r['top_result']}  {r['question']}")

out_path = Path(f"results/retrieval_db_{'filter' if use_filter else 'no_filter'}.csv")
out_path.parent.mkdir(exist_ok=True)
with out_path.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(results[0]))
    writer.writeheader()
    writer.writerows(results)
print(f"\nSaved to {out_path}")
