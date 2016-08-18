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


def blacklist_values():
    raise NotImplemented()

def nullify_regex():
    raise NotImplemented()

