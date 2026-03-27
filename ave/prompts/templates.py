"""Prompt templates for attribute-value extraction and few-shot example selection."""

import json

from jinja2 import Template


# ---------------------------------------------------------------------------
# System message (shared by SFT training and chat-style inference)
# ---------------------------------------------------------------------------

SYSTEM_MESSAGE = """\
You are an information extraction system. Extract product attributes from the given title and description.

Rules:
- Return exactly one valid JSON object.
- Use exactly the attribute names listed by the user as keys.
- If an attribute is missing or cannot be determined, return null.
- If multiple values apply, return them as a JSON array sorted alphabetically.
- Do not add extra keys. Do not explain. Use only information from the input text.
- The word "Null" in the input is a data artifact — ignore it."""


# ---------------------------------------------------------------------------
# User message template (used for all variants)
# ---------------------------------------------------------------------------

_USER_TEMPLATE = Template("""\
Category: {{ category }}

Attributes:
{{ attribute_list }}

Title: {{ title }}

Description: {{ description }}""")


def render_user_message(record: dict, schemas: dict[str, list[str]]) -> str:
    """Render the user-turn message for a single record."""
    category = record["category"]
    return _USER_TEMPLATE.render(
        category=category,
        attribute_list=", ".join(schemas[category]),
        title=record["input_title"],
        description=record["input_description"],
    )


# ---------------------------------------------------------------------------
# Chat message builders
# ---------------------------------------------------------------------------

def build_messages_zero_shot(
    record: dict,
    schemas: dict[str, list[str]],
) -> list[dict]:
    """Build chat messages for zero-shot inference (Variants A, B, E)."""
    return [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": render_user_message(record, schemas)},
    ]


def build_messages_few_shot(
    record: dict,
    schemas: dict[str, list[str]],
    train_by_cat: dict[str, list[dict]],
    n_examples: int = 3,
) -> list[dict]:
    """Build chat messages with few-shot examples (Variant C).

    Examples are inserted as user/assistant turn pairs before the target.
    """
    category = record["category"]
    examples = select_few_shot_examples(
        category, train_by_cat, n=n_examples, exclude_id=record["id"],
    )

    messages: list[dict] = [{"role": "system", "content": SYSTEM_MESSAGE}]
    for ex in examples:
        messages.append({"role": "user", "content": render_user_message(ex, schemas)})
        messages.append({"role": "assistant", "content": json.dumps(ex["gold_json"])})

    messages.append({"role": "user", "content": render_user_message(record, schemas)})
    return messages


# ---------------------------------------------------------------------------
# Few-shot example selection
# ---------------------------------------------------------------------------

def _fill_ratio(record: dict) -> float:
    """Fraction of non-null attributes in ``gold_json``."""
    gold = record["gold_json"]
    filled = sum(1 for v in gold.values() if v is not None)
    return filled / len(gold)


def select_few_shot_examples(
    category: str,
    train_by_cat: dict[str, list[dict]],
    n: int = 3,
    exclude_id: int | None = None,
) -> list[dict]:
    """Pick *n* diverse examples from training data for *category*.

    Strategy: sort by fill ratio and sample at evenly-spaced quantiles
    to get a mix of sparse and dense examples.
    """
    pool = [r for r in train_by_cat[category] if r["id"] != exclude_id]
    pool.sort(key=_fill_ratio)

    if len(pool) <= n:
        return pool

    step = len(pool) / n
    indices = [int(i * step + step / 2) for i in range(n)]
    return [pool[i] for i in indices]
