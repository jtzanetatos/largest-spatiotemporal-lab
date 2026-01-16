# Tools

This directory contains **repository-level developer and CI utilities**.

Scripts in `tools/` are:

- **Not imported** by production code
- **Safe to run in CI**
- Focused on **repo hygiene, validation, and automation**
- Deliberately conservative (stdlib-first where possible)

They complement, but do not replace, deployment-specific scripts found under
`deployment/**/scripts/`.

---

## Contents

### `release.py`

Safe release automation for template-based repositories.

What it does:

- Uses `pyproject.toml` `[project].version` as the **single source of truth**
- Ensures:
  - clean git working tree
  - correct release branch (default: `main`)
  - tag does not already exist
- Optionally runs quality gates:
  - `ruff check`
  - `ruff format --check`
  - `pytest` (exit code 5 treated as success)
- Bumps or sets version
- Creates annotated git tag (`vX.Y.Z`)
- Pushes commit + tag (unless disabled)

Example:

```bash
python tools/release.py --part patch
python tools/release.py --set-version 1.2.0 --dry-run
```

---

### `repo_check.py`

Validates that the repository **matches the ML template structure**.

What it checks:

- Required top-level files and directories
- Hydra config entrypoints and groups
- Deployment skeleton (docker / api / k8s / triton)
- Testing and notebook structure
- Community health files (`.github/` templates)
- CI pipeline presence (Woodpecker)

Use cases:

- CI guardrail for new repos
- Quick sanity check after refactors
- Template evolution validation

Example:

```bash
python tools/repo_check.py
python tools/repo_check.py --strict
```

---

### `data_check.py`

Validates **data layout, hygiene, and safety**.

What it checks:

- `data/` directory exists
- `data/README.md` exists (required)
- Optional structure (`raw/`, `processed/`, `external/`)
- DVC hygiene (if DVC is detected):
  - `.dvc/` directory present
  - `data/` ignored in `.gitignore`
- Large file guard:
  - fails (or warns) on files > threshold (default: 50MB)
- Optional cross-check with `config/data/base.yaml`

What it does **not** do:

- Download data
- Run pipelines
- Call `dvc`
- Require credentials

Example:

```bash
python tools/data_check.py
python tools/data_check.py --warn-only
python tools/data_check.py --check-config
```

---

## Design Principles

- **Stdlib-first** for critical tooling
- **Fail fast** with clear error messages
- **No side effects** unless explicitly requested
- **Template-friendly** (tolerates empty repos early on)
- **CI-safe** by default

---

## What does *not* belong here

- Training logic → `src/`
- Inference logic → `deployment/api/`
- Deployment pipelines → `deployment/**/scripts`
- Data processing → pipelines / notebooks

---

## Typical CI Usage

```bash
python tools/repo_check.py --strict
python tools/data_check.py
```

These tools are intentionally boring.  
That is a feature.
