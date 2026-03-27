# Experiment Plan: Execution Plan and Deliverables

## Deliverables

At the end of the first experiment, we should have:

1. a cleaned and canonicalized dataset split (stratified by category)
2. fixed per-category schemas (all 5 categories)
3. a prompt-only baseline
4. a constrained-decoding baseline
5. a few-shot baseline
6. a fine-tuned open-source baseline
7. at least one proprietary model baseline
8. a reusable evaluation pipeline
9. a result table across all variants
10. an error analysis summary

---

## Suggested Result Table

### Aggregate results

| Variant | Model                         | Valid JSON | Schema Adherence | Field F1 | Multi-value F1 | Exact Match | Hallucination Rate | Miss Rate | Avg Latency | Cost / 1k |
| ------- | ----------------------------- | ---------: | ---------------: | -------: | -------------: | ----------: | -----------------: | --------: | ----------: | --------: |
| A       | Prompt-only                   |            |                  |          |                |             |                    |           |             |           |
| B       | Prompt + constrained decoding |            |                  |          |                |             |                    |           |             |           |
| C       | Few-shot                      |            |                  |          |                |             |                    |           |             |           |
| D       | Fine-tuned open-source        |            |                  |          |                |             |                    |           |             |           |
| E       | Proprietary baseline          |            |                  |          |                |             |                    |           |             |           |

### Per-category breakdown (Field F1)

| Variant | Computers (436) | Home & Garden (356) | Office (297) | Jewelry (250) | Grocery (81) |
| ------- | --------------: | ------------------: | -----------: | ------------: | -----------: |
| A       |                 |                     |              |               |              |
| B       |                 |                     |              |               |              |
| C       |                 |                     |              |               |              |
| D       |                 |                     |              |               |              |
| E       |                 |                     |              |               |              |

---

## Recommended Execution Order

### Phase 1 — Data preparation

* clean input text ("Null" artifacts in titles)
* build per-category schemas for all 5 categories
* convert raw targets into canonical gold JSON (strip pid/score, handle multi-value, apply normalization)
* stratified train / validation / test split (70/10/20, stratify by category)
* save split assignments to file for reproducibility

### Phase 2 — Baselines

* run prompt-only baseline
* run constrained-decoding baseline
* run few-shot baseline
* evaluate all outputs

### Phase 3 — Fine-tuning

* prepare SFT dataset
* fine-tune a small open-source model
* evaluate on the same test set

### Phase 4 — Comparison

* compare all variants using the same metrics
* perform manual error analysis
* summarize trade-offs in quality, latency, and cost

---

## Recommended First Version

To avoid overcomplicating the first run, the initial version should be:

* all 5 categories with per-category schemas
* a limited number of models
* one fine-tuning approach
* one evaluation pipeline

### Minimal first experiment

* **Dataset:** WDC-PAVE (full, 1,420 records)
* **Scope:** all 5 categories with per-category schemas
* **Baselines:** prompt-only, constrained decoding, proprietary baseline
* **Fine-tuning:** one small open-source model with LoRA/QLoRA
* **Metrics:** valid JSON, schema adherence, field F1, multi-value F1, exact match, hallucination rate, miss rate, latency
* **Reporting:** aggregate + per-category breakdown

This will already provide a very strong learning setup.

---

## Summary

This experiment is designed as a structured comparison of extraction strategies for **attribute–value extraction into JSON**.

We use **WDC-PAVE** as the first dataset because it is a clean and practical entry point for this task. The experiment focuses on comparing:

* prompt-only extraction
* constrained decoding
* few-shot prompting
* fine-tuning of open-source models
* proprietary baselines

The most important principle is:

> Evaluate the task as **canonical structured extraction**, not as raw text generation.

That means:

* fixed schema per category (all 5 categories)
* canonical gold JSON with explicit multi-value handling
* case-insensitive content-based evaluation
* structure-based evaluation
* explicit handling of null and missing fields
* per-category reporting alongside aggregate metrics

This setup should give us both a strong learning exercise and a reusable benchmark template for future internal use cases.
