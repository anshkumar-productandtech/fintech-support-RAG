# Judge saved answers with Ragas, using an open model on OpenRouter as the judge (JUDGE_MODEL).
# Run it with:  python src/judge_answers.py            (the qids in results/human_ratings.csv)
#          or:  python src/judge_answers.py Q03 Q05
#
# For each qid, loads the question, answer and rewritten query from
# results/answers_rewrite.csv, rebuilds the 5 sources with answer.get_sources(), and
# scores three checks:
#   faithfulness  Ragas Faithfulness (0-1): share of the answer's claims the sources support
#   complete      y/n: every applicable fee, limit, time, compensation and condition is
#                 included, and conditional steps stay conditional
#   language      y/n: the answer is in the question's language
# Results are merged into results/judge_ratings.csv by qid, so runs can be split up.
import asyncio
import csv
import math
import os
import sys
from pathlib import Path

# Ragas sends usage analytics by default. Turn that off before importing it.
os.environ.setdefault("RAGAS_DO_NOT_TRACK", "true")

from dotenv import load_dotenv

import answer
from answer import get_sources

ANSWERS = Path("results/answers_rewrite.csv")
HUMAN = Path("results/human_ratings.csv")
OUTPUT = Path("results/judge_ratings.csv")
COLUMNS = [
    "qid", "faithfulness", "unsupported_claims",
    "complete", "complete_reason", "language", "language_reason",
]

# Free on OpenRouter (about 50 requests a day without credits; about 4 per answer).
# The earlier ratings were made with gemini-3.6-flash: results/judge_ratings_gemini-3.6-flash.csv
JUDGE_MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"
JUDGE_MAX_TOKENS = 8192
REQUEST_TIMEOUT = 120  # seconds per judge call
JUDGE_API_URL = "https://openrouter.ai/api/v1"
JUDGE_KEY_NAME = "OPENROUTER_API_KEY"
WAIT_BETWEEN_ANSWERS = 15  # seconds
RETRY_CODES = {429, 503, "timeout"}
RETRY_WAITS = [10, 20, 40]  # 3 waits = up to 4 tries per judge call

COMPLETE_CRITERION = (
    "The response includes every fee, minimum, time limit, compensation and eligibility "
    "condition from the sources that applies to the question, and keeps conditional steps "
    "conditional (it doesn't present a step as always needed when the source says it's "
    "only needed in some cases)."
)
LANGUAGE_CRITERION = (
    "The response is in the same language as the question: Hinglish (Hindi in English "
    "letters) for a Hinglish question, English for an English question."
)

# Placeholders in {braces} are filled by DiscreteMetric. The criteria have no braces.
COMPLETE_PROMPT = (
    "You are checking a draft support reply against the help center sources it was given.\n\n"
    "Criterion: " + COMPLETE_CRITERION + "\n\n"
    "Question:\n{user_input}\n\n"
    "Sources:\n{contexts}\n\n"
    "Response:\n{response}\n\n"
    "Does the response meet the criterion? Answer 'y' or 'n', and give a short reason that "
    "names anything missing or wrongly made unconditional."
)
LANGUAGE_PROMPT = (
    "You are checking the language of a draft support reply.\n\n"
    "Criterion: " + LANGUAGE_CRITERION + "\n\n"
    "Question:\n{user_input}\n\n"
    "Response:\n{response}\n\n"
    "Does the response meet the criterion? Answer 'y' or 'n', and give a short reason."
)


def status_code(exc):
    """The HTTP status behind an error, looking through wrapped exceptions.

    A request timeout counts as "timeout": when Gemini is overloaded it sometimes stops
    responding instead of returning 503, so it gets the same retries.
    """
    from openai import APITimeoutError

    seen = set()
    while exc is not None and id(exc) not in seen:
        seen.add(id(exc))
        if isinstance(exc, APITimeoutError):
            return "timeout"
        code = getattr(exc, "status_code", None)
        if isinstance(code, int):
            return code
        exc = exc.__cause__ or exc.__context__
    return None


async def with_retry(label, make_call):
    """Await make_call(), retrying on 429 and 503 with waits of 10, 20 and 40 seconds."""
    for attempt in range(len(RETRY_WAITS) + 1):
        try:
            return await make_call()
        except Exception as e:
            code = status_code(e)
            if code not in RETRY_CODES or attempt == len(RETRY_WAITS):
                raise
            wait = RETRY_WAITS[attempt]
            print(f"  {label}: got {code}, retrying in {wait}s")
            await asyncio.sleep(wait)


def load_rows():
    with ANSWERS.open(encoding="utf-8") as f:
        rows = {r["qid"]: r for r in csv.DictReader(f)}
    modes = {r["mode"] for r in rows.values()}
    if modes != {"rewrite"}:
        sys.exit(f"Problem: expected only rewrite-mode rows in {ANSWERS}, found {sorted(modes)}.")
    return rows


def default_qids():
    if not HUMAN.exists():
        sys.exit(f"Problem: {HUMAN} not found. Run: python src/make_review_sheet.py")
    with HUMAN.open(encoding="utf-8") as f:
        return [r["qid"] for r in csv.DictReader(f)]


def save(results):
    """Merge these results into the output file by qid."""
    merged = {}
    if OUTPUT.exists():
        with OUTPUT.open(encoding="utf-8") as f:
            merged = {r["qid"]: r for r in csv.DictReader(f)}
    merged.update({r["qid"]: r for r in results})
    with OUTPUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for qid in sorted(merged):
            w.writerow({c: merged[qid].get(c, "") for c in COLUMNS})


async def judge_one(row, llm, faithfulness, complete, language):
    question, response = row["question"], row["answer"]
    sources = get_sources(question, row["audience"], row["rewritten_query"])
    # Each source as the answer model saw it: title, then text (see answer.build_prompt).
    contexts = [f"{s['title']}\n{s['text']}" for s in sources]
    numbered = "\n\n".join(f"[{i}] {c}" for i, c in enumerate(contexts, start=1))

    # Faithfulness, run step by step with the metric's own methods so the verdict on
    # each claim is kept. ascore() makes the same calls but returns only the score.
    statements = await with_retry(
        "faithfulness statements",
        lambda: faithfulness._create_statements(question, response),
    )
    if statements:
        verdicts = await with_retry(
            "faithfulness verdicts",
            lambda: faithfulness._create_verdicts(statements, "\n".join(contexts)),
        )
        score = float(faithfulness._compute_score(verdicts))
        unsupported = [v for v in verdicts.statements if not v.verdict]
    else:
        score, unsupported = math.nan, []

    c = await with_retry(
        "complete",
        lambda: complete.ascore(llm=llm, user_input=question, contexts=numbered, response=response),
    )
    lang = await with_retry(
        "language",
        lambda: language.ascore(llm=llm, user_input=question, response=response),
    )
    for name, result in (("complete", c), ("language", lang)):
        if result.value not in ("y", "n"):
            raise RuntimeError(f"{name} judge gave no y/n: {result.reason}")

    return {
        "qid": row["qid"],
        "faithfulness": "" if math.isnan(score) else f"{score:.3f}",
        "unsupported_claims": " | ".join(f"{v.statement} ({v.reason})" for v in unsupported),
        "complete": c.value,
        "complete_reason": c.reason,
        "language": lang.value,
        "language_reason": lang.reason,
    }


def show(r, question):
    print(f"\n{r['qid']}  {question}")
    print(f"  faithfulness: {r['faithfulness'] or 'n/a (no claims found)'}")
    if r["unsupported_claims"]:
        for claim in r["unsupported_claims"].split(" | "):
            print(f"    unsupported: {claim}")
    print(f"  complete: {r['complete']}  {r['complete_reason']}")
    print(f"  language: {r['language']}  {r['language_reason']}")


async def main():
    if answer.SOURCES != "chunks" or answer.REWRITE != "on":
        sys.exit("Problem: run with the defaults (SOURCES=chunks, REWRITE=on) to match the saved answers.")
    load_dotenv()
    if not os.environ.get(JUDGE_KEY_NAME):
        sys.exit(f"Problem: {JUDGE_KEY_NAME} is not set. Add it to the .env file.")

    rows = load_rows()
    qids = sys.argv[1:] or default_qids()
    unknown = [q for q in qids if q not in rows]
    if unknown:
        sys.exit(f"Problem: not in {ANSWERS}: {', '.join(unknown)}")
    refused = [q for q in qids if rows[q]["refused"] != "False" or rows[q]["error"]]
    if refused:
        sys.exit(f"Problem: these have no answer to judge (refused or error): {', '.join(refused)}")

    from openai import AsyncOpenAI
    from ragas.llms import llm_factory
    from ragas.metrics import DiscreteMetric
    from ragas.metrics.collections import Faithfulness

    client = AsyncOpenAI(
        api_key=os.environ[JUDGE_KEY_NAME],
        base_url=JUDGE_API_URL,
        max_retries=0,  # retries are handled by with_retry(), with the waits above
        timeout=REQUEST_TIMEOUT,  # the default of 10 minutes let one stuck call stall a run
    )
    # Ragas caps output at 1024 tokens by default. Gemini's thinking tokens count against
    # that cap, which cut the structured output short, so raise it.
    llm = llm_factory(JUDGE_MODEL, client=client, max_tokens=JUDGE_MAX_TOKENS)
    faithfulness = Faithfulness(llm=llm)
    complete = DiscreteMetric(name="complete", allowed_values=["y", "n"], prompt=COMPLETE_PROMPT)
    language = DiscreteMetric(name="language", allowed_values=["y", "n"], prompt=LANGUAGE_PROMPT)

    print(f"Judging {len(qids)} answer(s) with {JUDGE_MODEL}")
    results = []
    try:
        for i, qid in enumerate(qids):
            if i:
                await asyncio.sleep(WAIT_BETWEEN_ANSWERS)
            r = await judge_one(rows[qid], llm, faithfulness, complete, language)
            results.append(r)
            show(r, rows[qid]["question"])
            save(results)  # save as we go, so a crash keeps what's done
    finally:
        await client.close()

    print(f"\nSaved {len(results)} row(s) to {OUTPUT}")


if __name__ == "__main__":
    asyncio.run(main())
