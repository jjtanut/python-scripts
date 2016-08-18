import unittest
import pandas as pd
import numpy as np
from pandas.util.testing import assert_frame_equal

from utilities.csv_cleaning import nullify_non_alphanum

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
