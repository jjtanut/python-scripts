from phonenumbers import phonenumberutil
import numpy as np
import pandas as pd

""" Wrapper functions around Python port of Google Phone Number Library to work across dataframes """


# values ignored for validation and cleaning.
IGNORED_VALUES = [None, np.nan]

def print_supported_regions():
    """
    print to stdout a list of supported region code abbreviations
    :return:
    """
    print(phonenumberutil.SUPPORTED_REGIONS)

def clean_phone_numbers(dataframe, phonenum_field, newField=None, region_string=None, region_field=None,
                use_orig_on_error=False):
    """
    Uses python port of Google PhoneNumLib to clean and format phone numbers within a dataframe
    see: https://github.com/daviddrysdale/python-phonenumbers

    :param dataframe: input dataframe that will be transformed
    :param phonenum_field: name of field that contains phone numbers to be verified/cleaned
    :param newField: optional parameter that specifies name of the field that should hold the existing phone numbers.
    If not specified, phone number will be cleaned in place. newField will be created if it does not exist.
    :param region_string: if not specified, then region abbreviation (e.g., 'US', 'CA') must be specified in region field.
            Otherwise, setting this sets the region that will be used to validate phone nums for all records.
    :param region_field: field in which country codes are specified. Note that these must be valid region codes supported
    in the phone number library. If both region_field and region_string are provided, it will attempt to use the region_field first,
    and if that fails, fall back on the region_string
    :param use_orig_on_error: what to do if an exception is encountered for that record. If true, paste the original record's value.
    If false, nullify value.
    :return: None (modifies orig data frame)
    """

    if (region_string is None and region_field is None):
        raise ValueError(
            "either country_code_string or country_code_field must be specified so phone validator knows what country to use.")

    if (region_string is not None and region_field is not None):
        print("Both country_code_field and country_code_string are specified, "
              "so if no valid region code is found, will default to the region_string")
        category = 'both_string_and_field'

        regions_list = dataframe[region_field].unique().tolist()
        regions_list.remove(np.nan)
        regions = set(regions_list)
        regions.add(region_string)
    elif (region_string is not None and region_field is None):
        category = 'only_region_string'

        regions = set([region_string])
    elif (region_string is None and region_field is not None):
        category = "only_region_field"

        regions_list = dataframe[region_field].unique().tolist()
        regions_list.remove(np.nan)
        regions = set(regions_list)

    # verify that all specified regions are supported. Note that this does not fix any incorrect casings in the orig data
    is_valid_regions, list_of_invalid_regions = _regions_are_supported(regions)
    if not is_valid_regions:
        raise ValueError('Your following specified regions are not supported: ' + str(list_of_invalid_regions))

    # if newField is specified, check if it already exists in dataframe. If not, initialize it.
    _initialize_col_if_not_present(dataframe, newField)

    # now iterate through rows and clean phone numbers
    _clean_phone_for_rows(dataframe=dataframe, phonenum_field=phonenum_field, newField=newField,
                          region_string=region_string, region_field=region_field, use_orig_on_error=use_orig_on_error,
                          category=category)

def _initialize_col_if_not_present(dataframe, newField):
    """
    Initialize column with all NaN values if it does not already exist in dataframe
    :param dataframe:
    :param newField: name of new field
    :return: None (modifies input dataframe in place)
    """
    if newField not in dataframe.columns.values.tolist() and newField not in IGNORED_VALUES:
        dataframe[newField] = np.nan


def _clean_phone_for_rows(dataframe, phonenum_field, newField, region_string, region_field, use_orig_on_error, category):
    """
    Called by main function to iterate through phone number elements and clean them one by one.
    Assumes region values have already been validated as supported region abbreviations.
    :param dataframe:
    :param phonenum_field:
    :param newField:
    :param region_string:
    :param region_field:
    :param use_orig_on_error:
    :param category:
    :return:
    """

    if not dataframe[phonenum_field].index.is_unique:
        raise IndexError('indexes/keys in dataframe must be unique per row for this function to work correctly!')

    NULL_VALUES = IGNORED_VALUES   # null values that will be ignored

    # looping through elements because phone num library doesn't allow bulk validation
    for idx, value in dataframe[phonenum_field].iteritems():
        # for trivial null cases, don't attempt to parse phonenum and just continue to next value
        if value in NULL_VALUES:
            # in the future, might want to add some logic here to update the other field. For now, don't do anything
            pass
        else:
            # set region to appropriate specified string, or string specified in a specific column-row
            if category == 'both_string_and_field':
                if dataframe[region_field][idx] not in NULL_VALUES:
                    region = str(dataframe[region_field][idx])
                else:
                    region = region_string
            elif category == 'only_region_field':
                if dataframe[region_field][idx] not in NULL_VALUES:
                    region = str(dataframe[region_field][idx])
                else:
                    region = None
            else:
                region = region_string

            # validate/format phone number, or nullify value as NaN
            try:
                # parse will raise an exception if value doesn't seem to be a phone number, so need to use a try block
                phonenum = phonenumberutil.parse(str(value), region=region, keep_raw_input=False,
                                              numobj=None, _check_region=True)

                # update with validated, formatted phone number, or nullify as NaN
                if phonenumberutil.is_valid_number_for_region(phonenum, region):
                    _update_element(dataframe=dataframe, phonenum_field=phonenum_field, newField=newField,
                                    index=idx, replacement_value=phonenum.national_number)
                else:
                    _update_element(dataframe=dataframe, phonenum_field=phonenum_field, newField=newField,
                                    index=idx, replacement_value=np.nan)
            except:
                # update value as NaN or paste original value
                if use_orig_on_error:
                    _update_element(dataframe=dataframe, phonenum_field=phonenum_field, newField=newField,
                                    index=idx, replacement_value=dataframe[phonenum_field][idx])
                else:
                    _update_element(dataframe=dataframe, phonenum_field=phonenum_field, newField=newField,
                                    index=idx, replacement_value=np.nan)

def _update_element(dataframe, phonenum_field, newField, index, replacement_value):
    """ Logic to update newField or update current phone num field"""
    NULL_VALUES = IGNORED_VALUES

    if replacement_value not in NULL_VALUES:
        replacement_value=str(replacement_value)

    if newField is not None:
        # update new field
        dataframe.loc[index:index, (newField)] = replacement_value
    else:
        # in place update on original phone num field
        dataframe.loc[index:index, (phonenum_field)] = replacement_value


def _regions_are_supported(regions):
    """
    Given a set of input region abbreviations, verify that they are supported in the phone number library. If not, return
    a set of region abbreviations that are not supported.
    :param regions: set of region codes
    :return: (boolean, set): boolean is true if all regions are supported region names in phone number library.
    Otherwise will return a set of elements that are not allowed regions.
    """
    supported_regions = phonenumberutil.SUPPORTED_REGIONS

    # ignore any null values from consideration
    regions = regions.difference(IGNORED_VALUES)

    is_supported = regions.issubset(supported_regions)

    if not is_supported:
        return is_supported, regions.difference(supported_regions)
    else:
        return is_supported, None