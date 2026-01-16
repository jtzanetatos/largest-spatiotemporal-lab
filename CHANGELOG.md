# Changelog

All notable changes to this project will be documented in this file.

The format is based on **Keep a Changelog**, and this project adheres to
**Semantic Versioning** for code releases (via `pyproject.toml` versioning and Git tags).

---

## [Unreleased]

### Added

- —

### Changed

- —

### Fixed

- —

### Deprecated

- —

### Removed

- —

### Security

- —

---

## [v0.1.0] - YYYY-MM-DD

### Added

- First public template release.
- Opinionated ML project structure (`src/`, `config/`, `deployment/`, `tests/`, `tools/`).
- Hydra-based configuration system (single source of truth).
- MLflow experiment tracking and model registry (alias-based lifecycle).
- Triton export and promotion workflow.
- Woodpecker CI pipelines (lint, test, promote).
- DVC pipeline scaffolding (optional, Hydra-aligned).
- FastAPI deployment path with Docker and Kubernetes manifests.
- Optional dashboards (Streamlit, NiceGUI).
- Repository hygiene tooling (`repo_check.py`, `data_check.py`, `release.py`).
- Notebook tooling (`nbstripout`, `nbdime`) and setup script.
- `.editorconfig`, `.gitattributes`, Dockerignore, and CI configs.

---

## Conventions

### Versioning

This template uses the version defined in **`pyproject.toml`** under `[project].version`
and Git tags created via:

```bash
python tools/release.py --part <patch|minor|major>
```

Tags pushed to `main` are intended to trigger CI/CD workflows.

### Entry Format

Each release section may include the following subsections:

- **Added** — new features  
- **Changed** — modifications to existing behaviour  
- **Deprecated** — functionality planned for removal  
- **Removed** — functionality removed  
- **Fixed** — bug fixes  
- **Security** — vulnerability fixes  

### How to Update

1. Add changes under **[Unreleased]** during development.
2. Before release, ensure **[Unreleased]** accurately reflects pending changes.
3. Run the release script:

   ```bash
   python tools/release.py --part patch
   ```

4. After tagging, move entries from **[Unreleased]** into a new version section.

---

## Notes

This changelog is **template-oriented** and intended to be reused across all projects
generated from this repository.
