# Data Configuration (`config/data/`)

This directory defines **dataset and data-loading configuration** used by the project.
Each YAML file in this directory is a **Hydra config variant** that describes *what data is used* and *how it is loaded*,
without embedding any data-processing logic.

The intent is to keep data concerns **declarative, reproducible, and composable**.

---

## What belongs here

Each data config should describe:

- **Dataset identity**
  - A stable `name` used for logging, MLflow tagging, and experiment traceability.
- **Dataset location**
  - A filesystem path (preferably anchored via `${paths.data_dir}`).
- **Optional split or index metadata**
  - Only if your pipeline materializes them.
- **Loader parameters**
  - Batch size, workers, shuffling, etc.
- **Optional DVC metadata**
  - Stable identifiers for data lineage (not dynamic hashes).

No transformation, preprocessing, or filtering logic should live in these files.

---

## Canonical structure (base.yaml)

Every project must define a canonical dataset configuration, typically `base.yaml`.

```yaml
name: "CHANGE_ME_dataset_name"
path: ${paths.data_dir}/processed/CHANGE_ME_dataset_name
format: null

splits: null
index: null

batch_size: 64
num_workers: 4
shuffle: true
pin_memory: true
persistent_workers: true

dvc:
  enabled: true
  data_path: "data/processed/CHANGE_ME_dataset_name"
  metadata_path: null
```

---

## Splits and indexing (optional)

### Explicit split files

If your pipeline produces explicit split files:

```yaml
splits:
  train: "train.parquet"
  val: "val.parquet"
  test: "test.parquet"
```

### Split/index metadata (common for image datasets)

If you train from a directory of raw images but produce metadata:

```yaml
index:
  split_file: ${paths.data_dir}/processed/my_dataset/splits.csv
  classmap_file: ${paths.data_dir}/processed/my_dataset/class_to_idx.json
```

If neither `splits` nor `index` is provided, the data loader is expected to infer splits from `path`.

---

## DVC integration (recommended)

The `dvc` section carries **stable identifiers only**.

- `data_path` should point to the **artifact consumed by training**
  (often under `data/processed/`, sometimes `data/raw/` for imagefolder datasets).
- Exact DVC hashes, lock information, and Git metadata should be resolved **at runtime** and logged to MLflow.

Dynamic metadata must not be written back into YAML files.

---

## Conventions and best practices

- Dataset names must be **semantic**, not config-mechanical (do not use "base" as a dataset name).
- Do not couple Hydra variant names to dataset paths.
- Prefer adding new YAML variants over conditional logic.
- Keep configs loader-agnostic; interpretation belongs in code.

---

## Example usage

```bash
# Use the default dataset
python -m src.spatiotemporal_lab.core.train data=base

# Override dataset path
python -m src.spatiotemporal_lab.core.train data.path=${paths.data_dir}/processed/v2

# Switch to another dataset variant
python -m src.spatiotemporal_lab.core.train data=imagenet
```

This directory is part of the project’s configuration contract and should evolve deliberately.
