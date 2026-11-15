# fintech-support-RAG

A retrieval-augmented generation (RAG) assistant for fintech customer support.

## Setup

Requirements: Python 3.10+ and Git.

Check that your environment is ready:

```bash
python src/check_setup.py
```

`GEMINI_API_KEY` is needed once the assistant starts generating answers. Set it as an environment variable or put it in a `.env` file. `.env` is already in `.gitignore`, so it won't be committed.

## Project layout

- `src/`: Python scripts
- `data/`: generated files (ignored by git, can be rebuilt)
- `requirements.txt`: Python libraries (empty for now; the early scripts use only built-in tools)
