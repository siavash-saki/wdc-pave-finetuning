# Experiment Plan: Data Preparation

## Data Cleaning

Before canonicalization, clean known data quality issues in the raw input.

### Input text cleaning

* **"Null" in titles:** 368 records (26%) contain literal `"Null"` in the product title — this is scraping noise, not product information. Strip trailing `Null`, trailing `"Null"`, and isolated `Null` tokens surrounded by whitespace. Do not strip `Null` when it appears as a substring inside a real word.
* **Short descriptions:** 7 records have descriptions under 50 characters. Keep them — they are valid products with minimal text.
* **No duplicates:** all 1,420 (title + description) pairs are unique. No deduplication needed.

### Metadata fields

The `target_scores` structure contains `pid` and `score` fields alongside the extracted values:

* `score` is always `1` across the entire dataset — it carries no information for this experiment. Strip it when building gold JSON.
* `pid` indicates provenance: `[0]` = extracted from title, `[1]` = extracted from description, `[0, 1]` = extractable from both. Strip it from gold JSON, but **log the pid distribution** per attribute for error analysis — it reveals whether models extract better from titles vs descriptions.

---

## Gold Data Preparation

The raw `target_scores` field must be converted into a canonical gold representation.

### Canonicalization rules

For each example:

1. Use the category schema
2. For every schema key:

   * if the attribute has a single gold value, store that value as a string
   * if the attribute has multiple valid gold values, store them as a sorted list
   * if the gold value is `n/a`, convert it to `null`
   * if the attribute is not present in the record, set it to `null`
3. Normalize the values consistently (see below)

### Multi-value handling

3.9% of attribute instances (456 out of 11,769) have multiple valid values. This is concentrated in:

* `Manufacturer` in Computers And Accessories (161 cases) — e.g., `["Hewlett-Packard", "Hewlett-Packard Enterprise"]`
* `Product Type` across categories (94 cases)
* `Color(s)` in Office Products (40 cases)

The maximum is 15 values for a single attribute instance (an extreme Part Number case).

**Gold representation:**

* single value → string: `"Manufacturer": "Dell"`
* multiple values → sorted list: `"Manufacturer": ["Hewlett-Packard", "Hewlett-Packard Enterprise"]`

**Sort order:** alphabetical, to ensure deterministic gold JSON.

### Normalization policy

These are **concrete decisions**, not options:

* **Trim whitespace:** yes
* **Collapse repeated spaces:** yes
* **Lowercase:** no — values like `"Hewlett-Packard"` and `"Intel Xeon Series"` are proper nouns. Instead, use **case-insensitive comparison at evaluation time**.
* **Manufacturer casing:** the gold data itself has annotator inconsistencies (`COMPAQ` vs `Compaq`, `PROLIANT` vs `ProLiant` vs `Proliant`). Do **not** attempt to fix these in gold. Handle via **case-insensitive matching** during evaluation.
* **Part number separators:** the normalized dataset already strips hyphens (`435952-B21` → `435952B21`). No extra normalization needed.
* **Numeric dimensions** (Height, Width, Depth, Length): gold values are already numeric strings (`"25.4"`, `"12.7"`). Keep as-is.
* **Units in values** (Cache, Capacity, Size/Weight): keep the unit as part of the value string (e.g., `"8 Megabytes"`, `"300 Gigabytes"`, `"12 Ounce"`). Do not split value from unit.

---

## Train / Validation / Test Split

Use a fixed split across the full dataset.

### Recommended split

* **70% train**
* **10% validation**
* **20% test**

### Stratified by category

The split must be **stratified by category** to preserve the category distribution in each subset. This is especially important for the small Grocery And Gourmet Food category (81 records — a naive random split could produce an unbalanced test set).

Use `sklearn.model_selection.train_test_split` with `stratify=category`.

### Important rules

* keep the same split for all models and variants
* do not change the test set between runs
* do not use test examples as few-shot examples
* save the split assignments (record ID → split) to a file for reproducibility
