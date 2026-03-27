# Experiment Plan: Prompt Design and Experiment Variants

## Prompt Design

The model should be asked to perform extraction under explicit constraints.

### Prompt template

```text
You are an information extraction system.

Task:
Extract the product attributes from the product title and description.

Category:
{CATEGORY}

Allowed attributes:
{ATTRIBUTE_LIST}

Rules:
- Return exactly one valid JSON object.
- Use exactly the attribute names above as keys.
- If an attribute is missing or cannot be determined from the text, return null.
- If multiple values apply to an attribute, return them as a JSON array.
- Do not add extra keys.
- Do not explain anything.
- Use only information from the input text.
- Do not guess.
- The word "Null" appearing in the input text is a data artifact, not a product attribute value. Ignore it.

Input title:
{TITLE}

Input description:
{DESCRIPTION}
```

This prompt becomes the basis for the prompt-only baseline.

---

## Experiment Variants

The experiment should compare several strategies.

### Variant A — Prompt-only baseline

* zero-shot prompt
* temperature = 0
* no constrained decoding

### Variant B — Prompt-only + constrained JSON decoding

* same prompt as Variant A
* output is constrained to valid JSON / schema-compatible JSON

### Variant C — Few-shot prompting

* same task as above
* include 2–5 examples in the prompt
* temperature = 0

### Variant D — Fine-tuned open-source model

* supervised fine-tuning on train split
* evaluated on the same validation and test splits

### Variant E — Proprietary baseline

* strong API model
* same task, same schema, same evaluation logic

This setup allows us to separate the effect of:

* prompting
* constrained decoding
* few-shot learning
* fine-tuning
* model family / model size

---

## Constrained Decoding

Constrained decoding should be included explicitly as a baseline.

Reason:

Without this baseline, we might mistakenly think that fine-tuning improved structural correctness, while in reality the improvement came from output constraints.

The experiment should therefore isolate:

* structural correctness due to constrained decoding
* semantic correctness due to model quality or fine-tuning
