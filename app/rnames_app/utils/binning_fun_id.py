#!/usr/bin/env python
# coding: utf-8

import time
import pandas as pd
import numpy as np
#from rnames_app.utils import rn_funs
from bisect import (bisect_left, bisect_right)
from types import SimpleNamespace
#from .rn_funs import *
<<<<<<< HEAD
import rn_funs


def bin_fun (c_rels, binning_scheme, binning_algorithm, ts_names, t_scales, not_spec):
    # I took out info parameter, jut to test binning locally
=======
from . import rn_funs


def bin_fun (c_rels, binning_scheme, binning_algorithm, ts_names, t_scales, not_spec):
    # I took out info parameter, just to test binning locally
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
    # info parameter is only used to update server on binning status
    #ts_names should be a df containing at least columns: 'id', 'ts_scheme' 
    #ts_scales should be a df containing at least columns: 'ts_name_id', 'structured_name_id'
    # c_rels should be a dataframe containing columns:
    #       'id','name_one_id','name_two_id', 'name_one_qualifier_stratigraphic_qualifier_name',
<<<<<<< HEAD
    #       'name_two_qualifier_stratigraphic_qualifier_name ', 'reference_id', 'reference_year'
    #! also required not_spec: a df with id's of structured names with name: 'not specified'
=======
    #       'name_two_qualifier_stratigraphic_qualifier_name ', 'reference_id', 'reference_year', 'reference_title'
    #! also required not_spec: a df with id's of structured names with name: 'not specified'
    
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
    not_spec = not_spec
        
    print("We begin with six search algorithms binning all relations within the given binning scheme with references.")
    print("This takes a few minutes....")
    start = time.time()

    # Binning algorithms

    if binning_algorithm == "shortest":
        b_scheme = "s"
        runrange = np.arange(0,1,1)
    if binning_algorithm == "youngest":
        b_scheme = "y"
        runrange = np.arange(0,2,1)
    if binning_algorithm == "compromise":
        b_scheme = "c"
        runrange = np.arange(0,3,1)
    if binning_algorithm == "combined":
        b_scheme = "cc"
        runrange = np.arange(0,3,1)
    
    # Prepare binning scheme
<<<<<<< HEAD
    
    t_scheme = binning_scheme
    x_names = ts_names[ts_names['ts_name']==t_scheme]
    used_ts = t_scales[t_scales['ts_name_id']==x_names['id'].values[0]]
    # rename columns in order to make compatible with following code
    used_ts = used_ts[['structured_name_id', 'sequence']]
    used_ts.rename(columns={'structured_name_id':'ts', 'sequence': 'ts_index'},inplace = True)


    
    # Prepare c_rels #
    # c_rels should be a dataframe containing columns:
    # id | name_one_id | name_two_id |name_one_qualifier_qualifier_name_name | 
    # name_two_qualifier_qualifier_name_name |reference_id
   
    c_rels = c_rels[['id', 'name_one_id', 'name_two_id','name_one_qualifier_stratigraphic_qualifier_name', 
                          'name_two_qualifier_stratigraphic_qualifier_name', 'reference_id', 'reference_year']]
    c_rels.rename(columns={'name_one_id': 'name_1', 'name_two_id':'name_2', 
                         'name_one_qualifier_stratigraphic_qualifier_name': 'strat_qualifier_1',
                         'name_two_qualifier_stratigraphic_qualifier_name': 'strat_qualifier_2'},inplace = True) # rename to fit following code
    # make c_rels two-sided
    c_relsx = c_rels[['id', 'name_2','strat_qualifier_2','name_1', 'strat_qualifier_1', 'reference_id', 'reference_year']]
    c_relsx.columns = ['id', 'name_1','strat_qualifier_1','name_2', 'strat_qualifier_2','reference_id', 'reference_year']
    c_rels = pd.concat([c_rels.reset_index(drop=False), c_relsx.reset_index(drop=False)], axis=0)
    c_rels = c_rels.reset_index(drop=True)
    
    # range limitation can now be taken out
    # qualifier_name_1/2 problem:
    # this is used in older code to identify the name_ids of the ids of the used_ts
    # so I replaced it with .isn used_ts['id'filter] 

    # range limitation
    #c_rels_sub = c_rels.loc[((c_rels["name_1"]== xrange))]
    #xsub1 = c_rels.loc[((c_rels["level_1"] <= c_rels_sub['level_1'].values[0])
                #& (c_rels["strat_qualifier_1"] == c_rels_sub['strat_qualifier_1'].values[0]))]
    #xsub2 = c_rels.loc[((c_rels["level_2"] <= c_rels_sub['level_1'].values[0])
                #& (c_rels["strat_qualifier_2"] == c_rels_sub['strat_qualifier_1'].values[0]))]
    #xsubs = pd.concat([xsub1['name_1'], xsub2['name_2']], axis=0, ignore_index=True)
    #xsubs = xsubs.drop_duplicates()
    #c_relsx = c_rels[~c_rels["name_1"].isin(xsubs)]
    #c_rels = c_relsx[~c_relsx["name_2"].isin(xsubs)]


    # this block identifies "not specified" - relations
    # c_rels_a = c_rels.loc[((c_rels["name_1"]=="not specified"))]
    #c_rels_b = c_rels.loc[((c_rels["name_2"]=="not specified"))]
    c_rels_a = c_rels[c_rels['name_1'].isin(not_spec['id'])]
    c_rels_b = c_rels[c_rels['name_2'].isin(not_spec['id'])]
=======
<<<<<<<< HEAD:app/rnames_app/utils/binning_fun.py
    # time_slices should be a dataframe containing columns : id | order | scheme
    #t_scheme = binning_scheme
    #used_ts = time_slices[time_slices['scheme']==binning_scheme]
    #used_ts = used_ts[['id', 'order']]
    #used_ts.rename(columns={'id': 'ts'},inplace = True) # rename to fit following code

    # range limitation
    c_rels_sub = c_rels.loc[((c_rels["name_1"]== xrange))]
    xsub1 = c_rels.loc[((c_rels["level_1"] <= c_rels_sub['level_1'].values[0])
                & (c_rels["strat_qualifier_1"] == c_rels_sub['strat_qualifier_1'].values[0]))]
    xsub2 = c_rels.loc[((c_rels["level_2"] <= c_rels_sub['level_1'].values[0])
                & (c_rels["strat_qualifier_2"] == c_rels_sub['strat_qualifier_1'].values[0]))]
    xsubs = pd.concat([xsub1['name_1'], xsub2['name_2']], axis=0, ignore_index=True)
    xsubs = xsubs.drop_duplicates()
    c_relsx = c_rels[~c_rels["name_1"].isin(xsubs)]
    c_rels = c_relsx[~c_relsx["name_2"].isin(xsubs)]


     # this block identifies "not specified" - relations
    c_rels_a = c_rels.loc[((c_rels["name_1"]=="not specified"))]
    c_rels_b = c_rels.loc[((c_rels["name_2"]=="not specified"))]
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d

    if len(c_rels_a) == 0:
        xnamesb = c_rels_b[['name_1', 'strat_qualifier_1', 'reference_id']]
        xnamesb.columns = ["name", "strat_qualifier","ref"]
        xnamesc = xnamesb
    if len(c_rels_b) == 0:
        xnamesb = c_rels_b[['name_2', 'strat_qualifier_2', 'reference_id']]
        xnamesb.columns = ["name", "strat_qualifier","ref"]
        xnamesc = xnamesb
    if len(c_rels_a) > 0:
        xnamesa = c_rels_a[['name_2', 'strat_qualifier_2','reference_id']]
        xnamesa.columns = ["name", "strat_qualifier","ref"]
        xnamesb = c_rels_b[['name_1', 'strat_qualifier_1', 'reference_id']]
        xnamesb.columns = ["name", "strat_qualifier","ref"]
        xnamesc = pd.concat((xnamesa,xnamesb), axis=0)
        xnames_raw1 = xnamesc.drop_duplicates()
    if len(c_rels_b) > 0:
        xnamesa = c_rels_b[['name_1', 'strat_qualifier_1','reference_id']]
        xnamesa.columns = ["name", "strat_qualifier","ref"]
        xnamesb = c_rels_a[['name_2', 'strat_qualifier_2', 'reference_id']]
        xnamesb.columns = ["name", "strat_qualifier","ref"]
        xnamesc = pd.concat((xnamesa,xnamesb), axis=0)
        xnames_raw1 = xnamesc.drop_duplicates()
    xnames_raw = xnamesc
    if len(c_rels_a) > 0 or len(c_rels_b) > 0:
<<<<<<< HEAD
        xnames_raw["combi"] = xnames_raw1["name"].astype(str).copy()+ '_' 
        + xnames_raw1["ref"].astype(str).copy()
    #xnamelist = xnames_raw["combi"].tolist()
=======
        xnames_raw["combi"] = xnames_raw1["name"] + xnames_raw1["ref"].astype(str).copy()
    #xnamelist = xnames_raw["combi"].tolist()
========
    
    t_scheme = binning_scheme
    x_names = ts_names[ts_names['ts_name']==t_scheme]
    used_ts = t_scales[t_scales['ts_name_id']==x_names['id'].values[0]]
    # rename columns in order to make compatible with following code
    used_ts = used_ts[['structured_name_id', 'sequence']]
    used_ts.rename(columns={'structured_name_id':'ts', 'sequence': 'ts_index'},inplace = True)
    
    # Get reference_id of PBDB relations. This is needed because thethey need to be excluded from 's' and 'cc'
    PBDB_id = c_rels.loc[(c_rels["reference_title"]=="Paleobiology Database"),["reference_id"]]
    PBDB_id = PBDB_id.drop_duplicates()
 
    # Prepare c_rels
    # c_rels should be a dataframe containing columns:
    # id | name_one_id | name_two_id |name_one_qualifier_qualifier_name_name | 
    # name_two_qualifier_qualifier_name_name |reference_id
   
    c_rels = c_rels[['id', 'name_one_id', 'name_two_id','name_one_qualifier_stratigraphic_qualifier_name', 
                          'name_two_qualifier_stratigraphic_qualifier_name', 'reference_id', 'reference_year']]
    c_rels.rename(columns={'name_one_id': 'name_1', 'name_two_id':'name_2', 
                         'name_one_qualifier_stratigraphic_qualifier_name': 'strat_qualifier_1',
                         'name_two_qualifier_stratigraphic_qualifier_name': 'strat_qualifier_2'},inplace = True) # rename to fit following code
    # make c_rels two-sided
    c_relsx = c_rels[['id', 'name_2','strat_qualifier_2','name_1', 'strat_qualifier_1', 'reference_id', 'reference_year']]
    c_relsx.columns = ['id', 'name_1','strat_qualifier_1','name_2', 'strat_qualifier_2','reference_id', 'reference_year']
    c_rels = pd.concat([c_rels.reset_index(drop=False), c_relsx.reset_index(drop=False)], axis=0)
    c_rels = c_rels.reset_index(drop=True)
    

    # this block identifies "not specified" - relations
    c_rels_a = c_rels[c_rels['name_1'].isin(not_spec['id'])]
    c_rels_b = c_rels[c_rels['name_2'].isin(not_spec['id'])]

    xnamesa = c_rels_b[['name_1', 'strat_qualifier_1','reference_id']]
    xnamesa.columns = ["name", "strat_qualifier","ref"]
    xnamesb = c_rels_a[['name_2', 'strat_qualifier_2', 'reference_id']]
    xnamesb.columns = ["name", "strat_qualifier","ref"]
    xnamesc = pd.concat((xnamesa,xnamesb), axis=0)
    xnames_raw = xnamesc.drop_duplicates()
    xnames_raw["combi"] = xnames_raw["name"].astype(str).copy()+ '_' + xnames_raw["ref"].astype(str).copy()
>>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d:app/rnames_app/utils/binning_fun_id.py
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d

    ##############################################################
    ##############################################################
    ##############################################################
    ##############################################################
    ##############################################################
    # the first tier has three binning rules and is based on direct relations

    c_rels_d = pd.merge(c_rels, used_ts, how= 'inner', left_on="name_2", right_on="ts")

    ##############################################################
    ##############################################################
    results = {}

    #rule 0 = all direct relations between chronostrat names and binning scheme
<<<<<<< HEAD
    results['rule_0'] = rule0(c_rels_d, t_scheme, runrange, used_ts, xnames_raw, b_scheme, not_spec)
=======
    results['rule_0'] = rule0(c_rels_d, t_scheme, runrange, used_ts, xnames_raw, b_scheme, not_spec, PBDB_id)
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
    #info.update()

    ##############################################################
    ##############################################################
    #rule 1 = all direct relations between biostrat names and binning scheme
<<<<<<< HEAD
    results['rule_1'] = rule1(c_rels_d, t_scheme, runrange, used_ts, xnames_raw, b_scheme, not_spec)
=======
    results['rule_1'] = rule1(c_rels_d, t_scheme, runrange, used_ts, xnames_raw, b_scheme, not_spec, PBDB_id)
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
    #info.update()

    ##############################################################
    ##############################################################
    ### Rule_2: direct relations between non-bio* with binning scheme
    ### except chronostratigraphy
<<<<<<< HEAD
    results['rule_2'] = rule2(results, c_rels_d, t_scheme, runrange, used_ts, xnames_raw, b_scheme, not_spec)
=======
    results['rule_2'] = rule2(results, c_rels_d, t_scheme, runrange, used_ts, xnames_raw, b_scheme, not_spec, PBDB_id)
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
    #info.update()

    ##############################################################
    ##############################################################
    # the second tier has two binning rules and bins all indirect names via biostrat

    ##############################################################
    ##############################################################
    #rule_3 all relations between biostrat and biostrat that refer indirectly to binning scheme
<<<<<<< HEAD
    results['rule_3'] = rule3(results, c_rels, t_scheme, runrange, used_ts, xnames_raw, b_scheme, not_spec)
=======
    results['rule_3'] = rule3(results, c_rels, t_scheme, runrange, used_ts, xnames_raw, b_scheme, not_spec, PBDB_id)
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
    #info.update()

    ##############################################################
    resis_bio = pd.concat([results['rule_1'], results['rule_3']], axis=0)
    resis_bio = pd.DataFrame.drop_duplicates(resis_bio)
    ### Rule 4: indirect relations of non-bio via resis_bio to binning scheme
    ### except direct chronostratigraphy links
<<<<<<< HEAD
    results['rule_4'] = rule4(results, resis_bio, c_rels, t_scheme, runrange, used_ts, xnames_raw, b_scheme, not_spec)
=======
    results['rule_4'] = rule4(results, resis_bio, c_rels, t_scheme, runrange, used_ts, xnames_raw, b_scheme, 
                              not_spec, PBDB_id)
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
    #info.update()

    ##################################################################################
    cr_g = c_rels.loc[~(c_rels["strat_qualifier_1"]=="Biostratigraphy")
                              & ~(c_rels["strat_qualifier_2"]=="Biostratigraphy"),
                              #& ~(c_rels["qualifier_name_1"]==t_scheme)
                              #& ~(c_rels["qualifier_name_2"]==t_scheme),
                              ["reference_id","name_1","name_2", "reference_year"]]
    
    cr_g =  cr_g[~cr_g["name_1"].isin(used_ts["ts"])]
    cr_g =  cr_g[~cr_g["name_2"].isin(used_ts["ts"])]
    
    ### Rule 5:  indirect relations of non-bio* to resis_4 with link to bio* (route via resi_4)
<<<<<<< HEAD
    results['rule_5'] = rule5(results, cr_g, resis_bio, c_rels, t_scheme, runrange, used_ts, xnames_raw, b_scheme, not_spec)
=======
    results['rule_5'] = rule5(results, cr_g, resis_bio, c_rels, t_scheme, runrange, used_ts, xnames_raw, b_scheme, 
                              not_spec, PBDB_id)
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
    #info.update()

    ##################################################################################
    ### Rule 6: indirect relations of non-bio* to resis_bio to binning scheme (route via resis_bio)
    #rule 6 corrected at 23.03.2020
<<<<<<< HEAD
    results['rule_6'] = rule6(results, cr_g, runrange, used_ts, xnames_raw, b_scheme, not_spec)
=======
    results['rule_6'] = rule6(results, cr_g, runrange, used_ts, xnames_raw, b_scheme, not_spec, PBDB_id)
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
    #info.update()

    end = time.time()
    dura = (end - start)/60

    print("############################################")
    print("The binning took", round(dura, 2), "minutes")
    print("############################################")

    print("Now we search for the shortest time bins within these 6 results.")
    ##################################################################################
    ##################################################################################
    ## search for shortest time bins among 5 & 6
    start = time.time()
    combi_names = shortest_time_bins(results, used_ts)
    end = time.time()
    #info.update()
    dura2 = (end - start)/60
    print("We find", len(combi_names),
          "binned names. It took ", round(dura, 2), "+", round(dura2, 2),  "minutes.")
    return combi_names

<<<<<<< HEAD
def rule0(c_rels_d, t_scheme, runrange, used_ts, xnames_raw, b_scheme, not_spec):
    #rule 0 = all direct relations between chronostrat names and binning scheme
    
    cr_x =  c_rels_d[c_rels_d["name_2"].isin(used_ts["ts"])]
    #cr_x =  cr_x.loc[~(cr_x["name_1"]=="not specified")]
    cr_x = cr_x[~cr_x['name_1'].isin(not_spec['id'])] 
    cr_x = cr_x.loc[((cr_x["strat_qualifier_1"]=="Chronostratigraphy")),
                              #& ((c_rels_d["qualifier_name_2"]==t_scheme)),
                              ["reference_id","name_1","name_2", "ts", "ts_index", "reference_year"]]

    for ibs in runrange:
        resi_0 = bin_names(ibs, cr_x, xnames_raw, bifu_selector='bfs')
=======
def rule0(c_rels_d, t_scheme, runrange, used_ts, xnames_raw, b_scheme, not_spec, PBDB_id):
    #rule 0 = all direct relations between chronostrat names and binning scheme
    
    cr_x =  c_rels_d[c_rels_d["name_2"].isin(used_ts["ts"])]
    cr_x = cr_x[~cr_x['name_1'].isin(not_spec['id'])] 
    cr_x = cr_x.loc[((cr_x["strat_qualifier_1"]=="Chronostratigraphy")),
                              ["reference_id","name_1","name_2", "ts", "ts_index", "reference_year"]]

    for ibs in runrange:
        resi_0 = bin_names(ibs, PBDB_id,cr_x, xnames_raw, bifu_selector='bfs')
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
        resi_0["rule"] = 0.0
        resi_0 = resi_0.loc(axis=1)["name", "oldest", "youngest", "ts_count", "refs", "rule"]
        resi_0 =  resi_0[~resi_0["name"].isin(used_ts["ts"])]
        resi_0 = pd.DataFrame.drop_duplicates(resi_0)
        resi_0 = resi_0[['name', 'oldest', 'youngest', 'ts_count', 'refs', 'rule']]
        if ibs == 0:
            resi_0s = resi_0
            resi_0s["b_scheme"] = "s"
        if ibs == 1:
            resi_0y = resi_0
            resi_0y["b_scheme"] = "y"
        if ibs == 2:
            resi_0c = resi_0
            resi_0c["b_scheme"] = "c"
    resi_0 = resi_0.dropna()
    if b_scheme == "cc":
        resi_0 = merge_cc(resi_0s, resi_0y, resi_0c, used_ts)
        resi_0['rule'] = 0.0

    resi_0 = resi_0.loc(axis=1)["name", "oldest", "youngest", "ts_count", "refs", "rule"]
    print("rule 0 has ", len(resi_0), "binned relations")
    print("Rule 0:  relations among named biostratigraphical units that have direct relations to binning scheme")
    return resi_0

<<<<<<< HEAD
def rule1(c_rels_d, t_scheme, runrange, used_ts, xnames_raw, b_scheme, not_spec):
=======
def rule1(c_rels_d, t_scheme, runrange, used_ts, xnames_raw, b_scheme, not_spec, PBDB_id):
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
    #rule 1 = all direct relations between biostrat names and binning scheme
    
    cr_a =  c_rels_d[c_rels_d["name_2"].isin(used_ts["ts"])]
    #take out  relations that also relate to not specified in same reference
<<<<<<< HEAD
    #cr_a =  cr_a.loc[~(cr_a["name_1"]=="not specified")]
    cr_a = cr_a[~cr_a['name_1'].isin(not_spec['id'])]
    cr_a = cr_a.loc[((cr_a["strat_qualifier_1"]=="Biostratigraphy")),
                              #& ((c_rels_d["qualifier_name_2"]==t_scheme)),
=======
    cr_a = cr_a[~cr_a['name_1'].isin(not_spec['id'])]
    cr_a = cr_a.loc[((cr_a["strat_qualifier_1"]=="Biostratigraphy")),
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
                              ["reference_id","name_1","name_2", "ts", "ts_index", "reference_year"]]
    
    
    for ibs in runrange:
<<<<<<< HEAD
        resi_1 = bin_names(ibs, cr_a, xnames_raw, bifu_selector='bfs')
=======
        resi_1 = bin_names(ibs, PBDB_id, cr_a, xnames_raw, bifu_selector='bfs')
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
        resi_1["rule"] = 1.0
        resi_1 = resi_1.loc(axis=1)["name", "oldest", "youngest", "ts_count", "refs", "rule"]
        resi_1 =  resi_1[~resi_1["name"].isin(used_ts["ts"])]
        resi_1 = pd.DataFrame.drop_duplicates(resi_1)
        resi_1 = resi_1[['name', 'oldest', 'youngest', 'ts_count', 'refs', 'rule']]
        if ibs == 0:
            resi_1s = resi_1
            resi_1s["b_scheme"] = "s"
        if ibs == 1:
            resi_1y = resi_1
            resi_1y["b_scheme"] = "y"
        if ibs == 2:
            resi_1c = resi_1
            resi_1c["b_scheme"] = "c"

    if b_scheme == "cc":
        resi_1 = merge_cc(resi_1s, resi_1y, resi_1c, used_ts)
        resi_1['rule'] = 1.0

    resi_1 = resi_1.loc(axis=1)["name", "oldest", "youngest", "ts_count", "refs", "rule"]
    print("rule 1 has ", len(resi_1), "binned relations")
    print("Rule 1: direct relations of named units to binning scheme")
    return resi_1

<<<<<<< HEAD
def rule2(results, c_rels_d, t_scheme, runrange, used_ts, xnames_raw, b_scheme, not_spec):
=======
def rule2(results, c_rels_d, t_scheme, runrange, used_ts, xnames_raw, b_scheme, not_spec, PBDB_id):
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
    resi_0 = results["rule_0"]
    ### Rule_2: direct relations between non-bio* with binning scheme
    ### except chronostratigraphy
    cr_c =  c_rels_d[c_rels_d["name_2"].isin(used_ts["ts"])]
<<<<<<< HEAD
    #cr_c =  cr_c.loc[~(cr_c["name_2"]=="not specified")]
    cr_c = cr_c[~cr_c['name_2'].isin(not_spec['id'])]
    cr_c = cr_c.loc[~(cr_c["strat_qualifier_1"]=="Biostratigraphy")
                          & ~(cr_c["strat_qualifier_1"]=="Chronostratigraphy"),
                          #& (c_rels_d["qualifier_name_2"]==t_scheme),
                              ["reference_id","name_1","name_2", "ts", "ts_index", "reference_year"]]
    
    for ibs in runrange:
        resi_2 = bin_names(ibs, cr_c, xnames_raw, bifu_selector='bfs')
=======
    cr_c = cr_c[~cr_c['name_2'].isin(not_spec['id'])]
    cr_c = cr_c.loc[~(cr_c["strat_qualifier_1"]=="Biostratigraphy")
                          & ~(cr_c["strat_qualifier_1"]=="Chronostratigraphy"),
                              ["reference_id","name_1","name_2", "ts", "ts_index", "reference_year"]]
    
    for ibs in runrange:
        resi_2 = bin_names(ibs, PBDB_id, cr_c, xnames_raw, bifu_selector='bfs')
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
        resi_2["rule"] = 2.0
        resi_2 = resi_2.loc(axis=1)["name", "oldest", "youngest", "ts_count", "refs", "rule"]
        resi_2 =  resi_2[~resi_2["name"].isin(used_ts["ts"])]
        resi_2 = pd.DataFrame.drop_duplicates(resi_2)
        resi_2 = resi_2[['name', 'oldest', 'youngest', 'ts_count', 'refs', 'rule']]
        if ibs == 0:
            resi_2s = resi_2
            resi_2s["b_scheme"] = "s"
        if ibs == 1:
            resi_2y = resi_2
            resi_2y["b_scheme"] = "y"
        if ibs == 2:
            resi_2c = resi_2
            resi_2c["b_scheme"] = "c"

    resi_2 = resi_2.dropna()
    if b_scheme == "cc":
        resi_2 = merge_cc(resi_2s, resi_2y, resi_2c, used_ts)
        resi_2['rule'] = 2.0

    resi_2= resi_2.loc(axis=1)["name", "oldest", "youngest", "ts_count", "refs", "rule"]
    resi_2 = resi_2[~resi_2["name"].isin(resi_0["name"])] # filter non-bio rule 0
    print("rule 2 has ", len(resi_2), "binned relations")
    print("Rule 2:  relations among named biostratigraphical units that have indirect relations to binning scheme")
    return resi_2

<<<<<<< HEAD
def rule3(results, c_rels, t_scheme, runrange, used_ts, xnames_raw, b_scheme, not_spec):
=======
def rule3(results, c_rels, t_scheme, runrange, used_ts, xnames_raw, b_scheme, not_spec, PBDB_id):
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
    resi_1 = results["rule_1"]
    #rule_3 all relations between biostrat and biostrat that refer indirectly to binning scheme
    cr_b = c_rels.loc[(c_rels["strat_qualifier_1"]=="Biostratigraphy")
                                  & (c_rels["strat_qualifier_2"]=="Biostratigraphy"),
<<<<<<< HEAD
                                  #&  ~(c_rels["qualifier_name_1"] == t_scheme)
                                  #&  ~(c_rels["qualifier_name_2"] == t_scheme),
=======
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
                                  ["reference_id","name_1","name_2", "reference_year"]]
    
    cr_b =  cr_b[~cr_b["name_1"].isin(used_ts["ts"])]
    cr_b =  cr_b[~cr_b["name_2"].isin(used_ts["ts"])]

    x1 = pd.merge(resi_1, cr_b, left_on="name", right_on="name_2") # name_2 is already binned here
    x1 = merge_time_info(x1, used_ts)
<<<<<<< HEAD
    #x1 =  x1.loc[~(x1["name_1"]=="not specified")]
=======
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
    x1 = x1[~x1['name_1'].isin(not_spec['id'])]
    x1 = x1[~x1["name_1"].isin(resi_1["name"])]# filter out all names that are already binned with rule 1
    # name_1 is already binned, name_2 not binned yet
    x1["rule"] = 3.6
    x1 = x1.drop_duplicates()
    # all names that are not binned via rule 1
    x2 = cr_b[~cr_b["name_1"].isin(x1["name_1"])]

    resi_3 = pd.DataFrame([] * 6, index=["name", "oldest", "youngest", "ts_count", "refs", "rule"])
    resi_3 = pd.DataFrame.transpose(resi_3)
    for ibs in runrange:
        for k in np.arange(1,5,1):
<<<<<<< HEAD
            x3 = bin_names(ibs, x1, xnames_raw, bifu_selector='bfs2', result_selector=result_selector_2)
=======
            x3 = bin_names(ibs, PBDB_id, x1, xnames_raw, bifu_selector='bfs2', result_selector=result_selector_2)
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
            x3["rule"] = 3.0+((k-1)*0.1)
            x3b = x3[~x3["name"].isin(resi_3["name"])] # filter for already binned names
            resi_3 = pd.concat([resi_3, x3b], axis=0, sort=True) # appended to previous ruling

            #create a new x1 based on above ruling
            if (k==1):
                x4a = pd.concat((resi_1, x3), axis=0)
            else:
                x4a = pd.concat((x4a, x3), axis=0)

            x4 = pd.merge(x4a, cr_b, left_on="name", right_on="name_2") # name_2 is already binned here
            x1 = merge_time_info(x4, used_ts)
<<<<<<< HEAD
            #x1 =  x1.loc[~(x1["name_1"]=="not specified")]
=======
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
            x1 = x1[~x1['name_1'].isin(not_spec['id'])]
            x1["rule"] = 3.7
            x1 = x1.drop_duplicates()
            x2b = cr_b[~cr_b["name_1"].isin(x1["name_1"])] # all not yet binned in cr_g
            x2b = pd.DataFrame.drop_duplicates(x2b)

            if k == 1:
                x6 = x3 # das ist ok nach zweitem durchlauf
            if len(x2)== len(x2b):
                break
            x2 = x2b
        if ibs == 0:
            resi_3s = resi_3
            resi_3s["b_scheme"] = "s"
        if ibs == 1:
            resi_3y = resi_3
            resi_3y["b_scheme"] = "y"
        if ibs == 2:
            resi_3c = resi_3
            resi_3c["b_scheme"] = "c"

    if b_scheme == "cc":
        resi_3 = merge_cc(resi_3s, resi_3y, resi_3c, used_ts)
        resi_3['rule'] = 3.9


    resi_3= resi_3.loc(axis=1)["name", "oldest", "youngest", "ts_count", "refs", "rule"]
    resi_3 = pd.DataFrame.drop_duplicates(resi_3)
    resi_3 = resi_3[~resi_3["name"].isin(resi_1["name"])] # filter non-bio rule 1
    print("rule 3 has ", len(resi_3), "binned relations")
    print("Rule 3:  relations among named biostratigraphical units that have direct relations to binning scheme")
    return resi_3

<<<<<<< HEAD
def rule4(results, resis_bio, c_rels, t_scheme, runrange, used_ts, xnames_raw, b_scheme, not_spec):
=======
def rule4(results, resis_bio, c_rels, t_scheme, runrange, used_ts, xnames_raw, b_scheme, not_spec, PBDB_id):
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
    resi_0 = results["rule_0"]
    resi_1 = results["rule_1"]
    resi_2 = results["rule_2"]
    resi_3 = results["rule_3"]
    ### Rule 4: indirect relations of non-bio via resis_bio to binning scheme
    ### except direct chronostratigraphy links

    cr_d = c_rels.loc[~(c_rels["strat_qualifier_1"]=="Biostratigraphy")
                              & (c_rels["strat_qualifier_2"]=="Biostratigraphy"),
<<<<<<< HEAD
                              #& ~(c_rels["qualifier_name_1"]==t_scheme)
                              #& ~(c_rels["qualifier_name_2"]==t_scheme),
=======
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
                              ["reference_id","name_1","name_2", "reference_year"]]
    
    cr_d =  cr_d[~cr_d["name_1"].isin(used_ts["ts"])]
    cr_d =  cr_d[~cr_d["name_2"].isin(used_ts["ts"])]
    cr_d =  cr_d[~cr_d["name_1"].isin(resi_0["name"])] #filter for chronostrat rule 0

    x1 = pd.merge(resis_bio, cr_d, left_on="name", right_on="name_2") # name_2 is already binned here
    x1 = merge_time_info(x1, used_ts)
    x1 = x1[~x1["name_1"].isin(resi_2["name"])] # filter non-bio rule 2
    x1 =  x1[~x1["name_1"].isin(resi_0["name"])] # filter direct chronostrat rule 0
<<<<<<< HEAD
    #x1 =  x1.loc[~(x1["name_1"]=="not specified")] # filter "Not specified"
=======
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
    x1 = x1[~x1['name_1'].isin(not_spec['id'])]
    x1["rule"] = 4.6
    x1 = x1.drop_duplicates()

    x2 = cr_d[~cr_d["name_1"].isin(resis_bio["name"])]

    resi_4 = pd.DataFrame([] * 6, index=["name", "oldest", "youngest", "ts_count", "refs", "rule"])
    resi_4 = pd.DataFrame.transpose(resi_4)
    for ibs in runrange:
        for k in np.arange(1,5,1):
<<<<<<< HEAD
            x3 = bin_names(ibs, x1, xnames_raw, bifu_selector='bfs2', result_selector=result_selector_2)
=======
            x3 = bin_names(ibs, PBDB_id, x1, xnames_raw, bifu_selector='bfs2', result_selector=result_selector_2)
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
            x3["rule"] = 4.0+((k-1)*0.1)
            x3b = x3[~x3["name"].isin(resi_4["name"])] # filter for already binned names
            resi_4 = pd.concat([resi_4, x3b], axis=0, sort=True) # appended to previous ruling
            x2a = cr_d[~cr_d["name_1"].isin(resi_4["name"])] # all non binned names in cr_g with current rule

            #now create a new x1 based on above ruling
            if (k==1):
                x4a = pd.concat((resis_bio, x3), axis=0)
            else:
                x4a = pd.concat((x4a, x3), axis=0)

            x4 = pd.merge(x4a, cr_d, left_on="name", right_on="name_2") # name_2 is already binned here
            x1 = merge_time_info(x4, used_ts)
            #x1 =  x1.loc[~(x1["name_1"]=="not specified")]
            x1 = x1[~x1['name_1'].isin(not_spec['id'])]
            x1 =  x1[~x1["name_1"].isin(resi_0["name"])]
            x1["rule"] = 6.7
            x1 = x1.drop_duplicates()

            if len(x2a)== len(x2):
                break
            x2 = x2a

        if ibs == 0:
            resi_4s = resi_4
            resi_4s["b_scheme"] = "s"
        if ibs == 1:
            resi_4y = resi_4
            resi_4y["b_scheme"] = "y"
        if ibs == 2:
            resi_4c = resi_4
            resi_4c["b_scheme"] = "c"

    if b_scheme == "cc":
        resi_4 = merge_cc(resi_4s, resi_4y, resi_4c, used_ts)
        resi_4['rule'] = 4.9

    resi_4 = pd.DataFrame.drop_duplicates(resi_4)
    resi_4 = resi_4[['name', 'oldest', 'youngest', 'ts_count', 'refs', 'rule']]
    combi_x = pd.concat([resi_0, resi_1, resi_2, resi_3], axis=0, sort=False)
    resi_4 = resi_4[~resi_4["name"].isin(combi_x["name"])] # filter non-bio rule 1
    print("rule 4 has ", len(resi_4), "binned relations")
    print("Rule 4:  relations among named non-biostratigraphical units that have direct relations to binning scheme")
    return resi_4

<<<<<<< HEAD
def rule5(results, cr_g, resis_bio, c_rels, t_scheme, runrange, used_ts, xnames_raw, b_scheme, not_spec):
=======
def rule5(results, cr_g, resis_bio, c_rels, t_scheme, runrange, used_ts, xnames_raw, b_scheme, not_spec, PBDB_id):
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
    resi_0 = results["rule_0"]
    resi_1 = results["rule_1"]
    resi_2 = results["rule_2"]
    resi_3 = results["rule_3"]
    resi_4 = results["rule_4"]
    ### Rule 5:  indirect relations of non-bio* to resis_4 with link to bio* (route via resi_4)

    x1 = pd.merge(resi_4, cr_g, left_on="name", right_on="name_2")
    x1 = merge_time_info(x1, used_ts)
    x1 = x1[~x1["name_1"].isin(resi_2["name"])] # filter first level  linked non-bio*
    x1 =  x1[~x1["name_1"].isin(resi_0["name"])] # filter direct  chronostrat rule 0
<<<<<<< HEAD
    #x1 =  x1.loc[~(x1["name_1"]=="not specified")]
=======
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
    x1 = x1[~x1['name_1'].isin(not_spec['id'])]
    x1["rule"] = 5.0
    x1 = x1.drop_duplicates()

    x2 = cr_g[~cr_g["name_2"].isin(resis_bio["name"])]

    resi_5 = pd.DataFrame([] * 6, index=["name", "oldest", "youngest", "ts_count", "refs", "rule"])
    resi_5 = pd.DataFrame.transpose(resi_5)
    for ibs in runrange:
        for k in np.arange(1,5,1):
<<<<<<< HEAD
            x3 = bin_names(ibs, x1, xnames_raw, bifu_selector='bfs2', result_selector=result_selector_2)
=======
            x3 = bin_names(ibs, PBDB_id, x1, xnames_raw, bifu_selector='bfs2', result_selector=result_selector_2)
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
            x3["rule"] = 5.0+((k-1)*0.1)
            x3b = x3[~x3["name"].isin(resi_5["name"])] # filter for already binned names
            resi_5 = pd.concat([resi_5, x3b], axis=0, sort=True) # appended to previous ruling
            x2a = cr_g[~cr_g["name_1"].isin(resi_5["name"])] # all non binned names in cr_g with current rule

            #create a new x1 based on above ruling
            if (k==1):
                x4a = pd.concat((resi_4, x3), axis=0)
            else:
                x4a = pd.concat((x4a, x3), axis=0)

            x4 = pd.merge(x4a, cr_g, left_on="name", right_on="name_2") # name_2 is already binned here
            x1 = merge_time_info(x4, used_ts)
<<<<<<< HEAD
            #x1 =  x1.loc[~(x1["name_1"]=="not specified")]
=======
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
            x1 = x1[~x1['name_1'].isin(not_spec['id'])]
            x1["rule"] = 5.7
            x1 = x1.drop_duplicates()

            if len(x2a)== len(x2):
                break
            x2 = x2a

        if ibs == 0:
            resi_5s = resi_5
            resi_5s["b_scheme"] = "s"
        if ibs == 1:
            resi_5y = resi_5
            resi_5y["b_scheme"] = "y"
        if ibs == 2:
            resi_5c = resi_5
            resi_5c["b_scheme"] = "c"
    if b_scheme == "cc":
        resi_5 = merge_cc(resi_5s, resi_5y, resi_5c, used_ts)
        resi_5['rule'] = 5.9


    resi_5 = pd.DataFrame.drop_duplicates(resi_5)
    resi_5 = resi_5[['name', 'oldest', 'youngest', 'ts_count', 'refs', 'rule']]
    combi_x = pd.concat([resi_0, resi_1, resi_2, resi_3, resi_4], axis=0, sort=False)
    resi_5 = resi_5[~resi_5["name"].isin(combi_x["name"])] # filter non-bio rule 1
    resi_5 = resi_5[~resi_5["name"].isin(used_ts['ts'])] # filter Dapingian problem
    print("rule 5 has ", len(resi_5), "binned relations")
    print("Rule 5:  relations among named non-biostratigraphical units that have indirect relations to binning scheme")
    print("via biostratigraphical units.")
    return resi_5

<<<<<<< HEAD
def rule6(results, cr_g, runrange, used_ts, xnames_raw, b_scheme, not_spec):
=======
def rule6(results, cr_g, runrange, used_ts, xnames_raw, b_scheme, not_spec, PBDB_id):
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
    resi_0 = results["rule_0"]
    resi_1 = results["rule_1"]
    resi_2 = results["rule_2"]
    resi_3 = results["rule_3"]
    resi_4 = results["rule_4"]

    ## search for shortest time bins among 5 & 6
    resis_nbio = pd.concat([resi_0, resi_2], axis=0)

    x1 = pd.merge(resis_nbio, cr_g, left_on="name", right_on="name_1")
    x1 = merge_time_info(x1, used_ts)
    x1 = x1[~x1["name_1"].isin(resi_0["name"])]
    x1 = x1[~x1["name_1"].isin(resi_2["name"])]# all first level linked non-bio* to rule 2
<<<<<<< HEAD
    #x1 =  x1.loc[~(x1["name_1"]=="not specified")]
=======
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
    x1 = x1[~x1['name_1'].isin(not_spec['id'])]
    x1["rule"] = 6.6 # only for control
    x1 = x1.drop_duplicates()

    x2 = cr_g[~cr_g["name_1"].isin(x1["name_1"])] # all not yet binned in cr_g
    x2 = pd.DataFrame.drop_duplicates(x2)
    resi_6 = pd.DataFrame([] * 6, index=["name", "oldest", "youngest", "ts_count", "refs", "rule"])
    resi_6 = pd.DataFrame.transpose(resi_6)
    for ibs in runrange:
        for k in np.arange(1,5,1):
<<<<<<< HEAD
            x3 = bin_names(ibs, x1, xnames_raw, bifu_selector='bfs2', result_selector=result_selector_2)
=======
            x3 = bin_names(ibs, PBDB_id, x1, xnames_raw, bifu_selector='bfs2', result_selector=result_selector_2)
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
            x3["rule"] = 6.0+((k-1)*0.1)
            x3b = x3[~x3["name"].isin(resi_6["name"])] # filter for already binned names
            resi_6 = pd.concat([resi_6, x3b], axis=0, sort=True) # appended to previous ruling; these are now binned

            #create a new x1 based on above ruling
            if (k==1):
                x4a = pd.concat((resi_3, x3), axis=0)
            else:
                x4a = pd.concat((x4a, x3), axis=0)

            x4 = pd.merge(x4a, cr_g, left_on="name", right_on="name_2") # name_2 is already binned here
            x1 = merge_time_info(x4, used_ts)
<<<<<<< HEAD
            #x1 =  x1.loc[~(x1["name_1"]=="not specified")]
=======
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
            x1 = x1[~x1['name_1'].isin(not_spec['id'])]
            x1["rule"] = 6.7
            x1 = x1.drop_duplicates()
            x2b = cr_g[~cr_g["name_1"].isin(x1["name_1"])] # all not yet binned in cr_g
            x2b = pd.DataFrame.drop_duplicates(x2b)

            if k == 1:
                x6 = x3 # das ist ok nach zweitem durchlauf
            if len(x2)== len(x2b):
                break
            x2 = x2b
        if ibs == 0:
            resi_6s = resi_6
            resi_6s["b_scheme"] = "s"
        if ibs == 1:
            resi_6y = resi_6
            resi_6y["b_scheme"] = "y"
        if ibs == 2:
            resi_6c = resi_6
            resi_6c["b_scheme"] = "c"

    if b_scheme == "cc":
        resi_6 = merge_cc(resi_6s, resi_6y, resi_6c, used_ts)
        resi_6['rule'] = 6.9

    resi_6 = pd.DataFrame.drop_duplicates(resi_6)
    resi_6 = resi_6[['name', 'oldest', 'youngest', 'ts_count', 'refs', 'rule']]
    combi_x = pd.concat([resi_0, resi_1, resi_2, resi_3, resi_4], axis=0, sort=False)
    resi_6 = resi_6[~resi_6["name"].isin(combi_x["name"])] # filter non-bio rule 1
    resi_6 = resi_6[~resi_6["name"].isin(used_ts['ts'])] 
    print("rule 6 has ", len(resi_6), "binned relations")
    print("Rule 6:  relations among named non-biostratigraphical units that have indirect relations to binning scheme")
    print("via non-biostratigraphical units.")
    return resi_6

def shortest_time_bins(results, used_ts):
    resi_0 = results["rule_0"]
    resi_1 = results["rule_1"]
    resi_2 = results["rule_2"]
    resi_3 = results["rule_3"]
    resi_4 = results["rule_4"]
    resi_5 = results["rule_5"]
    resi_6 = results["rule_6"]
    ## search for shortest time bins among 5 & 6
    # all where names of 5 and 6 in common and range is identical
    com_a = pd.merge(resi_5, resi_6,how='inner', on="name") # all names that 5 and 6 have in common
    cas = com_a.loc[com_a["youngest_x"]==com_a["youngest_y"],
                    ["name","rule_x","oldest_x", "youngest_x",
                     "ts_count_x", "refs_x", "oldest_y", "youngest_y", "ts_count_y", "refs_y"]]
    cas = cas.loc[cas["oldest_x"]==cas["oldest_y"],
                    ["name","rule_x","oldest_x", "youngest_x",
                     "ts_count_x", "refs_x", "oldest_y", "youngest_y", "ts_count_y", "refs_y"]]
    cas['refs'] = cas[['refs_x', 'refs_y']].apply(lambda x: ', '.join(x), axis=1)
    for k in cas.index.tolist():
        xs = pd.Series(cas.at[k,"refs"]).str.replace(",", '')
        xs = xs.str.split(pat = " ", expand=True)
        xs = xs.transpose()
        xs = pd.DataFrame.drop_duplicates(xs)
        xs = xs[0].apply(str)
        cas.at[k,"refs"]=xs.str.cat(sep=', ')
    com_56_r = cas[['name', 'oldest_x', 'youngest_x', 'ts_count_x', 'refs', 'rule_x']]
    com_56_r.columns = ['name', 'oldest', 'youngest', 'ts_count', 'refs', 'rule']
    com_56_r.loc[:,'rule'] = "5, 6" 

    # all where names of 5 and 6 in common and time length is identical
    car = com_a.loc[com_a["ts_count_x"]==com_a["ts_count_y"],
                    ["name","rule_x","oldest_x", "youngest_x", "oldest_y", "youngest_y",
                     "ts_count_x", "ts_count_y","refs_x", "refs_y"]]
    car = car[~car["name"].isin(cas["name"])]
    bnu = car["name"]
    bnu = bnu.drop_duplicates()
    bnurange = np.arange(0,len(bnu),1)
    com_56_d = pd.DataFrame([] * 6, index=["name", "oldest", "youngest", "ts_count", "refs", "rule"])
    for i in bnurange:
        i_name = bnu.iloc[i]
        car_sub = car.loc[car["name"]== i_name]
        car_suba = car_sub[['name', 'oldest_x', 'youngest_x', 'ts_count_x', 'refs_x']]
        car_suba.columns = ['name', 'oldest', 'youngest', 'ts_count', 'refs']
        car_subb = car_sub[['name', 'oldest_y', 'youngest_y', 'ts_count_y', 'refs_y']]
        car_subb.columns = ['name', 'oldest', 'youngest', 'ts_count', 'refs']
        car_sub  = pd.concat((car_suba, car_subb), axis=0)
        refs_f = pd.unique(car_sub['refs'])
        refs_f = pd.DataFrame(refs_f)
        refs_f = refs_f[0].apply(str)
        refs_f = refs_f.str.cat(sep=', ')
        cpts_youngest = pd.DataFrame([pd.unique(car_sub["youngest"])], index=["youngest"])
        cpts_youngest = cpts_youngest.transpose()
        cpts_oldest = pd.DataFrame([pd.unique(car_sub["oldest"])], index=["oldest"])
        cpts_oldest = cpts_oldest.transpose()
        res_youngest = car_sub["youngest"].iloc[0]
        res_oldest = car_sub["oldest"].iloc[0]
        ts_numbered = used_ts
<<<<<<< HEAD
        #ts_numbered['index1'] = used_ts.index # xchange BK
=======
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
        ts_numbered['index1'] = used_ts['ts_index'] # # xchange BK
        old_min = pd.merge(ts_numbered, cpts_oldest, left_on="ts", right_on="oldest")
        old_min = min(old_min["index1"])
        young_max = pd.merge(ts_numbered, cpts_youngest, left_on="ts", right_on="youngest")
        young_max = max(young_max["index1"])
        ts_c = young_max-old_min
<<<<<<< HEAD
        #res_youngest = ts_numbered.iloc[young_max] [0] # here is bug indexer out of bounds xchangeBK
        res_youngest = ts_numbered.iloc[young_max-1] [0] # corrected BK
        #res_oldest = ts_numbered.iloc[old_min] [0] # here is bug indexer out of bounds xchangeBK
=======
        res_youngest = ts_numbered.iloc[young_max-1] [0] # corrected BK
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
        res_oldest = ts_numbered.iloc[old_min-1] [0]  # corrected BK
        rule = "5, 6"
        com_56_da = pd.DataFrame([i_name, res_oldest,res_youngest, ts_c, refs_f, rule],
                           index=["name", "oldest", "youngest", "ts_count", "refs", "rule"])
        com_56_d = pd.concat([com_56_d, com_56_da], axis=1, sort=True)
    com_56_d = com_56_d.transpose()

    # all where names of 5 and 6 in common and duration is not similar
    # we take the complete range
    cau = com_a.loc[~(com_a["ts_count_x"] == com_a["ts_count_y"]),
                    ["name","rule_x","oldest_x", "youngest_x", "oldest_y", "youngest_y",
                     "ts_count_x", "ts_count_y","refs_x", "refs_y"]]
    bnu = cau["name"]
    bnu = bnu.drop_duplicates()
    bnurange = np.arange(0,len(bnu),1)
    rows = []
    for i in bnurange:
        i_name = bnu.iloc[i]
        cau_sub = cau.loc[cau["name"]== i_name]
        cau_suba = cau_sub[['name', 'oldest_x', 'youngest_x', 'ts_count_x', 'refs_x']]
        cau_suba.columns = ['name', 'oldest', 'youngest', 'ts_count', 'refs']
        cau_subb = cau_sub[['name', 'oldest_y', 'youngest_y', 'ts_count_y', 'refs_y']]
        cau_subb.columns = ['name', 'oldest', 'youngest', 'ts_count', 'refs']
        cau_sub  = pd.concat((cau_suba, cau_subb), axis=0)
        refs_f = pd.unique(cau_sub['refs'])
        refs_f = pd.DataFrame(refs_f)
        refs_f = refs_f[0].apply(str)
        refs_f = refs_f.str.cat(sep=', ')
        cpts_youngest = pd.DataFrame([pd.unique(cau_sub["youngest"])], index=["youngest"])
        cpts_youngest = cpts_youngest.transpose()
        cpts_oldest = pd.DataFrame([pd.unique(cau_sub["oldest"])], index=["oldest"])
        cpts_oldest = cpts_oldest.transpose()
        res_youngest = cau_sub["youngest"].iloc[0]
        res_oldest = cau_sub["oldest"].iloc[0]
        ts_numbered = used_ts
<<<<<<< HEAD
        #ts_numbered['index1'] = used_ts.index # xchange BK
=======
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
        ts_numbered['index1'] = used_ts['ts_index']
        old_min = pd.merge(ts_numbered, cpts_oldest, left_on="ts", right_on="oldest")
        old_min = min(old_min["index1"])
        young_max = pd.merge(ts_numbered, cpts_youngest, left_on="ts", right_on="youngest")
        young_max = max(young_max["index1"])
<<<<<<< HEAD
        ts_c = young_max-old_min
       
        res_youngest = ts_numbered.iloc[young_max-1] [0] # corrected
        #res_oldest = ts_numbered.iloc[old_min] [0] # here is bug indexer out of bounds xchangeBK
=======
        ts_c = young_max-old_min      
        res_youngest = ts_numbered.iloc[young_max-1] [0] # corrected
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
        res_oldest = ts_numbered.iloc[old_min-1] [0] # corrected
        rows.append((i_name, res_oldest,res_youngest, ts_c, refs_f, "5, 6"))
    com_56_s = pd.DataFrame(rows, columns=["name", "oldest", "youngest", "ts_count", "refs", "rule"])

    # all where 5 and 6 are not in common
    combi_56a = pd.concat([com_56_r, com_56_d, com_56_s], axis=0, sort=False)
    bnu = combi_56a["name"]
    c6 = resi_6[~resi_6["name"].isin(bnu)]
    c5 = resi_5[~resi_5["name"].isin(bnu)]

    combi_56 = pd.concat([com_56_r, com_56_d, com_56_s], axis=0, sort=False)
    combi_names = pd.concat([resi_0, resi_1, resi_2, resi_3, resi_4,
                             c5, combi_56, c6], axis=0, sort=False)

    return(combi_names)

def merge_cc(resi_s, resi_y, resi_c, used_ts):
    resi = pd.concat([resi_s, resi_y, resi_c])
    x2 = pd.merge(resi, used_ts, how= 'inner', left_on="oldest", right_on="ts")
    x2 = x2[['name', 'oldest', 'ts_index', 'youngest', 'ts_count',
             'refs', 'rule', "b_scheme"]]
    x2.rename(inplace=True, columns={'ts_index': 'oldest_index'})
    x2 = pd.merge(x2, used_ts, how= 'inner', left_on="youngest", right_on="ts")
    x2 = x2[['name', 'oldest', 'oldest_index', 'youngest', 'ts_index','ts_count',
             'refs', 'rule', "b_scheme"]]
    x2.rename(inplace=True, columns={'ts_index': 'youngest_index'})

    xal = pd.merge(pd.merge(resi_s,resi_y,on='name'),resi_c,on='name')

    # Sort x2 so binary search can be used to quickly find ranges
    x2 = x2.sort_values(by=['name', 'b_scheme'])

    # Create props to access column names easily
    col = column_names_as_props(x2)
    used_ts_col = column_names_as_props(used_ts)

    # Use data frames' underlying ndarrays directly
    x2 = x2.values
    used_ts = used_ts.values

    # Array to store results
    rows = []

    for i_name in xal["name"].dropna().unique():
    #i=2
        # Select range from data table
        x2_sub = x2[bisect_left(x2[:, col.name], i_name):bisect_right(x2[:, col.name], i_name)]

        # We need the oldest and youngest index in the ranges
        x2_subs = x2_sub[x2_sub[:, col.b_scheme] == 's']
        x2_suby = x2_sub[x2_sub[:, col.b_scheme] == 'y']
        x2_subc = x2_sub[x2_sub[:, col.b_scheme] == 'c']

        # youngest = max, oldest = min index
        x_range_s = np.array([np.min(x2_subs[:, col.oldest_index])])
        x_range_y = np.array([np.min(x2_suby[:, col.oldest_index])])
        x_range_c = np.array([np.min(x2_subc[:, col.oldest_index])])

        if np.min(x2_subs[:, col.oldest_index]) != np.max(x2_subs[:, col.youngest_index]):
            x_range_s = np.arange(np.min(x2_subs[:, col.oldest_index]), np.max(x2_subs[:, col.youngest_index])+1,1)
        if np.min(x2_suby[:, col.oldest_index]) != max(x2_suby[:, col.youngest_index]):
            x_range_y = np.arange(np.min(x2_suby[:, col.oldest_index]), np.max(x2_suby[:, col.youngest_index])+1,1)
        if np.min(x2_subc[:, col.oldest_index]) != max(x2_subc[:, col.youngest_index]):
            x_range_c = np.arange(np.min(x2_subc[:, col.oldest_index]), np.max(x2_subc[:, col.youngest_index])+1,1)

        rax = np.concatenate((x_range_s, x_range_y, x_range_c))
        # filter for third quantile, only bins with highest score
        rax_counts = np.unique(rax, return_counts=True) #rax_counts[0] is ts_bins, rax_counts[1] is counts
        rq = round(np.quantile(rax_counts[1], 0.75),0)
        rax_counts = rax_counts[0][rax_counts[1] >= rq]
        rax_sub = used_ts[np.isin(used_ts[:, 1], rax_counts)] # Inner join on table with only one column is identical to filtering

        max_ts_index = np.max(rax_sub[:, used_ts_col.ts_index])
        min_ts_index = np.min(rax_sub[:, used_ts_col.ts_index])

        x_youngest = rax_sub[rax_sub[:, used_ts_col.ts_index] == max_ts_index]
        x_oldest = rax_sub[rax_sub[:, used_ts_col.ts_index] == min_ts_index]

        ts_c = max_ts_index - min_ts_index

        # Collect unique references and concatenate them
        refs = set()
        for ref in x2_sub[:, col.refs]:
            for r in ref.split(', '):
                refs.add(r)

        refs_f = ', '.join(list(refs))

        rows.append((i_name, x_oldest[0, used_ts_col.ts], x_youngest[0, used_ts_col.ts], float(ts_c), refs_f))

    return pd.DataFrame(rows, columns=["name", "oldest", "youngest", "ts_count", "refs"])

def merge_time_info(x1, used_ts):
    columns = ['name_1', 'name_2', 'oldest', 'oldest_index', 'youngest', 'youngest_index', 'ts_count', 'refs',
        'rule', 'reference_id', "reference_year"]
    x1 = pd.merge(x1, used_ts, how= 'inner', left_on="oldest", right_on="ts") # time bin info is added here
    x1.rename(inplace=True, columns={'ts_index': 'oldest_index'})
    x1 = pd.merge(x1, used_ts, how= 'inner', left_on="youngest", right_on="ts") # time bin info is added here
    x1.rename(inplace=True, columns={'ts_index': 'youngest_index'})

    # Select appropriate columns
    x1 = x1[columns]

    # Swap name_1 and name_2 columns
    x1.rename(inplace=True, columns={
        'name_1': 'name_2',
        'name_2': 'name_1'
    })

    # x1 columns are now [name_2, name_1...]
    # x1m picks [name_1, name_2...]
    x1m = x1[columns]
    # Reset x1 column order for concatenation
    x1.columns = columns
    return pd.concat((x1,x1m), axis=0)

def column_names_as_props(df):
    # This function returns an object whose properties are the data frame's columns
    # and their values are the columns index.
    # E.g., for data frame with columns [name, reference, count] the returned object
    # has obj.name = 0, obj.reference = 1, and obj.count = 2
    return SimpleNamespace(**{k: v for v, k in enumerate(df.columns)})

def result_selector_1(name, data, col):
    # Concatenate references
    refs_f = ', '.join(map(str, np.unique(data[:, col.reference_id])))

    # youngest, oldest and ts_count
    ts_max = np.max(data[:, col.ts_index])
    ts_min = np.min(data[:, col.ts_index])
    ts_c = ts_max - ts_min

    youngest = data[data[:, col.ts_index] == ts_max]
    oldest = data[data[:, col.ts_index] == ts_min]

    return (name, oldest[0, col.ts], youngest[0, col.ts], ts_c, refs_f)

def result_selector_2(name, data, col):
    # Concatenate references
    refs_f = ', '.join(map(str, np.unique(data[:, col.reference_id])))

    # youngest, oldest and ts_count
    youngest_value = np.max(data[:, col.youngest_index])
    oldest_value = np.min(data[:, col.oldest_index])
    ts_c = youngest_value - oldest_value

    # find index of rows with maximum youngest_index and minimum oldest_index
    youngest = np.argmax(data[:, col.youngest_index])
    oldest = np.argmin(data[:, col.oldest_index])

    return (name, data[oldest, col.oldest], data[youngest, col.youngest], ts_c, refs_f)

<<<<<<< HEAD
def bin_names(ibs, ntts, xnames_raw, bifu_selector, result_selector=result_selector_1):
=======
def bin_names(ibs, PBDB_id, ntts, xnames_raw, bifu_selector, result_selector=result_selector_1):
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d
    if ntts.empty:
        return pd.DataFrame([], columns=["name", "oldest", "youngest", "ts_count", "refs"])

    col = SimpleNamespace()
    col.ntts = column_names_as_props(ntts)
    col.xnames = column_names_as_props(xnames_raw)

    bnu = pd.unique(ntts["name_1"])

    # Sort tables so ranges can be selected
    ntts = ntts.sort_values(by = ['name_1'])
    xnames_raw = xnames_raw.sort_values(by='name')

    # Use data frame's numpy ndarrays directly
    ntts = ntts.values
    xnames_raw = xnames_raw.values

    rows = []
    for name in bnu:
        # Select appropriate ranges from tables
        ntts_begin = bisect_left(ntts[:, col.ntts.name_1], name)
        ntts_end = bisect_right(ntts[:, col.ntts.name_1], name)
        xnames_begin = bisect_left(xnames_raw[:, col.xnames.name], name)
        xnames_end = bisect_right(xnames_raw[:, col.xnames.name], name)

        # No references for this name
        if xnames_begin == len(xnames_raw[:, col.xnames.name]):
            continue

        data = ntts[ntts_begin:ntts_end]
        xnames = xnames_raw[xnames_begin:xnames_end]

        # filter for references with "not specified"
        data = data[~np.isin(data[:, col.ntts.reference_id], xnames[:, col.xnames.ref])]

        if data.size == 0:
            continue

        # Filter data based on binning function in question
        if ibs == 0:
            if bifu_selector=='bfs':
<<<<<<< HEAD
                data = rn_funs.bifu_s(col.ntts, data)
            if bifu_selector=='bfs2':
                data = rn_funs.bifu_s2(col.ntts, data) 
        if ibs == 1:
            data = rn_funs.bifu_y(col.ntts, data)
        if ibs == 2:
            data = rn_funs.bifu_c(col.ntts, data)
=======
                data = rn_funs.bifu_s(col.ntts, data, PBDB_id)
            if bifu_selector=='bfs2':
                data = rn_funs.bifu_s2(col.ntts, data, PBDB_id) 
        if ibs == 1:
            data = rn_funs.bifu_y(col.ntts, data, PBDB_id)
        if ibs == 2:
            data = rn_funs.bifu_c(col.ntts, data, PBDB_id)
>>>>>>> 79ccdca133298101714b32f8f37e5df26040c51d

        # Use selector function to produce final result
        rows.append(result_selector(name, data, col.ntts))

    ret = pd.DataFrame(rows, columns=["name", "oldest", "youngest", "ts_count", "refs"])
    ret = pd.DataFrame.drop_duplicates(ret)
    ret.dropna()
    return ret
