# fintech-support-RAG

A retrieval-augmented generation (RAG) assistant for fintech customer support, built step by step, one lesson at a time.

## Setup

Requirements: Python 3.10+ and Git.

Check that your environment is ready:

```bash
python src/check_setup.py
```

`GEMINI_API_KEY` is needed from Lesson 8 onward. Set it as an environment variable or put it in a `.env` file. `.env` is already in `.gitignore`, so it won't be committed.

## Project layout

- `src/`: Python scripts
- `data/`: generated files (ignored by git, can be rebuilt)
- `requirements.txt`: Python libraries (added from Lesson 4)
