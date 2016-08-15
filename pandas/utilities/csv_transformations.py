import pandas as pd

def concat_fieldvalues(mydataframe, fieldnames, separator=' ', nan_substitute=''):
    """
    Concatenates data values across one or more fields (note: data to be concatenated must be the same type),
    with separator. Handles NaN's gracefully.

    :param mydataframe: dataframe containing data to be concatenated
    :param fieldnames: list of fieldnames to be concatenated
    :param separator: separator to be used. Default separator is single whitespace
    :param nan_substitute: character to be substituted for NaNs. Default is blank space.
    :return: dataframe
    """

    # trivial cases
    if len(fieldnames) <1: raise IOError('must designate at least one field to be concatenated')
    if len(fieldnames) == 1:
        return mydataframe[fieldnames[0]]

    firstfield = fieldnames[0]
    otherfields = fieldnames[1:]

    mydata = mydataframe[firstfield].str.cat(others=[mydataframe[col].str.strip() for col in otherfields], sep=separator, na_rep=nan_substitute)

    # strip any leading/trailing whitespaces
    mydata = mydata.map(str.strip)
    return mydata