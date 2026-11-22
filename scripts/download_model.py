# Download the embedding model's files into MODEL_CACHE_DIR, so the app doesn't fetch
# the model on every cold start. Run it once at build time:
#   MODEL_CACHE_DIR=model_cache python scripts/download_model.py
#
# The files are copied into one plain folder. Hugging Face's own cache links each file
# to a shared blob, and bundlers copy every link, which would ship the model three times.
import os
import shutil
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from fastembed import TextEmbedding

EMBED_MODEL = "BAAI/bge-small-en-v1.5"  # must match EMBED_MODEL in src/answer.py

load_dotenv()
target = os.getenv("MODEL_CACHE_DIR")
if not target:
    sys.exit("MODEL_CACHE_DIR is not set. Set it to the folder the app will read the model from.")
target = Path(target)

with tempfile.TemporaryDirectory() as tmp:
    TextEmbedding(EMBED_MODEL, cache_dir=tmp)
    snapshots = list(Path(tmp).glob("models--*/snapshots/*"))
    if len(snapshots) != 1:
        sys.exit(f"Expected one downloaded model snapshot, found {len(snapshots)}.")
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True)
    for f in snapshots[0].iterdir():
        shutil.copyfile(f, target / f.name)  # follows the link: a real copy of the file

model = TextEmbedding(EMBED_MODEL, specific_model_path=str(target))
next(iter(model.query_embed(["test"])))  # fails here if a file is missing
size_mb = sum(f.stat().st_size for f in target.iterdir()) / 1_048_576
print(f"{EMBED_MODEL} is ready in {target} ({size_mb:.1f} MB)")
