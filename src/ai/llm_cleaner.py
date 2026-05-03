"""OpenAI LLM integration for data cleaning."""
import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Optional

from openai import OpenAI
from openai import APIError, RateLimitError


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def add(self, usage: dict):
        self.prompt_tokens += usage.get("prompt_tokens", 0)
        self.completion_tokens += usage.get("completion_tokens", 0)
        self.total_tokens += usage.get("total_tokens", 0)


@dataclass
class LLMResponse:
    content: str
    raw: dict
    model: str
    usage: TokenUsage


@dataclass
class LLMCleaner:
    model: Optional[str] = None
    temperature: float = 0.1
    max_retries: int = 3
    retry_delay: float = 1.0
    max_batch_size: int = 100
    _client: OpenAI = field(default=None, init=False)
    _usage: TokenUsage = field(default_factory=TokenUsage, init=False)

    def __post_init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self._client = OpenAI(api_key=api_key)
        if self.model is None:
            self.model = os.getenv("AI_MODEL", "gpt-4o-mini")

    @property
    def usage(self) -> TokenUsage:
        return self._usage

    def _make_request(self, messages: list, response_format: Optional[dict] = None) -> LLMResponse:
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }
        if response_format:
            kwargs["response_format"] = response_format

        last_error: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                response = self._client.chat.completions.create(**kwargs)
                usage_data = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
                self._usage.add(usage_data)
                return LLMResponse(
                    content=response.choices[0].message.content,
                    raw=response.model_dump(),
                    model=response.model,
                    usage=TokenUsage(**usage_data),
                )
            except RateLimitError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
            except APIError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
        if last_error:
            raise last_error
        raise RuntimeError("LLM request failed after all retries")

    def clean_text_batch(self, texts: list[str], column_name: str = "text") -> list[dict]:
        texts_json = json.dumps([{"index": i, "value": t} for i, t in enumerate(texts)], ensure_ascii=False)
        prompt = f"""You are a data cleaning assistant. Given a batch of text values from a column called "{column_name}", clean and standardize them.

For each value, apply:
1. Spelling correction
2. Whitespace normalization (trim, fix double spaces, non-breaking spaces)
3. Encoding fix (fix UTF-8 mojibake like "cafÃ©" -> "café")
4. Standardization (e.g., "NY" / "N.Y." -> "New York")
5. Empty/null detection - mark truly empty vs "N/A", "null", "-", "."

Return a JSON array with objects containing:
- "index": original index
- "cleaned": the cleaned value (or null if truly empty)
- "is_empty": true if the value was essentially empty
- "changes": list of changes made

Example output format:
[
  {{"index": 0, "cleaned": "New York", "is_empty": false, "changes": ["standardized NY to New York"]}},
  {{"index": 1, "cleaned": null, "is_empty": true, "changes": ["detected as N/A"]}}
]

Input data:
{texts_json}"""

        messages = [{"role": "user", "content": prompt}]
        response = self._make_request(messages, response_format={"type": "json_object"})
        try:
            data = json.loads(response.content)
            results = data.get("results", data)
            if isinstance(results, list):
                return results
            return results.get("cleaned", [])
        except json.JSONDecodeError:
            raise ValueError(f"Failed to parse LLM response as JSON: {response.content}")

    def analyze_outliers(self, values: list[float], column_name: str = "values", context: str = "") -> list[dict]:
        values_json = json.dumps([{"index": i, "value": v} for i, v in enumerate(values)])
        prompt = f"""You are a data cleaning assistant. Review statistical outliers in the "{column_name}" column.

Context: {context or "No additional context provided"}

For each outlier value, decide:
1. Is it a data entry error (should be corrected/removed)?
2. Or is it a legitimate extreme value?
3. If erroneous, what correction would you apply?
4. If missing, what imputation strategy is best (mean, median, forward-fill, or "cannot determine")?

Return a JSON object with "decisions" array:
[
  {{
    "index": 0,
    "value": 999999,
    "is_error": true,
    "reason": "Clearly an error - age cannot be 999999",
    "suggested_action": "remove",
    "imputation": null
  }},
  {{
    "index": 1,
    "value": 99,
    "is_error": false,
    "reason": "Valid score - 99/100 is an excellent grade",
    "suggested_action": "keep",
    "imputation": null
  }}
]

Outlier data:
{values_json}"""

        messages = [{"role": "user", "content": prompt}]
        response = self._make_request(messages, response_format={"type": "json_object"})
        try:
            data = json.loads(response.content)
            return data.get("decisions", [])
        except json.JSONDecodeError:
            raise ValueError(f"Failed to parse LLM response as JSON: {response.content}")

    def find_semantic_duplicates(self, records: list[dict], threshold: float = 0.85, id_field: str = "id") -> list[dict]:
        records_json = json.dumps(records, ensure_ascii=False)
        prompt = f"""You are a data deduplication assistant. Find semantic duplicates among the given records.

Records are considered duplicates if they refer to the same entity (person, company, product, etc.), even if:
- Names are slightly different ("John Smith" vs "J. Smith" vs "Jonathan Smith")
- Contact info differs but structure is similar
- Minor spelling variations exist

For each pair of potential duplicates, return:
- "id1": the first record's {id_field}
- "id2": the second record's {id_field}
- "similarity": similarity score 0.0-1.0
- "reason": why they are likely duplicates

Only return pairs with similarity >= {threshold}.

Return format:
{{
  "duplicate_pairs": [
    {{"id1": "A1", "id2": "A2", "similarity": 0.95, "reason": "Same person - J. Smith and Jonathan Smith"}}
  ]
}}

Records:
{records_json}"""

        messages = [{"role": "user", "content": prompt}]
        response = self._make_request(messages, response_format={"type": "json_object"})
        try:
            data = json.loads(response.content)
            return data.get("duplicate_pairs", [])
        except json.JSONDecodeError:
            raise ValueError(f"Failed to parse LLM response as JSON: {response.content}")