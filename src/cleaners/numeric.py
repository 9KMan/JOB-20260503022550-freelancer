"""AI-assisted numeric cleaning."""
import os
import pandas as pd
import numpy as np
from typing import Optional

from src.ai.llm_cleaner import LLMCleaner


class NumericCleaner:
    def __init__(self, llm: Optional[LLMCleaner] = None, enabled: bool = True):
        self.llm = llm or LLMCleaner()
        self.enabled = enabled and os.getenv("OPENAI_API_KEY") is not None

    def clean_column(self, df: pd.DataFrame, column: str) -> tuple[pd.Series, list]:
        if not self.enabled or column not in df.columns:
            return df[column], []

        values = pd.to_numeric(df[column], errors="coerce")
        changes = []

        outlier_mask = self._detect_outliers(values)
        outlier_indices = np.where(outlier_mask)[0]

        if len(outlier_indices) == 0:
            return values, []

        outlier_values = values.loc[outlier_indices].tolist()
        column_context = self._get_column_context(df, column)

        try:
            decisions = self.llm.analyze_outliers(outlier_values, column_name=column, context=column_context)
        except Exception as e:
            raise RuntimeError(f"Numeric cleaning failed for column '{column}': {e}")

        cleaned = values.copy()
        for decision in decisions:
            idx = outlier_indices[decision["index"]]
            action = decision.get("suggested_action", "keep")

            if action == "remove":
                cleaned.loc[idx] = np.nan
                changes.append(f"Row {idx}: removed outlier {decision['value']} - {decision.get('reason', '')}")
            elif action == "keep":
                changes.append(f"Row {idx}: kept legitimate value {decision['value']} - {decision.get('reason', '')}")
            elif action == "impute":
                imp = decision.get("imputation")
                if imp == "mean":
                    cleaned.loc[idx] = values.mean()
                elif imp == "median":
                    cleaned.loc[idx] = values.median()
                elif imp == "forward-fill":
                    cleaned.loc[idx] = cleaned.loc[idx - 1] if idx > 0 else np.nan
                changes.append(f"Row {idx}: imputed {decision['value']} with {imp}")

        return cleaned, changes

    def _detect_outliers(self, series: pd.Series) -> np.ndarray:
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            return np.zeros(len(series), dtype=bool)
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        return (series < lower) | (series > upper)

    def _get_column_context(self, df: pd.DataFrame, column: str) -> str:
        samples = df[column].dropna().head(10).tolist()
        return f"Column '{column}' has sample values: {samples}"