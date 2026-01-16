# LargeST Spatiotemporal Lab

<p align="center">
  <!-- Optional banner image -->
  <img src="docs/figures/banner.svg" alt="LargeST Spatiotemporal Lab banner" width="100%" />
</p>

<p align="center">
  <!-- Version -->
  <img src="https://img.shields.io/github/v/tag/jtzanetatos/largest-spatiotemporal-lab?label=version" alt="Version">

  <!-- Python -->
  <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Python">

  <!-- License -->
  <img src="https://img.shields.io/badge/license-AGPL-3.0-green" alt="License">

  <!-- CI -->
  <img src="https://img.shields.io/badge/CI-Woodpecker-success" alt="CI">

  <!-- Stack -->
  <img src="https://img.shields.io/badge/config-Hydra-informational" alt="Hydra">
  <img src="https://img.shields.io/badge/tracking-MLflow-orange" alt="MLflow">
  <img src="https://img.shields.io/badge/data-DVC-blueviolet" alt="DVC">
  <img src="https://img.shields.io/badge/serving-FastAPI%20%7C%20Triton-ff69b4" alt="Serving">
</p>

> **One‑sentence summary of the project.**  
> Replace this text with a concise description of the problem and solution.

---

## Overview

## Overview

<!-- 
  TODO: Describe the project's purpose.
  - Problem: What are you solving?
  - Solution: What model/system are you building?
  - Context: Who is it for? 
-->

This project implements **[ ... ]** to solve **[ ... ]**. It accepts **[ inputs ]** and produces **[ outputs ]**.

---

## Key Features

<!-- 
  TODO: List 3-5 key capabilities. 
  Examples: "Real-time inference < 10ms", "Daily retraining pipeline", "Streamlit dashboard"
-->

- [ ] **Feature A**: ...
- [ ] **Feature B**: ...
- [ ] **Feature C**: ...

---

## Repository Structure

```text
.
├── config/                 # Hydra configuration (single source of truth)
├── data/                   # Dataset layout (DVC‑tracked)
├── deployment/             # Docker, API, dashboards, k8s, Triton
├── docs/                   # Design docs, ADRs, figures
├── notebooks/              # Exploration & experiments
├── src/
│   └── spatiotemporal_lab/     # Production Python package
├── tests/                  # Unit & integration tests
├── tools/                  # Repo hygiene & CI tooling
├── dvc.yaml                # Optional DVC pipeline stub
├── pyproject.toml          # Dependencies & version
├── CHANGELOG.md
├── TEMPLATE_GUIDE.md
└── README.md               # You are here
```

---

## Installation

This project uses **PEP 621** (`pyproject.toml`).

```bash
git clone https://github.com/jtzanetatos/largest-spatiotemporal-lab.git
cd largest-spatiotemporal-lab


# Recommended
uv sync

# Optional: Install extras
uv sync --extra notebooks
uv sync --extra mlops

```

---

## Documentation

- **[TEMPLATE_GUIDE.md](TEMPLATE_GUIDE.md)**: Engineering patterns, training, configuration, and deployment.
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Development setup, coding standards, and testing.

---

## License

AGPL-3.0. See [LICENSE](LICENSE).
