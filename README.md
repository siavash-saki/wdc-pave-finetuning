# Attribute–Value Extraction with LLM Fine-Tuning

A structured experiment comparing multiple LLM-based strategies for extracting product attributes and values from unstructured text into canonical JSON.

## Task

- **Input:** Product title + description
- **Output:** JSON object with product attributes and their extracted values, following a fixed per-category schema

## Dataset

[WDC-PAVE](https://webdatacommons.org/largescaleproductcorpus/wdc-pave/) (Product Attribute-Value Extraction) — 1,420 records across 5 product categories:

| Category                  | Records | Attributes |
|---------------------------|--------:|----------:|
| Computers And Accessories | 436     | 11        |
| Home And Garden           | 356     | 8         |
| Office Products           | 297     | 10        |
| Jewelry                   | 250     | 3         |
| Grocery And Gourmet Food  | 81      | 5         |

Data is split 70/10/20 (train/val/test), stratified by category.

## Experiment Variants

| Variant | Strategy | Description |
|---------|----------|-------------|
| A | Prompt-only (zero-shot) | Baseline prompt with schema constraints |
| B | Constrained JSON decoding | Same prompt + structural output constraints |
| C | Few-shot prompting | 2–5 in-context examples per category |
| D | Fine-tuned open-source | LoRA/QLoRA fine-tuning on the train split |
| E | Proprietary baseline | GPT-5.4 / GPT-5.4-nano via OpenAI API |

## Evaluation Metrics

- **Valid JSON rate** — can the output be parsed?
- **Schema adherence** — does it match the expected per-category schema?
- **Field-level F1** — precision/recall over (attribute, value) pairs (case-insensitive)
- **Multi-value F1** — set-level matching for attributes with multiple gold values
- **Exact match** — full object equality after canonicalization
- **Hallucination rate** — model predicts a value when gold is null
- **Miss rate** — model predicts null when gold has a value
- **Latency & cost** — per-example timing and cost per 1,000 examples

## Project Structure

```
├── ave/                    # Python package for the experiment
│   ├── configs/            # Schema definitions and config
│   ├── data/               # Data loading, cleaning, splitting
│   ├── evaluation/         # Metrics, comparison, error analysis
│   ├── inference/          # Baseline, few-shot, constrained, proprietary, fine-tuned inference
│   ├── prompts/            # Prompt templates
│   ├── training/           # SFT data preparation and fine-tuning
│   └── utils.py            # Shared utilities
├── ave-plan/               # Experiment design documents
├── data/WDC-PAVE/          # Raw and cleaned dataset files
│   ├── cleaned/            # Canonicalized splits + schemas + prompt templates
│   └── predictions/        # Model prediction outputs
└── notebooks/              # Step-by-step experiment notebooks
    ├── 01_eda_raw_data.ipynb
    ├── 02_cleaning_canonicalization.ipynb
    ├── 03_split_and_stats.ipynb
    ├── 03b_upload_to_hf.ipynb
    ├── 04_prompt_prototyping.ipynb
    ├── 05_baseline_inference.ipynb
    ├── 05_baseline_inference_colab.ipynb
    ├── 06_finetuning.ipynb
    ├── 07_proprietary_baseline.ipynb
    ├── 08_evaluation.ipynb
    └── 09_results_comparison.ipynb
```

## Setup

```bash
pip install -e .
```

Or install dependencies directly as needed — the notebooks document their requirements inline.

## License

This project uses the [WDC-PAVE dataset](https://webdatacommons.org/largescaleproductcorpus/wdc-pave/), which is provided for research purposes.
