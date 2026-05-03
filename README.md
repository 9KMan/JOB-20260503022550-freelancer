# AI Data Cleaning Automation

Automates data cleaning for mixed text + numerical datasets. Scrapes, normalizes, and outputs clean CSV/JSON ready for analysis.

## What It Does

- **Data Ingestion** — CSV, Excel, JSON input via CLI or drag-drop
- **Smart Cleaning** — Auto-detect and fix: missing values, duplicates, type errors, whitespace, encoding issues
- **Text Normalization** — Lowercase, strip punctuation, standardize casing
- **Numeric Validation** — Detect outliers, coerce types, fill missing with median/mean
- **Export** — Clean output as CSV, JSON, or Excel

## Quick Start

```bash
pip install -r requirements.txt
python cleaner.py --input data/raw/MessyData.csv --output data/clean/
```

## Project Structure

```
/data
  raw/              # Input files (dirty)
  clean/            # Output files (clean)
/src
  cleaner.py        # Main CLI entry point
  cleaners/
    text.py         # Text normalization
    numeric.py      # Numeric validation
    dedup.py        # Deduplication
  utils.py          # Shared helpers
/tests
  test_cleaner.py   # Unit tests
requirements.txt
Dockerfile
pytest.ini
README.md
```

## Tech Stack

Python 3.11 · pandas · numpy · openpyxl

## Usage Examples

```bash
# Clean a CSV
python cleaner.py --input data/raw/survey.csv --output data/clean/

# Dry run (see what would change)
python cleaner.py --input data/raw/survey.csv --dry-run

# Verbose output
python cleaner.py --input data/raw/survey.csv --verbose

# Skip deduplication
python cleaner.py --input data/raw/survey.csv --output data/clean/ --no-dedup

# Don't cap outliers
python cleaner.py --input data/raw/survey.csv --output data/clean/ --no-cap-outliers

# Specify columns explicitly
python cleaner.py --input data/raw/survey.csv --output data/clean/ \
    --text-columns name email --numeric-columns age salary
```

## Output

Clean dataset + `cleaning_report.txt` documenting all changes made.

## Running Tests

```bash
pytest tests/ -v
```

## Docker

```bash
docker build -t ai-data-cleaner .
docker run -v $(pwd)/data:/data ai-data-cleaner --input /data/raw/survey.csv --output /data/clean/
```
