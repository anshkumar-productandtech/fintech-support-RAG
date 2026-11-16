# Measure how well search finds the right article for each test question.
# Run it with:  python src/evaluate_retrieval.py section
#          or:  python src/evaluate_retrieval.py llamaindex
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

CHUNK_FILES = {
    "section": Path("data/chunks_by_section.jsonl"),
    "llamaindex": Path("data/chunks_llamaindex.jsonl"),
}
QUESTIONS = Path("tests/questions.csv")
MODEL = "BAAI/bge-small-en-v1.5"
TOP_K = 5

if len(sys.argv) != 2 or sys.argv[1] not in CHUNK_FILES:
    sys.exit("Usage: python src/evaluate_retrieval.py section|llamaindex")

name = sys.argv[1]
chunks_path = CHUNK_FILES[name]
vectors_path = Path(f"data/vectors_{name}.npy")
for path in (chunks_path, vectors_path, QUESTIONS):
    if not path.exists():
        sys.exit(f"Problem: {path} not found.")

# Imported after the argument check so a usage mistake fails fast and clean.
import numpy as np
from fastembed import TextEmbedding

with chunks_path.open(encoding="utf-8") as f:
    chunks = [json.loads(line) for line in f if line.strip()]
vectors = np.load(vectors_path)
if len(chunks) != len(vectors):
    sys.exit(f"Problem: {len(chunks)} chunks but {len(vectors)} vectors. Re-run embed_chunks.py {name}.")

with QUESTIONS.open(encoding="utf-8", newline="") as f:
    questions = [row for row in csv.DictReader(f) if row["answerable"].strip() == "yes"]
if not questions:
    sys.exit(f"Problem: no answerable questions in {QUESTIONS}.")

model = TextEmbedding(MODEL)
q = np.array(list(model.query_embed([row["question"] for row in questions])), dtype=np.float32)
q = q / np.linalg.norm(q, axis=1, keepdims=True)

# One row per question, one column per chunk.
scores = q @ vectors.T
order = np.argsort(-scores, axis=1)
doc_ids = np.array([chunk["doc_id"] for chunk in chunks])

results = []
for row, ranked in zip(questions, order):
    matches = np.nonzero(doc_ids[ranked] == row["expected_id"])[0]
    # If the expected article has no chunks at all, rank it after every chunk.
    rank = int(matches[0]) + 1 if len(matches) else len(chunks) + 1
    results.append({
        "qid": row["qid"],
        "topic": row["topic"],
        "expected_id": row["expected_id"],
        "rank": rank,
        "hit": rank <= TOP_K,
        "top_result": chunks[ranked[0]]["chunk_id"],
        "question": row["question"],
    })

total = len(results)
hits = sum(r["hit"] for r in results)
firsts = sum(r["rank"] == 1 for r in results)
mrr = sum(1 / r["rank"] for r in results) / total

print(f"Chunks: {name} ({len(chunks)} chunks), questions: {total}")
print(f"Hit rate (rank <= {TOP_K}): {hits}/{total} ({hits / total:.0%})")
print(f"Ranked 1st: {firsts}/{total}")
print(f"MRR: {mrr:.3f}")

by_topic = defaultdict(lambda: [0, 0])
for r in results:
    by_topic[r["topic"]][0] += r["hit"]
    by_topic[r["topic"]][1] += 1
print("\nHits per topic:")
for topic, (h, n) in sorted(by_topic.items()):
    print(f"  {topic}: {h}/{n}")

misses = [r for r in results if not r["hit"]]
print(f"\nMisses ({len(misses)}):")
for r in misses:
    print(f"  {r['qid']}  rank {r['rank']}  expected {r['expected_id']}  top {r['top_result']}  {r['question']}")

out_path = Path(f"results/retrieval_{name}.csv")
out_path.parent.mkdir(exist_ok=True)
with out_path.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(results[0]))
    writer.writeheader()
    writer.writerows(results)
print(f"\nSaved to {out_path}")
