# notebooks/

This directory contains **exploratory and experimental notebooks** used for
analysis, visualization, prototyping, and early-stage experimentation.

Notebooks should answer questions and guide development—not accumulate
production logic. Once ideas stabilize, promote reusable code into `src/`.

---

## Project-Specific Details (Fill Me In)

Complete this section when creating a new project from the template.

### Notebook Workflow

- Naming scheme (prefix style: 01-, 02-, etc.):  
- Expected sequence of notebooks (exploration → preprocessing → training → eval):  
- Any required environment variables, datasets, or configs used by notebooks:  

### Exploration Goals

- Key questions or hypotheses explored in notebooks:  
- Metrics, plots, or artifacts expected from notebook analysis:  
- Any domain-specific exploratory tasks:  

### Promotion Rules

- Criteria for promoting notebook code into `src/`:  
- Scripts or modules that notebooks typically import from `src/`:  

---

## Purpose

The `notebooks/` directory supports:

- Data exploration  
- Experiment tracking and idea testing  
- Visualization and sanity checks  
- Early model prototyping  
- Feature engineering trials  

Notebooks are **not** the source of truth for reusable logic—code should migrate to `src/`.

---

## Conventions

- Use **numeric prefixes** to indicate execution order:  
  - `01_data_exploration.ipynb`  
  - `02_preprocessing.ipynb`  
  - `03_training_baseline.ipynb`  
  - `10_experiments_model_X.ipynb`

- Keep notebooks **lightweight**:  
  - Avoid long-running cells  
  - Avoid storing huge arrays/plots inline  
  - Prefer small representative samples for exploration  

- Import configuration and utilities from `config/` and `src/` where possible.  
  Avoid duplicating logic inside notebooks.

- Use project configuration files (Hydra configs, `params.yaml`, etc.)
  for consistent data paths, seeds, and experiment settings.

---

## Best Practices (Shared Across All Repos)

- **Clear cell outputs before committing** to keep diffs clean.  
- Use **relative imports** or project initialization cells
  (e.g., `sys.path.insert(...)`) sparingly.  
- Prefer `.ipynb_checkpoints/` to remain untracked (default behavior).  
- Document conclusions or insights at the **bottom of each notebook**.  
- If notebooks generate artifacts, save them under `data/` (via DVC)
  or `docs/figures/`.

---

## Notes

- Notebooks must never contain secrets, API keys, or sensitive raw data.  
- Large-scale experiments should move to proper scripts or pipelines
  once validated.
