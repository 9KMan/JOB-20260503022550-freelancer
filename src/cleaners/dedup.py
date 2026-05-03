"""Deduplication module."""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional


def remove_duplicates(df: pd.DataFrame, subset: List[str] = None,
                      keep: str = 'first', report: List[Dict[str, Any]] = None) -> pd.DataFrame:
    """Remove duplicate rows."""
    if report is None:
        report = []

    original_rows = len(df)
    df = df.copy()

    if subset:
        df = df.drop_duplicates(subset=subset, keep=keep)
    else:
        df = df.drop_duplicates(keep=keep)

    removed = original_rows - len(df)
    if removed > 0:
        report.append({
            'type': 'deduplication',
            'description': f"Removed {removed} duplicate rows" + (f" (based on columns: {subset})" if subset else "")
        })

    return df


def find_duplicates(df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
    """Find duplicate rows."""
    if subset:
        return df[df.duplicated(subset=subset, keep=False)]
    return df[df.duplicated(keep=False)]
