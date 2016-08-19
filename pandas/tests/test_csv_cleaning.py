import unittest
import pandas as pd
import numpy as np
from pandas.util.testing import assert_frame_equal, assert_series_equal

from utilities.csv_cleaning import nullify_non_alphanum, nullify_fields_if_field_matches_pattern

class TestCsvCleaning_NullifyNonAlphaNum(unittest.TestCase):
    def setUp(self):
        self.mydf = pd.DataFrame({'field1': ['1', '---', '2', '2', '/.! *', '3'],
                             'field2': ['y', 'y', np.nan, '. .', 'z', 'a'],
                             'field3': ['1dfasdfa!', 1, 'a', '1 . 2', '.|', np.nan]})

    def test_nullify_entire_dataset(self):
        mydf = self.mydf.copy(deep=True)

        nullify_non_alphanum(mydf)

        expected = pd.DataFrame({'field1': ['1', np.nan, '2', '2', np.nan, '3'],
                             'field2': ['y', 'y', np.nan, np.nan, 'z', 'a'],
                             'field3': ['1dfasdfa!', 1, 'a', '1 . 2', np.nan, np.nan]})

        assert_frame_equal(mydf, expected)

    def test_nullify_two_fields(self):
        mydf = self.mydf.copy(deep=True)
        nullify_non_alphanum(mydf, ['field1', 'field3'])

        expected = pd.DataFrame({'field1': ['1', np.nan, '2', '2', np.nan, '3'],
                             'field2': ['y', 'y', np.nan, '. .', 'z', 'a'],
                             'field3': ['1dfasdfa!', 1, 'a', '1 . 2', np.nan, np.nan]})

        assert_frame_equal(mydf, expected)

class TestCsvCleaning_NullifyFieldsIfFieldMatchesPattern(unittest.TestCase):
    def setUp(self):
        self.mydf = pd.DataFrame({'field1': ['hello', 'hello1', 'dontstop', 'why', 'HELLO', '3'],
                             'field2': ['y', 'y', np.nan, '. .', 'z', 'a'],
                             'field3': ['1dfasdfa!', 1, 'a', '1 . 2', '.|', np.nan]})

    def test_nullifies_two_different_fields(self):
        mydf = self.mydf.copy(deep=True)
        pattern = 'hello'

        expected = pd.DataFrame({'field1': ['hello', 'hello1', 'dontstop', 'why', 'HELLO', '3'],
                             'field2': [np.nan, np.nan, np.nan, '. .', np.nan, 'a'],
                             'field3': [np.nan, np.nan, 'a', '1 . 2', np.nan, np.nan]})

        nullify_fields_if_field_matches_pattern(mydf, 'field1', pattern, ['field2', 'field3'], case_sensitive=False)

        assert_series_equal(expected['field1'], mydf['field1'])
        assert_series_equal(expected['field2'], mydf['field2'])
        assert_series_equal(expected['field3'], mydf['field3'])

    def test_nullifies_same_field(self):
        mydf = self.mydf.copy(deep=True)
        pattern = 'hello'

        expected = pd.DataFrame({'field1': [np.nan, np.nan, 'dontstop', 'why', np.nan, '3'],
                             'field2': ['y', 'y', np.nan, '. .', 'z', 'a'],
                             'field3': ['1dfasdfa!', 1, 'a', '1 . 2', '.|', np.nan]})

        nullify_fields_if_field_matches_pattern(mydf, 'field1', pattern, ['field1'], case_sensitive=False)

        assert_series_equal(expected['field1'], mydf['field1'])
        assert_series_equal(expected['field2'], mydf['field2'])
        assert_series_equal(expected['field3'], mydf['field3'])

    def test_doesnt_nullify_anything(self):
        mydf = self.mydf.copy(deep=True)
        pattern = 'hello there'

        expected = pd.DataFrame({'field1': ['hello', 'hello1', 'dontstop', 'why', 'HELLO', '3']})

        nullify_fields_if_field_matches_pattern(mydf, 'field1', pattern, ['field1'], case_sensitive=False)

        assert_series_equal(expected['field1'], mydf['field1'])