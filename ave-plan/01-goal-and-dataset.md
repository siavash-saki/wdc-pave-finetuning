# Experiment Plan: Attribute–Value Extraction with Open-Source LLMs

## Goal

We want to design and run a structured experiment for **attribute–value extraction** with LLMs.

The task is:

* **Input:** product title + product description
* **Output:** a JSON object containing product attributes and their values

This is not a general chatbot task. It is an **information extraction** task with structured output.

Our broader goal is to:

* learn how fine-tuning works in practice
* compare **prompt-only extraction** vs **fine-tuned extraction**
* compare **open-source models** vs **proprietary models**
* build a reusable evaluation setup for future internal use cases

---

## Dataset Options

For this kind of experiment, there are a couple of suitable public dataset options, especially in the area of product attribute extraction.

Two strong candidates are:

* **MAVE**

  * large-scale product attribute-value extraction dataset
  * good for scale and more advanced experiments
* **WDC-PAVE**

  * product offer attribute-value extraction dataset
  * smaller, cleaner, and easier to start with

### Decision: Use WDC-PAVE for the first experiment

We choose **WDC-PAVE** for the first experiment because:

* it already matches the task shape very well: **free text -> structured attributes**
* it is easier to inspect manually
* it is small enough for rapid experimentation
* it is suitable for comparing multiple extraction strategies without large compute cost
* it is a better dataset for learning the workflow before moving to larger-scale training

MAVE remains a good next step later if we want to scale the experiment.

---

## Problem Framing

The task should be framed as:

> **Extract attribute–value pairs from product text into a canonical JSON representation.**

Important:

* The output should be a **JSON object**
* The keys are the **allowed attributes**
* The values are the extracted values
* Missing attributes should be represented as `null`

This means the experiment is **not** about arbitrary JSON generation.
It is about **structured extraction into a known schema**.

---

## Key Design Decision

Even though each example in the dataset has a different set of populated attributes, the schema should **not** be different per example.

Instead:

* use **one fixed schema per category**
* build that schema as the **union of all attributes observed in that category**
* for each example, populate known fields and set the rest to `null`

### Per-category schemas (from the normalized dataset)

**Computers And Accessories** (11 attributes):
```json
{
  "Generation": null,
  "Part Number": null,
  "Product Type": null,
  "Cache": null,
  "Processor Type": null,
  "Processor Core": null,
  "Interface": null,
  "Manufacturer": null,
  "Capacity": null,
  "Ports": null,
  "Rotational Speed": null
}
```

**Home And Garden** (8 attributes):
```json
{
  "Product Type": null,
  "Color": null,
  "Length": null,
  "Width": null,
  "Height": null,
  "Depth": null,
  "Manufacturer Stock Number": null,
  "Retail UPC": null
}
```

**Office Products** (10 attributes):
```json
{
  "Product Type": null,
  "Color(s)": null,
  "Pack Quantity": null,
  "Length": null,
  "Width": null,
  "Height": null,
  "Depth": null,
  "Paper Weight": null,
  "Manufacturer Stock Number": null,
  "Retail UPC": null
}
```

**Jewelry** (3 attributes):
```json
{
  "Product Type": null,
  "Brand": null,
  "Model Number": null
}
```

**Grocery And Gourmet Food** (5 attributes):
```json
{
  "Product Type": null,
  "Brand": null,
  "Pack Quantity": null,
  "Retail UPC": null,
  "Size/Weight": null
}
```

Note: `Color` (Home And Garden) and `Color(s)` (Office Products) are distinct attributes in different categories — this is intentional in the dataset, not a naming inconsistency.

For each specific example, the non-null fields will differ, but the **expected output structure remains fixed per category**.

---

## Scope of the First Experiment

The full WDC-PAVE dataset is small enough (1,420 records, 5 categories, 24 unique attributes) to use in its entirety from the start.

### Scope

* use **all 5 categories** with per-category schemas
* build the fixed schema for each category (see above)
* create a canonical gold JSON for each example
* compare multiple model strategies on the same split
* report metrics both **aggregate** and **per-category**

| Category                   | Records | Attributes | % of dataset |
| -------------------------- | ------: | ---------: | -----------: |
| Computers And Accessories  |     436 |         11 |        30.7% |
| Home And Garden            |     356 |          8 |        25.1% |
| Office Products            |     297 |         10 |        20.9% |
| Jewelry                    |     250 |          3 |        17.6% |
| Grocery And Gourmet Food   |      81 |          5 |         5.7% |

Using all categories gives ~1,000 training examples instead of ~300, which is much more meaningful for fine-tuning. Per-category breakdown in evaluation reveals whether a model is strong on simple schemas (Jewelry, 3 attributes) but weak on complex ones (Computers, 11 attributes).
