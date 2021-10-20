'''
Created on Feb 27, 2019

@author: bkroger
'''
import pandas as pd
import numpy as np
from bisect import (bisect_left, bisect_right)

################################################################
# strictly searches for maximum compromise between all binnings
def bifu_c(ntts, xnames_raw):
    return ntts

def bifu_c2  (ntts, used_ts, xnames_raw):
    # ntts ['name_1', 'name_2', 'oldest', 'oldest_index', 'youngest', 'youngest_index', 'ts_count', 'refs', 'rule', 'reference_id', 'reference_year']
    # xnames ['name', 'strat_qualifier', 'ref', 'combi']
    k_reference_id = 9
    k_oldest = 2
    k_oldest_index = 3
    k_youngest = 4
    k_youngest_index = 5
    xk_ref = 2

    i_name = ntts[0, 0]

    xnames_set = xnames_raw
    var_exists = 'xnames_set' in locals()
    # if name also relates to "not specified"
    if var_exists == True:
        # filter for references with "not specified"
        bio_set = ntts[~np.isin(ntts[:, k_reference_id], xnames_set[:, xk_ref])]

    if bio_set.size > 0:
        cpts = bio_set
        # select all references

        # and collect the references which have that opinions
        refs_f = ', '.join(map(str, np.unique(cpts[:, k_reference_id])))

        # youngest, oldest and ts_count
        youngest_value = np.max(cpts[:, k_youngest_index])
        oldest_value = np.min(cpts[:, k_oldest_index])
        ts_c = oldest_value - youngest_value

        youngest = np.argmax(cpts[:, k_youngest_index])
        oldest = np.argmin(cpts[:, k_oldest_index])

        return (i_name, cpts[oldest, k_oldest], cpts[youngest, k_youngest], ts_c, refs_f)

    return (None, None, None, None, None)

################################################################
# strictly searches for youngest binnings
def bifu_y(ntts, xnames_raw):
    k_reference_year = 5
    max_y = max(ntts[:, k_reference_year])
    return ntts[ntts[:, k_reference_year] == max_y]

def bifu_y2  (ntts, used_ts, xnames_raw):
    # ntts ['name_1', 'name_2', 'oldest', 'oldest_index', 'youngest', 'youngest_index', 'ts_count', 'refs', 'rule', 'reference_id', 'reference_year']
    # xnames ['name', 'strat_qualifier', 'ref', 'combi']
    k_reference_id = 9
    k_reference_year = 10
    k_oldest = 2
    k_oldest_index = 3
    k_youngest = 4
    k_youngest_index = 5
    xk_ref = 2

    i_name = ntts[0, 0]

    xnames_set = xnames_raw
    var_exists = 'xnames_set' in locals()
    # if name also relates to "not specified"
    if var_exists == True:
        # filter for references with "not specified"
        bio_set = ntts[~np.isin(ntts[:, k_reference_id], xnames_set[:, xk_ref])]

    if bio_set.size > 0:
        # select all references
        max_y = np.max(bio_set[:, k_reference_year])
        cpts = bio_set[bisect_left(bio_set[:, k_reference_year], max_y):bisect_right(bio_set[:, k_reference_year], max_y)]

        # and collect the references which have that opinions
        refs_f = ', '.join(map(str, np.unique(cpts[:, k_reference_id])))

        # youngest, oldest and ts_count
        youngest_value = np.max(cpts[:, k_youngest_index])
        oldest_value = np.min(cpts[:, k_oldest_index])
        ts_c = oldest_value - youngest_value

        youngest = np.argmax(cpts[:, k_youngest_index])
        oldest = np.argmin(cpts[:, k_oldest_index])

        return (i_name, cpts[oldest, k_oldest], cpts[youngest, k_youngest], ts_c, refs_f)

    return (None, None, None, None, None)

################################################################
# strictly searches for shortest binnings
def bifu_s(ntts, xnames_raw):
    # ntts columns [reference_id, name_1, name_2, ts, ts_index, reference_year]
    # xnames ['name', 'strat_qualifier', 'ref', 'combi']
    k_reference_id = 0
    k_ts = 3
    k_ts_index = 4
    k_reference_year = 5
    xk_ref = 2

    rows = []

    for ref in pd.unique(ntts[:, k_reference_id]):
        cptx = ntts[ntts[:, k_reference_id]== ref]
        ts_min = cptx[0, k_ts_index]
        ts_max = cptx[np.size(cptx, 0) - 1, k_ts_index]

        ts_x = ts_max - ts_min
        rows.append((ref, ts_x))

    rows = np.array(rows)
    min_ts = np.min(rows[:, 1])
    short_ref = rows[rows[:, 1] == min_ts]
    bio_setb = ntts[np.isin(ntts[:, k_reference_id], short_ref[:, 0])]
    # search for youngest reference among those
    max_y = np.max(bio_setb[:, k_reference_year])
    return bio_setb[bio_setb[:, k_reference_year] == max_y]

def bifu_s2  (ntts, used_ts, xnames_raw):
    # ntts ['name_1', 'name_2', 'oldest', 'oldest_index', 'youngest', 'youngest_index', 'ts_count', 'refs', 'rule', 'reference_id', 'reference_year']
    # xnames ['name', 'strat_qualifier', 'ref', 'combi']
    k_reference_id = 9
    k_reference_year = 10
    k_oldest = 2
    k_oldest_index = 3
    k_youngest = 4
    k_youngest_index = 5
    xk_ref = 2

    i_name = ntts[0, 0]

    xnames_set = xnames_raw
    var_exists = 'xnames_set' in locals()
    # if name also relates to "not specified"
    if var_exists == True:
        # filter for references with "not specified"
        bio_set = ntts[~np.isin(ntts[:, k_reference_id], xnames_set[:, xk_ref])]

    if bio_set.size > 0:
        # select all references
        sorted_refs = bio_set[bio_set[:, k_reference_id].argsort()]
        rows = []
        min_delta = np.inf
        # search for shortest range
        for r_yx in np.unique(bio_set[:, k_reference_id]):
            cptx = sorted_refs[bisect_left(sorted_refs[:, k_reference_id], r_yx):bisect_right(sorted_refs[:, k_reference_id], r_yx)]
            ts_x = np.max(cptx[:, k_youngest_index]) - np.min(cptx[:, k_oldest_index])
            if ts_x == min_delta:
                rows.append(r_yx)
            if ts_x < min_delta:
                del rows[:]
                min_delta = ts_x
                rows.append(r_yx)

        bio_setb = bio_set[np.isin(bio_set[:, k_reference_id], rows)]
        # search for youngest reference among those
        max_y = max(bio_setb[:, k_reference_year])
        cpts = bio_setb[bisect_left(bio_setb[:, k_reference_year], max_y):bisect_right(bio_setb[:, k_reference_year], max_y)]
 
        # and collect the references which have that opinions
        refs_f = ', '.join(map(str, np.unique(cpts[:, k_reference_id])))

        # youngest, oldest and ts_count
        youngest_value = np.max(cpts[:, k_youngest_index])
        oldest_value = np.min(cpts[:, k_oldest_index])
        ts_c = oldest_value - youngest_value

        youngest = np.argmax(cpts[:, k_youngest_index])
        oldest = np.argmin(cpts[:, k_oldest_index])

        return (i_name, cpts[oldest, k_oldest], cpts[youngest, k_youngest], ts_c, refs_f)

    return (None, None, None, None, None)
