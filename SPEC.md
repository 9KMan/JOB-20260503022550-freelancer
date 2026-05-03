# SPEC.md — AI Data Cleaning Automation Tool

## 1. Project Overview

**Project Name:** CleanLLM — AI-Powered Data Cleaning CLI

**What it does:** A command-line tool that uses a Large Language Model (LLM) to intelligently clean and standardize messy datasets containing mixed text and numerical data. Unlike rule-based cleaners, CleanLLM uses AI to understand context, make smart decisions about data transformations, and handle edge cases that regex/rule approaches cannot.

**Target Users:** Data analysts, researchers, and businesses who work with messy real-world data exports (CRM exports, survey data, spreadsheets from multiple sources).

**Client:** Freelancer.com — AI Automation for Data Cleaning
**Budget:** $30–250 USD (MICRO tier)
**GitHub Repo:** https://github.com/9KMan/JOB-20260503022550-freelancer

---

## 2. Technical Stack

- **Language:** Python 3.11+
- **AI:** OpenAI API (GPT-4o-mini for cost efficiency; fallback to GPT-4o)
- **CLI:** argparse (native stdlib)
- **Data Processing:** pandas, numpy
- **LLM SDK:** openai Python SDK
- **Testing:** pytest
- **Container:** Docker

---

## 3. Architecture

```
cleaner.py (CLI entry point)
├── src/
│   ├── utils.py           # File I/O, config, report generation
│   ├── cleaners/
│   │   ├── text.py        # Text cleaning (AI-powered via LLM)
│   │   ├── numeric.py     # Numeric cleaning (AI-assisted outlier detection)
│   │   └── dedup.py       # Deduplication (AI semantic dedup)
│   └── ai/
│       └── llm_cleaner.py # LLM API calls, prompt templates, response parsing
├── tests/
│   └── test_cleaner.py    # Unit + integration tests
├── Dockerfile
├── requirements.txt
└── README.md
```

**API Key Management:** API key read from `OPENAI_API_KEY` environment variable. Key is never logged or stored.

---

## 4. Core AI Features (What Makes It "AI")

### 4.1 AI-Powered Text Cleaning
The LLM reviews each text field and applies context-aware corrections:
- **Spelling correction** — "New Yorrk" → "New York", "mangager" → "manager"
- **Standardization** — "NY" / "N.Y." / "New York City" → canonical "New York"
- **Whitespace normalization** — trailing spaces, double spaces, non-breaking spaces
- **Encoding fix** — decode garbled UTF-8 mojibake ("cafÃ©" → "café")
- **Empty/null detection** — distinguish truly empty from "N/A", "null", "-", "."

### 4.2 AI-Assisted Numeric Cleaning
- **Outlier detection** — LLM reviews values flagged as statistical outliers and decides if they're errors or legitimate extreme values (e.g., "999999" in age field = likely error; "99" in a 0-100 score = legitimate)
- **Unit normalization** — "1.5m" / "150cm" / "five feet" → standardized units
- **Format standardization** — "1,234.56" vs "1.234,56" based on column context
- **Missing value strategy** — LLM decides best imputation strategy (mean, median, forward-fill, or "cannot determine")

### 4.3 AI Semantic Deduplication
- **Exact dedup** — standard pandas drop_duplicates (baseline)
- **Semantic dedup** — LLM identifies near-duplicates: "John Smith" / "J. Smith" / "Jonathan Smith" / "john.smith@email.com" as same person (configurable threshold)
- **Fuzzy matching** — string similarity scoring for names, addresses, product names

### 4.4 Column Type Intelligence
- LLM infers column semantic type (name, address, email, phone, date, currency, etc.)
- Validates values against inferred type
- Flags anomalies for human review

---

## 5. CLI Interface

```bash
# Basic usage
python cleaner.py --input messy_data.csv --output cleaned/

# With OpenAI API key
export OPENAI_API_KEY="sk-..."
python cleaner.py --input data.csv --output ./cleaned/

# With options
python cleaner.py -i messy.csv -o ./out --dry-run        # Preview changes
python cleaner.py -i data.csv -o ./out --text-columns name email address
python cleaner.py -i data.csv -o ./out --no-ai-text      # Skip AI text cleaning
python cleaner.py -i data.csv -o ./out --ai-model gpt-4o  # Use GPT-4o
python cleaner.py -i data.csv -o ./out --verbose
```

---

## 6. Deliverables

| # | Deliverable | Description |
|---|-------------|-------------|
| 1 | `cleaner.py` | Main CLI entry point |
| 2 | `src/ai/llm_cleaner.py` | OpenAI API integration with retry, cost tracking |
| 3 | `src/cleaners/text.py` | AI-powered text cleaning pipeline |
| 4 | `src/cleaners/numeric.py` | AI-assisted numeric cleaning |
| 5 | `src/cleaners/dedup.py` | Exact + semantic deduplication |
| 6 | `src/utils.py` | File I/O, config, report generation |
| 7 | `requirements.txt` | Dependencies |
| 8 | `Dockerfile` | Containerized execution |
| 9 | `tests/test_cleaner.py` | Unit tests for core logic |
| 10 | `README.md` | Usage documentation |

---

## 7. Configuration

| Env Var | Required | Default | Description |
|---------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | — | OpenAI API key |
| `AI_MODEL` | No | `gpt-4o-mini` | Model to use |
| `AI_TEMPERATURE` | No | `0.1` | LLM temperature (low = deterministic) |
| `MAX_BATCH_SIZE` | No | `100` | Rows per LLM API call |
| `SEMANTIC_DEDUP_THRESHOLD` | No | `0.85` | Similarity threshold for semantic dedup |

---

## 8. Acceptance Criteria

1. ✅ CLI runs with `--input` and `--output` flags
2. ✅ Reads CSV, JSON, and XLSX files
3. ✅ Calls OpenAI API for text cleaning (requires valid API key)
4. ✅ Produces cleaned output file + `cleaning_report.txt`
5. ✅ `--dry-run` shows planned changes without modifying files
6. ✅ Handles missing API key gracefully with clear error message
7. ✅ All tests pass (`pytest tests/`)
8. ✅ Docker image builds and runs successfully
9. ✅ No hardcoded API keys; key read from environment only
10. ✅ README includes usage examples and setup instructions
