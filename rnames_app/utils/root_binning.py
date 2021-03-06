#!/usr/bin/env python
# coding: utf-8

# In[2]:


import time
import csv
import pandas as pd
import numpy as np
import rn_funs
import binning_fun

pd.set_option('display.max_columns', 30)
pd.set_option('display.max_rows', 5)

# In[3]:


# note: when structured names are getting more complicated use structured names id's instead of name
# this also means that the cron_relation input file should be just the structured_name id


# In[4]:


url = "http://karilint.pythonanywhere.com/rnames/api/relations/?format=json"
start = time.time()
cron_relations = pd.read_json (url)
#cron_relations = pd.read_csv("view_cron_relations.csv") # from file
end = time.time()
print("Downloaded ", len(cron_relations), "relations. Download time: ", end - start, "seconds")
cron_relations.to_csv("cron_relations.csv", index = False, header=True)


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
cron_relations.to_csv("cron_relations.csv", index = False, header=True)


# In[6]:


#### this goes into loop on binning_algorithm
### binning_algorithms: shortest, youngest, compromise, combined
robin_b = binning_fun.bin_fun(c_rels = cron_relations, binning_algorithm = "combined", binning_scheme = "b",
                              xrange = 'Ordovician')
robin_b.to_csv("x_robinb.csv", index = False, header=True)


# In[6]:


robin_w = binning_fun.bin_fun(c_rels = cron_relations, binning_algorithm = "combined", binning_scheme = "w",
                              xrange = 'Ordovician')
robin_w.to_csv("x_robinw.csv", index = False, header=True)


# In[7]:


robin_s = binning_fun.bin_fun(c_rels = cron_relations, binning_algorithm = "combined", binning_scheme = "s",
                              xrange = 'Phanerozoic')
robin_s.to_csv("x_robins.csv", index = False, header=True)


# In[8]:


robin_p = binning_fun.bin_fun(c_rels = cron_relations, binning_algorithm = "combined", binning_scheme = "p",
                              xrange = 'Phanerozoic')
robin_p.to_csv("x_robinp.csv", index = False, header=True)


# In[9]:


### match non-binned via merge: bergstr binning output
binning_algorithm = "shortest"
binner_b = robin_s[robin_s["name"].isin(rn_funs.berg_ts['ts'])]
binner_w = robin_s[robin_s["name"].isin(rn_funs.webby_ts['ts'])]

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
mwbs = pd.merge(mwbs, rn_funs.stages_ts, how= 'inner', left_on="oldest", right_on="ts")
x1 = mwbs[['name', 'oldest', 'ts_index', 'youngest', 'ts_count', 'refs']]
x1.columns = ['name', 'oldest', 'oldest_index', 'youngest', 'ts_count','refs']
x1 = pd.merge(x1, rn_funs.stages_ts, how= 'inner', left_on="youngest", right_on="ts")
x1 = x1[['name', 'oldest', 'oldest_index', 'youngest', 'ts_index','ts_count','refs']]
x1.columns = ['name', 'oldest', 'oldest_index', 'youngest', 'youngest_index', 'ts_count','refs']
mc_bw = pd.DataFrame([] * 5, index=["name", "oldest", "youngest", "ts_count", "refs"])
bnu = mwbs["name"]
bnu = bnu.drop_duplicates()
mc_bw = pd.DataFrame.transpose(mc_bw)
bnurange = np.arange(0,len(bnu),1)
for i in bnurange:
    i_name = bnu.iloc[i]
    bio_sel = pd.DataFrame([] * 5, index=["name", "oldest", "youngest", "ts_count", "refs"])
    bio_set = x1.loc[x1["name"] == i_name]
    if binning_algorithm == "combined" or binning_algorithm == "compromise":
        cpts = bio_set
    if binning_algorithm == "shortest" or binning_algorithm == "youngest":
        mincount = min(bio_set['ts_count'])
        cpts = bio_set.loc[bio_set["ts_count"] == mincount]
    refs_f = pd.unique(cpts['refs'])
    refs_f = pd.DataFrame(refs_f)
    refs_f = refs_f[0].apply(str)
    refs_f = refs_f.str.cat(sep=', ')
    cpts_youngest =  cpts.loc[(cpts["youngest_index"]== max(cpts["youngest_index"])), ['youngest']]
    cpts_oldest = cpts.loc[(cpts["oldest_index"]== min(cpts["oldest_index"])), ['oldest']]
    ts_c = max(cpts["youngest_index"])-min(cpts["oldest_index"])
    bio_sel = pd.DataFrame([[i_name, cpts_oldest.iloc[0,0], cpts_youngest.iloc[0,0], ts_c, refs_f]],
                               columns=["name", "oldest", "youngest", "ts_count", "refs"])
    mc_bw = pd.concat([mc_bw, bio_sel], axis=0, sort=True)
mc_bw = mc_bw[~mc_bw["name"].isin(rn_funs.stages_ts["ts"])]

rest_s =  robin_s[~robin_s["name"].isin(bnu)]
rest_s = rest_s[["name", "oldest", "youngest", "ts_count", "refs"]]
binned_stages = pd.concat([mc_bw, rest_s], axis=0, sort=True)

refs = binned_stages['refs']
refs = pd.DataFrame(refs)
bnurange = np.arange(0,len(refs),1)
for i in bnurange:
    refs_f = refs.iloc[i]
    #refs_f = refs_f.apply(str)
    refs_f = refs_f.str.cat(sep=', ')
    ref_list = refs_f.split(", ")
    ref_list_u = list(set(ref_list))
    ref_list_u = sorted(map(int, ref_list_u))
    ref_list_u = pd.DataFrame(ref_list_u)
    ref_list_u = ref_list_u.drop_duplicates()
    ref_list_u = ref_list_u[0].apply(str)
    str1 = ", "
    refs.iloc[i] = str1.join(ref_list_u)
binned_stages.loc[:,'refs'] = refs

binned_stages =  binned_stages[~binned_stages["name"].isin(rn_funs.stages_ts["ts"])]
binned_stages.to_csv("x_binned_stages.csv", index = False, header=True)


# In[10]:


### match non-binned via merge: period binning output
# s with p
binner_p = robin_p[robin_p["name"].isin(rn_funs.stages_ts['ts'])]
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

refs = binned_periods['refs']
refs = pd.DataFrame(refs)
bnurange = np.arange(0,len(refs),1)
for i in bnurange:
    refs_f = refs.iloc[i]
    #refs_f = refs_f.apply(str)
    refs_f = refs_f.str.cat(sep=', ')
    ref_list = refs_f.split(", ")
    ref_list_u = list(set(ref_list))
    ref_list_u = sorted(map(int, ref_list_u))
    ref_list_u = pd.DataFrame(ref_list_u)
    ref_list_u = ref_list_u.drop_duplicates()
    ref_list_u = ref_list_u[0].apply(str)
    str1 = ", "
    refs.iloc[i] = str1.join(ref_list_u)
binned_periods.loc[:,'refs'] = refs
binned_periods =  binned_periods[~binned_periods["name"].isin(rn_funs.periods_ts["ts"])]
binned_periods.to_csv("x_binned_periods.csv", index = False, header=True)


# In[ ]:
