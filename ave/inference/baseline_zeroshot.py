"""Variant A: zero-shot prompt-only baseline.  Greedy decoding, no constraints."""

from pathlib import Path

from ave.configs.schemas import CATEGORY_SCHEMAS
from ave.data.loader import load_splits
from ave.inference._local import load_model, run_inference
from ave.prompts.templates import build_messages_zero_shot
from ave.utils import save_jsonl

DEFAULT_MODEL = "Qwen/Qwen3-4B-Instruct-2507"


def run_variant_a(
    model_id: str = DEFAULT_MODEL,
    cleaned_dir: str | Path = "data/WDC-PAVE/cleaned",
    pred_dir: str | Path = "data/WDC-PAVE/predictions",
    split: str = "val",
) -> list[dict]:
    """Run Variant A on the chosen split and save predictions."""
    pred_dir = Path(pred_dir)
    pred_dir.mkdir(parents=True, exist_ok=True)

    train, val, test = load_splits(cleaned_dir)
    records = {"train": train, "val": val, "test": test}[split]

    model, tokenizer = load_model(model_id)
    preds = run_inference(
        model, tokenizer,
        records=records,
        message_builder=lambda rec: build_messages_zero_shot(rec, CATEGORY_SCHEMAS),
        variant_name="A_zero_shot",
        model_id=model_id,
    )

    out_path = pred_dir / f"variant_A_zero_shot_{split}.jsonl"
    save_jsonl(preds, out_path)
    return preds


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Variant A — zero-shot baseline")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--cleaned-dir", type=Path, default=Path("data/WDC-PAVE/cleaned"))
    parser.add_argument("--pred-dir", type=Path, default=Path("data/WDC-PAVE/predictions"))
    parser.add_argument("--split", default="val", choices=["train", "val", "test"])
    args = parser.parse_args()

    run_variant_a(args.model, args.cleaned_dir, args.pred_dir, args.split)
