# Judge only the language check on every answered question in one or more answer runs.
# Run it with:  python src/judge_language.py results/answers_rewrite.csv results/answers_language_fix.csv
#          or:  python src/judge_language.py --model gemini-3.5-flash-lite results/answers_rewrite.csv
#          or:  python src/judge_language.py --qids Q03 Q20 -- results/answers_rewrite.csv
#
# Uses the same prompt as judge_answers.py (LANGUAGE_PROMPT, unchanged). By default the
# judge is Nemotron on OpenRouter; once OpenRouter's daily limit is hit, the rest are
# judged with gemini-3.6-flash. --model picks one judge instead, with no fallback: a
# model starting with "gemini" uses GEMINI_API_KEY, anything else OpenRouter.
# Each row records which model judged it.
# Saves results/judge_language_<run>.csv per input file, merged by qid, so a rerun only
# judges the answers that have no rating yet.
import argparse
import asyncio
import csv
import os
import sys
from pathlib import Path

os.environ.setdefault("RAGAS_DO_NOT_TRACK", "true")

from dotenv import load_dotenv

from judge_answers import (
    JUDGE_API_URL, JUDGE_KEY_NAME, JUDGE_MAX_TOKENS, JUDGE_MODEL, LANGUAGE_PROMPT,
    REQUEST_TIMEOUT, WAIT_BETWEEN_ANSWERS, with_retry,
)

FALLBACK_MODEL = "gemini-3.6-flash"
FALLBACK_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
FALLBACK_KEY_NAME = "GEMINI_API_KEY"
COLUMNS = ["qid", "judge_model", "language", "language_reason"]


def endpoint(model):
    """(base URL, key name) for a judge model."""
    if model.startswith("gemini"):
        return FALLBACK_URL, FALLBACK_KEY_NAME
    return JUDGE_API_URL, JUDGE_KEY_NAME


def is_daily_limit(exc):
    """True if the error is a per-day quota (retrying today won't help)."""
    text = str(exc).lower()
    return "429" in text and ("per-day" in text or "per day" in text or "perday" in text)


def output_path(answers_path):
    return Path("results") / f"judge_language_{answers_path.stem.removeprefix('answers_')}.csv"


def load_existing(path):
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return {r["qid"]: r for r in csv.DictReader(f)}


def save(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for qid in sorted(rows):
            w.writerow({c: rows[qid].get(c, "") for c in COLUMNS})


class Judge:
    """The language metric on the current model, switching to the fallback once."""

    def __init__(self, model=None):
        from ragas.metrics import DiscreteMetric

        self.metric = DiscreteMetric(name="language", allowed_values=["y", "n"], prompt=LANGUAGE_PROMPT)
        self.clients = []
        # Fall back to Gemini only with the default judge; a chosen --model is used alone.
        self.can_fall_back = model is None
        model = model or JUDGE_MODEL
        self.use(model, *endpoint(model))

    def use(self, model, url, key_name):
        from openai import AsyncOpenAI
        from ragas.llms import llm_factory

        if not os.environ.get(key_name):
            sys.exit(f"Problem: {key_name} is not set. Add it to the .env file.")
        client = AsyncOpenAI(api_key=os.environ[key_name], base_url=url, max_retries=0, timeout=REQUEST_TIMEOUT)
        self.clients.append(client)
        self.model = model
        self.llm = llm_factory(model, client=client, max_tokens=JUDGE_MAX_TOKENS)

    async def judge(self, question, response):
        while True:
            try:
                result = await with_retry(
                    "language",
                    lambda: self.metric.ascore(llm=self.llm, user_input=question, response=response),
                )
            except Exception as e:
                if is_daily_limit(e) and self.can_fall_back:
                    print(f"  {self.model}: daily limit hit, switching to {FALLBACK_MODEL}")
                    self.can_fall_back = False
                    self.use(FALLBACK_MODEL, FALLBACK_URL, FALLBACK_KEY_NAME)
                    continue
                raise
            if result.value not in ("y", "n"):
                raise RuntimeError(f"language judge gave no y/n: {result.reason}")
            return result.value, result.reason

    async def close(self):
        for c in self.clients:
            await c.close()


def parse_args():
    p = argparse.ArgumentParser(description="Judge only the language check on answer runs.")
    p.add_argument("runs", nargs="+", type=Path, help="results/answers_<run>.csv files")
    p.add_argument("--model", help=f"judge model (default {JUDGE_MODEL}, with {FALLBACK_MODEL} as fallback)")
    p.add_argument("--qids", nargs="+", help="judge only these qids")
    return p.parse_args()


async def main():
    args = parse_args()
    paths = args.runs
    for p in paths:
        if not p.exists():
            sys.exit(f"Problem: {p} not found.")
    load_dotenv()

    judge = Judge(args.model)
    first = True
    try:
        for path in paths:
            with path.open(encoding="utf-8") as f:
                answered = [r for r in csv.DictReader(f) if r["refused"] == "False" and not r["error"]]
            if args.qids:
                answered = [r for r in answered if r["qid"] in args.qids]
            out = output_path(path)
            done = load_existing(out)
            todo = [r for r in answered if r["qid"] not in done]
            print(f"\n{path}: {len(answered)} answered, {len(todo)} to judge -> {out}")
            for r in todo:
                if not first:
                    await asyncio.sleep(WAIT_BETWEEN_ANSWERS)
                first = False
                value, reason = await judge.judge(r["question"], r["answer"])
                done[r["qid"]] = {"qid": r["qid"], "judge_model": judge.model,
                                  "language": value, "language_reason": reason}
                save(out, done)  # save as we go, so a crash keeps what's done
                print(f"  {r['qid']} {value}  ({judge.model})")
    finally:
        await judge.close()


if __name__ == "__main__":
    asyncio.run(main())
