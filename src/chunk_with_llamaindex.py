# Split each help article into chunks with LlamaIndex's SentenceSplitter.
# Run it with:  python src/chunk_with_llamaindex.py
# Needs data/docs.jsonl first:  python src/load_docs.py all
import json
from pathlib import Path

from llama_index.core.node_parser import SentenceSplitter

DOCS = Path("data/docs.jsonl")
OUTPUT = Path("data/chunks_llamaindex.jsonl")


def main():
    # chunk_size and chunk_overlap are counted in tokens, not words.
    splitter = SentenceSplitter(chunk_size=128, chunk_overlap=16)
    chunks = []
    with DOCS.open(encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            for number, text in enumerate(splitter.split_text(doc["text"]), start=1):
                chunks.append({
                    "chunk_id": f"{doc['id']}#{number}",
                    "doc_id": doc["id"],
                    "title": doc["title"],
                    "audience": doc["audience"],
                    "text": text,
                })

    with OUTPUT.open("w", encoding="utf-8") as out:
        for chunk in chunks:
            out.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    sizes = [len(chunk["text"].split()) for chunk in chunks]
    print(f"Saved {len(chunks)} chunks to {OUTPUT}")
    print(f"Words per chunk: average {sum(sizes) / len(sizes):.0f}, "
          f"smallest {min(sizes)}, largest {max(sizes)}")


main()
