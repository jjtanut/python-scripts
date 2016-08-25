import unittest
import pandas as pd
import numpy as np
from pandas.util.testing import assert_frame_equal, assert_series_equal

#add parent directory into search path
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__)) #current directory of the python script
sys.path.append(os.path.join(script_dir,os.pardir))

from utilities.multivalued_table import MultivaluedTable

class TestMultivaluedTableProfiling(unittest.TestCase):
    # need to test on dataframes with numbers in values
    # need to add case insensitive option
    def setUp(self):
        self.mydf = pd.DataFrame({'key': ['1', '1', '2', '2', '2', '3'],
                      'field1': ['y', 'y', np.nan, 'x', 'z', 'a'],
                      'field2': ['y', 'z', 'a', 'a', 'a', np.nan]})

    def test_profiling_works_for_strings_and_NaNs(self):
        mydf = self.mydf.copy(deep=True)

        expected = {'field1': {'min_uniques': 1, 'max_uniques': 2, 'avg_uniques': 1.3333333333333333},
                    'field2': {'min_uniques': 0, 'max_uniques': 2, 'avg_uniques': 1.0}}

        result = MultivaluedTable.profile_uniques(mydf, 'key', ['field1', 'field2'], outfile=None)

        self.assertEqual(result, expected)

    @unittest.skip("Need to implement testing output file")
    def test_write_to_output_file(self):
        mydf = self.mydf.copy(deep=True)

        result = MultivaluedTable.profile_uniquesprofile_uniques(mydf, 'key', ['field1', 'field2'], outfile='testfile.csv')

class TestMultivaluedTableWidening(unittest.TestCase):
    def setUp(self):
        self.mydf = pd.DataFrame({'key': ['aa', 'aa', 'bb', 'bb', 'bb', 'bb', 'cc', 'dd', 'ee'],
                      'field1': ['y', 'y', np.nan, 'x', 'y', 'xy', 'z', 'a', np.nan],
                      'field2': ['y', 'z', 'a', 'a', 'a', 'cc', np.nan, np.nan, np.nan],
                      'unique_vals': ['1', '1', '2', '2', '2', '2', '3', '4', np.nan]})

        self.uniques_profile_stats = MultivaluedTable.profile_uniques(self.mydf, 'key',
                                                                        ['field1', 'field2', 'unique_vals'],
                                                                        outfile=None)

    def test_generate_unique_key_dataframe(self):
        mydf = self.mydf.copy(deep=True)

        result = MultivaluedTable._generate_unique_key_dataframe(mydf, 'key')

        expected = pd.DataFrame([{'key': 'aa'},
                                 {'key': 'bb'},
                                 {'key': 'cc'},
                                 {'key': 'dd'},
                                 {'key': 'ee'}]).set_index('key')

        assert_frame_equal(result, expected)


    def test_unique_valued_field_works(self):
        """ ensure that a unique valued field returns a deduplicated dataframe. Fields containing only NaNs will not appear
         in the resulting dataframe """
        mydf = self.mydf.copy(deep=True)

        result = MultivaluedTable._unique_valued_field(mydf, 'key', 'unique_vals')

        expected = pd.DataFrame([{'key': 'aa', 'unique_vals': '1'},
                                 {'key': 'bb', 'unique_vals': '2'},
                                 {'key': 'cc', 'unique_vals': '3'},
                                 {'key': 'dd', 'unique_vals': '4'}]).set_index('key')

        assert_frame_equal(result, expected)

    def test_unique_valued_field_works_field_with_value_and_nan(self):
        """ Logic used in counting the max number of uniques by key will say a field has only 1 max unique if possible value
        for each key is a value and one or more NaNs. However, running pandas drop_duplicates will still retain these
        as 2 possible rows, so we drop all NaNs before running drop duplicates. Verify that this is the behavior """
        mydf = pd.DataFrame({'key': ['aa', 'aa', 'bb', 'bb', 'bb', 'bb', 'cc', 'dd', 'ee', 'ee'],
                             'field1': ['y', 'y', np.nan, 'x', 'y', 'xy', 'z', 'a', np.nan, np.nan],
                             'field2': ['y', 'z', 'a', 'a', 'a', 'cc', np.nan, np.nan, np.nan, np.nan],
                             'unique_vals': ['1', '1', '2', '2', '2', '2', '3', '4', np.nan, 'myvalue']})

        result = MultivaluedTable._unique_valued_field(mydf, 'key', 'unique_vals')

        expected = pd.DataFrame([{'key': 'aa', 'unique_vals': '1'},
                                 {'key': 'bb', 'unique_vals': '2'},
                                 {'key': 'cc', 'unique_vals': '3'},
                                 {'key': 'dd', 'unique_vals': '4'},
                                 {'key': 'ee', 'unique_vals': 'myvalue'}]).set_index('key')
        assert_frame_equal(result, expected)


    def test_widen_one_field_default_limits(self):
        """ ensure that a dataframe for a field with multivalued attributes returns the correct multi-column output,
        with and without limits """
        mydf = self.mydf.copy(deep=True)

        result = MultivaluedTable._widen_one_field(mydf, 'key', 'field1', self.uniques_profile_stats)

        expected = pd.DataFrame([{'key': 'aa', 'field1': 'y', 'field1_1': np.nan, 'field1_2': np.nan},
                                 {'key': 'bb', 'field1': 'x', 'field1_1': 'y', 'field1_2': 'xy'},
                                 {'key': 'cc', 'field1': 'z', 'field1_1': np.nan, 'field1_2': np.nan},
                                 {'key': 'dd', 'field1': 'a', 'field1_1': np.nan, 'field1_2': np.nan},
                                 {'key': 'ee', 'field1': np.nan, 'field1_1': np.nan, 'field1_2': np.nan}]).set_index('key')

        assert_frame_equal(result, expected)


    def test_widen_one_field_default_limit_2cols(self):
        """
        sample df has max of 3 columns, but you can limit it to output less than the max number of values per attribute
        in the dataset. This tests when you set limit to only have 2 columns instead of 3
        :return:
        """
        mydf = self.mydf.copy(deep=True)

        result = MultivaluedTable._widen_one_field(mydf, 'key', 'field1', self.uniques_profile_stats, limit=2)

        expected = pd.DataFrame([{'key': 'aa', 'field1': 'y', 'field1_1': np.nan},
                                 {'key': 'bb', 'field1': 'x', 'field1_1': 'y'},
                                 {'key': 'cc', 'field1': 'z', 'field1_1': np.nan},
                                 {'key': 'dd', 'field1': 'a', 'field1_1': np.nan},
                                 {'key': 'ee', 'field1': np.nan, 'field1_1': np.nan}]).set_index('key')

        assert_frame_equal(result, expected)

    def test_widen_multivalues_into_additional_columns(self):
        mydf = self.mydf.copy(deep=True)

        result = MultivaluedTable.widen_multivalues_into_additional_columns(mydf, 'key', ['field1', 'field2', 'unique_vals'])

        expected = pd.DataFrame([{'key': 'aa', 'field1': 'y', 'field1_1': np.nan, 'field1_2': np.nan, 'field2': 'y', 'field2_1': 'z', 'unique_vals': '1'},
                                 {'key': 'bb', 'field1': 'x', 'field1_1': 'y', 'field1_2': 'xy', 'field2': 'a', 'field2_1': 'cc', 'unique_vals': '2'},
                                 {'key': 'cc', 'field1': 'z', 'field1_1': np.nan, 'field1_2': np.nan, 'field2': np.nan, 'field2_1': np.nan, 'unique_vals': '3'},
                                 {'key': 'dd', 'field1': 'a', 'field1_1': np.nan, 'field1_2': np.nan, 'field2': np.nan, 'field2_1': np.nan, 'unique_vals': '4'},
                                 {'key': 'ee', 'field1': np.nan, 'field1_1': np.nan, 'field1_2': np.nan, 'field2': np.nan, 'field2_1': np.nan, 'unique_vals': np.nan}]).set_index('key')

        assert_frame_equal(result, expected)

    def test_widen_multivalues_into_additional_columns_for_empty_column(self):
        mydf = self.mydf.copy(deep=True)
        mydf['empty_field'] = np.nan

        result = MultivaluedTable.widen_multivalues_into_additional_columns(mydf, 'key',
                                                                            ['field1', 'field2', 'unique_vals', 'empty_field'])

        expected = pd.DataFrame([{'key': 'aa', 'field1': 'y', 'field1_1': np.nan, 'field1_2': np.nan, 'field2': 'y', 'field2_1': 'z', 'unique_vals': '1', 'empty_field': np.nan},
                                 {'key': 'bb', 'field1': 'x', 'field1_1': 'y', 'field1_2': 'xy', 'field2': 'a', 'field2_1': 'cc', 'unique_vals': '2', 'empty_field': np.nan},
                                 {'key': 'cc', 'field1': 'z', 'field1_1': np.nan, 'field1_2': np.nan, 'field2': np.nan, 'field2_1': np.nan, 'unique_vals': '3', 'empty_field': np.nan},
                                 {'key': 'dd', 'field1': 'a', 'field1_1': np.nan, 'field1_2': np.nan, 'field2': np.nan, 'field2_1': np.nan, 'unique_vals': '4', 'empty_field': np.nan},
                                 {'key': 'ee', 'field1': np.nan, 'field1_1': np.nan, 'field1_2': np.nan, 'field2': np.nan, 'field2_1': np.nan, 'unique_vals': np.nan, 'empty_field': np.nan},]).set_index('key')

        assert_series_equal(result['field1'], expected['field1'])
        assert_series_equal(result['empty_field'], expected['empty_field'])
