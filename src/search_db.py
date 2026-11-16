# Find the 5 chunks in Postgres closest in meaning to a question.
# Run it with:  python src/search_db.py "How do I link my bank account?"
#          or:  python src/search_db.py "When do I get my settlement?" merchant
import os
import sys

AUDIENCES = ["customer", "merchant"]
MODEL = "BAAI/bge-small-en-v1.5"
USAGE = 'Usage: python src/search_db.py "your question" [customer|merchant]'

if len(sys.argv) not in (2, 3) or not sys.argv[1].strip():
    sys.exit(USAGE)
question = sys.argv[1]
audience = sys.argv[2] if len(sys.argv) == 3 else None
if audience is not None and audience not in AUDIENCES:
    sys.exit(USAGE)

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

model = TextEmbedding(MODEL)
q = next(iter(model.query_embed([question])))
q = (q / np.linalg.norm(q)).astype(np.float32)

# <=> is cosine distance, so 1 - distance is cosine similarity.
# When audience is NULL the filter lets every row through.
SQL = """
    SELECT chunk_id, text, 1 - (embedding <=> %(q)s) AS score
    FROM chunks
    WHERE %(audience)s::text IS NULL OR audience = %(audience)s
    ORDER BY embedding <=> %(q)s
    LIMIT 5
"""

try:
    conn = psycopg.connect(url)
except psycopg.OperationalError as e:
    sys.exit(f"Problem: could not connect to the database. Is it running?\n{e}")

with conn:
    register_vector(conn)
    try:
        rows = conn.execute(SQL, {"q": q, "audience": audience}).fetchall()
    except psycopg.errors.UndefinedTable:
        sys.exit("Problem: the chunks table does not exist. Run: python src/load_db.py")

print(f"Question: {question}")
print(f"Audience: {audience or 'all'}")
for rank, (chunk_id, text, score) in enumerate(rows, start=1):
    snippet = text[:90].replace("\n", " ")
    print(f"{rank}  {score:.3f}  {chunk_id}  {snippet}")
