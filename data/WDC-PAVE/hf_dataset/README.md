---
license: cc-by-4.0
task_categories:
  - token-classification
  - text-generation
language:
  - en
tags:
  - attribute-extraction
  - product-data
  - structured-output
  - information-extraction
  - e-commerce
size_categories:
  - 1K<n<10K
configs:
  - config_name: default
    data_files:
      - split: train
        path: train.jsonl
      - split: validation
        path: val.jsonl
      - split: test
        path: test.jsonl
dataset_info:
  features:
    - name: id
      dtype: int64
    - name: category
      dtype: string
    - name: input_title
      dtype: string
    - name: input_description
      dtype: string
    - name: gold_json
      dtype: string
---

# WDC-PAVE: Attribute-Value Extraction Benchmark

A cleaned, canonicalized, and pre-split version of the [WDC Product Attribute-Value Extraction (PAVE)](https://webdatacommons.org/structureddata/2022-12/pave/) dataset, prepared for structured information extraction experiments with LLMs.

## Task

Given a product **title** and **description**, extract attribute-value pairs into a JSON object with a **fixed schema per product category**.

- **Input:** product title + product description (free text)
- **Output:** JSON object with category-specific attributes; missing values are `null`

This is a **structured extraction** task, not open-ended generation. Each category has a fixed set of expected attributes.

## Dataset Details

| | |
|---|---|
| **Source** | [WDC-PAVE](https://webdatacommons.org/structureddata/2022-12/pave/) (normalized variant) |
| **Records** | 1,420 |
| **Categories** | 5 |
| **Unique attributes** | 24 (3-11 per category) |
| **Split** | 70% train / 10% val / 20% test, stratified by category |
| **Random seed** | 42 |

### Category distribution

| Category | Train | Val | Test | Total | Attributes |
|---|---:|---:|---:|---:|---:|
| Computers And Accessories | 305 | 44 | 87 | 436 | 11 |
| Home And Garden | 250 | 35 | 71 | 356 | 8 |
| Office Products | 207 | 30 | 60 | 297 | 10 |
| Jewelry | 175 | 25 | 50 | 250 | 3 |
| Grocery And Gourmet Food | 57 | 8 | 16 | 81 | 5 |
| **Total** | **994** | **142** | **284** | **1,420** | |

### Per-category schemas

**Computers And Accessories** (11 attributes):
`Generation`, `Part Number`, `Product Type`, `Cache`, `Processor Type`, `Processor Core`, `Interface`, `Manufacturer`, `Capacity`, `Ports`, `Rotational Speed`

**Home And Garden** (8 attributes):
`Product Type`, `Color`, `Length`, `Width`, `Height`, `Depth`, `Manufacturer Stock Number`, `Retail UPC`

**Office Products** (10 attributes):
`Product Type`, `Color(s)`, `Pack Quantity`, `Length`, `Width`, `Height`, `Depth`, `Paper Weight`, `Manufacturer Stock Number`, `Retail UPC`

**Jewelry** (3 attributes):
`Product Type`, `Brand`, `Model Number`

**Grocery And Gourmet Food** (5 attributes):
`Product Type`, `Brand`, `Pack Quantity`, `Retail UPC`, `Size/Weight`

## Record format

Each JSONL record has the following fields:

```json
{
  "id": 8068358,
  "category": "Home And Garden",
  "input_title": "Pneumatic Lift Lab Stools w/Back ...",
  "input_description": "Pneumatic lift adjusts to accommodate ...",
  "gold_json": {
    "Product Type": "Furniture, Storage, Racks and Fixtures",
    "Color": "Black",
    "Length": null,
    "Width": null,
    "Height": "99.1",
    "Depth": null,
    "Manufacturer Stock Number": "SAF3430BL",
    "Retail UPC": null
  }
}
```

### Value conventions

- **Single value** -> string: `"Manufacturer": "Dell"`
- **Multiple values** -> sorted list: `"Manufacturer": ["Hewlett-Packard", "Hewlett-Packard Enterprise"]`
- **Missing / not applicable** -> `null`
- Multi-value attributes occur in 3.9% of attribute instances

## Data preparation

The following cleaning steps were applied to the raw WDC-PAVE normalized variant:

1. **Title cleaning:** Stripped literal `"Null"` scraping artifacts from 368 product titles (26% of records)
2. **Gold canonicalization:** Parsed `target_scores` structure into flat JSON per category schema; converted `n/a` to `null`; sorted multi-value lists alphabetically
3. **Normalization:** Trimmed whitespace, collapsed repeated spaces. Casing is preserved (use case-insensitive comparison at evaluation time)
4. **Schema enforcement:** Each record's `gold_json` contains all attributes for its category, with `null` for absent values

## Suggested evaluation metrics

1. **Valid JSON rate** -- can the output be parsed?
2. **Schema adherence** -- correct keys, no extras, valid types?
3. **Field-level precision / recall / F1** -- case-insensitive, set-level matching for multi-value attributes
4. **Object exact match** -- full JSON matches gold?
5. **Null handling** -- hallucination rate, miss rate, null accuracy
6. **Latency** and **cost per 1,000 examples**

## Citation

If you use this dataset, please cite the original WDC-PAVE paper:

```bibtex
@inproceedings{primpeli2023wdcpave,
  title={Product Attribute Value Extraction using Large Language Models},
  author={Primpeli, Anna and Bizer, Christian},
  year={2023}
}
```

## License

This dataset inherits the [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) license from the original WDC-PAVE dataset.
