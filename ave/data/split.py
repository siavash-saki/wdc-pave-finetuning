"""Stratified train / validation / test split (70/10/20) by category.

Reads ``cleaned_with_gold.jsonl``, produces per-split JSONL files and a
``split_assignments.json`` for reproducibility.
"""

import json
from collections import Counter
from pathlib import Path

from sklearn.model_selection import train_test_split

from ave.utils import load_jsonl, save_jsonl

RANDOM_STATE = 42
SPLIT_RATIOS = {"train": 0.70, "val": 0.10, "test": 0.20}


def stratified_split(
    records: list[dict],
    random_state: int = RANDOM_STATE,
) -> dict[str, list[dict]]:
    """Split *records* into train / val / test, stratified by category.

    Returns ``{"train": [...], "val": [...], "test": [...]}``.
    """
    categories = [rec["category"] for rec in records]

    # 80/20 → train+val vs test
    train_val, test = train_test_split(
        records,
        test_size=0.20,
        stratify=categories,
        random_state=random_state,
    )

    # Split the 80% into train (87.5% of 80% ≈ 70%) and val (12.5% of 80% ≈ 10%)
    train, val = train_test_split(
        train_val,
        test_size=0.125,
        stratify=[r["category"] for r in train_val],
        random_state=random_state,
    )

    return {"train": train, "val": val, "test": test}


def save_splits(
    splits: dict[str, list[dict]],
    out_dir: str | Path,
) -> None:
    """Write per-split JSONL files, assignment map, and metadata."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Per-split JSONL
    for split_name, split_data in splits.items():
        save_jsonl(split_data, out_dir / f"{split_name}.jsonl")

    # Split assignments  (record id → split name)
    assignments = {}
    for split_name, split_data in splits.items():
        for rec in split_data:
            assignments[rec["id"]] = split_name
    with open(out_dir / "split_assignments.json", "w") as f:
        json.dump(assignments, f, indent=2)

    # Metadata
    total = sum(len(d) for d in splits.values())
    metadata = {
        "random_state": RANDOM_STATE,
        "split_ratios": SPLIT_RATIOS,
        "stratify_by": "category",
        "total_records": total,
        "split_counts": {s: len(d) for s, d in splits.items()},
        "category_counts_per_split": {
            s: dict(Counter(r["category"] for r in d))
            for s, d in splits.items()
        },
    }
    with open(out_dir / "split_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    for s, d in splits.items():
        print(f"  {s}: {len(d):,} records ({len(d)/total*100:.1f}%)")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create stratified splits")
    parser.add_argument(
        "--cleaned", type=Path, default=Path("data/WDC-PAVE/cleaned/cleaned_with_gold.jsonl"),
    )
    parser.add_argument("--out", type=Path, default=Path("data/WDC-PAVE/cleaned"))
    args = parser.parse_args()

    data = load_jsonl(args.cleaned)
    splits = stratified_split(data)
    save_splits(splits, args.out)
