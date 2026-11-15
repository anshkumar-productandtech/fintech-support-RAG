import os
import shutil
import sys

print("Python version:", sys.version.split()[0])
if sys.version_info < (3, 10):
    sys.exit("Problem: you need Python 3.10 or newer.")

if shutil.which("git"):
    print("Git: installed")
else:
    sys.exit("Problem: Git is missing.")

if os.environ.get("GEMINI_API_KEY"):
    print("GEMINI_API_KEY: found (hidden)")
else:
    print("GEMINI_API_KEY: not set yet (only needed for generating answers)")

print("All good. Setup is ready.")
