# Download the embedding model into MODEL_CACHE_DIR, so the app doesn't fetch it on
# every cold start. Run it once at build time:
#   MODEL_CACHE_DIR=./model_cache python scripts/download_model.py
import os
import sys

from dotenv import load_dotenv
from fastembed import TextEmbedding

EMBED_MODEL = "BAAI/bge-small-en-v1.5"  # must match EMBED_MODEL in src/answer.py

load_dotenv()
cache_dir = os.getenv("MODEL_CACHE_DIR")
if not cache_dir:
    sys.exit("MODEL_CACHE_DIR is not set. Set it to the folder the app will read the model from.")

model = TextEmbedding(EMBED_MODEL, cache_dir=cache_dir)
next(iter(model.query_embed(["test"])))  # fails here if the download is incomplete
print(f"{EMBED_MODEL} is ready in {cache_dir}")
