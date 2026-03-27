"""Shared model loading and generation for local (transformers) inference.

Used by Variants A, B, and C.
"""

import json
import time

import torch
from tqdm.auto import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer

from ave.utils import extract_json


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

def load_model(
    model_id: str,
    dtype: torch.dtype = torch.bfloat16,
    attn_implementation: str = "sdpa",
):
    """Load a causal-LM and its tokenizer.

    Returns ``(model, tokenizer)``.
    """
    device = (
        "cuda" if torch.cuda.is_available()
        else "mps" if torch.backends.mps.is_available()
        else "cpu"
    )

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=dtype,
        device_map="auto",
        attn_implementation=attn_implementation,
    )
    model.eval()

    n_params = sum(p.numel() for p in model.parameters())
    print(f"Loaded {model_id} ({n_params:,} params, {model.dtype}, device={device})")
    return model, tokenizer


# ---------------------------------------------------------------------------
# Single-example generation
# ---------------------------------------------------------------------------

@torch.no_grad()
def generate_response(
    model,
    tokenizer,
    messages: list[dict],
    max_new_tokens: int = 512,
    temperature: float | None = None,
) -> dict:
    """Generate from *model* given chat *messages*.

    Returns a dict with keys: ``raw_output``, ``parsed_json``,
    ``parse_error``, ``input_tokens``, ``output_tokens``, ``latency_s``.
    """
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    inputs = tokenizer(
        [text], return_tensors="pt", add_special_tokens=False,
    ).to(model.device)
    input_len = inputs["input_ids"].shape[1]

    gen_kwargs: dict = {"max_new_tokens": max_new_tokens}
    if temperature is not None and temperature > 0:
        gen_kwargs.update(do_sample=True, temperature=temperature, top_p=0.95)
    else:
        gen_kwargs["do_sample"] = False

    t0 = time.perf_counter()
    output_ids = model.generate(**inputs, **gen_kwargs)
    latency = time.perf_counter() - t0

    new_tokens = output_ids[0, input_len:]
    raw_output = tokenizer.decode(new_tokens, skip_special_tokens=True)
    parsed_json, parse_error = extract_json(raw_output)

    return {
        "raw_output": raw_output,
        "parsed_json": parsed_json,
        "parse_error": parse_error,
        "input_tokens": input_len,
        "output_tokens": len(new_tokens),
        "latency_s": round(latency, 3),
    }


# ---------------------------------------------------------------------------
# Batch runner
# ---------------------------------------------------------------------------

def run_inference(
    model,
    tokenizer,
    records: list[dict],
    message_builder,
    variant_name: str,
    model_id: str,
    max_new_tokens: int = 512,
    temperature: float | None = None,
) -> list[dict]:
    """Run inference over *records* and return standardised prediction dicts.

    *message_builder* is a callable ``(record) -> list[dict]`` that
    builds the chat messages for each record.
    """
    predictions = []
    for rec in tqdm(records, desc=f"Variant {variant_name}"):
        messages = message_builder(rec)
        result = generate_response(
            model, tokenizer, messages,
            max_new_tokens=max_new_tokens, temperature=temperature,
        )
        predictions.append({
            "id": rec["id"],
            "category": rec["category"],
            "variant": variant_name,
            "model": model_id,
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
    return predictions
