import numpy as np

def nullify_non_alphanum(dataframe, fields=None):
    """
    Nullify in place any values that have no alphanumeric characters (note: does not take into account latin chars.
    Nullified values are converted to NaNs.

    :param dataframe:
    :param fields: optional list of fieldnames to be nullified. If not specified, runs across entire dataset.
    :return:
    """

    if fields is None:
        dataframe.replace({r'^[^a-zA-Z0-9]*$': np.nan}, regex=True, inplace=True)
    else:
        # TODO: there's probably a more efficient way to do this than looping through each field
        for field in fields:
            dataframe[field].replace({r'^[^a-zA-Z0-9]*$': np.nan}, regex=True, inplace=True)

def nullify_fields_if_field_matches_pattern(dataframe, field_containing_pattern, pattern, fields_to_nullify, case_sensitive=False):
    """
    Can be used to nullify one or more fields if another field matches a certain pattern.
    Can also be used to nullify values in one field if values in that field match a certain pattern (i.e., blacklisting values)
    Note: Keys must be unique by row; otherwise will not work correctly
    :param dataframe:
    :param field_containing_pattern:
    :param fields_to_nullify: list of fieldnames specifying the fields to nullify. Can nullify the same field (i.e., blacklist)
    :param case_sensitive: whether matching is case sensitive or not. Default is False (i.e., not case sensitive)
    :return: None (nullifies the dataframe in place)
    """
    rows_that_contain = dataframe[field_containing_pattern].str.contains(pattern, case=case_sensitive)

    if not rows_that_contain.index.is_unique:
        raise IndexError("indexes in dataframe must be unique")

    # store indexes of rows that match pattern in a list to be used for locating elements to update
    # TODO: there is likely a more pandas-efficient way to do this (via slices, etc) instead of O(n) iteration
    indexes_for_match = []
    for idx, row in rows_that_contain.iteritems():
        if row == True:     # because of numpy quirk, must use == instead of "is True" for boolean
            indexes_for_match.append(idx)

    for field in fields_to_nullify:
        dataframe.loc[indexes_for_match, (field)] = np.nan


def blacklist_values():
    raise NotImplemented()

def nullify_regex():
    raise NotImplemented()

