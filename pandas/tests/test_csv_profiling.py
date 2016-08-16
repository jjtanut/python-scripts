import unittest
import pandas as pd
import numpy as np
from utilities.csv_profiling import profile_uniques

class TestCsvProfiling(unittest.TestCase):
    # need to test on dataframes with numbers in values
    # need to add case insensitive option

    def test_profiling_works_for_strings_and_NaNs(self):
        mydf = pd.DataFrame({'key': ['1', '1', '2', '2', '2', '3'],
                      'field1': ['y', 'y', np.nan, 'x', 'z', 'a'],
                      'field2': ['y', 'z', 'a', 'a', 'a', np.nan]})

        expected = [{'field': 'field1', 'avg_uniques': 1.3333333333333333, 'min_uniques': 1, 'max_uniques': 2},
                    {'field': 'field2', 'avg_uniques': 1.0, 'min_uniques': 0, 'max_uniques': 2}]

        result = profile_uniques(mydf, 'key', ['field1', 'field2'], outfile=None)

        self.assertListEqual(result, expected)

