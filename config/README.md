# Configuration (`config/`)

This directory contains all configuration files for the project and is designed to be used with **Hydra**.
Hydra composes configuration from multiple *config groups* (e.g. data, model, trainer) and allows clean,
reproducible overrides via the command line.

The goal of this directory is to keep **all experiment, training, and tooling configuration declarative,
composable, and version-controlled**.

---

## How this directory is used

- **`config/config.yaml`**  
  The Hydra **entrypoint configuration**.
  - Defines which config groups are enabled by default (`defaults:`)
  - Holds project-wide settings shared across tools (project metadata, paths, seeds)
  - Defines Hydra run and sweep directory behavior

- **Subdirectories** under `config/` are **Hydra config groups**:
  - Each subdirectory represents a single concern (data, model, trainer, etc.)
  - Each YAML file inside a group is a *variant* that can be selected or overridden

At runtime, Hydra composes all selected configs into a single resolved configuration that is passed to the
application entrypoint.

---

## Config groups overview

Typical groups in this template:

- **`data/`**  
  Dataset configuration and data-loading parameters.
  May also include DVC-related identifiers (dataset name, version, stage).

- **`model/`**  
  Model selection and hyperparameters.
  Each model config **must define a stable `name` field**.

- **`trainer/`**  
  Training runtime configuration (e.g. PyTorch Lightning `Trainer` options).

- **`logging/`**  
  Logging configuration (backend selection, log levels, sinks).

- **`mlflow/`**  
  MLflow tracking configuration (tracking URI, experiment naming policy, tags).

- **`experiment/`** *(optional)*  
  Named presets that override multiple groups at once (e.g. `baseline`, `debug`).

---

## Common usage examples

```bash
# Default run (uses defaults from config.yaml)
python -m src.spatiotemporal_lab.core.train

# Select specific variants
python -m src.spatiotemporal_lab.core.train model=conv_autoencoder data=base trainer=base

# Override individual parameters
python -m src.spatiotemporal_lab.core.train trainer.max_epochs=20 model.lr=1e-4

# Use a named experiment preset (if defined)
python -m src.spatiotemporal_lab.core.train experiment=baseline
```

---

## Template checklist for a new project

When creating a new project from this template:

### 1. Update project identity

Edit `config/config.yaml`:

```yaml
project:
  name: "YOUR_PROJECT_NAME"
  env: "local"
```

### 2. Ensure a baseline variant exists for each group

Minimum expected files:

```text
config/
  config.yaml

  data/
    base.yaml

  model/
    base.yaml

  trainer/
    base.yaml

  logging/
    base.yaml

  mlflow/
    base.yaml
```

### 3. Required conventions

- **Model configs must define a name**:

```yaml
# config/model/base.yaml
name: "my_model"
```

- **Data configs should define a dataset identifier**:

```yaml
# config/data/base.yaml
name: "my_dataset"
```

These identifiers are used for:

- Run directory structure
- Checkpoint paths
- MLflow run naming and tagging

### 4. Recommended extensions

- Add additional variants as the project grows:

```text
config/model/
  small.yaml
  large.yaml

config/data/
  local.yaml
  production.yaml

config/trainer/
  fast_dev.yaml
```

- Add reusable experiment presets under `config/experiment/` when useful.

---

## Design principles

- Prefer **many small, composable configs** over large monolithic files
- Keep configuration declarative; avoid logic inside YAML
- Use CLI overrides for quick experimentation, config variants for reproducibility
- Treat this directory as part of the project’s public contract
