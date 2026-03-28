"""Variant B: zero-shot + constrained JSON decoding via ``outlines``."""

import json
import time
from pathlib import Path

from tqdm.auto import tqdm

from ave.configs.schemas import CATEGORY_SCHEMAS, all_json_schemas
from ave.data.loader import load_splits
from ave.inference._local import load_model
from ave.prompts.templates import build_messages_zero_shot
from ave.utils import save_jsonl

DEFAULT_MODEL = "Qwen/Qwen3-4B-Instruct-2507"


def run_variant_b(
    model_id: str = DEFAULT_MODEL,
    cleaned_dir: str | Path = "data/WDC-PAVE/cleaned",
    pred_dir: str | Path = "data/WDC-PAVE/predictions",
    split: str = "val",
) -> list[dict]:
    """Run Variant B on the chosen split and save predictions."""
    import outlines
    from outlines import Generator
    from outlines.types import JsonSchema

    pred_dir = Path(pred_dir)
    pred_dir.mkdir(parents=True, exist_ok=True)

    train, val, test = load_splits(cleaned_dir)
    records = {"train": train, "val": val, "test": test}[split]

    model, tokenizer = load_model(model_id)

    # Build outlines wrappers (outlines v1.0+ API)
    outlines_model = outlines.from_transformers(model, tokenizer)
    json_schemas = all_json_schemas()
    generators = {
        cat: Generator(outlines_model, JsonSchema(schema))
        for cat, schema in json_schemas.items()
    }
    print(f"Built {len(generators)} constrained JSON generators")

    predictions: list[dict] = []
    for rec in tqdm(records, desc="Variant B (constrained)"):
        messages = build_messages_zero_shot(rec, CATEGORY_SCHEMAS)
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        generator = generators[rec["category"]]

        t0 = time.perf_counter()
        try:
            raw_output = generator(text, max_new_tokens=512)
            latency = time.perf_counter() - t0

            pred_json = json.loads(raw_output)
            parse_error = None
        except Exception as e:
            latency = time.perf_counter() - t0
            pred_json = None
            parse_error = f"Constrained generation failed: {e}"
            raw_output = str(e)

        predictions.append({
            "id": rec["id"],
            "category": rec["category"],
            "variant": "B_constrained",
            "model": model_id,
            "gold_json": rec["gold_json"],
            "pred_json": pred_json,
            "raw_output": raw_output,
            "parse_error": parse_error,
            "input_tokens": -1,
            "output_tokens": -1,
            "latency_s": round(latency, 3),
        })

    n_parsed = sum(1 for p in predictions if p["pred_json"] is not None)
    avg_lat = sum(p["latency_s"] for p in predictions) / len(predictions)
    print(f"B_constrained: {n_parsed}/{len(predictions)} parsed "
          f"({n_parsed/len(predictions)*100:.1f}%), avg latency {avg_lat:.2f}s")

    out_path = pred_dir / f"variant_B_constrained_{split}.jsonl"
    save_jsonl(predictions, out_path)
    return predictions


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Variant B — constrained JSON decoding")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--cleaned-dir", type=Path, default=Path("data/WDC-PAVE/cleaned"))
    parser.add_argument("--pred-dir", type=Path, default=Path("data/WDC-PAVE/predictions"))
    parser.add_argument("--split", default="val", choices=["train", "val", "test"])
    args = parser.parse_args()

    run_variant_b(args.model, args.cleaned_dir, args.pred_dir, args.split)
