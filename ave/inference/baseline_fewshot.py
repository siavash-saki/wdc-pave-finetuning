"""Variant C: few-shot prompting with in-context examples.  Greedy decoding."""

from pathlib import Path

from ave.configs.schemas import CATEGORY_SCHEMAS
from ave.data.loader import index_by_category, load_splits
from ave.inference._local import load_model, run_inference
from ave.prompts.templates import build_messages_few_shot
from ave.utils import save_jsonl

DEFAULT_MODEL = "Qwen/Qwen3-4B-Instruct-2507"


def run_variant_c(
    model_id: str = DEFAULT_MODEL,
    cleaned_dir: str | Path = "data/WDC-PAVE/cleaned",
    pred_dir: str | Path = "data/WDC-PAVE/predictions",
    split: str = "val",
    n_examples: int = 3,
) -> list[dict]:
    """Run Variant C on the chosen split and save predictions."""
    pred_dir = Path(pred_dir)
    pred_dir.mkdir(parents=True, exist_ok=True)

    train, val, test = load_splits(cleaned_dir)
    records = {"train": train, "val": val, "test": test}[split]
    train_by_cat = index_by_category(train)

    model, tokenizer = load_model(model_id)
    preds = run_inference(
        model, tokenizer,
        records=records,
        message_builder=lambda rec: build_messages_few_shot(
            rec, CATEGORY_SCHEMAS, train_by_cat, n_examples=n_examples,
        ),
        variant_name=f"C_few_shot_{n_examples}",
        model_id=model_id,
    )

    out_path = pred_dir / f"variant_C_few_shot_{n_examples}_{split}.jsonl"
    save_jsonl(preds, out_path)
    return preds


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Variant C — few-shot baseline")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--cleaned-dir", type=Path, default=Path("data/WDC-PAVE/cleaned"))
    parser.add_argument("--pred-dir", type=Path, default=Path("data/WDC-PAVE/predictions"))
    parser.add_argument("--split", default="val", choices=["train", "val", "test"])
    parser.add_argument("--n-examples", type=int, default=3)
    args = parser.parse_args()

    run_variant_c(args.model, args.cleaned_dir, args.pred_dir, args.split, args.n_examples)
