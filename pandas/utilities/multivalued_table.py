import pandas as pd
import numpy as np
import csv

class MultivaluedTable(object):
    """
    This is a static method class. These MultivaluedTable methods are useful when rows in the original DataFrame may
    not have unique keys within a specified key field, and you need to profile and restructure the DataFrame to contain
    unique keys per row, transforming any multivalued attributes as necessary. You may have such a dataset
    when someone gives you a denormalized csv created by joining several database tables, for example.
    """
    def __init__(self):
        """
        """

    @staticmethod
    def _generate_unique_key_dataframe(orig_dataframe, keyfield):
        """ generates a new dataframe containing only unique keys. This will be the base dataframe for
        merging additional columns containing widened attributes """

        df_by_unique_key = pd.DataFrame()
        df_by_unique_key[keyfield] = orig_dataframe[keyfield].unique()

        return df_by_unique_key.set_index(keyfield)

    @staticmethod
    def profile_uniques(dataframe, keyfield, fields_to_profile, casesensitive=False, outfile=None, debug_multiple_uniques=False):
        """
        Analyzes the max, min, and average number of unique values in a csv around a key field, grouped by each field
        specified in the input. (NaNs are not counted as values). Outputs these results to a csv if desired.

        :param keyfield: string representing the column name of key column
        :param fields_to_profile: list of fieldnames identifying fields to provile
        :param casesensitive: currently does not do anything
        :param outfile: path and name of file to write results to
        :param debug_print_uniques: set to True to print out a list of uniques for all records that have >1 unique value
        :return: a nested dictionary {"fieldname1": {"max_uniques": 1, ... }, "fieldname2": {...} }
        """

        # initializing dictwriter headers and list to hold dict objects
        header = ["field", "max_uniques", "avg_uniques", "min_uniques"]
        all_field_stats = dict()

        for field in fields_to_profile:
            # Equivalent to: SELECT keyfield, COUNT(distinct field) FROM table GROUP BY keyfield
            count_by_key = dataframe.groupby(keyfield)[field].nunique()

            # if user wants to debug, print output to stdout
            if debug_multiple_uniques:
                uniques = dataframe.groupby(keyfield)[field].unique()
                for idx, value in count_by_key.iteritems():
                    if value>1: print("recordKey: " + str(idx) + ", values: " + str(uniques[idx]))

            fieldstats = {"max_uniques": count_by_key.max(),
                          "avg_uniques": count_by_key.mean(),
                          "min_uniques": count_by_key.min()}
            all_field_stats[field] = fieldstats

            del fieldstats, count_by_key

        if outfile is not None:
            # write results to an output file, overwriting any existing data
            print("writing to outfile at location: " + str(outfile))
            with open(outfile, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=header)
                writer.writeheader()
                for key in all_field_stats:
                    writer.writerow({"field": key,
                                     "max_uniques": all_field_stats[key]["max_uniques"],
                                     "avg_uniques": all_field_stats[key]["avg_uniques"],
                                     "min_uniques": all_field_stats[key]["min_uniques"]})

        return all_field_stats

    @staticmethod
    def widen_multivalues_into_additional_columns(orig_dataframe, keyfield, fields, limit=10):
        """ Profiles and then expands columns up to the specified limit, appending additional columns to the
        original dataset as necessary to accommodate multi-valued attributes

        :param fields: list of fieldnames to be widened
        """

        # profile the fields to determine max uniques by key. If max is 1 then is trivial
        uniques_profile_stats = MultivaluedTable.profile_uniques(orig_dataframe, keyfield, fields)

        # initialize dataframe that holds only unique entity ids, which will be merged to create final dataframe
        entity_ids = MultivaluedTable._generate_unique_key_dataframe(orig_dataframe, keyfield)

        merged_dataframe = entity_ids.copy(deep=True)

        for field in fields:
            # trivial case of there being only one unique value or no unique values per key
            if uniques_profile_stats[field]['max_uniques'] <= 1:
                df_to_join = MultivaluedTable._unique_valued_field(orig_dataframe, keyfield, field)
            else:
                df_to_join = MultivaluedTable._widen_one_field(orig_dataframe, keyfield, field, uniques_profile_stats, limit)

            # now merge (join) to uniques table
            merged_dataframe = merged_dataframe.merge(df_to_join, left_index=True, right_index=True, how='left')

        return merged_dataframe

    @staticmethod
    def _unique_valued_field(orig_dataframe, keyfield, field):
        """
        returns a 2 column dataframe of keyfield (as index) and the field to be used. Works if field is empty, defined
         as there only being NaNs for all values
        :param field:
        :return: a two-column dataframe consisting of deduplicated keys and values, with keys set as dataframe index
        """
        new_df = orig_dataframe[[keyfield, field]].dropna().drop_duplicates(subset=[keyfield, field]).set_index(keyfield)
        return new_df

    @staticmethod
    def _widen_one_field(orig_dataframe, keyfield, field, uniques_profile_stats, limit=10):
        """
        Not very efficient, but does the job for now, especially since pandas pivot has bugs
        :param dataframe:
        :param keyfield:
        :param field:
        :param limit:
        :return: dataframe with key field values as indexes and columns expanded
        """

        max_uniques = uniques_profile_stats[field]['max_uniques']

        uniques_by_key = orig_dataframe.groupby(keyfield)[field].unique()
        num_uniques_by_key = orig_dataframe.groupby(keyfield)[field].nunique()

        # create a series for each possible value up to the max num of uniques or the limit. These will represent
        # the additional columns used to hold multi-values
        max_columns = min(max_uniques, limit)
        values_by_col = {}  # initialize an empty list that will hold dictionaries which will be converted to series
        for i in range(0, max_columns):
            if i == 0:
                fieldname = field
            else:
                fieldname = field + "_" + str(i)

            values_by_col[fieldname] = {}  # initialize empty dicts, each dict will have unique series keys as its keys

        for idx, val in uniques_by_key.iteritems():
            # remove NaNs from consideration within each array of unique values when populating columns
            # otherwise you can get NaNs populated first instead of actual values
            # numpy arrays don't do well with object data types, so hacky conversion to list of strings for now
            unique_values= [x for x in val.astype('str').tolist() if x != 'nan']

            for i in range(0, max_columns):
                if i == 0:
                    fieldname = field
                else:
                    fieldname = field + "_" + str(i)

                if i < num_uniques_by_key[idx]:
                    values_by_col[fieldname][idx] = unique_values[i]
                else:
                    values_by_col[fieldname][idx] = np.nan

        new_df = pd.DataFrame(values_by_col)
        new_df.index.name = keyfield    # set index name

        return new_df