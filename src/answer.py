# Answer a support question from the help center, with numbered citations.
# Run it with:  python src/answer.py "How do I link my bank account?" customer
#          or:  python src/answer.py "When do I get my settlement?" merchant
#
# Other scripts can import search, build_prompt, generate, cited_numbers and answer.
import os
import re
import sys
import time
from functools import lru_cache

AUDIENCES = ["customer", "merchant"]
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
LLM_MODEL = "gemini-3.5-flash-lite"
TOP_K = 5
REFUSAL = "NOT_IN_HELP_CENTER"
USAGE = 'Usage: python src/answer.py "your question" customer|merchant'

# US$ per 1 million tokens.
INPUT_PRICE = 0.30
OUTPUT_PRICE = 2.50

# Retry on rate limits (429) and overload (503): wait 2, 4, then 8 seconds.
RETRY_CODES = {429, 503}
RETRY_WAITS = [2, 4, 8]  # 3 waits = up to 4 tries

# TODO: replace with the 6 rules from the reference code.
SYSTEM_PROMPT = f"""You are a support assistant for a payments app. Follow these rules:
1. Answer only from the numbered sources provided. Do not use outside knowledge.
2. Cite the source number in square brackets, like [1], after every fact you use.
3. If the sources do not contain the answer, reply with exactly {REFUSAL} and nothing else.
4. Never invent fees, limits, timelines or phone numbers that are not in the sources.
5. Answer for the stated audience (customer or merchant) only.
6. Keep the answer short and clear: a few sentences or numbered steps."""

SQL = """
    SELECT chunk_id, title, text
    FROM chunks
    WHERE audience = %(audience)s
    ORDER BY embedding <=> %(q)s
    LIMIT %(k)s
"""


@lru_cache(maxsize=1)
def _embed_model():
    from fastembed import TextEmbedding

    return TextEmbedding(EMBED_MODEL)


@lru_cache(maxsize=1)
def _genai_client():
    from dotenv import load_dotenv
    from google import genai

    load_dotenv()
    # The client reads GEMINI_API_KEY from the environment.
    return genai.Client()


def search(question, audience):
    """Return the top 5 chunks for this audience as dicts with chunk_id, title, text."""
    import numpy as np
    import psycopg
    from dotenv import load_dotenv
    from pgvector.psycopg import register_vector

    if audience not in AUDIENCES:
        raise ValueError(f"audience must be one of {AUDIENCES}, got {audience!r}")

    load_dotenv()
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set. Add it to the .env file.")

    q = next(iter(_embed_model().query_embed([question])))
    q = (q / np.linalg.norm(q)).astype(np.float32)

    with psycopg.connect(url) as conn:
        register_vector(conn)
        rows = conn.execute(SQL, {"q": q, "audience": audience, "k": TOP_K}).fetchall()

    return [{"chunk_id": c, "title": t, "text": x} for c, t, x in rows]


def build_prompt(question, audience, sources):
    """Number the sources [1]..[n] with their article titles, then add the question."""
    parts = [f"[{i}] {s['title']}\n{s['text']}" for i, s in enumerate(sources, start=1)]
    parts.append(f"The {audience} asks: {question}")
    return "\n\n".join(parts)


def generate(prompt):
    """Call Gemini and return the raw response. Retries on 429 and 503."""
    from google.genai import errors, types

    client = _genai_client()
    config = types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, temperature=0.2)

    for attempt in range(len(RETRY_WAITS) + 1):
        try:
            return client.models.generate_content(model=LLM_MODEL, contents=prompt, config=config)
        except errors.APIError as e:
            if e.code not in RETRY_CODES or attempt == len(RETRY_WAITS):
                raise
            time.sleep(RETRY_WAITS[attempt])


_CITATION = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")


def cited_numbers(answer):
    """Every source number cited, sorted and unique. Handles [1], [1, 2] and [2][3]."""
    found = set()
    for group in _CITATION.findall(answer):
        found.update(int(n) for n in re.findall(r"\d+", group))
    return sorted(found)


def answer(question, audience):
    """Search, prompt, generate, and return the answer with citations, tokens and cost."""
    start = time.perf_counter()
    sources = search(question, audience)
    response = generate(build_prompt(question, audience, sources))
    text = (response.text or "").strip()

    usage = response.usage_metadata
    input_tokens = (usage.prompt_token_count or 0) if usage else 0
    output_tokens = (
        (usage.candidates_token_count or 0) + (usage.thoughts_token_count or 0) if usage else 0
    )
    cost = (input_tokens * INPUT_PRICE + output_tokens * OUTPUT_PRICE) / 1_000_000

    cited = cited_numbers(text)
    return {
        "text": text,
        "sources": sources,
        "cited": cited,
        "invalid_citations": [n for n in cited if not 1 <= n <= len(sources)],
        "refused": text == REFUSAL,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": cost,
        "seconds": time.perf_counter() - start,
    }


if __name__ == "__main__":
    if len(sys.argv) != 3 or not sys.argv[1].strip() or sys.argv[2] not in AUDIENCES:
        sys.exit(USAGE)

    result = answer(sys.argv[1], sys.argv[2])

    print(result["text"])
    print("\nSources:")
    for i, s in enumerate(result["sources"], start=1):
        mark = "  (cited)" if i in result["cited"] else ""
        print(f"[{i}] {s['title']}  {s['chunk_id']}{mark}")
    if result["invalid_citations"]:
        print(f"\nWarning: cites sources that don't exist: {result['invalid_citations']}")
    print(
        f"\nTokens: {result['input_tokens']} in, {result['output_tokens']} out"
        f"  |  Cost: ${result['cost_usd']:.6f}  |  {result['seconds']:.1f}s"
    )
