"""Shared utilities for data cleaning."""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Union, List, Dict, Any


def load_data(file_path: Union[str, Path]) -> pd.DataFrame:
    """Load data from CSV, Excel, or JSON file."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == '.csv':
        return pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')
    elif suffix in ['.xlsx', '.xls']:
        return pd.read_excel(file_path, engine='openpyxl')
    elif suffix == '.json':
        return pd.read_json(file_path, encoding='utf-8')
    else:
        raise ValueError(f"Unsupported file format: {suffix}")


def save_data(df: pd.DataFrame, file_path: Union[str, Path], format: str = None) -> None:
    """Save DataFrame to CSV, Excel, or JSON."""
    path = Path(file_path)
    if format is None:
        format = path.suffix.lower().lstrip('.')

    Path(file_path).parent.mkdir(parents=True, exist_ok=True)

    if format == 'csv':
        df.to_csv(file_path, index=False, encoding='utf-8')
    elif format in ['xlsx', 'xls']:
        df.to_excel(file_path, index=False, engine='openpyxl')
    elif format == 'json':
        df.to_json(file_path, orient='records', indent=2, force_ascii=False)
    else:
        raise ValueError(f"Unsupported output format: {format}")


def get_column_types(df: pd.DataFrame) -> Dict[str, str]:
    """Classify columns as numeric, text, or mixed."""
    types = {}
    for col in df.columns:
        if df[col].dtype.kind in 'iufc':
            types[col] = 'numeric'
        elif df[col].dtype == 'object':
            types[col] = 'text'
        else:
            types[col] = 'other'
    return types


def generate_report(changes: List[Dict[str, Any]], output_path: Union[str, Path]) -> None:
    """Generate a cleaning report."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("DATA CLEANING REPORT\n")
        f.write("=" * 60 + "\n\n")
        if not changes:
            f.write("No cleaning changes made.\n")
            return
        for i, change in enumerate(changes, 1):
            f.write(f"{i}. {change['type']}: {change['description']}\n")
        f.write(f"\nTotal changes: {len(changes)}\n")
