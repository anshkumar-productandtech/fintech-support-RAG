# fintech-support-RAG

A retrieval-augmented generation (RAG) assistant for fintech customer support.

## Setup

Requirements: Python 3.10+ and Git.

Check that your environment is ready:

```bash
python src/check_setup.py
```

Put your API keys in a `.env` file (or set them as environment variables). `.env` is already in `.gitignore`, so it won't be committed.

```
GEMINI_API_KEY=
OPENROUTER_API_KEY=
```

- `GEMINI_API_KEY`: needed once the assistant starts generating answers.
- `OPENROUTER_API_KEY`: needed by `src/judge_answers.py`, which judges answers with a free open model on OpenRouter.

## Project layout

- `src/`: Python scripts
- `data/`: generated files (ignored by git, can be rebuilt)
- `requirements.txt`: Python libraries