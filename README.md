# CleanLLM - AI-Powered Data Cleaning CLI

An AI-powered command-line tool that uses OpenAI's GPT-4o-mini to intelligently clean and standardize messy datasets containing mixed text and numerical data.

## Features

- **AI-Powered Text Cleaning**: Context-aware spelling correction, standardization, whitespace normalization, encoding fixes
- **AI-Assisted Numeric Cleaning**: Intelligent outlier detection and imputation decisions
- **Semantic Deduplication**: Identifies near-duplicates using LLM understanding
- **Multi-format Support**: CSV, JSON, XLSX file formats

## Setup

### Prerequisites

- Python 3.11+
- OpenAI API key

### Installation

```bash
pip install -r requirements.txt
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `AI_MODEL` | No | `gpt-4o-mini` | Model to use |
| `AI_TEMPERATURE` | No | `0.1` | LLM temperature |
| `MAX_BATCH_SIZE` | No | `100` | Rows per API call |
| `SEMANTIC_DEDUP_THRESHOLD` | No | `0.85` | Similarity threshold |

## Usage

### Basic

```bash
export OPENAI_API_KEY="sk-..."
python cleaner.py --input messy_data.csv --output ./cleaned/
```

### Options

```bash
# Preview changes (dry run)
python cleaner.py -i data.csv -o ./out --dry-run

# Specify columns
python cleaner.py -i data.csv -o ./out --text-columns name email address --numeric-columns age salary

# Skip AI features
python cleaner.py -i data.csv -o ./out --no-ai-text --no-ai-dedup

# Use different model
python cleaner.py -i data.csv -o ./out --ai-model gpt-4o

# Verbose output
python cleaner.py -i data.csv -o ./out --verbose
```

## Docker

```bash
docker build -t cleanllm .
docker run -e OPENAI_API_KEY="sk-..." -v $(pwd)/data:/data cleanllm --input /data/messy.csv --output /data/cleaned/
```

## Output

- Cleaned data file (same format as input)
- `cleaning_report.txt` with details of changes made and API usage

## Testing

```bash
pytest tests/
```