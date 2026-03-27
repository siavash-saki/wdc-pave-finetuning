"""Dataset loading utilities for the WDC-PAVE benchmark."""

import json
from collections import defaultdict
from pathlib import Path

from ave.utils import load_jsonl


def load_schemas(cleaned_dir: str | Path) -> dict[str, list[str]]:
    """Load ``category_schemas.json`` from *cleaned_dir*."""
    with open(Path(cleaned_dir) / "category_schemas.json") as f:
        return json.load(f)


def load_json_schemas(cleaned_dir: str | Path) -> dict[str, dict]:
    """Load ``json_schemas_for_decoding.json`` (for constrained decoding)."""
    with open(Path(cleaned_dir) / "json_schemas_for_decoding.json") as f:
        return json.load(f)


def load_splits(
    cleaned_dir: str | Path,
) -> tuple[list[dict], list[dict], list[dict]]:
    """Load train / val / test JSONL splits.

    Returns ``(train, val, test)`` as lists of record dicts.
    """
    d = Path(cleaned_dir)
    train = load_jsonl(d / "train.jsonl")
    val = load_jsonl(d / "val.jsonl")
    test = load_jsonl(d / "test.jsonl")
    return train, val, test


def index_by_category(records: list[dict]) -> dict[str, list[dict]]:
    """Group *records* by their ``category`` field."""
    by_cat: dict[str, list[dict]] = defaultdict(list)
    for rec in records:
        by_cat[rec["category"]].append(rec)
    return dict(by_cat)
