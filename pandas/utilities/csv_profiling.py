import pandas as pd
import numpy as np
import csv

def profile_uniques(dataframe, keyfield, fields_to_profile, casesensitive=False, outfile=None):
    """
    Analyzes the max, min, and average number of unique values in a csv around a key field, grouped by each field
    specified in the input. (NaNs are not counted as values)
    :param keyfield: string representing the column name of key column
    :param fields_to_profile: list of fieldnames identifying fields to provile
    :param casesensitive: currently does not do anything
    :param outfile: path and name of file to write results to
    :return: list of dicts representing stats by field
    """

    # initializing dictwriter headers and list to hold dict objects
    header = ["field", "max_uniques", "avg_uniques", "min_uniques"]
    all_field_stats = []


    for field in fields_to_profile:
        # Equivalent to: SELECT keyfield, COUNT(distinct field) FROM table GROUP BY keyfield
        count_by_key = dataframe.groupby(keyfield)[field].nunique()
        fieldstats = {"field": field,
                      "max_uniques": count_by_key.max(),
                      "avg_uniques": count_by_key.mean(),
                      "min_uniques": count_by_key.min()}
        all_field_stats.append(fieldstats)

        del fieldstats, count_by_key

    if outfile is not None:
        # write results to an output file, overwriting any existing data
        print("write to outfile")
        with open(outfile, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            writer.writeheader()
            for row in all_field_stats:
                writer.writerow(row)

    return all_field_stats




