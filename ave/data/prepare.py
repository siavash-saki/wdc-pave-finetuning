"""Data cleaning and canonicalization for WDC-PAVE.

Reads ``normalized_target_scores.jsonl``, applies cleaning rules, builds
canonical gold JSON per record, and writes ``cleaned_with_gold.jsonl``
plus ``category_schemas.json``.
"""

import json
from pathlib import Path

from ave.configs.schemas import CATEGORY_SCHEMAS
from ave.utils import clean_null_artifact, load_jsonl, normalize_value, save_jsonl


# ---------------------------------------------------------------------------
# Gold JSON construction
# ---------------------------------------------------------------------------

def extract_gold_values(attr_dict: dict) -> list[str]:
    """Extract real gold values from a ``target_scores`` attribute entry.

    Returns an empty list when the attribute is marked ``n/a`` (missing).
    """
    values = []
    for val_key, val_detail in attr_dict.items():
        if val_key == "n/a" or val_detail == "n/a":
            continue
        values.append(normalize_value(val_key))
    return values


def build_gold_json(record: dict, schema: list[str]) -> dict:
    """Build canonical gold JSON for one record.

    * Present single-value → ``str``
    * Present multi-value  → sorted ``list[str]``
    * Missing / n-a        → ``None``
    """
    target = record["target_scores"]
    gold: dict = {}
    for attr in schema:
        if attr in target:
            values = extract_gold_values(target[attr])
            if len(values) == 0:
                gold[attr] = None
            elif len(values) == 1:
                gold[attr] = values[0]
            else:
                gold[attr] = sorted(values)
        else:
            gold[attr] = None
    return gold


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_gold(record: dict, schemas: dict[str, list[str]]) -> list[str]:
    """Validate a cleaned record's ``gold_json``.  Returns a list of issues."""
    issues = []
    cat = record["category"]
    gold = record["gold_json"]
    schema = schemas[cat]

    gold_keys = list(gold.keys())
    if gold_keys != schema:
        missing = set(schema) - set(gold_keys)
        extra = set(gold_keys) - set(schema)
        if missing:
            issues.append(f"missing keys: {missing}")
        if extra:
            issues.append(f"extra keys: {extra}")
        if not missing and not extra:
            issues.append("key order mismatch")

    for key, val in gold.items():
        if val is None:
            continue
        elif isinstance(val, str):
            if val == "":
                issues.append(f"'{key}' is empty string")
        elif isinstance(val, list):
            if len(val) < 2:
                issues.append(f"'{key}' is list with {len(val)} element(s)")
            if not all(isinstance(v, str) for v in val):
                issues.append(f"'{key}' list has non-string elements")
            if any(v == "" for v in val):
                issues.append(f"'{key}' list has empty strings")
            if val != sorted(val):
                issues.append(f"'{key}' list not sorted: {val}")
        else:
            issues.append(f"'{key}' has unexpected type: {type(val).__name__}")

    return issues


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def prepare(
    raw_path: str | Path,
    out_dir: str | Path,
) -> list[dict]:
    """Run the full cleaning pipeline.

    1. Load raw JSONL
    2. Clean titles (remove ``Null`` artifacts)
    3. Build canonical gold JSON per record
    4. Validate all gold JSONs
    5. Write ``cleaned_with_gold.jsonl`` and ``category_schemas.json``

    Returns the list of cleaned records.
    """
    raw = load_jsonl(raw_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cleaned: list[dict] = []
    for rec in raw:
        category = rec["category"]
        schema = CATEGORY_SCHEMAS[category]
        gold = build_gold_json(rec, schema)
        cleaned.append({
            "id": rec["id"],
            "category": category,
            "input_title": clean_null_artifact(rec["input_title"]),
            "input_description": rec["input_description"],
            "gold_json": gold,
        })

    # Validate
    issues_found = 0
    for rec in cleaned:
        issues = validate_gold(rec, CATEGORY_SCHEMAS)
        if issues:
            issues_found += len(issues)
            print(f"  ID={rec['id']} ({rec['category']}): {issues}")
    if issues_found:
        print(f"WARNING: {issues_found} validation issues found")
    else:
        print(f"All {len(cleaned):,} gold JSONs passed validation.")

    # Write outputs
    save_jsonl(cleaned, out_dir / "cleaned_with_gold.jsonl")
    with open(out_dir / "category_schemas.json", "w") as f:
        json.dump(CATEGORY_SCHEMAS, f, indent=2)
    print(f"Saved {len(cleaned):,} cleaned records to {out_dir}")

    return cleaned


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Clean and canonicalize WDC-PAVE data")
    parser.add_argument("--raw", type=Path, default=Path("data/WDC-PAVE/normalized_target_scores.jsonl"))
    parser.add_argument("--out", type=Path, default=Path("data/WDC-PAVE/cleaned"))
    args = parser.parse_args()

    prepare(args.raw, args.out)
