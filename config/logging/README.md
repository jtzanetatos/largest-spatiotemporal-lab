# Logging Configuration (`config/logging/`)

This directory defines **application logging configuration**.
It is designed to support a Hydra-first workflow while allowing you to use **loguru** as the primary logger.

Key goals:

- One consistent logging policy across scripts (train/eval/infer/pipelines)
- Unified logs under repo-root `${paths.logs_dir}`
- Compatibility with third-party libraries that use stdlib `logging` (Hydra, Lightning, etc.)

Recommended approach:

- Use `from loguru import logger` in your application code.
- Bridge stdlib `logging` into loguru so Hydra/Lightning logs are captured in the same sinks.

---

## What belongs here

- Log level (INFO/DEBUG/WARNING)
- Console logging on/off
- File logging on/off and file path
- Rotation/retention/compression settings (loguru sinks)
- Whether to bridge stdlib logging into loguru

Hydra run directories (`hydra.run.dir`) are configured in `config/config.yaml`.
This group controls where and how logs are written.

---

## Canonical structure (base.yaml)

```yaml
backend: loguru
level: INFO

console:
  enabled: true

file:
  enabled: true
  path: ${paths.logs_dir}/${project.name}.log
  rotation: "50 MB"
  retention: "10 days"
  compression: "zip"

bridge_stdlib: true
capture_warnings: true
```

Notes:

- `file.path` should be anchored at `${paths.logs_dir}` (repo root) so it is stable even when Hydra changes CWD.
- If you prefer per-model log files, set: `${paths.logs_dir}/${model.name}.log`.

---

## Example usage

```bash
# Default logging
python -m src.spatiotemporal_lab.core.train

# Increase verbosity
python -m src.spatiotemporal_lab.core.train logging.level=DEBUG

# Disable file logging
python -m src.spatiotemporal_lab.core.train logging.file.enabled=false
```

This directory is part of the project’s configuration contract and should evolve deliberately.
