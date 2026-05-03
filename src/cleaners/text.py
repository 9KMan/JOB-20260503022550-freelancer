"""AI-powered text cleaning using LLM."""
import os
import pandas as pd
from typing import Optional

from src.ai.llm_cleaner import LLMCleaner


class TextCleaner:
    def __init__(self, llm: Optional[LLMCleaner] = None, enabled: bool = True):
        self.llm = llm or LLMCleaner()
        self.enabled = enabled and os.getenv("OPENAI_API_KEY") is not None

    def clean_column(self, df: pd.DataFrame, column: str) -> tuple[pd.Series, list]:
        if not self.enabled or column not in df.columns:
            return df[column], []

        texts = df[column].fillna("").astype(str).tolist()
        changes = []

        max_batch = int(os.getenv("MAX_BATCH_SIZE", 100))
        all_results = []

        for i in range(0, len(texts), max_batch):
            batch = texts[i:i + max_batch]
            try:
                results = self.llm.clean_text_batch(batch, column_name=column)
                all_results.extend(results)
            except Exception as e:
                raise RuntimeError(f"Text cleaning failed for column '{column}': {e}")

        cleaned_values = []
        for idx, result in enumerate(all_results):
            if result.get("is_empty", False):
                cleaned_values.append(None)
            else:
                cleaned_values.append(result.get("cleaned", texts[idx]))
            for change in result.get("changes", []):
                changes.append(f"Row {idx}: {change}")

        return pd.Series(cleaned_values, index=df.index), changes