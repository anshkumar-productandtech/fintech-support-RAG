# Load the section chunks and their vectors into a Postgres table.
# Run it with:  python src/load_db.py
import json
import os
import sys
from pathlib import Path

import numpy as np
import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector

CHUNKS = Path("data/chunks_by_section.jsonl")
VECTORS = Path("data/vectors_section.npy")

load_dotenv()
url = os.environ.get("DATABASE_URL")
if not url:
    sys.exit("Problem: DATABASE_URL is not set. Add it to the .env file.")

for path in (CHUNKS, VECTORS):
    if not path.exists():
        sys.exit(f"Problem: {path} not found. Run the chunking and embedding scripts first.")

with CHUNKS.open(encoding="utf-8") as f:
    chunks = [json.loads(line) for line in f if line.strip()]
vectors = np.load(VECTORS)
if len(chunks) != len(vectors):
    sys.exit(f"Problem: {len(chunks)} chunks but {len(vectors)} vectors. Re-run: python src/embed_chunks.py section")

try:
    conn = psycopg.connect(url)
except psycopg.OperationalError as e:
    sys.exit(f"Problem: could not connect to the database. Is it running?\n{e}")

with conn:
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    # The extension must exist before psycopg can learn the vector type.
    register_vector(conn)

    conn.execute("DROP TABLE IF EXISTS chunks")
    conn.execute("""
        CREATE TABLE chunks (
            chunk_id  text PRIMARY KEY,
            doc_id    text NOT NULL,
            title     text NOT NULL,
            audience  text NOT NULL,
            text      text NOT NULL,
            embedding vector(384) NOT NULL
        )
    """)
    conn.execute("ALTER TABLE chunks ENABLE ROW LEVEL SECURITY")

    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO chunks (chunk_id, doc_id, title, audience, text, embedding)"
            " VALUES (%s, %s, %s, %s, %s, %s)",
            [
                (c["chunk_id"], c["doc_id"], c["title"], c["audience"], c["text"], v)
                for c, v in zip(chunks, vectors)
            ],
        )

    total = conn.execute("SELECT count(*) FROM chunks").fetchone()[0]
    per_audience = conn.execute(
        "SELECT audience, count(*) FROM chunks GROUP BY audience ORDER BY audience"
    ).fetchall()

print(f"Loaded {total} rows into the chunks table")
for audience, n in per_audience:
    print(f"  {audience}: {n}")
