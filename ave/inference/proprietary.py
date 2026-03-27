"""Variant E: proprietary API model baseline via OpenRouter.

Uses the OpenAI-compatible chat completions endpoint with the same
zero-shot prompt as Variant A.
"""

import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from tqdm.auto import tqdm

from ave.configs.schemas import CATEGORY_SCHEMAS
from ave.data.loader import load_splits
from ave.prompts.templates import build_messages_zero_shot
from ave.utils import extract_json, model_slug, save_jsonl

DEFAULT_MODELS = [
    "openai/GPT-5.4-nano",
    "openai/GPT-5.4",
]


def _make_client() -> OpenAI:
    """Create an OpenRouter client from environment."""
    load_dotenv()
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    )


def call_api(
    client: OpenAI,
    messages: list[dict],
    model: str,
    temperature: float = 0,
    max_tokens: int = 512,
    max_retries: int = 3,
) -> dict:
    """Call the API with retries.  Returns the standard result dict."""
    last_error = None
    for attempt in range(max_retries):
        try:
            t0 = time.perf_counter()
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            latency = time.perf_counter() - t0
            break
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                print(f"  API error (attempt {attempt+1}): {e}. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                return {
                    "raw_output": "",
                    "parsed_json": None,
                    "parse_error": f"API failed after {max_retries} retries: {last_error}",
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "latency_s": 0,
                }

    raw_output = response.choices[0].message.content or ""
    usage = response.usage
    input_tokens = usage.prompt_tokens if usage else 0
    output_tokens = usage.completion_tokens if usage else 0

    parsed_json, parse_error = extract_json(raw_output)

    return {
        "raw_output": raw_output,
        "parsed_json": parsed_json,
        "parse_error": parse_error,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "latency_s": round(latency, 3),
    }


def run_variant_e(
    model_name: str,
    cleaned_dir: str | Path = "data/WDC-PAVE/cleaned",
    pred_dir: str | Path = "data/WDC-PAVE/predictions",
    split: str = "val",
) -> list[dict]:
    """Run Variant E for a single API model on the chosen split."""
    pred_dir = Path(pred_dir)
    pred_dir.mkdir(parents=True, exist_ok=True)

    train, val, test = load_splits(cleaned_dir)
    records = {"train": train, "val": val, "test": test}[split]

    client = _make_client()
    slug = model_slug(model_name)
    variant_name = f"E_{slug}"

    predictions: list[dict] = []
    total_in = total_out = 0

    for rec in tqdm(records, desc=f"Variant E ({model_name})"):
        messages = build_messages_zero_shot(rec, CATEGORY_SCHEMAS)
        result = call_api(client, messages, model=model_name)

        total_in += result["input_tokens"]
        total_out += result["output_tokens"]

        predictions.append({
            "id": rec["id"],
            "category": rec["category"],
            "variant": variant_name,
            "model": model_name,
            "gold_json": rec["gold_json"],
            "pred_json": result["parsed_json"],
            "raw_output": result["raw_output"],
            "parse_error": result["parse_error"],
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"],
            "latency_s": result["latency_s"],
        })

    n_parsed = sum(1 for p in predictions if p["pred_json"] is not None)
    avg_lat = sum(p["latency_s"] for p in predictions) / len(predictions)
    print(f"{variant_name}: {n_parsed}/{len(predictions)} parsed "
          f"({n_parsed/len(predictions)*100:.1f}%), avg latency {avg_lat:.2f}s")
    print(f"Total tokens: {total_in:,} in + {total_out:,} out = {total_in+total_out:,}")

    out_path = pred_dir / f"variant_E_{slug}_{split}.jsonl"
    save_jsonl(predictions, out_path)
    return predictions


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Variant E — proprietary API baseline")
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    parser.add_argument("--cleaned-dir", type=Path, default=Path("data/WDC-PAVE/cleaned"))
    parser.add_argument("--pred-dir", type=Path, default=Path("data/WDC-PAVE/predictions"))
    parser.add_argument("--split", default="val", choices=["train", "val", "test"])
    args = parser.parse_args()

    for m in args.models:
        run_variant_e(m, args.cleaned_dir, args.pred_dir, args.split)
