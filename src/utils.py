"""File I/O, configuration, and report generation."""
import json
import os
from pathlib import Path
from datetime import datetime
import pandas as pd


SUPPORTED_EXTENSIONS = {".csv", ".json", ".xlsx", ".xls"}


def load_data(file_path: str) -> pd.DataFrame:
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}. Supported: {SUPPORTED_EXTENSIONS}")

    if ext == ".csv":
        return pd.read_csv(file_path)
    elif ext == ".json":
        return pd.read_json(file_path)
    elif ext in {".xlsx", ".xls"}:
        return pd.read_excel(file_path)


def save_data(df: pd.DataFrame, file_path: str):
    path = Path(file_path)
    ext = path.suffix.lower()

    os.makedirs(path.parent, exist_ok=True)

    if ext == ".csv":
        df.to_csv(file_path, index=False)
    elif ext == ".json":
        df.to_json(file_path, orient="records", indent=2)
    elif ext in {".xlsx", ".xls"}:
        df.to_excel(file_path, index=False)


def generate_report(
    input_file: str,
    output_file: str,
    original_rows: int,
    cleaned_rows: int,
    changes: list,
    token_usage: dict,
    dry_run: bool = False,
) -> str:
    report_lines = [
        "=" * 60,
        "CLEANLLM - Data Cleaning Report",
        "=" * 60,
        f"Timestamp: {datetime.now().isoformat()}",
        f"Input file: {input_file}",
        f"Output file: {output_file}",
        f"Mode: {'DRY RUN' if dry_run else 'LIVE'}",
        "",
        "Summary:",
        f"  Original rows: {original_rows}",
        f"  Cleaned rows: {cleaned_rows}",
        f"  Rows removed: {original_rows - cleaned_rows}",
        "",
        "Changes made:",
    ]

    if changes:
        for change in changes:
            report_lines.append(f"  - {change}")
    else:
        report_lines.append("  (none)")

    if token_usage:
        report_lines.extend([
            "",
            "API Usage:",
            f"  Prompt tokens: {token_usage.get('prompt_tokens', 0):,}",
            f"  Completion tokens: {token_usage.get('completion_tokens', 0):,}",
            f"  Total tokens: {token_usage.get('total_tokens', 0):,}",
        ])

    report_lines.extend([
        "",
        "=" * 60,
    ])

    report = "\n".join(report_lines)
    return report


def save_report(report: str, output_path: str):
    report_path = Path(output_path).parent / "cleaning_report.txt"
    os.makedirs(report_path.parent, exist_ok=True)
    with open(report_path, "w") as f:
        f.write(report)


def get_column_types(df: pd.DataFrame) -> dict[str, str]:
    types = {}
    for col in df.columns:
        if df[col].dtype in ["int64", "float64"]:
            types[col] = "numeric"
        else:
            types[col] = "text"
    return types


def get_config() -> dict:
    return {
        "model": os.getenv("AI_MODEL", "gpt-4o-mini"),
        "temperature": float(os.getenv("AI_TEMPERATURE", 0.1)),
        "max_batch_size": int(os.getenv("MAX_BATCH_SIZE", 100)),
        "semantic_dedup_threshold": float(os.getenv("SEMANTIC_DEDUP_THRESHOLD", 0.85)),
    }