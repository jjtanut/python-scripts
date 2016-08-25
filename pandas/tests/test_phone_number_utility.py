import unittest
import pandas as pd
import numpy as np
from pandas.util.testing import assert_frame_equal, assert_series_equal

#add parent directory into search path
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__)) #current directory of the python script
sys.path.append(os.path.join(script_dir,os.pardir))

from utilities.phone_number_utility import _regions_are_supported, clean_phone_numbers

class TestPhoneRegions(unittest.TestCase):

    def test_regions_are_supported_valid_inputs(self):
        """
        verify that valid regions are handled correctly
        """
        myregions = set(['MZ', 'TW', 'US'])

        supported, incorrect_values = _regions_are_supported(myregions)

        self.assertTrue(supported)
        self.assertIsNone(incorrect_values)

    def test_regions_are_supported_valid_inputs_with_nulls(self):
        """
        verify that invalid regions return False and return the set of invalid regions
        """
        myregions = set(['MZ', 'TW', 'US', None, np.nan])

        supported, incorrect_values = _regions_are_supported(myregions)

        self.assertTrue(supported)
        self.assertIsNone(incorrect_values)

    def test_regions_are_supported_invalid_lowercase_inputs(self):
        # Currently, lowercase region abbreviations are not handled so they will be detected as invalid inputs
        myregions = set(['MZ', 'tw', 'us'])

        expected_incorrect_values = set(['tw', 'us'])

        supported, incorrect_values = _regions_are_supported(myregions)

        self.assertFalse(supported)
        self.assertSetEqual(incorrect_values, expected_incorrect_values)

    def test_regions_are_supported_invalid_uppercase_inputs(self):
        myregions = set(['MZ', 'TW', 'US', 'AZZZZ', '1212'])

        expected_incorrect_values = set(['AZZZZ', '1212'])

        supported, incorrect_values = _regions_are_supported(myregions)

        self.assertFalse(supported)
        self.assertSetEqual(incorrect_values, expected_incorrect_values)

class TestPhoneNumberCleaning(unittest.TestCase):
    def setUp(self):
        # list of [input phone, region country, expected corrected phone]
        self.starbucks_vancouver = ['(604) 264-0954', 'CA', '6042640954']
        self.london_eye_ticketoff = ['+44 (0)871 781 3000', 'GB', '8717813000']
        self.london_eye_ticketoff2 = ['0871 781 3000', 'GB', '8717813000']
        self.boston_mikes_pastry = ['(617) 742-3050', 'US', '6177423050']
        self.starbucks_toronto = ['4165938570', 'CA', '4165938570']
        self.ontario_tim_hortons = ['807 467 8667', 'CA', '8074678667']
        self.madrid_laMallorquina_bakery = ['+34 915 21 12 01', 'ES', '915211201']

        # 8 possible formats for starbucks toronto phone number
        starbucks_toronto_examples = ['416-593-8570', '416-5938570', '416.593.8570', '416-5938570', '416-5938570',
                                    '416-5938570', '4165938570', '416 593 8570']


        self.mydf = pd.DataFrame({'key': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
                     'goodphones': [starbucks_toronto_examples[0], starbucks_toronto_examples[1], starbucks_toronto_examples[2],
                                    starbucks_toronto_examples[3], starbucks_toronto_examples[4], starbucks_toronto_examples[5],
                                    starbucks_toronto_examples[6], starbucks_toronto_examples[7]],
                     'badphones': ['416-593-8570', '4165938570', np.nan, 'BILL_TO', '  ', '', 'SHIP_TO',
                                   'BILL_TO'],
                     'phones_by_country': [self.starbucks_vancouver[0], self.london_eye_ticketoff[0], np.nan, self.boston_mikes_pastry[0],
                                           self.starbucks_toronto[0], self.ontario_tim_hortons[0], self.madrid_laMallorquina_bakery[0],
                                            self.london_eye_ticketoff2[0]],
                     'regions_all_valid': [self.starbucks_vancouver[1], self.london_eye_ticketoff[1], np.nan, self.boston_mikes_pastry[1],
                                           self.starbucks_toronto[1], self.ontario_tim_hortons[1], self.madrid_laMallorquina_bakery[1],
                                            self.london_eye_ticketoff2[1]],
                     'regions_incorrect_missing_codes': [self.starbucks_vancouver[1], 'ABAC', np.nan, self.boston_mikes_pastry[1],
                                           np.nan, self.ontario_tim_hortons[1], self.madrid_laMallorquina_bakery[1],
                                            self.london_eye_ticketoff2[1]],
                     'regions_valid_but_missing_or_invalid_canada': [np.nan, self.london_eye_ticketoff[1], np.nan,
                                                          self.boston_mikes_pastry[1],
                                                          np.nan, 'GB',
                                                          self.madrid_laMallorquina_bakery[1],
                                                          self.london_eye_ticketoff2[1]]
                     }).set_index('key')

        self.mydf_nonuniquekeys = pd.DataFrame({'key': ['a', 'b', 'a', 'd', 'e', 'f', 'g', 'c'],
                     'goodphones': ['416-593-8570', '416-5938570', '416-5938570', '416-5938570', '416-5938570',
                                    '416-5938570', '416-5938570',
                                    '416-5938570']}).set_index('key')

        self.mydf_generatedkeys = pd.DataFrame({'key': ['a', 'b', 'a', 'd', 'e', 'f', 'g', 'c'],
                                                'goodphones': ['416-593-8570', '416-5938570', '416-5938570',
                                                               '416-5938570', '416-5938570',
                                                               '416-5938570', '416-5938570',
                                                               '416-5938570']})

    def test_input_df_works_with_pandas_generated_keys(self):
        # any dataframe with pandas generated keys will work because they are unique
        mydf = self.mydf_generatedkeys.copy(deep=True)
        clean_phone_numbers(mydf, phonenum_field='goodphones', newField='correctedPhones', region_string='CA',
                            region_field=None,
                            use_orig_on_error=False)

    def test_input_df_with_nonuniquekeys_raises_error(self):
        # using a dataframe with nonunique keys should raise an Index exception
        mydf = self.mydf_nonuniquekeys.copy(deep=True)

        self.assertRaises(IndexError, clean_phone_numbers, mydf,
                          phonenum_field='goodphones', region_string='CA', region_field=None, use_orig_on_error=False)

    def test_clean_phone_numbers_all_valid_phonenums_and_put_into_new_field_using_region_string(self):
        orig_mydf = self.mydf
        mydf = self.mydf.copy(deep=True)

        correctedphone = self.starbucks_toronto[2]
        expected = pd.DataFrame({'key': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
                                  'correctedPhones': [correctedphone, correctedphone, correctedphone, correctedphone,
                                                 correctedphone, correctedphone, correctedphone, correctedphone]
                                  }).set_index('key')

        clean_phone_numbers(mydf, phonenum_field='goodphones', newField='correctedPhones', region_string='CA', region_field=None,
                            use_orig_on_error=False)

        # new field should hold formatted + validated phones, orig phone field should not be changed
        assert_series_equal(mydf['correctedPhones'], expected['correctedPhones'])
        assert_series_equal(mydf['goodphones'], orig_mydf['goodphones'])


    def test_clean_phone_numbers_some_bad_phonenums_and_put_into_new_field_using_region_string(self):
        orig_mydf = self.mydf
        mydf = self.mydf.copy(deep=True)

        correctedphone = self.starbucks_toronto[2]
        expected = pd.DataFrame({'key': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
                                  'correctedPhones': [correctedphone, correctedphone, np.nan, np.nan,
                                                 np.nan, np.nan, np.nan, np.nan]
                                  }).set_index('key')

        clean_phone_numbers(mydf, phonenum_field='badphones', newField='correctedPhones', region_string='CA', region_field=None,
                            use_orig_on_error=False)

        # new field should hold formatted + validated phones, orig phone field should not be changed
        assert_series_equal(mydf['correctedPhones'], expected['correctedPhones'])
        assert_series_equal(mydf['goodphones'], orig_mydf['goodphones'])

    def test_clean_phone_numbers_some_bad_phonenums_and_put_into_new_field_using_region_string_use_orig_on_error(self):
        orig_mydf = self.mydf
        mydf = self.mydf.copy(deep=True)

        correctedphone = self.starbucks_toronto[2]
        expected = pd.DataFrame({'key': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
                                  'correctedPhones': [correctedphone, correctedphone, np.nan, 'BILL_TO',
                                                 '  ', '', 'SHIP_TO', 'BILL_TO']
                                  }).set_index('key')

        clean_phone_numbers(mydf, phonenum_field='badphones', newField='correctedPhones', region_string='CA', region_field=None,
                            use_orig_on_error=True)

        # new field should hold formatted + validated phones, orig phone field should not be changed
        assert_series_equal(mydf['correctedPhones'], expected['correctedPhones'])
        assert_series_equal(mydf['goodphones'], orig_mydf['goodphones'])

    def test_clean_phone_numbers_all_valid_phonenums_and_put_into_new_field_using_region_field(self):
        """ Verify that valid phone numbers with valid region codes specified in a region field are
         pasted into a new field when this option is specified """
        orig_mydf = self.mydf
        mydf = self.mydf.copy(deep=True)

        expected = pd.DataFrame({'key': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
                                'correctedPhones': [self.starbucks_vancouver[2], self.london_eye_ticketoff[2], np.nan,
                                                          self.boston_mikes_pastry[2],
                                                          self.starbucks_toronto[2], self.ontario_tim_hortons[2],
                                                          self.madrid_laMallorquina_bakery[2],
                                                          self.london_eye_ticketoff2[2]]
                                 }).set_index('key')

        clean_phone_numbers(mydf, phonenum_field='phones_by_country', newField='correctedPhones', region_field='regions_all_valid',
                            use_orig_on_error=False)

        # new field should hold formatted + validated phones, orig phone field should not be changed
        assert_series_equal(mydf['correctedPhones'], expected['correctedPhones'])
        assert_series_equal(mydf['goodphones'], orig_mydf['goodphones'])

    def test_clean_phone_numbers_all_valid_phonenums_and_replace_orig_field_using_region_field(self):
        """ Verify that valid phone numbers with valid region codes specified in a region field replaces
        the original phone number field's values when this option is specified """
        mydf = self.mydf.copy(deep=True)

        expected = pd.DataFrame({'key': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
                                'phones_by_country': [self.starbucks_vancouver[2], self.london_eye_ticketoff[2], np.nan,
                                                          self.boston_mikes_pastry[2],
                                                          self.starbucks_toronto[2], self.ontario_tim_hortons[2],
                                                          self.madrid_laMallorquina_bakery[2],
                                                          self.london_eye_ticketoff2[2]]
                                 }).set_index('key')

        clean_phone_numbers(mydf, phonenum_field='phones_by_country', region_field='regions_all_valid',
                            use_orig_on_error=False)

        # orig phone number field should hold formatted + validated phones
        assert_series_equal(mydf['phones_by_country'], expected['phones_by_country'])

    def test_clean_phone_numbers_incorrect_region_field_value(self):
        """ Verify that exception is thrown if there are invalid region values within the region field """
        mydf = self.mydf.copy(deep=True)

        expected = pd.DataFrame({'key': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
                                'phones_by_country': [self.starbucks_vancouver[2], self.london_eye_ticketoff[2], np.nan,
                                                          self.boston_mikes_pastry[2],
                                                          self.starbucks_toronto[2], self.ontario_tim_hortons[2],
                                                          self.madrid_laMallorquina_bakery[2],
                                                          self.london_eye_ticketoff2[2]]
                                 }).set_index('key')

        self.assertRaises(ValueError, clean_phone_numbers, mydf,
                        phonenum_field='phones_by_country', region_field='regions_incorrect_missing_codes',
                            use_orig_on_error=False)

    def test_clean_phone_numbers_valid_numbers_but_no_region_field_values_are_nullified(self):
        """ Verify that if number is valid but region field does not have a value for that number or if country is wrong
        (in this case canadian numbers), then phone num library will detect it as invalid """
        orig_mydf = self.mydf
        mydf = self.mydf.copy(deep=True)

        expected = pd.DataFrame({'key': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
                                'correctedPhones': [np.nan, # first element has no country code so not viewed as valid
                                                      self.london_eye_ticketoff[2],
                                                      np.nan, # input phone was NaN
                                                      self.boston_mikes_pastry[2],
                                                      np.nan, # has no country code
                                                      np.nan, # has incorrect country code (GB)
                                                      self.madrid_laMallorquina_bakery[2],
                                                      self.london_eye_ticketoff2[2]]
                                 }).set_index('key')

        clean_phone_numbers(mydf, phonenum_field='phones_by_country', newField='correctedPhones', #region_string='CA',
                            region_field='regions_valid_but_missing_or_invalid_canada', use_orig_on_error=False)

        # new field should hold formatted + validated phones, orig phone field should not be changed
        assert_series_equal(mydf['correctedPhones'], expected['correctedPhones'])
        assert_series_equal(mydf['goodphones'], orig_mydf['goodphones'])

    def test_clean_phone_numbers_valid_numbers_with_incorrect_regionfield_but_correct_region_string(self):
        """ Verify that if number is valid but region field does not have a value for that number or if country is wrong
        (in this case canadian numbers), but you have a fallback default region string, it will still work"""
        orig_mydf = self.mydf
        mydf = self.mydf.copy(deep=True)

        expected = pd.DataFrame({'key': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'],
                                'phones_by_country': [self.starbucks_vancouver[2], # first element has no country code
                                                                    # so would not viewed as valid, except
                                                                    # in this case we specify the default region
                                                      self.london_eye_ticketoff[2],
                                                      np.nan, # input phone was NaN
                                                      self.boston_mikes_pastry[2],
                                                      self.starbucks_toronto[2], # has no country code
                                                                    # so would not viewed as valid, except
                                                                    # in this case we specify the default region
                                                      np.nan, # has incorrect country code (GB) so we wouldn't use the
                                                                # (in this case correct) substitute region_string
                                                      self.madrid_laMallorquina_bakery[2],
                                                      self.london_eye_ticketoff2[2]]
                                 }).set_index('key')

        # replace in place
        clean_phone_numbers(mydf, phonenum_field='phones_by_country', region_string='CA',
                            region_field='regions_valid_but_missing_or_invalid_canada', use_orig_on_error=False)

        # new field should hold formatted + validated phones, orig phone field should not be changed
        assert_series_equal(mydf['phones_by_country'], expected['phones_by_country'])