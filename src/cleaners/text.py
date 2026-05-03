"""Text normalization module."""
import pandas as pd
import numpy as np
import re
from typing import List, Dict, Any


def normalize_text_column(series: pd.Series) -> pd.Series:
    """Normalize text: lowercase, strip whitespace, remove punctuation."""
    result = series.copy()
    result = result.astype(str).str.lower()
    result = result.str.strip()
    result = result.str.replace(r'[^\w\s]', '', regex=True)
    result = result.replace('nan', np.nan)
    result = result.replace('none', np.nan)
    return result


def fix_whitespace(series: pd.Series) -> pd.Series:
    """Fix whitespace issues (multiple spaces, tabs, newlines)."""
    result = series.copy()
    result = result.astype(str).str.replace(r'\s+', ' ', regex=True)
    result = result.str.strip()
    result = result.replace('nan', np.nan)
    return result


def standardize_casing(series: pd.Series, style: str = 'lower') -> pd.Series:
    """Standardize text casing."""
    result = series.copy()
    if style == 'lower':
        result = result.astype(str).str.lower()
    elif style == 'upper':
        result = result.astype(str).str.upper()
    elif style == 'title':
        result = result.astype(str).str.title()
    result = result.replace('nan', np.nan)
    return result


def clean_text(df: pd.DataFrame, text_columns: List[str] = None, report: List[Dict[str, Any]] = None) -> pd.DataFrame:
    """Apply text cleaning to text columns."""
    if report is None:
        report = []

    df = df.copy()
    if text_columns is None:
        text_columns = df.select_dtypes(include='object').columns.tolist()

    for col in text_columns:
        if col not in df.columns:
            continue
        original_nulls = df[col].isna().sum()
        df[col] = normalize_text_column(df[col])
        df[col] = fix_whitespace(df[col])

        new_nulls = df[col].isna().sum()
        if new_nulls != original_nulls:
            report.append({
                'type': 'text',
                'description': f"Column '{col}': normalized text, {new_nulls} null values after cleaning"
            })

    return df
