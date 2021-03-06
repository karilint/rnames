#!/usr/bin/env python
# coding: utf-8

import time
import csv
import pandas as pd
import numpy as np
#from rnames_app.utils import rn_funs
import rn_funs

def bin_fun (c_rels, binning_scheme, binning_algorithm, xrange):

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
        used_ts = rn_funs.rassm_ts
        t_scheme = "TimeSlice_Rassmussen"
    if binning_scheme == "w":
        used_ts = rn_funs.webby_ts
        t_scheme = "TimeSlice_Webby"
    if binning_scheme == "b":
        used_ts = rn_funs.berg_ts
        t_scheme = "TimeSlice_Bergstrom"
    if binning_scheme == "s":
        used_ts = rn_funs.stages_ts
        t_scheme = "Stage"
    if binning_scheme == "p":
        used_ts = rn_funs.periods_ts
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
    xnames_raw["combi"] = xnames_raw1["name"] + xnames_raw1["ref"].astype(str).copy()
    #xnames_raw.to_csv("xnames.csv", index = False, header=True)
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
    #rule 0 = all direct relations between chronostrat names and binning scheme
    cr_x = c_rels_d.loc[((c_rels_d["strat_qualifier_1"]=="Chronostratigraphy"))
                              & ((c_rels_d["qualifier_name_2"]==t_scheme)),
                              ["reference_id","name_1","name_2", "ts", "ts_index", "reference_year"]]

    cr_x =  cr_x.loc[~(cr_x["name_1"]=="not specified")]
    bnu = cr_x["name_1"]
    bnu = bnu.drop_duplicates()
    bnurange = np.arange(0,len(bnu),1)

    for ibs in runrange:
        resi_0 = pd.DataFrame([] * 5, index=["name", "oldest", "youngest", "ts_count", "refs"])
        resi_0 = pd.DataFrame.transpose(resi_0)
        for i in bnurange:
            if ibs == 0:
                resi_0a = rn_funs.bifu_s(cr_x.loc[cr_x["name_1"]==bnu.iloc[i]], used_ts, xnames_raw)
            if ibs == 1:
                resi_0a = rn_funs.bifu_y(cr_x.loc[cr_x["name_1"]==bnu.iloc[i]], used_ts, xnames_raw)
            if ibs == 2:
                resi_0a = rn_funs.bifu_c(cr_x.loc[cr_x["name_1"]==bnu.iloc[i]], used_ts, xnames_raw)
            resi_0 = pd.concat([resi_0, resi_0a], axis=0, sort=True)
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
        resi_0 = pd.concat([resi_0s, resi_0y, resi_0c])
        x1 = pd.merge(resi_0, used_ts, how= 'inner', left_on="oldest", right_on="ts")
        x1 = x1[['name', 'oldest', 'ts_index', 'youngest', 'ts_count',
                 'refs', 'rule', "b_scheme"]]
        x1.columns = ['name', 'oldest', 'oldest_index', 'youngest', 'ts_count',
                      'refs', 'rule', "b_scheme"]
        x1 = pd.merge(x1, used_ts, how= 'inner', left_on="youngest", right_on="ts")
        x1 = x1[['name', 'oldest', 'oldest_index', 'youngest', 'ts_index','ts_count',
                 'refs', 'rule', "b_scheme"]]
        x1.columns = ['name', 'oldest', 'oldest_index', 'youngest', 'youngest_index', 'ts_count',
                      'refs', 'rule', "b_scheme"]
        x_resi = pd.DataFrame([] * 5, index=["name", "oldest", "youngest", "ts_count", "refs"])
        x_resi = pd.DataFrame.transpose(x_resi)
        xal = pd.merge(pd.merge(resi_0s,resi_0y,on='name'),resi_0c,on='name')
        bnu = xal["name"]
        bnu = bnu.drop_duplicates()
        bnu = bnu.dropna()
        bnurange = np.arange(0,len(bnu),1)
        for i in bnurange:
        #i=2
            i_name = bnu.iloc[i]
            x1_sub = x1.loc[((x1["name"]== i_name))]
            x1_subs = x1.loc[((x1["name"]== i_name) & (x1["b_scheme"]== "s"))]
            x1_suby = x1.loc[((x1["name"]== i_name) & (x1["b_scheme"]== "y"))]
            x1_subc = x1.loc[((x1["name"]== i_name) & (x1["b_scheme"]== "c"))]
            # youngest = max, oldest = min index
            x_range_s = np.array([min(x1_subs["oldest_index"])])
            x_range_y = np.array([min(x1_suby["oldest_index"])])
            x_range_c = np.array([min(x1_subc["oldest_index"])])

            if min(x1_subs["oldest_index"]) != max(x1_subs["youngest_index"]):
                x_range_s = np.arange(min(x1_subs["oldest_index"]),max(x1_subs["youngest_index"])+1,1)
            if min(x1_suby["oldest_index"]) != max(x1_suby["youngest_index"]):
                x_range_y = np.arange(min(x1_suby["oldest_index"]),max(x1_suby["youngest_index"])+1,1)
            if min(x1_subc["oldest_index"]) != max(x1_subc["youngest_index"]):
                x_range_c = np.arange(min(x1_subc["oldest_index"]),max(x1_subc["youngest_index"])+1,1)

            rax = np.concatenate((x_range_s, x_range_s, x_range_c))
            # filter for third quantile, only bins with highest score
            rax_counts = pd.DataFrame(np.unique(rax, return_counts=True), index = ['ts_bins', 'counts'])
            rax_counts = rax_counts.transpose()
            rq = round(np.quantile(rax_counts['counts'], 0.75),0)
            rax_sub = rax_counts.loc[rax_counts['counts']>= rq, ['ts_bins']]
            rax_sub = pd.merge(rax_sub, used_ts, how= 'inner', left_on="ts_bins", right_on="ts_index")
            x_youngest = rax_sub.loc[(rax_sub["ts_index"]== max(rax_sub["ts_index"])), ['ts']]
            x_oldest = rax_sub.loc[(rax_sub["ts_index"]== min(rax_sub["ts_index"])), ['ts']]
            ts_c = max(rax_sub["ts_index"])-min(rax_sub["ts_index"])
            refs_f = pd.unique(x1_sub['refs'])
            refs_f = pd.DataFrame(refs_f)
            refs_f = refs_f[0].apply(str)
            refs_f = refs_f.str.cat(sep=', ')
            ref_list = refs_f.split(", ")
            ref_list_u = list(set(ref_list))
            str1 = ", "
            refs_f = str1.join(ref_list_u)
            x_resib = pd.DataFrame([[i_name, x_oldest.iloc[0,0], x_youngest.iloc[0,0], ts_c, refs_f]],
                               columns=["name", "oldest", "youngest", "ts_count", "refs"])
            x_resi = pd.concat([x_resi, x_resib], axis=0, sort=True)
        resi_0 = x_resi
        resi_0['rule'] = 0.0

    resi_0 = resi_0.loc(axis=1)["name", "oldest", "youngest", "ts_count", "refs", "rule"]
    print("rule 0 has ", len(resi_0), "binned relations")
    print("Rule 0:  relations among named biostratigraphical units that have direct relations to binning scheme")
    resi_0.to_csv("x_rule0.csv", index = False, header=True)

    ##############################################################
    ##############################################################
    #rule 1 = all direct relations between biostrat names and binning scheme
    cr_a = c_rels_d.loc[((c_rels_d["strat_qualifier_1"]=="Biostratigraphy"))
                              & ((c_rels_d["qualifier_name_2"]==t_scheme)),
                              ["reference_id","name_1","name_2", "ts", "ts_index", "reference_year"]]
    #take out  relations that also relate to not specified in same reference
    cr_a =  cr_a.loc[~(cr_a["name_1"]=="not specified")]
    bnu = cr_a["name_1"]
    bnu = bnu.drop_duplicates()
    bnurange = np.arange(0,len(bnu),1)

    for ibs in runrange:
        resi_1 = pd.DataFrame([] * 5, index=["name", "oldest", "youngest", "ts_count", "refs"])
        resi_1 = pd.DataFrame.transpose(resi_1)
        for i in bnurange:
            if ibs == 0:
                resi_1a = rn_funs.bifu_s(cr_a.loc[cr_a["name_1"]==bnu.iloc[i]], used_ts, xnames_raw)
            if ibs == 1:
                resi_1a = rn_funs.bifu_y(cr_a.loc[cr_a["name_1"]==bnu.iloc[i]], used_ts, xnames_raw)
            if ibs == 2:
                resi_1a = rn_funs.bifu_c(cr_a.loc[cr_a["name_1"]==bnu.iloc[i]], used_ts, xnames_raw)
            resi_1 = pd.concat([resi_1, resi_1a], axis=0, sort=True)
        resi_1 = resi_1.dropna()
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
        resi_1 = pd.concat([resi_1s, resi_1y, resi_1c])
        x1 = pd.merge(resi_1, used_ts, how= 'inner', left_on="oldest", right_on="ts")
        x1 = x1[['name', 'oldest', 'ts_index', 'youngest', 'ts_count',
                 'refs', 'rule', "b_scheme"]]
        x1.columns = ['name', 'oldest', 'oldest_index', 'youngest', 'ts_count',
                      'refs', 'rule', "b_scheme"]
        x1 = pd.merge(x1, used_ts, how= 'inner', left_on="youngest", right_on="ts")
        x1 = x1[['name', 'oldest', 'oldest_index', 'youngest', 'ts_index','ts_count',
                 'refs', 'rule', "b_scheme"]]
        x1.columns = ['name', 'oldest', 'oldest_index', 'youngest', 'youngest_index', 'ts_count',
                      'refs', 'rule', "b_scheme"]
        x_resi = pd.DataFrame([] * 5, index=["name", "oldest", "youngest", "ts_count", "refs"])
        x_resi = pd.DataFrame.transpose(x_resi)
        xal = pd.merge(pd.merge(resi_1s,resi_1y,on='name'),resi_1c,on='name')
        bnu = xal["name"]
        bnu = bnu.drop_duplicates()
        bnu = bnu.dropna()
        bnurange = np.arange(0,len(bnu),1)
        for i in bnurange:
        #i=2
            i_name = bnu.iloc[i]
            x1_sub = x1.loc[((x1["name"]== i_name))]
            x1_subs = x1.loc[((x1["name"]== i_name) & (x1["b_scheme"]== "s"))]
            x1_suby = x1.loc[((x1["name"]== i_name) & (x1["b_scheme"]== "y"))]
            x1_subc = x1.loc[((x1["name"]== i_name) & (x1["b_scheme"]== "c"))]
            # youngest = max, oldest = min index
            x_range_s = np.array([min(x1_subs["oldest_index"])])
            x_range_y = np.array([min(x1_suby["oldest_index"])])
            x_range_c = np.array([min(x1_subc["oldest_index"])])

            if min(x1_subs["oldest_index"]) != max(x1_subs["youngest_index"]):
                x_range_s = np.arange(min(x1_subs["oldest_index"]),max(x1_subs["youngest_index"])+1,1)
            if min(x1_suby["oldest_index"]) != max(x1_suby["youngest_index"]):
                x_range_y = np.arange(min(x1_suby["oldest_index"]),max(x1_suby["youngest_index"])+1,1)
            if min(x1_subc["oldest_index"]) != max(x1_subc["youngest_index"]):
                x_range_c = np.arange(min(x1_subc["oldest_index"]),max(x1_subc["youngest_index"])+1,1)

            rax = np.concatenate((x_range_s, x_range_s, x_range_c))
            # filter for third quantile, only bins with highest score
            rax_counts = pd.DataFrame(np.unique(rax, return_counts=True), index = ['ts_bins', 'counts'])
            rax_counts = rax_counts.transpose()
            rq = round(np.quantile(rax_counts['counts'], 0.75),0)
            rax_sub = rax_counts.loc[rax_counts['counts']>= rq, ['ts_bins']]
            rax_sub = pd.merge(rax_sub, used_ts, how= 'inner', left_on="ts_bins", right_on="ts_index")
            x_youngest = rax_sub.loc[(rax_sub["ts_index"]== max(rax_sub["ts_index"])), ['ts']]
            x_oldest = rax_sub.loc[(rax_sub["ts_index"]== min(rax_sub["ts_index"])), ['ts']]
            ts_c = max(rax_sub["ts_index"])-min(rax_sub["ts_index"])
            refs_f = pd.unique(x1_sub['refs'])
            refs_f = pd.DataFrame(refs_f)
            refs_f = refs_f[0].apply(str)
            refs_f = refs_f.str.cat(sep=', ')
            ref_list = refs_f.split(", ")
            ref_list_u = list(set(ref_list))
            str1 = ", "
            refs_f = str1.join(ref_list_u)
            x_resib = pd.DataFrame([[i_name, x_oldest.iloc[0,0], x_youngest.iloc[0,0], ts_c, refs_f]],
                               columns=["name", "oldest", "youngest", "ts_count", "refs"])
            x_resi = pd.concat([x_resi, x_resib], axis=0, sort=True)
        resi_1 = x_resi
        resi_1['rule'] = 1.0

    resi_1 = resi_1.loc(axis=1)["name", "oldest", "youngest", "ts_count", "refs", "rule"]
    print("rule 1 has ", len(resi_1), "binned relations")
    print("Rule 1: direct relations of named units to binning scheme")
    resi_1.to_csv("x_rule1.csv", index = False, header=True)

    ##############################################################
    ##############################################################
    ### Rule_2: direct relations between non-bio* with binning scheme
    ### except chronostratigraphy

    cr_c = c_rels_d.loc[~(c_rels_d["strat_qualifier_1"]=="Biostratigraphy")
                          & ~(c_rels_d["strat_qualifier_1"]=="Chronostratigraphy")
                          & (c_rels_d["qualifier_name_2"]==t_scheme),
                              ["reference_id","name_1","name_2", "ts", "ts_index", "reference_year"]]
    cr_c =  cr_c.loc[~(cr_c["name_1"]=="not specified")]
    bnu = cr_c["name_1"]
    bnu = bnu.drop_duplicates()
    bnurange = np.arange(0,len(bnu),1)

    for ibs in runrange:
        resi_2 = pd.DataFrame([] * 5, index=["name", "oldest", "youngest", "ts_count", "refs"])
        resi_2 = pd.DataFrame.transpose(resi_2)
        for i in bnurange:
            if ibs == 0:
                resi_2a = rn_funs.bifu_s(cr_c.loc[cr_c["name_1"]==bnu.iloc[i]], used_ts, xnames_raw)
            if ibs == 1:
                resi_2a = rn_funs.bifu_y(cr_c.loc[cr_c["name_1"]==bnu.iloc[i]], used_ts, xnames_raw)
            if ibs == 2:
                resi_2a = rn_funs.bifu_c(cr_c.loc[cr_c["name_1"]==bnu.iloc[i]], used_ts, xnames_raw)
            resi_2 = pd.concat([resi_2, resi_2a], axis=0, sort=True)
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
        resi_2 = pd.concat([resi_2s, resi_2y, resi_2c])
        x1 = pd.merge(resi_2, used_ts, how= 'inner', left_on="oldest", right_on="ts")
        x1 = x1[['name', 'oldest', 'ts_index', 'youngest', 'ts_count',
                 'refs', 'rule', "b_scheme"]]
        x1.columns = ['name', 'oldest', 'oldest_index', 'youngest', 'ts_count',
                      'refs', 'rule', "b_scheme"]
        x1 = pd.merge(x1, used_ts, how= 'inner', left_on="youngest", right_on="ts")
        x1 = x1[['name', 'oldest', 'oldest_index', 'youngest', 'ts_index','ts_count',
                 'refs', 'rule', "b_scheme"]]
        x1.columns = ['name', 'oldest', 'oldest_index', 'youngest', 'youngest_index', 'ts_count',
                      'refs', 'rule', "b_scheme"]
        x_resi = pd.DataFrame([] * 5, index=["name", "oldest", "youngest", "ts_count", "refs"])
        x_resi = pd.DataFrame.transpose(x_resi)
        xal = pd.merge(pd.merge(resi_2s,resi_2y,on='name'),resi_2c,on='name')
        bnu = xal["name"]
        bnu = bnu.drop_duplicates()
        bnu = bnu.dropna()
        bnurange = np.arange(0,len(bnu),1)
        for i in bnurange:
        #i=2
            i_name = bnu.iloc[i]
            x1_sub = x1.loc[((x1["name"]== i_name))]
            x1_subs = x1.loc[((x1["name"]== i_name) & (x1["b_scheme"]== "s"))]
            x1_suby = x1.loc[((x1["name"]== i_name) & (x1["b_scheme"]== "y"))]
            x1_subc = x1.loc[((x1["name"]== i_name) & (x1["b_scheme"]== "c"))]
            # youngest = max, oldest = min index
            x_range_s = np.array([min(x1_subs["oldest_index"])])
            x_range_y = np.array([min(x1_suby["oldest_index"])])
            x_range_c = np.array([min(x1_subc["oldest_index"])])

            if min(x1_subs["oldest_index"]) != max(x1_subs["youngest_index"]):
                x_range_s = np.arange(min(x1_subs["oldest_index"]),max(x1_subs["youngest_index"])+1,1)
            if min(x1_suby["oldest_index"]) != max(x1_suby["youngest_index"]):
                x_range_y = np.arange(min(x1_suby["oldest_index"]),max(x1_suby["youngest_index"])+1,1)
            if min(x1_subc["oldest_index"]) != max(x1_subc["youngest_index"]):
                x_range_c = np.arange(min(x1_subc["oldest_index"]),max(x1_subc["youngest_index"])+1,1)

            rax = np.concatenate((x_range_s, x_range_s, x_range_c))
            # filter for third quantile, only bins with highest score
            rax_counts = pd.DataFrame(np.unique(rax, return_counts=True), index = ['ts_bins', 'counts'])
            rax_counts = rax_counts.transpose()
            rq = round(np.quantile(rax_counts['counts'], 0.75),0)
            rax_sub = rax_counts.loc[rax_counts['counts']>= rq, ['ts_bins']]
            rax_sub = pd.merge(rax_sub, used_ts, how= 'inner', left_on="ts_bins", right_on="ts_index")
            x_youngest = rax_sub.loc[(rax_sub["ts_index"]== max(rax_sub["ts_index"])), ['ts']]
            x_oldest = rax_sub.loc[(rax_sub["ts_index"]== min(rax_sub["ts_index"])), ['ts']]
            ts_c = max(rax_sub["ts_index"])-min(rax_sub["ts_index"])
            refs_f = pd.unique(x1_sub['refs'])
            refs_f = pd.DataFrame(refs_f)
            refs_f = refs_f[0].apply(str)
            refs_f = refs_f.str.cat(sep=', ')
            ref_list = refs_f.split(", ")
            ref_list_u = list(set(ref_list))
            str1 = ", "
            refs_f = str1.join(ref_list_u)
            x_resib = pd.DataFrame([[i_name, x_oldest.iloc[0,0], x_youngest.iloc[0,0], ts_c, refs_f]],
                               columns=["name", "oldest", "youngest", "ts_count", "refs"])
            x_resi = pd.concat([x_resi, x_resib], axis=0, sort=True)
        resi_2 = x_resi
        resi_2['rule'] = 2.0

    resi_2= resi_2.loc(axis=1)["name", "oldest", "youngest", "ts_count", "refs", "rule"]
    resi_2 = resi_2[~resi_2["name"].isin(resi_0["name"])] # filter non-bio rule 0
    print("rule 2 has ", len(resi_2), "binned relations")
    print("Rule 2:  relations among named biostratigraphical units that have indirect relations to binning scheme")
    resi_2.to_csv("x_rule2.csv", index = False, header=True)

    ##############################################################
    ##############################################################
    ##############################################################
    ##############################################################
    ##############################################################
    # the second tier has two binning rules and bins all indirect names via biostrat

    ##############################################################
    ##############################################################
    #rule_3 all relations between biostrat and biostrat that refer indirectly to binning scheme
    cr_b = c_rels.loc[(c_rels["strat_qualifier_1"]=="Biostratigraphy")
                                  & (c_rels["strat_qualifier_2"]=="Biostratigraphy")
                                  &  ~(c_rels["qualifier_name_1"] == t_scheme)
                                  &  ~(c_rels["qualifier_name_2"] == t_scheme),
                                  ["reference_id","name_1","name_2", "reference_year"]]

    x1 = pd.merge(resi_1, cr_b, left_on="name", right_on="name_2") # name_2 is already binned here
    x1 = pd.merge(x1, used_ts, how= 'inner', left_on="oldest", right_on="ts") # time bin info is added here
    x1 = x1[['name_2', 'name_1', 'oldest', "ts_index", 'youngest', 'ts_count', 'refs',
             'rule', 'reference_id', "reference_year"]]
    x1.columns = ['name_2', 'name_1', 'oldest', "oldest_index", 'youngest', 'ts_count', 'refs',
                  'rule', 'reference_id', "reference_year"]
    x1 = pd.merge(x1, used_ts, how= 'inner', left_on="youngest", right_on="ts") # time bin info is added here
    x1 = x1[['name_2', 'name_1', 'oldest', "oldest_index", 'youngest', "ts_index", 'ts_count', 'refs',
             'rule', 'reference_id', "reference_year"]]
    x1.columns = ['name_2', 'name_1', 'oldest', "oldest_index", 'youngest', 'youngest_index', 'ts_count', 'refs',
                  'rule', 'reference_id', "reference_year"]
    x1m = x1[['name_1', 'name_2', 'oldest', "oldest_index", 'youngest', "youngest_index", 'ts_count', 'refs',
             'rule', 'reference_id', "reference_year"]]
    x1.columns = ['name_1', 'name_2', 'oldest', "oldest_index", 'youngest', 'youngest_index', 'ts_count', 'refs',
                  'rule', 'reference_id', "reference_year"]
    x1  = pd.concat((x1,x1m), axis=0)
    x1 =  x1.loc[~(x1["name_1"]=="not specified")]
    x1 = x1[~x1["name_1"].isin(resi_1["name"])]# filter out all names that are already binned with rule 1
    # name_1 is already binned, name_2 not binned yet
    x1["rule"] = 3.6
    pd.DataFrame.head(x1)
    x1 = x1.drop_duplicates()
    # all names that are not binned via rule 1
    x2 = cr_b[~cr_b["name_1"].isin(x1["name_1"])]

    resi_3 = pd.DataFrame([] * 6, index=["name", "oldest", "youngest", "ts_count", "refs", "rule"])
    resi_3 = pd.DataFrame.transpose(resi_3)
    for ibs in runrange:
        for k in np.arange(1,5,1):
            bnu = x1["name_1"]
            bnu = bnu.drop_duplicates()
            bnurange = np.arange(0,len(bnu),1)

            x3 = pd.DataFrame([] * 5, index=["name", "oldest", "youngest", "ts_count", "refs"])
            x3 = pd.DataFrame.transpose(x3)
            for i in bnurange:
                if ibs == 0:
                    x3a = rn_funs.bifu_s2(x1.loc[x1["name_1"]==bnu.iloc[i]], used_ts, xnames_raw)
                if ibs == 1:
                    x3a = rn_funs.bifu_y2(x1.loc[x1["name_1"]==bnu.iloc[i]], used_ts, xnames_raw)
                if ibs == 2:
                    x3a = rn_funs.bifu_c2(x1.loc[x1["name_1"]==bnu.iloc[i]], used_ts, xnames_raw)
                x3 = pd.concat([x3, x3a], axis=0, sort=True)
            x3 = pd.DataFrame.drop_duplicates(x3)
            x3 = x3.dropna()
            x3["rule"] = 3.0+((k-1)*0.1)
            x3b = x3[~x3["name"].isin(resi_3["name"])] # filter for already binned names
            resi_3 = pd.concat([resi_3, x3b], axis=0, sort=True) # appended to previous ruling
            pd.DataFrame.head(resi_3)
            x2a = cr_b[~cr_b["name_2"].isin(resi_1["name"])] #  # all non binned names yet

            #create a new x1 based on above ruling
            if (k==1):
                x4a = pd.concat((resi_1, x3), axis=0)
            else:
                x4a = pd.concat((x4a, x3), axis=0)

            x4 = pd.merge(x4a, cr_b, left_on="name", right_on="name_2") # name_2 is already binned here
            x4 = pd.merge(x4, used_ts, how= 'inner', left_on="oldest", right_on="ts") # time bin info is added here
            x4 = x4[['name_2', 'name_1', 'oldest', "ts_index", 'youngest', 'ts_count', 'refs',
                     'rule', 'reference_id', "reference_year"]]
            x4.columns = ['name_2', 'name_1', 'oldest', "oldest_index", 'youngest', 'ts_count', 'refs',
                          'rule', 'reference_id', "reference_year"]
            x4 = pd.merge(x4, used_ts, how= 'inner', left_on="youngest", right_on="ts") # time bin info is added here
            x4 = x4[['name_2', 'name_1', 'oldest', "oldest_index", 'youngest', "ts_index", 'ts_count', 'refs',
                     'rule', 'reference_id', "reference_year"]]
            x4.columns = ['name_2', 'name_1', 'oldest', "oldest_index", 'youngest', 'youngest_index', 'ts_count', 'refs',
                          'rule', 'reference_id', "reference_year"]
            x4m = x4[['name_1', 'name_2', 'oldest', "oldest_index", 'youngest', "youngest_index", 'ts_count', 'refs',
                     'rule', 'reference_id', "reference_year"]]
            x4.columns = ['name_1', 'name_2', 'oldest', "oldest_index", 'youngest', 'youngest_index', 'ts_count', 'refs',
                          'rule', 'reference_id', "reference_year"]
            x1  = pd.concat((x4,x4m), axis=0)
            x1 =  x1.loc[~(x1["name_1"]=="not specified")]
            x1["rule"] = 3.7
            pd.DataFrame.head(x1)
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
        resi_3 = pd.concat([resi_3s, resi_3y, resi_3c])
        x2 = pd.merge(resi_3, used_ts, how= 'inner', left_on="oldest", right_on="ts")
        x2 = x2[['name', 'oldest', 'ts_index', 'youngest', 'ts_count',
                 'refs', 'rule', "b_scheme"]]
        x2.columns = ['name', 'oldest', 'oldest_index', 'youngest', 'ts_count',
                      'refs', 'rule', "b_scheme"]
        x2 = pd.merge(x2, used_ts, how= 'inner', left_on="youngest", right_on="ts")
        x2 = x2[['name', 'oldest', 'oldest_index', 'youngest', 'ts_index','ts_count',
                 'refs', 'rule', "b_scheme"]]
        x2.columns = ['name', 'oldest', 'oldest_index', 'youngest', 'youngest_index', 'ts_count',
                      'refs', 'rule', "b_scheme"]
        x_resi = pd.DataFrame([] * 5, index=["name", "oldest", "youngest", "ts_count", "refs"])
        x_resi = pd.DataFrame.transpose(x_resi)
        xal = pd.merge(pd.merge(resi_3s,resi_3y,on='name'),resi_3c,on='name')
        bnu = xal["name"]
        bnu = bnu.drop_duplicates()
        bnu = bnu.dropna()
        bnurange = np.arange(0,len(bnu),1)
        for i in bnurange:
        #i=2
            i_name = bnu.iloc[i]
            x2_sub = x2.loc[((x2["name"]== i_name))]
            x2_subs = x2.loc[((x2["name"]== i_name) & (x2["b_scheme"]== "s"))]
            x2_suby = x2.loc[((x2["name"]== i_name) & (x2["b_scheme"]== "y"))]
            x2_subc = x2.loc[((x2["name"]== i_name) & (x2["b_scheme"]== "c"))]
            # youngest = max, oldest = min index
            x_range_s = np.array([min(x2_subs["oldest_index"])])
            x_range_y = np.array([min(x2_suby["oldest_index"])])
            x_range_c = np.array([min(x2_subc["oldest_index"])])

            if min(x2_subs["oldest_index"]) != max(x2_subs["youngest_index"]):
                x_range_s = np.arange(min(x2_subs["oldest_index"]),max(x2_subs["youngest_index"])+1,1)
            if min(x2_suby["oldest_index"]) != max(x2_suby["youngest_index"]):
                x_range_y = np.arange(min(x2_suby["oldest_index"]),max(x2_suby["youngest_index"])+1,1)
            if min(x2_subc["oldest_index"]) != max(x2_subc["youngest_index"]):
                x_range_c = np.arange(min(x2_subc["oldest_index"]),max(x2_subc["youngest_index"])+1,1)

            rax = np.concatenate((x_range_s, x_range_s, x_range_c))
            # filter for third quantile, only bins with highest score
            rax_counts = pd.DataFrame(np.unique(rax, return_counts=True), index = ['ts_bins', 'counts'])
            rax_counts = rax_counts.transpose()
            rq = round(np.quantile(rax_counts['counts'], 0.75),0)
            rax_sub = rax_counts.loc[rax_counts['counts']>= rq, ['ts_bins']]
            rax_sub = pd.merge(rax_sub, used_ts, how= 'inner', left_on="ts_bins", right_on="ts_index")
            x_youngest = rax_sub.loc[(rax_sub["ts_index"]== max(rax_sub["ts_index"])), ['ts']]
            x_oldest = rax_sub.loc[(rax_sub["ts_index"]== min(rax_sub["ts_index"])), ['ts']]
            ts_c = max(rax_sub["ts_index"])-min(rax_sub["ts_index"])
            refs_f = pd.unique(x2_sub['refs'])
            refs_f = pd.DataFrame(refs_f)
            refs_f = refs_f[0].apply(str)
            refs_f = refs_f.str.cat(sep=', ')
            ref_list = refs_f.split(", ")
            ref_list_u = list(set(ref_list))
            str1 = ", "
            refs_f = str1.join(ref_list_u)
            x_resib = pd.DataFrame([[i_name, x_oldest.iloc[0,0], x_youngest.iloc[0,0], ts_c, refs_f]],
                               columns=["name", "oldest", "youngest", "ts_count", "refs"])
            x_resi = pd.concat([x_resi, x_resib], axis=0, sort=True)
        resi_3 = x_resi
        resi_3['rule'] = 3.9


    resi_3= resi_3.loc(axis=1)["name", "oldest", "youngest", "ts_count", "refs", "rule"]
    resi_3 = pd.DataFrame.drop_duplicates(resi_3)
    resi_3 = resi_3[~resi_3["name"].isin(resi_1["name"])] # filter non-bio rule 1
    print("rule 3 has ", len(resi_3), "binned relations")
    print("Rule 3:  relations among named biostratigraphical units that have direct relations to binning scheme")
    resi_3.to_csv("x_rule3.csv", index = False, header=True)

    ##############################################################
    ### Rule 4: indirect relations of non-bio via resis_bio to binning scheme
    ### except direct chronostratigraphy links
    resis_bio = pd.concat([resi_1, resi_3], axis=0)
    #resis_bio.to_csv('resis_bio.csv') # all binnings via bio only = Bio*

    cr_d = c_rels.loc[~(c_rels["strat_qualifier_1"]=="Biostratigraphy")
                              & (c_rels["strat_qualifier_2"]=="Biostratigraphy")
                              & ~(c_rels["qualifier_name_1"]==t_scheme)
                              & ~(c_rels["qualifier_name_2"]==t_scheme),
                              ["reference_id","name_1","name_2", "reference_year"]]

    cr_d =  cr_d[~cr_d["name_1"].isin(resi_0["name"])] #filter for chronostrat rule 0
    resis_bio = pd.DataFrame.drop_duplicates(resis_bio)
    x1 = pd.merge(resis_bio, cr_d, left_on="name", right_on="name_2") # name_2 is already binned here
    x1 = pd.merge(x1, used_ts, how= 'inner', left_on="oldest", right_on="ts") # time bin info is added here
    x1 = x1[['name_2', 'name_1', 'oldest', "ts_index", 'youngest', 'ts_count', 'refs',
             'rule', 'reference_id', "reference_year"]]
    x1.columns = ['name_2', 'name_1', 'oldest', "oldest_index", 'youngest', 'ts_count', 'refs',
                  'rule', 'reference_id', "reference_year"]
    x1 = pd.merge(x1, used_ts, how= 'inner', left_on="youngest", right_on="ts") # time bin info is added here
    x1 = x1[['name_2', 'name_1', 'oldest', "oldest_index", 'youngest', "ts_index", 'ts_count', 'refs',
             'rule', 'reference_id', "reference_year"]]
    x1.columns = ['name_2', 'name_1', 'oldest', "oldest_index", 'youngest', 'youngest_index', 'ts_count', 'refs',
                  'rule', 'reference_id', "reference_year"]
    x1m = x1[['name_1', 'name_2', 'oldest', "oldest_index", 'youngest', "youngest_index", 'ts_count', 'refs',
             'rule', 'reference_id', "reference_year"]]
    x1.columns = ['name_1', 'name_2', 'oldest', "oldest_index", 'youngest', 'youngest_index', 'ts_count', 'refs',
                  'rule', 'reference_id', "reference_year"]
    x1  = pd.concat((x1,x1m), axis=0)
    x1 = x1[~x1["name_1"].isin(resi_2["name"])] # filter non-bio rule 2
    x1 =  x1[~x1["name_1"].isin(resi_0["name"])] # filter direct chronostrat rule 0
    x1 =  x1.loc[~(x1["name_1"]=="not specified")] # filter "Not specified"
    x1["rule"] = 4.6
    pd.DataFrame.head(x1)
    x1 = x1.drop_duplicates()

    x2 = cr_d[~cr_d["name_1"].isin(resis_bio["name"])]

    resi_4 = pd.DataFrame([] * 6, index=["name", "oldest", "youngest", "ts_count", "refs", "rule"])
    resi_4 = pd.DataFrame.transpose(resi_4)
    for ibs in runrange:
        for k in np.arange(1,5,1):
            bnu = x1["name_1"]
            bnu = bnu.drop_duplicates()
            bnurange = np.arange(0,len(bnu),1)

            x3 = pd.DataFrame([] * 5, index=["name", "oldest", "youngest", "ts_count", "refs"])
            x3 = pd.DataFrame.transpose(x3)
            for i in bnurange:
                if ibs == 0:
                    x3a = rn_funs.bifu_s2(x1.loc[x1["name_1"]==bnu.iloc[i]], used_ts, xnames_raw)
                if ibs == 1:
                    x3a = rn_funs.bifu_y2(x1.loc[x1["name_1"]==bnu.iloc[i]], used_ts, xnames_raw)
                if ibs == 2:
                    x3a = rn_funs.bifu_c2(x1.loc[x1["name_1"]==bnu.iloc[i]], used_ts, xnames_raw)
                x3 = pd.concat([x3, x3a], axis=0, sort=True)
            x3 = pd.DataFrame.drop_duplicates(x3)
            x3 = x3.dropna()
            x3["rule"] = 4.0+((k-1)*0.1)
            x3b = x3[~x3["name"].isin(resi_4["name"])] # filter for already binned names
            resi_4 = pd.concat([resi_4, x3b], axis=0, sort=True) # appended to previous ruling
            pd.DataFrame.head(resi_4)
            x2a = cr_d[~cr_d["name_1"].isin(resi_4["name"])] # all non binned names in cr_g with current rule

            #now create a new x1 based on above ruling
            if (k==1):
                x4a = pd.concat((resis_bio, x3), axis=0)
            else:
                x4a = pd.concat((x4a, x3), axis=0)

            x4 = pd.merge(x4a, cr_d, left_on="name", right_on="name_2") # name_2 is already binned here
            x4 = pd.merge(x4, used_ts, how= 'inner', left_on="oldest", right_on="ts") # time bin info is added here
            x4 = x4[['name_2', 'name_1', 'oldest', "ts_index", 'youngest', 'ts_count', 'refs',
                     'rule', 'reference_id', "reference_year"]]
            x4.columns = ['name_2', 'name_1', 'oldest', "oldest_index", 'youngest', 'ts_count', 'refs',
                          'rule', 'reference_id', "reference_year"]
            x4 = pd.merge(x4, used_ts, how= 'inner', left_on="youngest", right_on="ts") # time bin info is added here
            x4 = x4[['name_2', 'name_1', 'oldest', "oldest_index", 'youngest', "ts_index", 'ts_count', 'refs',
                     'rule', 'reference_id', "reference_year"]]
            x4.columns = ['name_2', 'name_1', 'oldest', "oldest_index", 'youngest', 'youngest_index',
                          'ts_count', 'refs', 'rule', 'reference_id', "reference_year"]
            x4m = x4[['name_1', 'name_2', 'oldest', "oldest_index", 'youngest', "youngest_index", 'ts_count', 'refs',
                     'rule', 'reference_id', "reference_year"]]
            x4.columns = ['name_1', 'name_2', 'oldest', "oldest_index", 'youngest', 'youngest_index',
                          'ts_count', 'refs', 'rule', 'reference_id', "reference_year"]
            x1  = pd.concat((x4,x4m), axis=0)
            x1 =  x1.loc[~(x1["name_1"]=="not specified")]
            x1 =  x1[~x1["name_1"].isin(resi_0["name"])]
            x1["rule"] = 6.7
            pd.DataFrame.head(x1)
            x1 = x1.drop_duplicates()
            x2b = cr_d[~cr_d["name_1"].isin(x1["name_1"])] # all not yet binned in cr_g
            x2b = pd.DataFrame.drop_duplicates(x2b)

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
            resi_4 = pd.concat([resi_4s, resi_4y, resi_4c])
            x2 = pd.merge(resi_4, used_ts, how= 'inner', left_on="oldest", right_on="ts")
            x2 = x2[['name', 'oldest', 'ts_index', 'youngest', 'ts_count',
                     'refs', 'rule', "b_scheme"]]
            x2.columns = ['name', 'oldest', 'oldest_index', 'youngest', 'ts_count',
                          'refs', 'rule', "b_scheme"]
            x2 = pd.merge(x2, used_ts, how= 'inner', left_on="youngest", right_on="ts")
            x2 = x2[['name', 'oldest', 'oldest_index', 'youngest', 'ts_index','ts_count',
                     'refs', 'rule', "b_scheme"]]
            x2.columns = ['name', 'oldest', 'oldest_index', 'youngest', 'youngest_index', 'ts_count',
                          'refs', 'rule', "b_scheme"]
            x_resi = pd.DataFrame([] * 5, index=["name", "oldest", "youngest", "ts_count", "refs"])
            x_resi = pd.DataFrame.transpose(x_resi)
            xal = pd.merge(pd.merge(resi_4s,resi_4y,on='name'),resi_4c,on='name')
            bnu = xal["name"]
            bnu = bnu.drop_duplicates()
            bnu = bnu.dropna()
            bnurange = np.arange(0,len(bnu),1)
            for i in bnurange:
            #i=2
                i_name = bnu.iloc[i]
                x2_sub = x2.loc[((x2["name"]== i_name))]
                x2_subs = x2.loc[((x2["name"]== i_name) & (x2["b_scheme"]== "s"))]
                x2_suby = x2.loc[((x2["name"]== i_name) & (x2["b_scheme"]== "y"))]
                x2_subc = x2.loc[((x2["name"]== i_name) & (x2["b_scheme"]== "c"))]
                # youngest = max, oldest = min index
                x_range_s = np.array([min(x2_subs["oldest_index"])])
                x_range_y = np.array([min(x2_suby["oldest_index"])])
                x_range_c = np.array([min(x2_subc["oldest_index"])])

                if min(x2_subs["oldest_index"]) != max(x2_subs["youngest_index"]):
                    x_range_s = np.arange(min(x2_subs["oldest_index"]),max(x2_subs["youngest_index"])+1,1)
                if min(x2_suby["oldest_index"]) != max(x2_suby["youngest_index"]):
                    x_range_y = np.arange(min(x2_suby["oldest_index"]),max(x2_suby["youngest_index"])+1,1)
                if min(x2_subc["oldest_index"]) != max(x2_subc["youngest_index"]):
                    x_range_c = np.arange(min(x2_subc["oldest_index"]),max(x2_subc["youngest_index"])+1,1)

                rax = np.concatenate((x_range_s, x_range_s, x_range_c))
                # filter for third quantile, only bins with highest score
                rax_counts = pd.DataFrame(np.unique(rax, return_counts=True), index = ['ts_bins', 'counts'])
                rax_counts = rax_counts.transpose()
                rq = round(np.quantile(rax_counts['counts'], 0.75),0)
                rax_sub = rax_counts.loc[rax_counts['counts']>= rq, ['ts_bins']]
                rax_sub = pd.merge(rax_sub, used_ts, how= 'inner', left_on="ts_bins", right_on="ts_index")
                x_youngest = rax_sub.loc[(rax_sub["ts_index"]== max(rax_sub["ts_index"])), ['ts']]
                x_oldest = rax_sub.loc[(rax_sub["ts_index"]== min(rax_sub["ts_index"])), ['ts']]
                ts_c = max(rax_sub["ts_index"])-min(rax_sub["ts_index"])
                refs_f = pd.unique(x2_sub['refs'])
                refs_f = pd.DataFrame(refs_f)
                refs_f = refs_f[0].apply(str)
                refs_f = refs_f.str.cat(sep=', ')
                ref_list = refs_f.split(", ")
                ref_list_u = list(set(ref_list))
                str1 = ", "
                refs_f = str1.join(ref_list_u)
                x_resib = pd.DataFrame([[i_name, x_oldest.iloc[0,0], x_youngest.iloc[0,0], ts_c, refs_f]],
                                   columns=["name", "oldest", "youngest", "ts_count", "refs"])
                x_resi = pd.concat([x_resi, x_resib], axis=0, sort=True)
            resi_4 = x_resi
            resi_4['rule'] = 4.9

    resi_4 = pd.DataFrame.drop_duplicates(resi_4)
    resi_4 = resi_4[['name', 'oldest', 'youngest', 'ts_count', 'refs', 'rule']]
    combi_x = pd.concat([resi_0, resi_1, resi_2, resi_3], axis=0, sort=False)
    resi_4 = resi_4[~resi_4["name"].isin(combi_x["name"])] # filter non-bio rule 1
    print("rule 4 has ", len(resi_4), "binned relations")
    print("Rule 4:  relations among named non-biostratigraphical units that have direct relations to binning scheme")
    resi_4.to_csv("x_rule4.csv", index = False, header=True)

    ##################################################################################
    ### Rule 5:  indirect relations of non-bio* to resis_4 with link to bio* (route via resi_4)

    cr_g = c_rels.loc[~(c_rels["strat_qualifier_1"]=="Biostratigraphy")
                              & ~(c_rels["strat_qualifier_2"]=="Biostratigraphy")
                              & ~(c_rels["qualifier_name_1"]==t_scheme)
                              & ~(c_rels["qualifier_name_2"]==t_scheme),
                              ["reference_id","name_1","name_2", "reference_year"]]
    cr_g.to_csv("x_cr_g.csv", index = False, header=True)
    x1 = pd.merge(resi_4, cr_g, left_on="name", right_on="name_2")
    x1 = pd.merge(x1, used_ts, how= 'inner', left_on="oldest", right_on="ts") # time bin info is added here
    x1 = x1[['name_2', 'name_1', 'oldest', "ts_index", 'youngest', 'ts_count', 'refs',
             'rule', 'reference_id', "reference_year"]]
    x1.columns = ['name_2', 'name_1', 'oldest', "oldest_index", 'youngest', 'ts_count', 'refs',
                  'rule', 'reference_id', "reference_year"]
    x1 = pd.merge(x1, used_ts, how= 'inner', left_on="youngest", right_on="ts") # time bin info is added here
    x1 = x1[['name_2', 'name_1', 'oldest', "oldest_index", 'youngest', "ts_index", 'ts_count', 'refs',
             'rule', 'reference_id', "reference_year"]]
    x1.columns = ['name_2', 'name_1', 'oldest', "oldest_index", 'youngest', 'youngest_index', 'ts_count', 'refs',
                  'rule', 'reference_id', "reference_year"]
    x1m = x1[['name_1', 'name_2', 'oldest', "oldest_index", 'youngest', "youngest_index", 'ts_count', 'refs',
             'rule', 'reference_id', "reference_year"]]
    x1.columns = ['name_1', 'name_2', 'oldest', "oldest_index", 'youngest', 'youngest_index', 'ts_count', 'refs',
                  'rule', 'reference_id', "reference_year"]
    x1  = pd.concat((x1,x1m), axis=0)
    x1 = x1[~x1["name_1"].isin(resi_2["name"])] # filter first level  linked non-bio*
    x1 =  x1[~x1["name_1"].isin(resi_0["name"])] # filter direct  chronostrat rule 0
    x1 =  x1.loc[~(x1["name_1"]=="not specified")]
    x1["rule"] = 5.0
    pd.DataFrame.head(x1)
    x1 = x1.drop_duplicates()

    x2 = cr_g[~cr_g["name_2"].isin(resis_bio["name"])]

    resi_5 = pd.DataFrame([] * 6, index=["name", "oldest", "youngest", "ts_count", "refs", "rule"])
    resi_5 = pd.DataFrame.transpose(resi_5)
    for ibs in runrange:
        for k in np.arange(1,5,1):
            bnu = x1["name_1"] # changed from name_1 23.03
            bnu = bnu.drop_duplicates()
            bnurange = np.arange(0,len(bnu),1)
            x3 = pd.DataFrame([] * 5, index=["name", "oldest", "youngest", "ts_count", "refs"])
            x3 = pd.DataFrame.transpose(x3)
            for i in bnurange:
                if ibs == 0:
                    x3a = rn_funs.bifu_s2(x1.loc[x1["name_1"]==bnu.iloc[i]], used_ts, xnames_raw)
                if ibs == 1:
                    x3a = rn_funs.bifu_y2(x1.loc[x1["name_1"]==bnu.iloc[i]], used_ts, xnames_raw)
                if ibs == 2:
                    x3a = rn_funs.bifu_c2(x1.loc[x1["name_1"]==bnu.iloc[i]], used_ts, xnames_raw)
                x3 = pd.concat([x3, x3a], axis=0, sort=True)
            x3 = pd.DataFrame.drop_duplicates(x3)
            x3 = x3.dropna()
            x3["rule"] = 5.0+((k-1)*0.1)
            x3b = x3[~x3["name"].isin(resi_5["name"])] # filter for already binned names
            resi_5 = pd.concat([resi_5, x3b], axis=0, sort=True) # appended to previous ruling
            pd.DataFrame.head(resi_5)
            x2a = cr_g[~cr_g["name_1"].isin(resi_5["name"])] # all non binned names in cr_g with current rule

            #create a new x1 based on above ruling
            if (k==1):
                x4a = pd.concat((resi_4, x3), axis=0)
            else:
                x4a = pd.concat((x4a, x3), axis=0)

            x4 = pd.merge(x4a, cr_g, left_on="name", right_on="name_2") # name_2 is already binned here
            x4 = pd.merge(x4, used_ts, how= 'inner', left_on="oldest", right_on="ts") # time bin info is added here
            x4 = x4[['name_2', 'name_1', 'oldest', "ts_index", 'youngest', 'ts_count', 'refs',
                     'rule', 'reference_id', "reference_year"]]
            x4.columns = ['name_2', 'name_1', 'oldest', "oldest_index", 'youngest', 'ts_count', 'refs',
                          'rule', 'reference_id', "reference_year"]
            x4 = pd.merge(x4, used_ts, how= 'inner', left_on="youngest", right_on="ts") # time bin info is added here
            x4 = x4[['name_2', 'name_1', 'oldest', "oldest_index", 'youngest', "ts_index", 'ts_count', 'refs',
                     'rule', 'reference_id', "reference_year"]]
            x4.columns = ['name_2', 'name_1', 'oldest', "oldest_index", 'youngest', 'youngest_index',
                          'ts_count', 'refs', 'rule', 'reference_id', "reference_year"]
            x4m = x4[['name_1', 'name_2', 'oldest', "oldest_index", 'youngest', "youngest_index", 'ts_count', 'refs',
                     'rule', 'reference_id', "reference_year"]]
            x4.columns = ['name_1', 'name_2', 'oldest', "oldest_index", 'youngest', 'youngest_index',
                          'ts_count', 'refs', 'rule', 'reference_id', "reference_year"]
            x1  = pd.concat((x4,x4m), axis=0)
            x1 =  x1.loc[~(x1["name_1"]=="not specified")]
            x1["rule"] = 5.7
            pd.DataFrame.head(x1)
            x1 = x1.drop_duplicates()
            x2b = cr_g[~cr_g["name_1"].isin(x1["name_1"])] # all not yet binned in cr_g
            x2b = pd.DataFrame.drop_duplicates(x2b)

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
            resi_5 = pd.concat([resi_5s, resi_5y, resi_5c])
            x2 = pd.merge(resi_5, used_ts, how= 'inner', left_on="oldest", right_on="ts")
            x2 = x2[['name', 'oldest', 'ts_index', 'youngest', 'ts_count',
                     'refs', 'rule', "b_scheme"]]
            x2.columns = ['name', 'oldest', 'oldest_index', 'youngest', 'ts_count',
                          'refs', 'rule', "b_scheme"]
            x2 = pd.merge(x2, used_ts, how= 'inner', left_on="youngest", right_on="ts")
            x2 = x2[['name', 'oldest', 'oldest_index', 'youngest', 'ts_index','ts_count',
                     'refs', 'rule', "b_scheme"]]
            x2.columns = ['name', 'oldest', 'oldest_index', 'youngest', 'youngest_index', 'ts_count',
                          'refs', 'rule', "b_scheme"]
            x_resi = pd.DataFrame([] * 5, index=["name", "oldest", "youngest", "ts_count", "refs"])
            x_resi = pd.DataFrame.transpose(x_resi)
            xal = pd.merge(pd.merge(resi_5s,resi_5y,on='name'),resi_5c,on='name')
            bnu = xal["name"]
            bnu = bnu.drop_duplicates()
            bnu = bnu.dropna()
            bnurange = np.arange(0,len(bnu),1)
            for i in bnurange:
            #i=2
                i_name = bnu.iloc[i]
                x2_sub = x2.loc[((x2["name"]== i_name))]
                x2_subs = x2.loc[((x2["name"]== i_name) & (x2["b_scheme"]== "s"))]
                x2_suby = x2.loc[((x2["name"]== i_name) & (x2["b_scheme"]== "y"))]
                x2_subc = x2.loc[((x2["name"]== i_name) & (x2["b_scheme"]== "c"))]
                # youngest = max, oldest = min index
                x_range_s = np.array([min(x2_subs["oldest_index"])])
                x_range_y = np.array([min(x2_suby["oldest_index"])])
                x_range_c = np.array([min(x2_subc["oldest_index"])])

                if min(x2_subs["oldest_index"]) != max(x2_subs["youngest_index"]):
                    x_range_s = np.arange(min(x2_subs["oldest_index"]),max(x2_subs["youngest_index"])+1,1)
                if min(x2_suby["oldest_index"]) != max(x2_suby["youngest_index"]):
                    x_range_y = np.arange(min(x2_suby["oldest_index"]),max(x2_suby["youngest_index"])+1,1)
                if min(x2_subc["oldest_index"]) != max(x2_subc["youngest_index"]):
                    x_range_c = np.arange(min(x2_subc["oldest_index"]),max(x2_subc["youngest_index"])+1,1)

                rax = np.concatenate((x_range_s, x_range_s, x_range_c))
                # filter for third quantile, only bins with highest score
                rax_counts = pd.DataFrame(np.unique(rax, return_counts=True), index = ['ts_bins', 'counts'])
                rax_counts = rax_counts.transpose()
                rq = round(np.quantile(rax_counts['counts'], 0.75),0)
                rax_sub = rax_counts.loc[rax_counts['counts']>= rq, ['ts_bins']]
                rax_sub = pd.merge(rax_sub, used_ts, how= 'inner', left_on="ts_bins", right_on="ts_index")
                x_youngest = rax_sub.loc[(rax_sub["ts_index"]== max(rax_sub["ts_index"])), ['ts']]
                x_oldest = rax_sub.loc[(rax_sub["ts_index"]== min(rax_sub["ts_index"])), ['ts']]
                ts_c = max(rax_sub["ts_index"])-min(rax_sub["ts_index"])
                refs_f = pd.unique(x2_sub['refs'])
                refs_f = pd.DataFrame(refs_f)
                refs_f = refs_f[0].apply(str)
                refs_f = refs_f.str.cat(sep=', ')
                ref_list = refs_f.split(", ")
                ref_list_u = list(set(ref_list))
                str1 = ", "
                refs_f = str1.join(ref_list_u)
                x_resib = pd.DataFrame([[i_name, x_oldest.iloc[0,0], x_youngest.iloc[0,0], ts_c, refs_f]],
                                   columns=["name", "oldest", "youngest", "ts_count", "refs"])
                x_resi = pd.concat([x_resi, x_resib], axis=0, sort=True)
            resi_5 = x_resi
            resi_5['rule'] = 5.9


    resi_5 = pd.DataFrame.drop_duplicates(resi_5)
    resi_5 = resi_5[['name', 'oldest', 'youngest', 'ts_count', 'refs', 'rule']]
    combi_x = pd.concat([resi_0, resi_1, resi_2, resi_3, resi_4], axis=0, sort=False)
    resi_5 = resi_5[~resi_5["name"].isin(combi_x["name"])] # filter non-bio rule 1
    resi_5 = resi_5[~resi_5["name"].isin(used_ts['ts'])] # filter Dapingian problem
    print("rule 5 has ", len(resi_5), "binned relations")
    print("Rule 5:  relations among named non-biostratigraphical units that have indirect relations to binning scheme")
    print("via biostratigraphical units.")
    resi_5.to_csv("x_rule5.csv", index = False, header=True)

    ##################################################################################
    ### Rule 6: indirect relations of non-bio* to resis_bio to binning scheme (route via resis_bio)
    #rule 6 corrected at 23.03.2020
    resis_nbio = pd.concat([resi_0, resi_2], axis=0)
    resis_nbio.to_csv('resis_nbio.csv') # all binnings via bio non bio only

    x1 = pd.merge(resis_nbio, cr_g, left_on="name", right_on="name_1")
    x1 = pd.merge(x1, used_ts, how= 'inner', left_on="oldest", right_on="ts") # time bin info is added here
    x1 = x1[['name_2', 'name_1', 'oldest', "ts_index", 'youngest', 'ts_count', 'refs',
             'rule', 'reference_id', "reference_year"]]
    x1.columns = ['name_2', 'name_1', 'oldest', "oldest_index", 'youngest', 'ts_count', 'refs',
                  'rule', 'reference_id', "reference_year"]
    x1 = pd.merge(x1, used_ts, how= 'inner', left_on="youngest", right_on="ts") # time bin info is added here
    x1 = x1[['name_2', 'name_1', 'oldest', "oldest_index", 'youngest', "ts_index", 'ts_count', 'refs',
             'rule', 'reference_id', "reference_year"]]
    x1.columns = ['name_2', 'name_1', 'oldest', "oldest_index", 'youngest', 'youngest_index', 'ts_count', 'refs',
                  'rule', 'reference_id', "reference_year"]
    x1m = x1[['name_1', 'name_2', 'oldest', "oldest_index", 'youngest', "youngest_index", 'ts_count', 'refs',
             'rule', 'reference_id', "reference_year"]]
    x1.columns = ['name_1', 'name_2', 'oldest', "oldest_index", 'youngest', 'youngest_index', 'ts_count', 'refs',
                  'rule', 'reference_id', "reference_year"]
    x1  = pd.concat((x1,x1m), axis=0)
    x1 = x1[~x1["name_1"].isin(resi_0["name"])]
    x1 = x1[~x1["name_1"].isin(resi_2["name"])]# all first level linked non-bio* to rule 2
    x1 =  x1.loc[~(x1["name_1"]=="not specified")]
    x1["rule"] = 6.6 # only for control
    pd.DataFrame.head(x1)
    x1 = x1.drop_duplicates()
    x1.to_csv("x_x1.csv", index = False, header=True)

    x2 = cr_g[~cr_g["name_1"].isin(x1["name_1"])] # all not yet binned in cr_g
    x2 = pd.DataFrame.drop_duplicates(x2)
    x2.to_csv("x_x2.csv", index = False, header=True)
    resi_6 = pd.DataFrame([] * 6, index=["name", "oldest", "youngest", "ts_count", "refs", "rule"])
    resi_6 = pd.DataFrame.transpose(resi_6)
    for ibs in runrange:
        for k in np.arange(1,5,1):
            bnu = x1["name_1"]
            bnu = bnu.drop_duplicates()
            bnurange = np.arange(0,len(bnu),1)
            x3 = pd.DataFrame([] * 5, index=["name", "oldest", "youngest", "ts_count", "refs"])
            x3 = pd.DataFrame.transpose(x3)
            #for loop runs through each name_1
            for i in bnurange:
                if ibs == 0:
                    x3a = rn_funs.bifu_s2(x1.loc[x1["name_1"]==bnu.iloc[i]], used_ts, xnames_raw)
                if ibs == 1:
                    x3a = rn_funs.bifu_y2(x1.loc[x1["name_1"]==bnu.iloc[i]], used_ts, xnames_raw)
                if ibs == 2:
                    x3a = rn_funs.bifu_c2(x1.loc[x1["name_1"]==bnu.iloc[i]], used_ts, xnames_raw)
                x3 = pd.concat([x3, x3a], axis=0, sort=True)
            x3 = pd.DataFrame.drop_duplicates(x3)
            x3 = x3.dropna()
            x3["rule"] = 6.0+((k-1)*0.1)
            x3b = x3[~x3["name"].isin(resi_6["name"])] # filter for already binned names
            resi_6 = pd.concat([resi_6, x3b], axis=0, sort=True) # appended to previous ruling; these are now binned
            pd.DataFrame.head(resi_6)
            x2a = cr_g[~cr_g["name_1"].isin(resi_6["name"])] # all non binned names in cr_g with current rule

            #create a new x1 based on above ruling
            if (k==1):
                x4a = pd.concat((resi_3, x3), axis=0)
            else:
                x4a = pd.concat((x4a, x3), axis=0)

            x4 = pd.merge(x4a, cr_g, left_on="name", right_on="name_2") # name_2 is already binned here
            x4 = pd.merge(x4, used_ts, how= 'inner', left_on="oldest", right_on="ts") # time bin info is added here
            x4 = x4[['name_2', 'name_1', 'oldest', "ts_index", 'youngest', 'ts_count', 'refs',
                     'rule', 'reference_id', "reference_year"]]
            x4.columns = ['name_2', 'name_1', 'oldest', "oldest_index", 'youngest', 'ts_count', 'refs',
                          'rule', 'reference_id', "reference_year"]
            x4 = pd.merge(x4, used_ts, how= 'inner', left_on="youngest", right_on="ts") # time bin info is added here
            x4 = x4[['name_2', 'name_1', 'oldest', "oldest_index", 'youngest', "ts_index", 'ts_count', 'refs',
                     'rule', 'reference_id', "reference_year"]]
            x4.columns = ['name_2', 'name_1', 'oldest', "oldest_index", 'youngest', 'youngest_index',
                          'ts_count', 'refs', 'rule', 'reference_id', "reference_year"]
            x4m = x4[['name_1', 'name_2', 'oldest', "oldest_index", 'youngest', "youngest_index", 'ts_count', 'refs',
                     'rule', 'reference_id', "reference_year"]]
            x4.columns = ['name_1', 'name_2', 'oldest', "oldest_index", 'youngest', 'youngest_index',
                          'ts_count', 'refs', 'rule', 'reference_id', "reference_year"]
            x1  = pd.concat((x4,x4m), axis=0)
            x1 =  x1.loc[~(x1["name_1"]=="not specified")]
            x1["rule"] = 6.7
            pd.DataFrame.head(x1)
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
            resi_6 = pd.concat([resi_6s, resi_6y, resi_6c])
            x2 = pd.merge(resi_6, used_ts, how= 'inner', left_on="oldest", right_on="ts")
            x2 = x2[['name', 'oldest', 'ts_index', 'youngest', 'ts_count',
                     'refs', 'rule', "b_scheme"]]
            x2.columns = ['name', 'oldest', 'oldest_index', 'youngest', 'ts_count',
                          'refs', 'rule', "b_scheme"]
            x2 = pd.merge(x2, used_ts, how= 'inner', left_on="youngest", right_on="ts")
            x2 = x2[['name', 'oldest', 'oldest_index', 'youngest', 'ts_index','ts_count',
                     'refs', 'rule', "b_scheme"]]
            x2.columns = ['name', 'oldest', 'oldest_index', 'youngest', 'youngest_index', 'ts_count',
                          'refs', 'rule', "b_scheme"]
            x_resi = pd.DataFrame([] * 5, index=["name", "oldest", "youngest", "ts_count", "refs"])
            x_resi = pd.DataFrame.transpose(x_resi)
            xal = pd.merge(pd.merge(resi_6s,resi_6y,on='name'),resi_6c,on='name')
            bnu = xal["name"]
            bnu = bnu.drop_duplicates()
            bnu = bnu.dropna()
            bnurange = np.arange(0,len(bnu),1)
            for i in bnurange:
            #i=2
                i_name = bnu.iloc[i]
                x2_sub = x2.loc[((x2["name"]== i_name))]
                x2_subs = x2.loc[((x2["name"]== i_name) & (x2["b_scheme"]== "s"))]
                x2_suby = x2.loc[((x2["name"]== i_name) & (x2["b_scheme"]== "y"))]
                x2_subc = x2.loc[((x2["name"]== i_name) & (x2["b_scheme"]== "c"))]
                # youngest = max, oldest = min index
                x_range_s = np.array([min(x2_subs["oldest_index"])])
                x_range_y = np.array([min(x2_suby["oldest_index"])])
                x_range_c = np.array([min(x2_subc["oldest_index"])])

                if min(x2_subs["oldest_index"]) != max(x2_subs["youngest_index"]):
                    x_range_s = np.arange(min(x2_subs["oldest_index"]),max(x2_subs["youngest_index"])+1,1)
                if min(x2_suby["oldest_index"]) != max(x2_suby["youngest_index"]):
                    x_range_y = np.arange(min(x2_suby["oldest_index"]),max(x2_suby["youngest_index"])+1,1)
                if min(x2_subc["oldest_index"]) != max(x2_subc["youngest_index"]):
                    x_range_c = np.arange(min(x2_subc["oldest_index"]),max(x2_subc["youngest_index"])+1,1)

                rax = np.concatenate((x_range_s, x_range_s, x_range_c))
                # filter for third quantile, only bins with highest score
                rax_counts = pd.DataFrame(np.unique(rax, return_counts=True), index = ['ts_bins', 'counts'])
                rax_counts = rax_counts.transpose()
                rq = round(np.quantile(rax_counts['counts'], 0.75),0)
                rax_sub = rax_counts.loc[rax_counts['counts']>= rq, ['ts_bins']]
                rax_sub = pd.merge(rax_sub, used_ts, how= 'inner', left_on="ts_bins", right_on="ts_index")
                x_youngest = rax_sub.loc[(rax_sub["ts_index"]== max(rax_sub["ts_index"])), ['ts']]
                x_oldest = rax_sub.loc[(rax_sub["ts_index"]== min(rax_sub["ts_index"])), ['ts']]
                ts_c = max(rax_sub["ts_index"])-min(rax_sub["ts_index"])
                refs_f = pd.unique(x2_sub['refs'])
                refs_f = pd.DataFrame(refs_f)
                refs_f = refs_f[0].apply(str)
                refs_f = refs_f.str.cat(sep=', ')
                ref_list = refs_f.split(", ")
                ref_list_u = list(set(ref_list))
                str1 = ", "
                refs_f = str1.join(ref_list_u)
                x_resib = pd.DataFrame([[i_name, x_oldest.iloc[0,0], x_youngest.iloc[0,0], ts_c, refs_f]],
                                   columns=["name", "oldest", "youngest", "ts_count", "refs"])
                x_resi = pd.concat([x_resi, x_resib], axis=0, sort=True)
            resi_6 = x_resi
            resi_6['rule'] = 6.9

    resi_6 = pd.DataFrame.drop_duplicates(resi_6)
    resi_6 = resi_6[['name', 'oldest', 'youngest', 'ts_count', 'refs', 'rule']]
    combi_x = pd.concat([resi_0, resi_1, resi_2, resi_3, resi_4], axis=0, sort=False)
    resi_6 = resi_6[~resi_6["name"].isin(combi_x["name"])] # filter non-bio rule 1
    resi_6 = resi_6[~resi_6["name"].isin(used_ts['ts'])] # filter Dapingian problem
    print("rule 6 has ", len(resi_6), "binned relations")
    print("Rule 6:  relations among named non-biostratigraphical units that have indirect relations to binning scheme")
    print("via non-biostratigraphical units.")
    resi_6.to_csv("x_rule6.csv", index = False, header=True)

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
    #com_56_r.to_csv("x_com_56_r.csv", index = False, header=True)

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
    #com_56_d.to_csv("x_com_56_d.csv", index = False, header=True)

    # all where names of 5 and 6 in common and duration is not similar
    # we take the complete range
    cau = com_a.loc[~(com_a["ts_count_x"] == com_a["ts_count_y"]),
                    ["name","rule_x","oldest_x", "youngest_x", "oldest_y", "youngest_y",
                     "ts_count_x", "ts_count_y","refs_x", "refs_y"]]
    bnu = cau["name"]
    bnu = bnu.drop_duplicates()
    bnurange = np.arange(0,len(bnu),1)
    com_56_s = pd.DataFrame([] * 6, index=["name", "oldest", "youngest", "ts_count", "refs", "rule"])
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
        com_56_sa = pd.DataFrame([i_name, res_oldest,res_youngest, ts_c, refs_f, "5, 6"],
                           index=["name", "oldest", "youngest", "ts_count", "refs", "rule"])
        com_56_s = pd.concat([com_56_s, com_56_sa], axis=1, sort=True)
    com_56_s = com_56_s.transpose()
    #com_56_s.to_csv("x_com_56_s.csv", index = False, header=True)

    # all where 5 and 6 are not in common
    combi_56a = pd.concat([com_56_r, com_56_d, com_56_s], axis=0, sort=False)
    bnu = combi_56a["name"]
    c6 = resi_6[~resi_6["name"].isin(bnu)]
    c5 = resi_5[~resi_5["name"].isin(bnu)]
    #c6.to_csv("x_c6.csv", index = False, header=True)
    #c5.to_csv("x_c5.csv", index = False, header=True)

    combi_56 = pd.concat([com_56_r, com_56_d, com_56_s], axis=0, sort=False)
    #combi_56.to_csv("combi_56.csv", index = False, header=True)
    combi_names = pd.concat([resi_0, resi_1, resi_2, resi_3, resi_4,
                             c5, combi_56, c6], axis=0, sort=False)
    combi_names.to_csv("x_combi_names.csv", index = False, header=True)

    end = time.time()
    dura2 = (end - start)/60

    print("We find", len(combi_names),
          "binned names. It took ", round(dura, 2), "+", round(dura2, 2),  "minutes.")
    return(combi_names)
