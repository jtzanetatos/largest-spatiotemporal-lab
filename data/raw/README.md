# raw/ — Raw, Immutable Data

## Purpose

This directory stores **immutable raw data exactly as obtained** from the original source.
No manual editing, transformations, or cleaning should be applied here.

Raw data may come from:

- Data dumps  
- External APIs  
- Partner datasets  
- Public datasets  
- User-provided inputs  

Raw files should generally be managed by DVC or excluded from Git.

---

## Dataset Template (Fill for Your Project)

### Source

- Origin: [TODO: where the raw data comes from]
- Acquisition method: [TODO: manual/API/download]
- Version / Date: [TODO]

### Format

- File types: [CSV/JSON/Parquet/etc.]
- Volume/size: [TODO]
- Schema (if applicable):  
  - `column_1`: [description]  
  - `column_2`: [description]  

### Notes

- License restrictions: [TODO]
- Known issues in raw data: [TODO]
- How often it updates: [TODO]
