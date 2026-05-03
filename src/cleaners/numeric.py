"""Numeric validation and cleaning module."""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional


def coerce_numeric(series: pd.Series, fill_value: Optional[float] = None) -> pd.Series:
    """Coerce column to numeric, replacing non-numeric values."""
    result = pd.to_numeric(series, errors='coerce')
    if fill_value is not None:
        result = result.fillna(fill_value)
    return result


def fill_missing_numeric(series: pd.Series, method: str = 'median') -> pd.Series:
    """Fill missing numeric values with mean or median."""
    result = series.copy()
    if method == 'mean':
        fill_val = result.mean()
    elif method == 'median':
        fill_val = result.median()
    else:
        raise ValueError(f"Unknown fill method: {method}")
    return result.fillna(fill_val)


def detect_outliers_iqr(series: pd.Series, multiplier: float = 1.5) -> pd.Series:
    """Detect outliers using IQR method."""
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - multiplier * IQR
    upper = Q3 + multiplier * IQR
    return series.between(lower, upper)


def cap_outliers(series: pd.Series, multiplier: float = 1.5) -> pd.Series:
    """Cap outliers to IQR boundaries."""
    result = series.copy()
    Q1 = result.quantile(0.25)
    Q3 = result.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - multiplier * IQR
    upper = Q3 + multiplier * IQR
    return result.clip(lower=lower, upper=upper)


def clean_numeric(df: pd.DataFrame, numeric_columns: List[str] = None,
                   fill_method: str = 'median', cap_outliers_flag: bool = True,
                   report: List[Dict[str, Any]] = None) -> pd.DataFrame:
    """Apply numeric cleaning to numeric columns."""
    if report is None:
        report = []

    df = df.copy()
    if numeric_columns is None:
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()

    for col in numeric_columns:
        if col not in df.columns:
            continue
        original_dtype = df[col].dtype
        original_nulls = df[col].isna().sum()
        original_outliers = (~detect_outliers_iqr(df[col])).sum()

        df[col] = coerce_numeric(df[col])

        if fill_method:
            df[col] = fill_missing_numeric(df[col], method=fill_method)

        if cap_outliers_flag:
            df[col] = cap_outliers(df[col])

        new_nulls = df[col].isna().sum()
        new_outliers = (~detect_outliers_iqr(df[col])).sum()

        if original_nulls != new_nulls or original_outliers != new_outliers or original_dtype != df[col].dtype:
            report.append({
                'type': 'numeric',
                'description': f"Column '{col}': coerced to numeric, {new_nulls} nulls, {new_outliers} outliers capped"
            })

    return df
