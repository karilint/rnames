#!/usr/bin/env python
# coding: utf-8

# In[2]:


import time
import csv
import pandas as pd
import numpy as np
from bisect import (bisect_left, bisect_right)
from .rn_funs import *
from .binning_fun import *

def main_binning_fun(cron_relations, cron_columns, time_slices, info):
    pd.set_option('display.max_columns', 30)
    pd.set_option('display.max_rows', 5)
    start = time.time()

    # Create a data frame from the ordered list of time slice scheme names
    def make_ts_df(values):
        index = np.arange(0, len(values), 1)
        df = pd.DataFrame({'ts': values, 'ts_index': index}, index=index)
        df = df.append({'ts' : 'not specified' , 'ts_index' : len(values)} , ignore_index=True)
        return df

    for k in time_slices.keys():
        time_slices[k] = make_ts_df(time_slices[k])

    cron_relations = pd.DataFrame(cron_relations, columns=cron_columns)

    # Filter references with no year
    cron_relations = cron_relations[~np.isnan(cron_relations['reference_year'])]

    # In[3]:


    # note: when structured names are getting more complicated use structured names id's instead of name
    # this also means that the cron_relation input file should be just the structured_name id


    # In[4]:


    # In[5]:


    # make cron_relations two sided
    cron_relationsx = cron_relations[['id', 'reference_id', 'reference_year', 'name_2',
           'qualifier_name_2', 'strat_qualifier_2', 'level_2',
           'locality_name_2', 'name_1', 'qualifier_name_1',
           'strat_qualifier_1', 'level_1', 'locality_name_1']]
    cron_relationsx.columns = ['id', 'reference_id', 'reference_year', 'name_1',
           'qualifier_name_1', 'strat_qualifier_1', 'level_1',
           'locality_name_1', 'name_2', 'qualifier_name_2',
           'strat_qualifier_2', 'level_2', 'locality_name_2']
    cron_relations = pd.concat([cron_relations.reset_index(drop=False), cron_relationsx.reset_index(drop=False)], axis=0)
    cron_relations = cron_relations.reset_index(drop=True)


    # In[6]:


    #### this goes into loop on binning_algorithm
    ### binning_algorithms: shortest, youngest, compromise, combined
    robin_b = bin_fun(
        c_rels=cron_relations.copy(),
        binning_algorithm="combined",
        binning_scheme="b",
        xrange='Ordovician',
        time_slices=time_slices,
        info=info.berg_updater(),
    )

    # In[6]:

    robin_w = bin_fun(
        c_rels=cron_relations.copy(),
        binning_algorithm="combined",
        binning_scheme="w",
        xrange='Ordovician',
        time_slices=time_slices,
        info=info.webby_updater(),
    )

    # In[7]:

    robin_s = bin_fun(
        c_rels=cron_relations.copy(),
        binning_algorithm="combined",
        binning_scheme="s",
        xrange='Phanerozoic',
        time_slices=time_slices,
        info=info.stages_updater(),
    )
    # In[8]:
    robin_p = bin_fun(
        c_rels=cron_relations.copy(),
        binning_algorithm="combined",
        binning_scheme="p",
        xrange='Phanerozoic',
        time_slices=time_slices,
        info=info.periods_updater(),
    )

    berg_ts = time_slices['berg']
    webby_ts = time_slices['webby']
    stages_ts = time_slices['stages']
    periods_ts = time_slices['periods']
    # In[9]:


    ### match non-binned via merge: bergstr binning output
    binning_algorithm = "shortest"
    binner_b = robin_s[robin_s["name"].isin(berg_ts['ts'])]
    binner_w = robin_s[robin_s["name"].isin(webby_ts['ts'])]

    mws = pd.merge(robin_w, binner_w, how= 'inner', left_on="oldest", right_on ='name')
    mws['refs'] = mws[['refs_x', 'refs_y']].apply(', '.join, axis=1)
    mws = mws[['name_x', 'oldest_y', 'youngest_x', 'ts_count_y', 'refs']]
    mws.columns = ['name', 'oldest', 'youngest', 'ts_count','refs']
    mws = pd.merge(mws, binner_w, how= 'inner', left_on="youngest", right_on ='name')
    mws['refs'] = mws[['refs_x', 'refs_y']].apply(', '.join, axis=1)
    mws = mws[['name_x', 'oldest_x', 'youngest_y', 'ts_count_y', 'refs']]
    mws.columns = ['name', 'oldest', 'youngest', 'ts_count','refs']

    mbs = pd.merge(robin_b, binner_b, how= 'inner', left_on="oldest", right_on ='name')
    mbs['refs'] = mbs[['refs_x', 'refs_y']].apply(', '.join, axis=1)
    mbs = mbs[['name_x', 'oldest_y', 'youngest_x', 'ts_count_y', 'refs']]
    mbs.columns = ['name', 'oldest', 'youngest', 'ts_count','refs']
    mbs = pd.merge(mbs, binner_b, how= 'inner', left_on="youngest", right_on ='name')
    mbs['refs'] = mbs[['refs_x', 'refs_y']].apply(', '.join, axis=1)
    mbs = mbs[['name_x', 'oldest_x', 'youngest_y', 'ts_count_y', 'refs']]
    mbs.columns = ['name', 'oldest', 'youngest', 'ts_count','refs']

    mwbs = pd.concat([mws, mbs], axis=0, sort=True)
    mwbs = pd.merge(mwbs, stages_ts, how= 'inner', left_on="oldest", right_on="ts")
    x1 = mwbs[['name', 'oldest', 'ts_index', 'youngest', 'ts_count', 'refs']]
    x1.columns = ['name', 'oldest', 'oldest_index', 'youngest', 'ts_count','refs']
    x1 = pd.merge(x1, stages_ts, how= 'inner', left_on="youngest", right_on="ts")
    x1 = x1[['name', 'oldest', 'oldest_index', 'youngest', 'ts_index','ts_count','refs']]
    x1.columns = ['name', 'oldest', 'oldest_index', 'youngest', 'youngest_index', 'ts_count','refs']
    x1 = x1.sort_values(by='name')
    x1 = x1.values

    # x1 column indices
    k_name = 0
    k_oldest = 1
    k_oldest_index = 2
    k_youngest = 3
    k_youngest_index = 4
    k_ts_count = 5
    k_refs = 6

    bnu = mwbs["name"].drop_duplicates()
    rows = []
    for i_name in bnu:
        bio_set = x1[bisect_left(x1[:, k_name], i_name):bisect_right(x1[:, k_name], i_name)]

        if binning_algorithm == "combined" or binning_algorithm == "compromise":
            cpts = bio_set
        if binning_algorithm == "shortest" or binning_algorithm == "youngest":
            mincount = np.min(bio_set[:, k_ts_count])
            cpts = bio_set[bio_set[:, k_ts_count] == mincount]

        refs_f = ', '.join(map(str, np.unique(cpts[:, k_refs])))
        max_youngest = np.max(cpts[:, k_youngest_index])
        min_oldest = np.min(cpts[:, k_oldest_index])

        cpts_youngest = cpts[cpts[:, k_youngest_index] == max_youngest]
        cpts_oldest = cpts[cpts[:, k_oldest_index] == min_oldest]
        ts_c = max_youngest - min_oldest

        rows.append((i_name, cpts_oldest[0, k_oldest], cpts_youngest[0, k_youngest], ts_c, refs_f))

    mc_bw = pd.DataFrame(rows, columns=["name", "oldest", "youngest", "ts_count", "refs"])
    mc_bw = mc_bw[~mc_bw["name"].isin(stages_ts["ts"])]

    rest_s =  robin_s[~robin_s["name"].isin(bnu)]
    rest_s = rest_s[["name", "oldest", "youngest", "ts_count", "refs"]]
    binned_stages = pd.concat([mc_bw, rest_s], axis=0, sort=True)

    refs = []
    for refs_f in binned_stages['refs']:
        refs_f = sorted(list(set(refs_f.split(', '))))
        refs.append(', '.join(refs_f))

    binned_stages.loc[:,'refs'] = refs

    binned_stages =  binned_stages[~binned_stages["name"].isin(stages_ts["ts"])]
    info.binned_stages_updater().update()

    # In[10]:


    ### match non-binned via merge: period binning output
    # s with p
    binner_p = robin_p[robin_p["name"].isin(stages_ts['ts'])]
    msp = pd.merge(binned_stages, binner_p, how= 'inner', left_on="oldest", right_on ='name')
    msp['refs'] = msp[['refs_x', 'refs_y']].apply(', '.join, axis=1)
    msp = msp[['name_x', 'oldest_y', 'youngest_x', 'ts_count_y', 'refs']]
    msp.columns = ['name', 'oldest', 'youngest', 'ts_count','refs']
    msp = pd.merge(msp, binner_p, how= 'inner', left_on="youngest", right_on ='name')
    msp['refs'] = msp[['refs_x', 'refs_y']].apply(', '.join, axis=1)
    msp = msp[['name_x', 'oldest_x', 'youngest_y', 'ts_count_y', 'refs']]
    msp.columns = ['name', 'oldest', 'youngest', 'ts_count','refs']

    bnu = msp["name"]
    bnu = bnu.drop_duplicates()
    rest_p =  robin_p[~robin_p["name"].isin(bnu)]
    rest_p = rest_p[['name', 'oldest', 'youngest', 'ts_count', 'refs']]
    binned_periods = pd.concat([msp, rest_p], axis=0, sort=True)

    refs = []
    for refs_f in binned_periods['refs']:
        refs_f = sorted(list(set(refs_f.split(', '))))
        refs.append(', '.join(refs_f))

    binned_periods.loc[:,'refs'] = refs
    binned_periods =  binned_periods[~binned_periods["name"].isin(periods_ts["ts"])]
    info.binned_periods_updater().update()
    # In[ ]:

    return {
        'duration': time.time() - start,
        'berg': robin_b,
        'webby': robin_w,
        'stages': robin_s,
        'periods': robin_p,
        'binned_stages': binned_stages,
        'binned_periods': binned_periods
    }
