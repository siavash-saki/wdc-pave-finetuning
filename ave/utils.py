"""Shared helpers: JSONL I/O, value normalization, JSON parsing."""

import json
import re
from pathlib import Path


# ---------------------------------------------------------------------------
# JSONL I/O
# ---------------------------------------------------------------------------

def load_jsonl(path: str | Path) -> list[dict]:
    """Read a JSONL file and return a list of dicts."""
    with open(path) as f:
        return [json.loads(line) for line in f]


def save_jsonl(records: list[dict], path: str | Path) -> None:
    """Write a list of dicts as JSONL."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")


# ---------------------------------------------------------------------------
# Value normalization
# ---------------------------------------------------------------------------

def normalize_value(val: str) -> str:
    """Trim whitespace and collapse repeated spaces.  No lowercasing."""
    return re.sub(r"\s+", " ", val).strip()


def clean_null_artifact(title: str) -> str:
    """Remove scraping 'Null' artifacts from product titles.

    Handles trailing ``Null`` / ``"Null"`` and isolated mid-string tokens
    without touching substrings like ``Nullable``.
    """
    cleaned = re.sub(r'\s*"?\s*Null\s*"?\s*$', "", title)
    cleaned = re.sub(r"\bNull\b", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = cleaned.rstrip('"').rstrip()
    return cleaned


# ---------------------------------------------------------------------------
# JSON extraction from model output
# ---------------------------------------------------------------------------

def extract_json(text: str) -> tuple[dict | None, str | None]:
    """Try to parse a JSON object from *text*.

    Returns ``(parsed_dict, None)`` on success or
    ``(None, error_message)`` on failure.
    """
    # 1. Direct parse
    try:
        return json.loads(text), None
    except json.JSONDecodeError:
        pass

    # 2. Markdown code-block
    code_block = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if code_block:
        try:
            return json.loads(code_block.group(1)), None
        except json.JSONDecodeError:
            pass

    # 3. Bare JSON object
    json_match = re.search(
        r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL
    )
    if json_match:
        try:
            return json.loads(json_match.group()), None
        except json.JSONDecodeError as e:
            return None, f"JSON extraction failed: {e}"

    return None, "No JSON object found in output"


# ---------------------------------------------------------------------------
# Schema helpers
# ---------------------------------------------------------------------------

def model_slug(model_name: str) -> str:
    """Convert a model name to a filesystem-safe slug."""
    return model_name.replace("/", "_").replace(":", "_")
