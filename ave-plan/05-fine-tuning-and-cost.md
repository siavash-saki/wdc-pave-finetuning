# Experiment Plan: Fine-Tuning and Cost Tracking

## Fine-Tuning Setup

The fine-tuning task should be framed as supervised structured extraction.

### Training sample format

Each training example should contain:

* instruction / task description
* product title
* product description
* target JSON

### Important controls

* use the exact same schema in training and evaluation
* keep decoding deterministic during evaluation
* use the same canonicalization in gold and prediction
* log all hyperparameters

### First recommendation

Use parameter-efficient fine-tuning first:

* LoRA or QLoRA

This is the most practical way to compare before/after fine-tuning without excessive cost.

---

## AWS Cost Components to Track Later

When the experiment moves to AWS, relevant cost categories include:

* training compute
* batch inference compute
* notebook / workspace compute
* model storage
* data storage
* endpoint cost, if real-time deployment is used

### In practical terms

Track separately:

#### Training cost

* training instance time
* attached storage
* checkpoint storage

#### Batch evaluation cost

* notebook or job instance time
* model loading overhead
* storage

#### Real-time deployment cost

* endpoint uptime
* instance hourly cost
* autoscaling replicas
* attached storage

### Recommendation

For the benchmark phase, prefer **batch inference**, not a persistent endpoint.
It is simpler and usually cheaper.
