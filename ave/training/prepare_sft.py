"""Convert cleaned data into chat-format SFT training examples.

Each example is a 3-turn conversation:
  system  → extraction instructions
  user    → category + attributes + product text
  assistant → gold JSON
"""

import json
from pathlib import Path

from ave.prompts.templates import SYSTEM_MESSAGE, render_user_message
from ave.utils import load_jsonl, save_jsonl


def build_sft_example(record: dict, schemas: dict[str, list[str]]) -> dict:
    """Build one chat-format training example."""
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": render_user_message(record, schemas)},
            {"role": "assistant", "content": json.dumps(record["gold_json"])},
        ]
    }


def prepare_sft_dataset(
    records: list[dict],
    schemas: dict[str, list[str]],
    out_path: str | Path,
) -> list[dict]:
    """Build SFT examples for all *records* and save as JSONL."""
    examples = [build_sft_example(rec, schemas) for rec in records]
    save_jsonl(examples, out_path)
    print(f"Saved {len(examples):,} SFT examples to {out_path}")
    return examples


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Prepare SFT training data")
    parser.add_argument("--cleaned-dir", type=Path, default=Path("data/WDC-PAVE/cleaned"))
    parser.add_argument("--out", type=Path, default=Path("data/WDC-PAVE/sft/train_sft.jsonl"))
    args = parser.parse_args()

    from ave.data.loader import load_schemas

    train = load_jsonl(args.cleaned_dir / "train.jsonl")
    schemas = load_schemas(args.cleaned_dir)
    prepare_sft_dataset(train, schemas, args.out)
