# Trainer Configuration (`config/trainer/`)

This directory defines **training runtime configuration**. It is intended to work with Hydra composition and to scale
as projects grow.

This group covers:

- Trainer/runtime settings (epochs, devices, precision, accumulation, etc.)
- Callback configuration (checkpointing, early stopping, LR monitoring, etc.)

**MLflow is handled separately** (Pattern A):

- MLflow configuration and run tracking live under `config/mlflow/`
- The training entrypoint is responsible for starting/stopping MLflow runs and logging params/metrics/artifacts
- Trainer configs should not duplicate MLflow settings

---

## Recommended structure

```text
config/trainer/
  README.md
  base.yaml
  fast_dev.yaml            # quick sanity/CI runs

  callbacks/
    README.md
    base.yaml              # standard callbacks
    minimal.yaml           # optional: fewer callbacks
```

---

## What belongs here

### Trainer runtime settings

Examples (Lightning):

- `max_epochs`
- `accelerator`, `devices`
- `precision`
- `accumulate_grad_batches`
- `log_every_n_steps`
- `limit_*_batches` (debugging)

### Callbacks

Examples:

- Model checkpointing (dirpath should use `${paths.checkpoints_dir}`)
- Early stopping
- Learning rate monitoring

---

## Best practices

- Keep training logic in code; keep runtime knobs and callback wiring in config.
- Prefer small, composable variants over large monolithic configs.
- Use `fast_dev.yaml` for quick feedback and CI smoke runs.
- Keep checkpoint paths anchored at repo root via `${paths.checkpoints_dir}` (safe with Hydra `chdir=true`).

---

## Usage examples

```bash
# Default training configuration
python -m src.spatiotemporal_lab.core.train

# Quick dev run
python -m src.spatiotemporal_lab.core.train trainer=fast_dev

# Override runtime parameters
python -m src.spatiotemporal_lab.core.train trainer.max_epochs=50 trainer.precision=16
```
