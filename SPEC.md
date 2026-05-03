# SPEC: AI Data Cleaning Automation Tool

## 1. Project Overview

**Project:** AI-powered data cleaning automation for mixed text + numerical datasets.  
**GitHub Repo:** https://github.com/9KMan/JOB-20260503022550-freelancer

Cleans dirty CSV/Excel/JSON data: fixes missing values, removes duplicates, normalizes text, validates numeric fields, and exports clean datasets ready for analysis.

## 2. Technical Stack

- Python 3.11+
- pandas, numpy, openpyxl
- pytest (tests)
- Docker

## 3. Architecture

```
cleaner.py          # CLI entry point
src/
  utils.py          # Shared helpers (type detection, column profiling)
  cleaners/
    text.py         # Text normalization (lowercase, strip, deduplicate whitespace)
    numeric.py      # Numeric validation (outliers, type coercion, fill missing)
    dedup.py        # Deduplication (exact + fuzzy)
data/
  raw/              # Input files
  clean/            # Output files
```

## 4. Key Components

| Component | Description |
|---|---|
| `cleaner.py` | CLI: `--input`, `--output`, `--dry-run`, `--verbose` |
| `text.py` | Text normalization, whitespace, encoding fixes |
| `numeric.py` | Outlier detection, type coercion, median/mode fill |
| `dedup.py` | Exact + fuzzy deduplication |
| `utils.py` | Column profiling, type detection, change reporting |

## 5. Deliverables

- [x] `cleaner.py` — main CLI entry point
- [x] `src/cleaners/text.py` — text normalization
- [x] `src/cleaners/numeric.py` — numeric validation
- [x] `src/cleaners/dedup.py` — deduplication
- [x] `src/utils.py` — shared helpers
- [x] `requirements.txt` — pandas, numpy, openpyxl
- [x] `Dockerfile` — containerized execution
- [x] `tests/test_cleaner.py` — pytest unit tests
- [x] `README.md` — usage docs with examples

## 6. Usage

```bash
# Clean a dataset
python cleaner.py --input data/raw/survey.csv --output data/clean/

# Dry run (preview changes)
python cleaner.py --input data/raw/survey.csv --dry-run

# Docker
docker build -t cleaner . && docker run -v $(pwd)/data:/data cleaner --input /data/raw/input.csv --output /data/clean/
```

## 7. Output

- Cleaned dataset (CSV/JSON/Excel)
- `cleaning_report.txt` — documents all changes made
