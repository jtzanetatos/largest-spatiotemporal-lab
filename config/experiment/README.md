# Experiment Presets (`config/experiment/`)

This directory defines **named experiment presets**.
Experiment presets are *intent-level configurations* that compose existing config groups
(`data/`, `model/`, `trainer/`, `logging/`, `mlflow/`) into **reproducible, reviewable run recipes**.

They are optional but strongly recommended once a project matures beyond ad-hoc experimentation.

---

## What experiment presets are

An experiment preset is a **thin, compositional config** that answers:

> "Which combination of data, model, and trainer represents the thing we care about right now?"

Experiment presets:

- select existing config variants
- apply a small number of overrides
- encode training-time intent (e.g. debug vs baseline)
- are version-controlled and traceable

They do **not** define new models, datasets, or infrastructure.

---

## What belongs here

Typical uses include:

- **`debug`** — fast sanity checks and local iteration
- **`baseline`** — canonical training recipe used for comparisons
- **`ablation_*`** — controlled changes for research comparisons
- **`benchmark_*`** — fixed recipes for regression testing

Experiment presets should remain **small and readable**.

If a preset requires many overrides, consider creating a new
`model/`, `data/`, or `trainer/` variant instead.

---

## Lifecycle intent (important)

Experiment presets are the **correct place** to set training-time lifecycle intent.

This template uses:

- `mlflow.tags.lifecycle_intent` to record intent at training time
- MLflow Model Registry **aliases** to control actual deployment state

Example:

- `debug` → `lifecycle_intent: dev`
- `baseline` → `lifecycle_intent: staging`

Lifecycle intent does **not** control deployment by itself.

---

## Canonical presets in this template

### `debug.yaml`

- Uses a fast development trainer (`trainer=fast_dev`)
- Enables `debug=true`
- Intended for local sanity checks and CI smoke tests

### `baseline.yaml`

- Canonical, reproducible training recipe
- Stable seed and settings
- Intended as the reference for model comparison and evaluation

---

## Usage examples

```bash
# Run with no preset (explicit configuration only)
python -m src.spatiotemporal_lab.core.train

# Fast debug run
python -m src.spatiotemporal_lab.core.train experiment=debug

# Canonical baseline run
python -m src.spatiotemporal_lab.core.train experiment=baseline
```

---

## Best practices

- Prefer experiment presets over long CLI override strings
- Keep presets intent-focused and minimal
- Treat experiment names as part of the repo’s public API
- Promote models only from well-defined presets (e.g. baseline)

This directory ties together otherwise stable configuration components
into meaningful, auditable experiments.
