'''
Created on Feb 27, 2019

@author: bkroger
'''
import pandas as pd
import numpy as np
from bisect import (bisect_left, bisect_right)


# col variable contains properties ntts and xnames. These variables have all of their data frame
# column names as property names with the column index as their assigned value.

# ntts is is a combination of names, binning scheme, and time slice information. The ndarray only
# ever contains entries for a single name, and the entries are further sorted depending
# on the function.

################################################################
# strictly searches for maximum compromise between all binnings
def bifu_c(col, ntts, xnames_raw):
    return ntts

def bifu_c2  (col, ntts, xnames_raw):
    return ntts

################################################################
# strictly searches for youngest binnings
def bifu_y(col, ntts, xnames_raw):
    max_y = max(ntts[:, col.ntts.reference_year])
    return ntts[ntts[:, col.ntts.reference_year] == max_y]

def bifu_y2  (col, ntts, xnames_raw):
    max_y = np.max(ntts[:, col.ntts.reference_year])
    # ntts is sorted by reference year so binary search can be used
    return ntts[bisect_left(ntts[:, col.ntts.reference_year], max_y):bisect_right(ntts[:, col.ntts.reference_year], max_y)]

################################################################
# strictly searches for shortest binnings
def bifu_s(col, ntts, xnames_raw):
    rows = []

    for ref in pd.unique(ntts[:, col.ntts.reference_id]):
        cptx = ntts[ntts[:, col.ntts.reference_id]== ref]
        # ntts is sorted by reference id and ts_index
        # Since cptx only contains entries with same reference id the minimum and maximun
        # ts index for any given reference id is found on the first and last rows.
        ts_min = cptx[0, col.ntts.ts_index]
        ts_max = cptx[np.size(cptx, 0) - 1, col.ntts.ts_index]

        ts_x = ts_max - ts_min
        rows.append((ref, ts_x))

    rows = np.array(rows)
    min_ts = np.min(rows[:, 1])
    short_ref = rows[rows[:, 1] == min_ts]
    bio_setb = ntts[np.isin(ntts[:, col.ntts.reference_id], short_ref[:, 0])]
    # search for youngest reference among those
    max_y = np.max(bio_setb[:, col.ntts.reference_year])
    return bio_setb[bio_setb[:, col.ntts.reference_year] == max_y]

def bifu_s2(col, ntts, xnames_raw):
    # select all references
    rows = []
    min_delta = np.inf

    # search for shortest range
    # Append all reference ids matching the shortest found range (min_delta) to rows
    # If shorter range is found, clear rows and lower min_delta to the new range
    sorted_refs = ntts[ntts[:, col.ntts.reference_id].argsort()]
    for r_yx in np.unique(ntts[:, col.ntts.reference_id]):
        # sorted_refs is sorted by reference id so finding all entries matching the refs can be done quickly with binary search
        cptx = sorted_refs[bisect_left(sorted_refs[:, col.ntts.reference_id], r_yx):bisect_right(sorted_refs[:, col.ntts.reference_id], r_yx)]
        ts_x = np.max(cptx[:, col.ntts.youngest_index]) - np.min(cptx[:, col.ntts.oldest_index])
        if ts_x == min_delta:
            rows.append(r_yx)
        if ts_x < min_delta:
            del rows[:]
            min_delta = ts_x
            rows.append(r_yx)

    bio_setb = ntts[np.isin(ntts[:, col.ntts.reference_id], rows)]
    # search for youngest reference among those
    max_y = max(bio_setb[:, col.ntts.reference_year])
    # ntts is sorted by reference year so binary search can be used
    return bio_setb[bisect_left(bio_setb[:, col.ntts.reference_year], max_y):bisect_right(bio_setb[:, col.ntts.reference_year], max_y)]
