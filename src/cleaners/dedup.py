"""Deduplication with exact and semantic matching."""
import os
import pandas as pd
import numpy as np
from typing import Optional

from src.ai.llm_cleaner import LLMCleaner


class DedupCleaner:
    def __init__(self, llm: Optional[LLMCleaner] = None, threshold: Optional[float] = None):
        self.llm = llm or LLMCleaner()
        self.threshold = threshold if threshold is not None else float(os.getenv("SEMANTIC_DEDUP_THRESHOLD", 0.85))
        self.enabled = os.getenv("OPENAI_API_KEY") is not None

    def deduplicate(self, df: pd.DataFrame, columns: Optional[list[str]] = None) -> tuple[pd.DataFrame, list]:
        changes = []
        original_len = len(df)

        df_exact = df.drop_duplicates(subset=columns, keep="first")
        exact_removed = original_len - len(df_exact)
        if exact_removed > 0:
            changes.append(f"Removed {exact_removed} exact duplicates")

        if not self.enabled or df_exact.empty:
            return df_exact, changes

        df_semantic = self._semantic_dedup(df_exact, columns if columns is not None else df_exact.columns.tolist())
        semantic_removed = len(df_exact) - len(df_semantic)
        if semantic_removed > 0:
            changes.append(f"Removed {semantic_removed} semantic duplicates")

        return df_semantic, changes

    def _semantic_dedup(self, df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
        if df.empty or len(df) < 2:
            return df

        id_field = "_record_id"
        df = df.copy()
        df[id_field] = range(len(df))

        records = df[columns + [id_field]].to_dict("records") if columns else df.to_dict("records")

        try:
            duplicate_pairs = self.llm.find_semantic_duplicates(records, threshold=self.threshold, id_field=id_field)
        except Exception:
            return df

        if not duplicate_pairs:
            return df

        ids_to_remove = set()
        for pair in duplicate_pairs:
            ids_to_remove.add(pair["id2"])

        return df[~df[id_field].isin(ids_to_remove)].drop(columns=[id_field])