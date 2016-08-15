import unittest
from utilities.csv_transformations import concat_fields
import pandas as pd
import numpy as np
from pandas.util.testing import assert_series_equal

class TestCsvConcatenationTransformations(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({'a': ['x', np.nan, 'x'],
                            'b': ['y', 'y', np.nan],
                            'c': ['z', 'z', np.nan],
                            'd': ['x', np.nan, 1]})

    def test_strings_NaNs_are_concatenated(self):
        self.df["new_concat_field_ab"] = concat_fields(self.df, ['a','b'])
        self.df["new_concat_field_abc"] = concat_fields(self.df, ['a', 'b', 'c'])

        expected_result_ab = pd.DataFrame({'new_concat_field_ab': ['x y', 'y', 'x']})
        expected_result_abc = pd.DataFrame({'new_concat_field_abc': ['x y z', 'y z', 'x']})

        assert_series_equal(self.df["new_concat_field_ab"], expected_result_ab['new_concat_field_ab'])
        assert_series_equal(self.df["new_concat_field_abc"], expected_result_abc['new_concat_field_abc'])

    @unittest.skip("This currently fails because doesn't convert ints to strings")
    def test_strings_NaNs_numbers_are_concatenated(self):
        self.df["new_concat_field_abd"] = concat_fields(self.df, ['a', 'b', 'd'])
        expected_result_abd = pd.DataFrame({'new_concat_field_abd': ['x y x', 'y', 'x 1']})

        assert_series_equal(self.df["new_concat_field_abd"], expected_result_abd['new_concat_field_abd'])

    def test_single_field_is_returned(self):
        # any fields with NaN will still come out NaN if not concatenated with other fields
        self.df["new_concat_field_a"] = concat_fields(self.df, ['a'])
        expected_result_ab = pd.DataFrame({'new_concat_field_a': ['x', np.nan, 'x']})

        assert_series_equal(self.df["new_concat_field_a"], expected_result_ab['new_concat_field_a'])

    @unittest.skip("not implemented")
    def test_leading_trailing_whitespaces_in_fields_are_stripped(self):
        """ should currently fail if there are leading/trailing whitespaces in any single column and you expect these to be stripped out"""


    def tearDown(self):
        del self.df

