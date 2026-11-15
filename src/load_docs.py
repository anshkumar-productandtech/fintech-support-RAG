# Load Kuberix's help articles into one file.
# Run it with:  python src/load_docs.py all
import json
import sys
from pathlib import Path

ARTICLES = Path("help-center")
OUTPUT = Path("data/docs.jsonl")
AUDIENCES = ["customer", "merchant", "all"]


def split_front_matter(raw):
    # An article starts with settings between two '---' lines. Split them off.
    settings = {}
    if not raw.startswith("---"):
        return settings, raw
    _, header, body = raw.split("---", 2)
    for line in header.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            settings[key.strip()] = value.strip()
    return settings, body.strip()


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in AUDIENCES:
        sys.exit("Say which audience: customer, merchant or all")
    audience = sys.argv[1]

    OUTPUT.parent.mkdir(exist_ok=True)
    count = 0
    words = 0
    with OUTPUT.open("w", encoding="utf-8") as out:
        for path in sorted(ARTICLES.glob("*.md")):
            settings, body = split_front_matter(path.read_text(encoding="utf-8"))
            if audience != "all" and settings["audience"] != audience:
                continue
            page = {
                "id": settings["id"],
                "title": settings["title"],
                "audience": settings["audience"],
                "category": settings["category"],
                "text": body,
            }
            out.write(json.dumps(page, ensure_ascii=False) + "\n")
            count += 1
            words += len(body.split())

    print(f"Saved {count} articles ({words:,} words) to {OUTPUT}")


main()