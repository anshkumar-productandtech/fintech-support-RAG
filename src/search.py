# Find the 5 chunks closest in meaning to a question.
# Run it with:  python src/search.py section "How do I link my bank account?"
#          or:  python src/search.py llamaindex "How do I link my bank account?"
import json
import sys
from pathlib import Path

CHUNK_FILES = {
    "section": Path("data/chunks_by_section.jsonl"),
    "llamaindex": Path("data/chunks_llamaindex.jsonl"),
}
MODEL = "BAAI/bge-small-en-v1.5"
TOP_K = 5

if len(sys.argv) != 3 or sys.argv[1] not in CHUNK_FILES or not sys.argv[2].strip():
    sys.exit('Usage: python src/search.py section|llamaindex "your question"')

name, question = sys.argv[1], sys.argv[2]
chunks_path = CHUNK_FILES[name]
vectors_path = Path(f"data/vectors_{name}.npy")
for path in (chunks_path, vectors_path):
    if not path.exists():
        sys.exit(f"Problem: {path} not found. Run the chunking and embedding scripts first.")

# Imported after the argument check so a usage mistake fails fast and clean.
import numpy as np
from fastembed import TextEmbedding

with chunks_path.open(encoding="utf-8") as f:
    chunks = [json.loads(line) for line in f if line.strip()]
vectors = np.load(vectors_path)
if len(chunks) != len(vectors):
    sys.exit(f"Problem: {len(chunks)} chunks but {len(vectors)} vectors. Re-run embed_chunks.py {name}.")

model = TextEmbedding(MODEL)
q = next(iter(model.query_embed([question])))
q = q / np.linalg.norm(q)

# Both sides have length 1, so the dot product is the cosine similarity.
scores = vectors @ q
top = np.argsort(scores)[::-1][:TOP_K]

for rank, i in enumerate(top, start=1):
    snippet = chunks[i]["text"][:90].replace("\n", " ")
    print(f"{rank}  {scores[i]:.3f}  {chunks[i]['chunk_id']}  {snippet}")
