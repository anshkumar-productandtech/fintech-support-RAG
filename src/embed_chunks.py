# Embed every chunk's text and save the vectors as a numpy array.
# Run it with:  python src/embed_chunks.py section
#          or:  python src/embed_chunks.py llamaindex
import json
import sys
import time
from pathlib import Path

CHUNK_FILES = {
    "section": Path("data/chunks_by_section.jsonl"),
    "llamaindex": Path("data/chunks_llamaindex.jsonl"),
}
MODEL = "BAAI/bge-small-en-v1.5"

if len(sys.argv) != 2 or sys.argv[1] not in CHUNK_FILES:
    sys.exit("Usage: python src/embed_chunks.py section|llamaindex")

name = sys.argv[1]
chunks_path = CHUNK_FILES[name]
if not chunks_path.exists():
    sys.exit(f"Problem: {chunks_path} not found. Run the chunking script first.")

# Imported after the argument check so a usage mistake fails fast and clean.
import numpy as np
from fastembed import TextEmbedding

with chunks_path.open(encoding="utf-8") as f:
    chunks = [json.loads(line) for line in f if line.strip()]
texts = [chunk["text"] for chunk in chunks]

start = time.perf_counter()
model = TextEmbedding(MODEL)
vectors = np.array(list(model.passage_embed(texts)), dtype=np.float32)
# Scale every vector to length 1 so a dot product equals cosine similarity.
vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
seconds = time.perf_counter() - start

out_path = Path(f"data/vectors_{name}.npy")
np.save(out_path, vectors)

print(f"Embedded {vectors.shape[0]} chunks from {chunks_path}")
print(f"Each vector has {vectors.shape[1]} numbers")
print(f"Took {seconds:.1f} seconds")
print(f"Saved to {out_path}")
