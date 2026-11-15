# Split each help article into chunks, one per "## " section.
# Run it with:  python src/chunk_by_section.py
# Needs data/docs.jsonl first:  python src/load_docs.py all
import json
from pathlib import Path

DOCS = Path("data/docs.jsonl")
OUTPUT = Path("data/chunks_by_section.jsonl")


def split_sections(text):
    # Start a new section at every "## " line. Text before the first "## "
    # (the article's intro) is a section too. The "# " title line is skipped.
    sections = [[]]
    for line in text.splitlines():
        if line.startswith("# "):
            continue
        if line.startswith("## "):
            sections.append([])
        sections[-1].append(line)
    joined = ("\n".join(lines).strip() for lines in sections)
    return [section for section in joined if section]


def main():
    chunks = []
    with DOCS.open(encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            for number, section in enumerate(split_sections(doc["text"]), start=1):
                chunks.append({
                    "chunk_id": f"{doc['id']}#{number}",
                    "doc_id": doc["id"],
                    "title": doc["title"],
                    "audience": doc["audience"],
                    "text": f"{doc['title']}\n\n{section}",
                })

    with OUTPUT.open("w", encoding="utf-8") as out:
        for chunk in chunks:
            out.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    sizes = [len(chunk["text"].split()) for chunk in chunks]
    print(f"Saved {len(chunks)} chunks to {OUTPUT}")
    print(f"Words per chunk: average {sum(sizes) / len(sizes):.0f}, "
          f"smallest {min(sizes)}, largest {max(sizes)}")


main()
