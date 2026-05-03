"""Tests for AI Data Cleaning Automation Tool."""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import load_data, save_data, get_column_types, generate_report
from src.cleaners.text import normalize_text_column, clean_text
from src.cleaners.numeric import coerce_numeric, fill_missing_numeric, clean_numeric
from src.cleaners.dedup import remove_duplicates, find_duplicates


class TestTextCleaning:
    def test_normalize_text_column(self):
        s = pd.Series(['Hello  World', 'TEST!', '  spaces  '])
        result = normalize_text_column(s)
        assert result.tolist() == ['hello  world', 'test', 'spaces']

    def test_clean_text(self):
        df = pd.DataFrame({'name': ['John', 'JOHN', '  john  '], 'age': [25, 30, 35]})
        result = clean_text(df, text_columns=['name'])
        assert result['name'].tolist() == ['john', 'john', 'john']


class TestNumericCleaning:
    def test_coerce_numeric(self):
        s = pd.Series(['1', '2', 'abc', '4'])
        result = coerce_numeric(s)
        assert result.tolist() == [1.0, 2.0, np.nan, 4.0]

    def test_fill_missing_numeric(self):
        s = pd.Series([1.0, np.nan, 3.0, np.nan, 5.0])
        result = fill_missing_numeric(s, method='median')
        assert result.tolist() == [1.0, 3.0, 3.0, 3.0, 5.0]

    def test_clean_numeric(self):
        df = pd.DataFrame({'value': ['1', '2', 'abc', '4', '5']})
        result = clean_numeric(df, numeric_columns=['value'])
        assert result['value'].dtype in [np.float64, np.int64]


class TestDeduplication:
    def test_remove_duplicates(self):
        df = pd.DataFrame({'a': [1, 2, 1], 'b': [1, 2, 1]})
        result = remove_duplicates(df)
        assert len(result) == 2

    def test_find_duplicates(self):
        df = pd.DataFrame({'a': [1, 2, 1], 'b': [1, 2, 1]})
        result = find_duplicates(df)
        assert len(result) == 1


class TestUtils:
    def test_get_column_types(self):
        df = pd.DataFrame({'text': ['a', 'b'], 'num': [1, 2]})
        types = get_column_types(df)
        assert types['text'] == 'text'
        assert types['num'] == 'numeric'

    def test_load_and_save_data(self, tmp_path):
        df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        csv_path = tmp_path / 'test.csv'
        save_data(df, csv_path)
        loaded = load_data(csv_path)
        assert loaded.shape == (2, 2)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
