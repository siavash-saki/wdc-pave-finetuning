# Experiment Plan: Evaluation Strategy

## Evaluation Strategy

The evaluation should not rely on raw JSON text equality.

Instead, we evaluate both:

1. **structure quality**
2. **attribute-value correctness**

### 1. Valid JSON rate

Definition:

* can the model output be parsed as JSON?

Implementation:

* parse with `json.loads`
* success = valid
* failure = invalid

Metric:

* `valid_json_rate = valid_outputs / total_outputs`

---

### 2. Schema adherence

Definition:

* does the parsed JSON follow the expected schema?

Check for:

* object structure
* required keys present
* no extra keys
* allowed value types
* list vs string vs null consistency

Metric:

* `schema_adherence_rate = outputs_passing_schema / total_outputs`

This is different from valid JSON.
A JSON can be valid but still structurally wrong.

---

### 3. Field-level precision / recall / F1

This is one of the most important metrics.

Treat each extracted `(attribute, value)` pair as a prediction.

For each example:

* **True Positive (TP):** predicted pair exists in gold
* **False Positive (FP):** predicted pair not in gold
* **False Negative (FN):** gold pair missing in prediction

Then compute:

* **Precision = TP / (TP + FP)**
* **Recall = TP / (TP + FN)**
* **F1 = harmonic mean of precision and recall**

### Interpretation

* **Precision:** when the model predicts a value, how often is it correct?
* **Recall:** how many gold values did the model successfully recover?
* **F1:** balanced summary of both

### Comparison rules

All value comparisons should be **case-insensitive** to account for annotator inconsistencies in the gold data (e.g., `COMPAQ` vs `Compaq`).

### Multi-value evaluation

When an attribute has multiple gold values (stored as a list), use **set-level matching**:

* normalize both gold and predicted to sets (after case-insensitive normalization)
* **TP** = |predicted ∩ gold|
* **FP** = |predicted − gold|
* **FN** = |gold − predicted|

When gold is a list and prediction is a single string: treat prediction as a set of one element. When gold is a single string and prediction is a list: treat gold as a set of one element.

Report a separate **multi-value F1** alongside overall field F1 to track whether models struggle specifically with multi-value attributes (3.9% of attribute instances).

### Recommendation

For this metric, compute it on **non-null extracted values**.

---

### 4. Object exact match

Definition:

* after parsing and canonicalization, does the full predicted JSON exactly match the full gold JSON?

This is a strict metric.

Metric:

* `object_exact_match = fully_correct_examples / total_examples`

This should be reported together with field-level F1, because exact match can be very harsh.

---

### 5. Null / missing-field handling

This should be measured explicitly.

#### a) Hallucination rate

Gold is `null`, but the model predicts a value.

Metric:

* `hallucination_rate = false_non_null_predictions / gold_null_fields`

#### b) Miss rate

Gold has a value, but the model predicts `null`.

Metric:

* `miss_rate = missed_non_null_fields / gold_non_null_fields`

#### c) Null accuracy

Gold is `null` and model correctly predicts `null`.

This matters a lot in extraction tasks.

---

### 6. Latency

Measure:

* average time per example
* total runtime
* optionally p50 / p95 latency

For batch experiments, examples per second or examples per minute are also useful.

---

### 7. Cost per 1,000 examples

This should be tracked differently for API models and self-hosted models.

#### For proprietary API models

Track:

* input tokens
* output tokens
* retry count
* per-token pricing

Compute:

* cost per 1,000 examples

#### For open-source self-hosted models

Track:

* compute hours
* GPU / instance type
* training runtime
* inference runtime
* storage if relevant

Compute:

* effective cost per 1,000 examples

### For the current Colab phase

Even if no direct money is spent, still log:

* GPU hours
* wall-clock time
* throughput

This will help estimate later AWS cost.

---

## Error Analysis

In addition to aggregate metrics, manually inspect a sample of failed predictions.

### Suggested error buckets

* wrong value extracted
* partially correct value
* hallucinated value
* formatting issue
* normalization mismatch
* missed obvious attribute
* extra unsupported field

A manual review of 50–100 errors will provide very valuable insight.
