#!/usr/bin/env python
# coding: utf-8

import time
import csv
import pandas as pd
import numpy as np
#from rnames_app.utils import rn_funs
from bisect import (bisect_left, bisect_right)
from types import SimpleNamespace
from .rn_funs import *

def bin_fun (c_rels, binning_scheme, binning_algorithm, xrange, time_slices, info):

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

    # Binning schemes

    if binning_scheme == "r":
        used_ts = time_slices['rassm']
        t_scheme = "TimeSlice_Rassmussen"
    if binning_scheme == "w":
        used_ts = time_slices['webby']
        t_scheme = "TimeSlice_Webby"
    if binning_scheme == "b":
        used_ts = time_slices['berg']
        t_scheme = "TimeSlice_Bergstrom"
    if binning_scheme == "s":
        used_ts = time_slices['stages']
        t_scheme = "Stage"
    if binning_scheme == "p":
        used_ts = time_slices['periods']
        t_scheme = "Period"

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
        xnames_raw["combi"] = xnames_raw1["name"] + xnames_raw1["ref"].astype(str).copy()
    #xnamelist = xnames_raw["combi"].tolist()

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
    results['rule_0'] = rule0(c_rels_d, t_scheme, runrange, used_ts, xnames_raw, b_scheme)
    info.update()

    ##############################################################
    ##############################################################
    #rule 1 = all direct relations between biostrat names and binning scheme
    results['rule_1'] = rule1(c_rels_d, t_scheme, runrange, used_ts, xnames_raw, b_scheme)
    info.update()

    ##############################################################
    ##############################################################
    ### Rule_2: direct relations between non-bio* with binning scheme
    ### except chronostratigraphy
    results['rule_2'] = rule2(results, c_rels_d, t_scheme, runrange, used_ts, xnames_raw, b_scheme)
    info.update()

    ##############################################################
    ##############################################################
    # the second tier has two binning rules and bins all indirect names via biostrat

    ##############################################################
    ##############################################################
    #rule_3 all relations between biostrat and biostrat that refer indirectly to binning scheme
    results['rule_3'] = rule3(results, c_rels, t_scheme, runrange, used_ts, xnames_raw, b_scheme)
    info.update()

    ##############################################################
    resis_bio = pd.concat([results['rule_1'], results['rule_3']], axis=0)
    resis_bio = pd.DataFrame.drop_duplicates(resis_bio)
    ### Rule 4: indirect relations of non-bio via resis_bio to binning scheme
    ### except direct chronostratigraphy links
    results['rule_4'] = rule4(results, resis_bio, c_rels, t_scheme, runrange, used_ts, xnames_raw, b_scheme)
    info.update()

    ##################################################################################
    cr_g = c_rels.loc[~(c_rels["strat_qualifier_1"]=="Biostratigraphy")
                              & ~(c_rels["strat_qualifier_2"]=="Biostratigraphy")
                              & ~(c_rels["qualifier_name_1"]==t_scheme)
                              & ~(c_rels["qualifier_name_2"]==t_scheme),
                              ["reference_id","name_1","name_2", "reference_year"]]
    ### Rule 5:  indirect relations of non-bio* to resis_4 with link to bio* (route via resi_4)
    results['rule_5'] = rule5(results, cr_g, resis_bio, c_rels, t_scheme, runrange, used_ts, xnames_raw, b_scheme)
    info.update()

    ##################################################################################
    ### Rule 6: indirect relations of non-bio* to resis_bio to binning scheme (route via resis_bio)
    #rule 6 corrected at 23.03.2020
    results['rule_6'] = rule6(results, cr_g, runrange, used_ts, xnames_raw, b_scheme)
    info.update()

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
    info.update()
    dura2 = (end - start)/60
    print("We find", len(combi_names),
          "binned names. It took ", round(dura, 2), "+", round(dura2, 2),  "minutes.")
    return combi_names

def rule0(c_rels_d, t_scheme, runrange, used_ts, xnames_raw, b_scheme):
    cr_x = c_rels_d.loc[((c_rels_d["strat_qualifier_1"]=="Chronostratigraphy"))
                              & ((c_rels_d["qualifier_name_2"]==t_scheme)),
                              ["reference_id","name_1","name_2", "ts", "ts_index", "reference_year"]]

    cr_x =  cr_x.loc[~(cr_x["name_1"]=="not specified")]

    for ibs in runrange:
        resi_0 = bin_unique_names_0(ibs, cr_x, xnames_raw)
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

def rule1(c_rels_d, t_scheme, runrange, used_ts, xnames_raw, b_scheme):
    #rule 1 = all direct relations between biostrat names and binning scheme
    cr_a = c_rels_d.loc[((c_rels_d["strat_qualifier_1"]=="Biostratigraphy"))
                              & ((c_rels_d["qualifier_name_2"]==t_scheme)),
                              ["reference_id","name_1","name_2", "ts", "ts_index", "reference_year"]]
    #take out  relations that also relate to not specified in same reference
    cr_a =  cr_a.loc[~(cr_a["name_1"]=="not specified")]

    for ibs in runrange:
        resi_1 = bin_unique_names_0(ibs, cr_a, xnames_raw)
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

def rule2(results, c_rels_d, t_scheme, runrange, used_ts, xnames_raw, b_scheme):
    resi_0 = results["rule_0"]
    ### Rule_2: direct relations between non-bio* with binning scheme
    ### except chronostratigraphy
    cr_c = c_rels_d.loc[~(c_rels_d["strat_qualifier_1"]=="Biostratigraphy")
                          & ~(c_rels_d["strat_qualifier_1"]=="Chronostratigraphy")
                          & (c_rels_d["qualifier_name_2"]==t_scheme),
                              ["reference_id","name_1","name_2", "ts", "ts_index", "reference_year"]]
    cr_c =  cr_c.loc[~(cr_c["name_1"]=="not specified")]

    for ibs in runrange:
        resi_2 = bin_unique_names_0(ibs, cr_c, xnames_raw)
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

def rule3(results, c_rels, t_scheme, runrange, used_ts, xnames_raw, b_scheme):
    resi_1 = results["rule_1"]
    #rule_3 all relations between biostrat and biostrat that refer indirectly to binning scheme
    cr_b = c_rels.loc[(c_rels["strat_qualifier_1"]=="Biostratigraphy")
                                  & (c_rels["strat_qualifier_2"]=="Biostratigraphy")
                                  &  ~(c_rels["qualifier_name_1"] == t_scheme)
                                  &  ~(c_rels["qualifier_name_2"] == t_scheme),
                                  ["reference_id","name_1","name_2", "reference_year"]]

    x1 = pd.merge(resi_1, cr_b, left_on="name", right_on="name_2") # name_2 is already binned here
    x1 = merge_time_info(x1, used_ts)
    x1 =  x1.loc[~(x1["name_1"]=="not specified")]
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
            x3 = bin_unique_names_1(ibs, x1, xnames_raw)
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
            x1 =  x1.loc[~(x1["name_1"]=="not specified")]
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

def rule4(results, resis_bio, c_rels, t_scheme, runrange, used_ts, xnames_raw, b_scheme):
    resi_0 = results["rule_0"]
    resi_1 = results["rule_1"]
    resi_2 = results["rule_2"]
    resi_3 = results["rule_3"]
    ### Rule 4: indirect relations of non-bio via resis_bio to binning scheme
    ### except direct chronostratigraphy links

    cr_d = c_rels.loc[~(c_rels["strat_qualifier_1"]=="Biostratigraphy")
                              & (c_rels["strat_qualifier_2"]=="Biostratigraphy")
                              & ~(c_rels["qualifier_name_1"]==t_scheme)
                              & ~(c_rels["qualifier_name_2"]==t_scheme),
                              ["reference_id","name_1","name_2", "reference_year"]]

    cr_d =  cr_d[~cr_d["name_1"].isin(resi_0["name"])] #filter for chronostrat rule 0

    x1 = pd.merge(resis_bio, cr_d, left_on="name", right_on="name_2") # name_2 is already binned here
    x1 = merge_time_info(x1, used_ts)
    x1 = x1[~x1["name_1"].isin(resi_2["name"])] # filter non-bio rule 2
    x1 =  x1[~x1["name_1"].isin(resi_0["name"])] # filter direct chronostrat rule 0
    x1 =  x1.loc[~(x1["name_1"]=="not specified")] # filter "Not specified"
    x1["rule"] = 4.6
    x1 = x1.drop_duplicates()

    x2 = cr_d[~cr_d["name_1"].isin(resis_bio["name"])]

    resi_4 = pd.DataFrame([] * 6, index=["name", "oldest", "youngest", "ts_count", "refs", "rule"])
    resi_4 = pd.DataFrame.transpose(resi_4)
    for ibs in runrange:
        for k in np.arange(1,5,1):
            x3 = bin_unique_names_1(ibs, x1, xnames_raw)
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
            x1 =  x1.loc[~(x1["name_1"]=="not specified")]
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

def rule5(results, cr_g, resis_bio, c_rels, t_scheme, runrange, used_ts, xnames_raw, b_scheme):
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
    x1 =  x1.loc[~(x1["name_1"]=="not specified")]
    x1["rule"] = 5.0
    x1 = x1.drop_duplicates()

    x2 = cr_g[~cr_g["name_2"].isin(resis_bio["name"])]

    resi_5 = pd.DataFrame([] * 6, index=["name", "oldest", "youngest", "ts_count", "refs", "rule"])
    resi_5 = pd.DataFrame.transpose(resi_5)
    for ibs in runrange:
        for k in np.arange(1,5,1):
            x3 = bin_unique_names_1(ibs, x1, xnames_raw)
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
            x1 =  x1.loc[~(x1["name_1"]=="not specified")]
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

def rule6(results, cr_g, runrange, used_ts, xnames_raw, b_scheme):
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
    x1 =  x1.loc[~(x1["name_1"]=="not specified")]
    x1["rule"] = 6.6 # only for control
    x1 = x1.drop_duplicates()

    x2 = cr_g[~cr_g["name_1"].isin(x1["name_1"])] # all not yet binned in cr_g
    x2 = pd.DataFrame.drop_duplicates(x2)
    resi_6 = pd.DataFrame([] * 6, index=["name", "oldest", "youngest", "ts_count", "refs", "rule"])
    resi_6 = pd.DataFrame.transpose(resi_6)
    for ibs in runrange:
        for k in np.arange(1,5,1):
            x3 = bin_unique_names_1(ibs, x1, xnames_raw)
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
            x1 =  x1.loc[~(x1["name_1"]=="not specified")]
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
    resi_6 = resi_6[~resi_6["name"].isin(used_ts['ts'])] # filter Dapingian problem
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
    com_56_r.loc[:,'rule'] = "5, 6" # this is the place where the erreor message come from, may be in line 815 add the value

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
        ts_numbered['index1'] = used_ts.index
        old_min = pd.merge(ts_numbered, cpts_oldest, left_on="ts", right_on="oldest")
        old_min = min(old_min["index1"])
        young_max = pd.merge(ts_numbered, cpts_youngest, left_on="ts", right_on="youngest")
        young_max = max(young_max["index1"])
        ts_c = young_max-old_min
        res_youngest = ts_numbered.iloc[young_max] [0]
        res_oldest = ts_numbered.iloc[old_min] [0]
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
        ts_numbered['index1'] = used_ts.index
        old_min = pd.merge(ts_numbered, cpts_oldest, left_on="ts", right_on="oldest")
        old_min = min(old_min["index1"])
        young_max = pd.merge(ts_numbered, cpts_youngest, left_on="ts", right_on="youngest")
        young_max = max(young_max["index1"])
        ts_c = young_max-old_min
        res_youngest = ts_numbered.iloc[young_max] [0]
        res_oldest = ts_numbered.iloc[old_min] [0]
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
    k_oldest_index = 2
    k_youngest_index = 4
    k_ref = 6
    k_b_scheme = 8

    resi = pd.concat([resi_s, resi_y, resi_c])
    x2 = pd.merge(resi, used_ts, how= 'inner', left_on="oldest", right_on="ts")
    x2 = x2[['name', 'oldest', 'ts_index', 'youngest', 'ts_count',
             'refs', 'rule', "b_scheme"]]
    x2.rename(inplace=True, columns={'ts_index': 'oldest_index'})
    x2 = pd.merge(x2, used_ts, how= 'inner', left_on="youngest", right_on="ts")
    x2 = x2[['name', 'oldest', 'oldest_index', 'youngest', 'ts_index','ts_count',
             'refs', 'rule', "b_scheme"]]
    x2.rename(inplace=True, columns={'ts_index': 'youngest_index'})
    rows = []

    xal = pd.merge(pd.merge(resi_s,resi_y,on='name'),resi_c,on='name')

    # Sort x2 so binary search can be used to quickly find ranges
    x2 = x2.sort_values(by=['name', 'b_scheme'])
    x2 = x2.values
    used_ts = used_ts.values

    for i_name in xal["name"].dropna().unique():
    #i=2
        x2_sub = x2[bisect_left(x2[:, 0], i_name):bisect_right(x2[:, 0], i_name)]

        # We need the oldest and youngest index in the ranges
        x2_subs = x2_sub[bisect_left(x2_sub[:, k_b_scheme], 's'):bisect_right(x2_sub[:, k_b_scheme], 's')]
        x2_suby = x2_sub[bisect_left(x2_sub[:, k_b_scheme], 'y'):bisect_right(x2_sub[:, k_b_scheme], 'y')]
        x2_subc = x2_sub[bisect_left(x2_sub[:, k_b_scheme], 'c'):bisect_right(x2_sub[:, k_b_scheme], 'c')]
        # youngest = max, oldest = min index
        x_range_s = np.array([np.min(x2_subs[:, k_oldest_index])])
        x_range_y = np.array([np.min(x2_suby[:, k_oldest_index])])
        x_range_c = np.array([np.min(x2_subc[:, k_oldest_index])])

        if np.min(x2_subs[:, k_oldest_index]) != np.max(x2_subs[:, k_youngest_index]):
            x_range_s = np.arange(np.min(x2_subs[:, k_oldest_index]), np.max(x2_subs[:, k_youngest_index])+1,1)
        if np.min(x2_suby[:, k_oldest_index]) != max(x2_suby[:, k_youngest_index]):
            x_range_y = np.arange(np.min(x2_suby[:, k_oldest_index]), np.max(x2_suby[:, k_youngest_index])+1,1)
        if np.min(x2_subc[:, k_oldest_index]) != max(x2_subc[:, k_youngest_index]):
            x_range_c = np.arange(np.min(x2_subc[:, k_oldest_index]), np.max(x2_subc[:, k_youngest_index])+1,1)

        rax = np.concatenate((x_range_s, x_range_s, x_range_c))
        # filter for third quantile, only bins with highest score
        rax_counts = np.unique(rax, return_counts=True) #rax_counts[0] is ts_bins, rax_counts[1] is counts
        rq = round(np.quantile(rax_counts[1], 0.75),0)
        rax_counts = rax_counts[0][rax_counts[1] >= rq]

        # used_ts column indices
        k_ts = 0
        k_ts_index = 1

        # Inner join on table with only one column is identical to filtering
        rax_sub = used_ts[np.isin(used_ts[:, 1], rax_counts)]

        rax_sub_max = np.max(rax_sub[:, k_ts_index])
        rax_sub_min = np.min(rax_sub[:, k_ts_index])

        x_youngest = rax_sub[rax_sub[:, k_ts_index] == rax_sub_max]
        x_oldest = rax_sub[rax_sub[:, k_ts_index] == rax_sub_min]

        ts_c = rax_sub_max - rax_sub_min

        refs = set()
        for ref in x2_sub[:, k_ref]:
            for r in ref.split(', '):
                refs.add(r)

        refs_f = ', '.join(list(refs))

        rows.append((i_name, x_oldest[0, k_ts], x_youngest[0, k_ts], float(ts_c), refs_f))

    return pd.DataFrame(rows, columns=["name", "oldest", "youngest", "ts_count", "refs"])

def merge_time_info(x1, used_ts):
    columns = ['name_1', 'name_2', 'oldest', 'oldest_index', 'youngest', 'youngest_index', 'ts_count', 'refs',
        'rule', 'reference_id', "reference_year"]
    x1 = pd.merge(x1, used_ts, how= 'inner', left_on="oldest", right_on="ts") # time bin info is added here
    x1.rename(inplace=True, columns={'ts_index': 'oldest_index'})
    x1 = pd.merge(x1, used_ts, how= 'inner', left_on="youngest", right_on="ts") # time bin info is added here
    x1.rename(inplace=True, columns={'ts_index': 'youngest_index'})
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

def bin_unique_names_0(ibs, cr_x, xnames_raw):
    if cr_x.empty:
        return pd.DataFrame([], columns=["name", "oldest", "youngest", "ts_count", "refs"])
    col = SimpleNamespace()
    col.ntts = SimpleNamespace(**{k: v for v, k in enumerate(cr_x.columns)})
    col.xnames = SimpleNamespace(**{k: v for v, k in enumerate(xnames_raw.columns)})

    bnu = pd.unique(cr_x["name_1"])
    # Data is sorted to quickly find the range in the dataframe matching a given name
    # The data is further sorted to enable quick filtering in bifu_s
    cr_x = cr_x.sort_values(by = ['name_1', 'reference_id', 'ts_index'])
    cr_x = cr_x.values
    # References is sorted by name to find rows matching a name with binary search
    xnames_raw = xnames_raw.sort_values(by='name')
    xnames_raw = xnames_raw.values

    rows = []
    for name in bnu:
        cr_x_begin = bisect_left(cr_x[:, col.ntts.name_1], name)
        cr_x_end = bisect_right(cr_x[:, col.ntts.name_1], name)
        xnames_begin = bisect_left(xnames_raw[:, col.xnames.name], name)
        xnames_end = bisect_right(xnames_raw[:, col.xnames.name], name)

        if xnames_begin == len(xnames_raw[col.xnames.name]):
            continue

        data = cr_x[cr_x_begin:cr_x_end]
        xnames = xnames_raw[xnames_begin:xnames_end]

        data = data[~np.isin(data[:, col.ntts.reference_id], xnames[:, col.xnames.ref])]

        if data.size == 0:
            continue

        # select all references
        if ibs == 0:
            data = bifu_s(col, data, xnames)
        if ibs == 1:
            data = bifu_y(col, data, xnames)
        if ibs == 2:
            data = bifu_c(col, data, xnames)

        # and collect the references which have that opinions
        refs_f = ', '.join(map(str, np.unique(data[:, col.ntts.reference_id])))

        # youngest, oldest and ts_count
        ts_max = np.max(data[:, col.ntts.ts_index])
        ts_min = np.min(data[:, col.ntts.ts_index])
        ts_c = ts_max - ts_min

        youngest = data[data[:, col.ntts.ts_index] == ts_max]
        oldest = data[data[:, col.ntts.ts_index] == ts_min]

        rows.append((name, oldest[0, col.ntts.ts], youngest[0, col.ntts.ts], ts_c, refs_f))

    ret = pd.DataFrame(rows, columns=["name", "oldest", "youngest", "ts_count", "refs"])
    return ret.dropna()

def bin_unique_names_1(ibs, x1, xnames_raw):
    if x1.empty:
        return pd.DataFrame([], columns=["name", "oldest", "youngest", "ts_count", "refs"])

    col = SimpleNamespace()
    col.ntts = SimpleNamespace(**{k: v for v, k in enumerate(x1.columns)})
    col.xnames = SimpleNamespace(**{k: v for v, k in enumerate(xnames_raw.columns)})

    rows = []
    # Data is sorted by name and reference year
    # Only rows matching the name are passed to the binning functions.
    # Finding these ranges can be done quickly from the sorted data with binary search
    # Within each name the rows are sorted by reference year allowing fast filtering in the binning functions.
    x1 = x1.sort_values(by=['name_1', 'reference_year'])
    # References is sorted by name to find rows matching a name with binary search
    xnames_raw = xnames_raw.sort_values(by='name')
    x1_list = list(x1['name_1'])
    xnames_list = list(xnames_raw['name'])

    x1 = x1.values
    xnames_raw = xnames_raw.values

    for name in np.unique(x1_list):
        x1_begin = bisect_left(x1_list, name)
        x1_end = bisect_right(x1_list, name)
        xnames_begin = bisect_left(xnames_list, name)
        xnames_end = bisect_right(xnames_list, name)

        if xnames_begin == len(xnames_raw):
            continue

        data = x1[x1_begin:x1_end]
        xnames = xnames_raw[xnames_begin:xnames_end]

        data = data[~np.isin(data[:, col.ntts.reference_id], xnames[:, col.xnames.ref])]

        if data.size == 0:
            continue

        if ibs == 0:
            data = bifu_s2(col, data, xnames)
        if ibs == 1:
            data = bifu_y2(col, data, xnames)
        if ibs == 2:
            data = bifu_c2(col, data, xnames)

        refs_f = ', '.join(map(str, np.unique(data[:, col.ntts.reference_id])))

        youngest_value = np.max(data[:, col.ntts.youngest_index])
        oldest_value = np.min(data[:, col.ntts.oldest_index])
        ts_c = oldest_value - youngest_value

        youngest = np.argmax(data[:, col.ntts.youngest_index])
        oldest = np.argmin(data[:, col.ntts.oldest_index])

        rows.append((name, data[oldest, col.ntts.oldest], data[youngest, col.ntts.youngest], ts_c, refs_f))


    x3 = pd.DataFrame(rows, columns=["name", "oldest", "youngest", "ts_count", "refs"])
    x3 = pd.DataFrame.drop_duplicates(x3)
    x3 = x3.dropna()
    return x3