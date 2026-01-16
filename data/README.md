# Data Directory

This directory organizes datasets used throughout the project.  
It follows a structure inspired by best practices in machine learning and data engineering, with clear separation between raw data, intermediate artifacts, and final modeling datasets.

All data placed here should be tracked using appropriate mechanisms (e.g., DVC, storage buckets, external volumes).  
Large data files should **not** be committed to Git directly.

---

## Directory Overview

### `raw/`

Immutable source data collected from its original provider.  
No manual modifications are allowed.  
This data is the foundation for all processing steps.

### `interim/`

Intermediate transformed data generated during processing, cleaning, or feature extraction.  
Used to accelerate reproducible pipelines without recomputing early steps.

### `processed/`

Final cleaned and feature-ready datasets used for model training, validation, and testing.  
Typically includes train/val/test splits and engineered features.

### `external/`

Third-party supplemental data such as enrichments, lookup tables, metadata sets, or reference taxonomies.

---

## How to Use This Directory

- Store each dataset in the appropriate subdirectory.
- Use the README in each subfolder to document:
  - Dataset source  
  - File formats  
  - Schema  
  - Transformations applied  
  - Notes or assumptions  
- Keep transformations reproducible via scripts, notebooks, or DVC pipelines.
- Treat these subfolders as part of the project’s data contract.

---

## Notes and Recommendations

- Use `.gitignore` and DVC to manage data responsibly.
- Always document:
  - Dataset origin  
  - Licensing constraints  
  - Versioning or update frequency  
  - Known issues or limitations  
- Prefer interoperable formats (CSV, Parquet, JSON, NumPy arrays) depending on your workflow.
