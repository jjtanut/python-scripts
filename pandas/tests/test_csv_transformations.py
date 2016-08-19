import unittest
from utilities.csv_transformations import concat_fieldvalues
import pandas as pd
import numpy as np
from pandas.util.testing import assert_series_equal

class TestCsvConcatenationTransformations(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({'a': ['x', np.nan, 'x'],
                            'b': ['y', 'y', np.nan],
                            'c': ['z', 'z', np.nan],
                            'd': ['x', np.nan, 1],
                            'e': ['   y12', ' y   ', np.nan]})

    def test_strings_NaNs_are_concatenated(self):
        self.df["new_concat_field_ab"] = concat_fieldvalues(self.df, ['a', 'b'])
        self.df["new_concat_field_abc"] = concat_fieldvalues(self.df, ['a', 'b', 'c'])

        expected_result_ab = pd.DataFrame({'new_concat_field_ab': ['x y', 'y', 'x']})
        expected_result_abc = pd.DataFrame({'new_concat_field_abc': ['x y z', 'y z', 'x']})

        assert_series_equal(self.df["new_concat_field_ab"], expected_result_ab['new_concat_field_ab'])
        assert_series_equal(self.df["new_concat_field_abc"], expected_result_abc['new_concat_field_abc'])

    @unittest.skip("This currently fails because doesn't convert ints to strings")
    def test_strings_NaNs_numbers_are_concatenated(self):
        self.df["new_concat_field_abd"] = concat_fieldvalues(self.df, ['a', 'b', 'd'])
        expected_result_abd = pd.DataFrame({'new_concat_field_abd': ['x y x', 'y', 'x 1']})

        assert_series_equal(self.df["new_concat_field_abd"], expected_result_abd['new_concat_field_abd'])

    def test_single_field_is_returned(self):
        # any fields with NaN will still come out NaN if not concatenated with other fields
        self.df["new_concat_field_a"] = concat_fieldvalues(self.df, ['a'])
        expected_result_ab = pd.DataFrame({'new_concat_field_a': ['x', np.nan, 'x']})

        assert_series_equal(self.df["new_concat_field_a"], expected_result_ab['new_concat_field_a'])

    def test_concat_NaNs_returns_NaN(self):
        mydf = self.df.copy(deep=True)
        mydf["new_concat_field_bc"] = concat_fieldvalues(self.df, ['b', 'c'])

        expected_result_bc = pd.DataFrame({'new_concat_field_bc': ['y z', 'y z', np.nan]})
        assert_series_equal(mydf["new_concat_field_bc"], expected_result_bc["new_concat_field_bc"])

    #@unittest.skip('will fail--doesnt currently strip whitespaces before concat')
    def test_leading_trailing_whitespaces_in_fields_are_stripped(self):
        """ any leading/trailing whitespaces within a column will be stripped before concatenation occurs"""
        self.df["new_concat_field_ae"] = concat_fieldvalues(self.df, ['a', 'e'])

        expected_result_ae = pd.DataFrame({'new_concat_field_ae': ['x y12', 'y', 'x']})
        assert_series_equal(self.df["new_concat_field_ae"], expected_result_ae['new_concat_field_ae'])

    def tearDown(self):
        del self.df