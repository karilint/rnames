'''
Created on Feb 27, 2019

@author: bkroger
'''
import pandas as pd
import numpy as np
from bisect import (bisect_left, bisect_right)


# col variable contains column names as property names with the column index as their assigned value.
# ntts is a numpy ndarray which contains a combination of names, binning scheme, and time slice
# information. The ndarray only ever contains entries for a single name

################################################################
# strictly searches for maximum compromise between all binnings
def bifu_c(col, ntts, PBDB_id):
    return ntts

################################################################
# strictly searches for youngest binnings
def bifu_y(col, ntts, PBDB_id):
    # if only PBDB relations exist in ntts (PBDB==ntts) do not filter, if not prefer own data
    nttsx = ntts[np.isin(ntts[:, col.reference_id], PBDB_id['reference_id'])]
    if (nttsx.shape[0]>0) & (nttsx.shape[0]<ntts.shape[0]):
        ntts[np.isin(~ntts[:, col.reference_id], PBDB_id['reference_id'])]

    max_y = np.max(ntts[:, col.reference_year])
    return ntts[ntts[:, col.reference_year] == max_y]

################################################################
# strictly searches for shortest binnings
def bifu_s(col, ntts, PBDB_id):
    rows = []

    # Calculate time slice deltas for references
    for ref in pd.unique(ntts[:, col.reference_id]):
        cptx = ntts[ntts[:, col.reference_id]== ref]
        ts_min = np.min(cptx[:, col.ts_index])
        ts_max = np.max(cptx[:, col.ts_index])
        ts_x = ts_max - ts_min
        rows.append((ref, ts_x))
    rows = np.array(rows)

    # Select references with minimal time slice delta
    min_ts = np.min(rows[:, 1])
    short_ref = rows[rows[:, 1] == min_ts]

    # Select rows whose reference has minimal time slice delta
    bio_setb = ntts[np.isin(ntts[:, col.reference_id], short_ref[:, 0])]

    # if only PBDB relations exist in ntts (PBDB==ntts) do not filter if not prefer own data
    bio_setx = bio_setb[np.isin(bio_setb[:, col.reference_id], PBDB_id['reference_id'])]
    if (bio_setx.shape[0]>0) & (bio_setx.shape[0]<bio_setb.shape[0]):
        bio_setb = bio_setb[~np.isin(bio_setb[:, col.reference_id], PBDB_id['reference_id'])]

    # search for youngest reference among those
    max_y = np.max(bio_setb[:, col.reference_year])
          
    return bio_setb[bio_setb[:, col.reference_year] == max_y]

def bifu_s2(col, ntts, PBDB_id):
    # select all references
    rows = []
    min_delta = np.inf

    # search for shortest range
    # Append all reference ids matching the shortest found range (min_delta) to rows
    # If shorter range is found, clear rows and lower min_delta to the new range

    # Sort so binary search can be used
    sorted_refs = ntts[ntts[:, col.reference_id].argsort()]
    for r_yx in np.unique(ntts[:, col.reference_id]):
        # sorted_refs is sorted by reference id so finding all entries matching the refs can be done quickly with binary search
        # Select rows with this reference
        cptx_begin = bisect_left(sorted_refs[:, col.reference_id], r_yx)
        cptx_end = bisect_right(sorted_refs[:, col.reference_id], r_yx)
        cptx = sorted_refs[cptx_begin:cptx_end]

        # Calculate range delta
        ts_x = np.max(cptx[:, col.youngest_index]) - np.min(cptx[:, col.oldest_index])

        if ts_x == min_delta:
            rows.append(r_yx)
        if ts_x < min_delta:
            del rows[:]
            min_delta = ts_x
            rows.append(r_yx)

    # Filter for references with shortest delta
    bio_setb = ntts[np.isin(ntts[:, col.reference_id], rows)]

    # if only PBDB relations exist in ntts (PBDB==ntts) do not filter if not prefer own data
    bio_setx = bio_setb[np.isin(bio_setb[:, col.reference_id], PBDB_id['reference_id'])]
    if (bio_setx.shape[0]>0) & (bio_setx.shape[0]<bio_setb.shape[0]):
        bio_setb = bio_setb[~np.isin(bio_setb[:, col.reference_id], PBDB_id['reference_id'])]

    max_y = np.max(bio_setb[:, col.reference_year])
    
    return bio_setb[bio_setb[:, col.reference_year] == max_y]
