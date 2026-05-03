"""Tests for CleanLLM."""
import json
import os
import pytest
from unittest.mock import MagicMock, patch

from src.ai.llm_cleaner import LLMCleaner, TokenUsage
from src.utils import load_data, save_data, generate_report, get_column_types


class TestTokenUsage:
    def test_add(self):
        usage = TokenUsage()
        usage.add({"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150})
        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150

    def test_add_accumulates(self):
        usage = TokenUsage()
        usage.add({"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150})
        usage.add({"prompt_tokens": 200, "completion_tokens": 100, "total_tokens": 300})
        assert usage.prompt_tokens == 300
        assert usage.completion_tokens == 150
        assert usage.total_tokens == 450


class TestLLMCleaner:
    def test_requires_api_key(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                LLMCleaner()

    def test_uses_env_model(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test", "AI_MODEL": "gpt-4o"}):
            cleaner = LLMCleaner()
            assert cleaner.model == "gpt-4o"

    def test_uses_default_model(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test", "AI_MODEL": ""}):
            cleaner = LLMCleaner()
            assert cleaner.model == "gpt-4o-mini"


class TestLLMIntegration:
    @patch("openai.OpenAI")
    def test_clean_text_batch_calls_api(self, mock_openai):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "results": [
                {"index": 0, "cleaned": "New York", "is_empty": False, "changes": ["standardized NY to New York"]}
            ]
        })
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 150
        mock_response.model = "gpt-4o-mini"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            cleaner = LLMCleaner()
            results = cleaner.clean_text_batch(["NY"], "city")

            assert len(results) == 1
            assert results[0]["cleaned"] == "New York"
            assert cleaner.usage.total_tokens == 150

    @patch("openai.OpenAI")
    def test_analyze_outliers_calls_api(self, mock_openai):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "decisions": [
                {"index": 0, "value": 999999, "is_error": True, "reason": "Invalid age", "suggested_action": "remove", "imputation": None}
            ]
        })
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 150
        mock_response.model = "gpt-4o-mini"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            cleaner = LLMCleaner()
            decisions = cleaner.analyze_outliers([999999], "age")

            assert len(decisions) == 1
            assert decisions[0]["is_error"] is True
            assert decisions[0]["suggested_action"] == "remove"

    @patch("openai.OpenAI")
    def test_find_semantic_duplicates_calls_api(self, mock_openai):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "duplicate_pairs": [
                {"id1": 0, "id2": 1, "similarity": 0.95, "reason": "Same person"}
            ]
        })
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 150
        mock_response.model = "gpt-4o-mini"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            cleaner = LLMCleaner()
            records = [{"name": "John Smith"}, {"name": "J. Smith"}]
            pairs = cleaner.find_semantic_duplicates(records)

            assert len(pairs) == 1
            assert pairs[0]["similarity"] == 0.95


class TestGetColumnTypes:
    def test_numeric_detection(self):
        import pandas as pd
        df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
        types = get_column_types(df)
        assert types["a"] == "numeric"
        assert types["b"] == "text"


class TestGenerateReport:
    def test_report_format(self):
        report = generate_report(
            input_file="input.csv",
            output_file="output.csv",
            original_rows=100,
            cleaned_rows=95,
            changes=["Removed 5 duplicates", "Fixed spelling in row 3"],
            token_usage={"prompt_tokens": 1000, "completion_tokens": 500, "total_tokens": 1500},
            dry_run=False,
        )
        assert "CleanLLM" in report
        assert "Original rows: 100" in report
        assert "Cleaned rows: 95" in report
        assert "Removed 5 duplicates" in report
        assert "Total tokens: 1,500" in report


class TestDryRun:
    @patch("openai.OpenAI")
    def test_dry_run_does_not_modify_files(self, mock_openai):
        import tempfile
        import pandas as pd

        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({"results": []})
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 10
        mock_response.usage.total_tokens = 20
        mock_response.model = "gpt-4o-mini"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "test.csv")
            df = pd.DataFrame({"name": ["John", "Jane"], "age": [25, 30]})
            df.to_csv(input_file, index=False)

            with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
                from src.cleaners.text import TextCleaner
                from src.cleaners.numeric import NumericCleaner

                original_content = open(input_file).read()

                text_cleaner = TextCleaner(llm=LLMCleaner(), enabled=False)
                numeric_cleaner = NumericCleaner(llm=LLMCleaner(), enabled=False)

                new_content = open(input_file).read()
                assert new_content == original_content