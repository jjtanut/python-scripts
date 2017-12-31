__author__ = 'junjaytan'

import unittest
import random
import select
from mock import MagicMock, Mock, patch


class TestSequenceFunctions(unittest.TestCase):
    """ A testcase is created by subclassing unittest.TestCase.

    The 3 individual tests are defined with methods that start with the letters
    test. This naming convention informs the test runner about which methods
    represent tests.
    """
    def setUp(self):
        self.seq = range(10)

    def test_shuffle(self):
        # make sure the shuffled sequence does not lose any elements
        random.shuffle(self.seq)
        self.seq.sort()
        self.assertEqual(self.seq, range(10))

        # should raise an exception for an immutable sequence
        self.assertRaises(TypeError, random.shuffle, (1, 2, 3))

    def test_choice(self):
        element = random.choice(self.seq)
        self.assertTrue(element in self.seq)

    def test_sample(self):
        with self.assertRaises(ValueError):
            random.sample(self.seq, 20)
        for element in random.sample(self.seq, 5):
            self.assertTrue(element in self.seq)

    def mock_function(self):
        # Mock out function to return the same value regardless of how many or
        # what args you provide.
        get_merge_rule_from_form = MagicMock(return_value="Majority Rules")
        print get_merge_rule_from_form("300")

    def mock_out_python_module(self):
        # let's assume your script uses a standard or external python module
        # such as uuid (which generates random guids and you're using the uuid1
        # function. You'll need to mock this function out because otherwise its
        # output is randomized.
        # To do this, just prefix the original class with your module name:
        your_script_name.uuid = MagicMock()
        your_script_name.uuid.uuid1 = MagicMock(
            return_value="ac5bb6d4-499c-11e4-a1c8-80e65023571e")


def my_method():
    random.shuffle()


class TestMockInbuiltFunctions(unittest.TestCase):
    @patch('random.shuffle', return_value=Mock())
    def test_it(self, mock_random_shuffle):
        mock_random_shuffle.side_effect = Exception

        with self.assertRaises(Exception):
            my_method()


if __name__ == '__main__':
    unittest.main()
