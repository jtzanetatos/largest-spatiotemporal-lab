# Model Configuration (`config/model/`)

This directory defines **model configuration** used by the project.
Each YAML file in this directory is a **Hydra config variant** that specifies *which model is used* and *how it is instantiated*,
including its core hyperparameters.

The intent is to keep model definition **declarative, reproducible, and decoupled** from training/runtime logic.

---

## What belongs here

Each model config should describe:

- **Model identity**
  - A stable `name` used for run directories, checkpoint paths, and MLflow run naming/tags.
- **Instantiation target**
  - A Hydra `_target_` pointing to the model or LightningModule class.
- **Model-specific hyperparameters**
  - Architecture and optimization parameters intrinsic to the model.

Trainer/runtime concerns (epochs, devices, precision, etc.) must not live here.

---

## Canonical structure (base.yaml)

Every project must define a canonical model configuration, typically `base.yaml`.

```yaml
name: "CHANGE_ME_model_name"

_target_: spatiotemporal_lab.models.MyModel  # CHANGE_ME

hidden_dim: 256
num_layers: 2
dropout: 0.1

lr: 1e-3
weight_decay: 0.0
```

---

## Required conventions

- **`name` is mandatory**  
  It must be a stable, semantic identifier (do not use "base" as a model name).

- **`_target_` must be importable**  
  Hydra must be able to instantiate the model without conditional logic.

- Model configs must be **self-contained**  
  They should not assume a specific trainer, device, or environment.

---

## Lightning vs pure models

Recommended pattern:

- Point `_target_` to a **LightningModule** that encapsulates:
  - the model
  - forward pass
  - loss computation
  - optimizer configuration

This allows the training entrypoint to remain generic and fully config-driven.

If you use pure `nn.Module` classes:

- your training code must wrap or handle optimization explicitly
- the config structure here remains valid

---

## Adding new model variants

To add a new model, create a new YAML file:

```text
config/model/
  resnet50.yaml
```

Example:

```yaml
name: "resnet50"

_target_: spatiotemporal_lab.models.ResNet50

pretrained: true
num_classes: 1000
lr: 3e-4
```

Switch models via CLI:

```bash
python -m src.spatiotemporal_lab.core.train model=resnet50
```

---

## Best practices

- Prefer multiple small variants over one large conditional config.
- Keep model configs free of data- and trainer-specific logic.
- Treat this directory as part of the project’s public configuration contract.
