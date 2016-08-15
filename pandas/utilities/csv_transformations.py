import pandas as pd

def concat_fields(mydataframe, fieldnames, separator=' ', nan_substitute=''):
    """
    Concatenates data in fields, handling NaN's gracefully
    Might want to have an option to strip leading/trailing spaces too
    :param fieldname: desired name for generated field containing concatenated data that will be appended to your dataframe
    :param fields: list of fieldnames to be concatenated
    :return: dataframe
    """

    # trivial cases
    if len(fieldnames) <1: raise LookupError('must send in at least one fieldname')
    if len(fieldnames) == 1:
        return mydataframe[fieldnames[0]]

    firstfield = fieldnames[0]
    otherfields = fieldnames[1:]

    mydata = mydataframe[firstfield].str.cat(others=[mydataframe[col] for col in otherfields], sep=separator, na_rep=nan_substitute)

    # strip any leading/trailing whitespaces
    mydata = mydata.map(str.strip)
    return mydata