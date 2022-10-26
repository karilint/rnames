#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
from . import binning_fun_id 
from . import binning_fun_PBDB
from . import binning_fun_macrostrat
from . import binning_fun_abs_time
from . import binning_fun_rule9

def main_binning_fun(binning_scheme, ts_names = None, t_scales = None, res_rels_RN_raw = None, res_sn_raw = None):
    ###################
    ###################
    # first we download and create all objects needed for binning
    # res_rels_RN_raw = download_relations_from_api()

    #print(res_rels_RN_raw.keys())

    # make relations two sided
    res_rels_RN = res_rels_RN_raw[['id', 'name_one_id', 'name_two_id',
                                   'name_one_name_name', 'name_two_name_name',
                                   'name_one_qualifier_qualifier_name_name',
                                   'name_two_qualifier_qualifier_name_name',
                                   'reference_id','reference_year','reference_title',
                                   'database_origin']]
    res_rels_RN_rw = res_rels_RN_raw[['id', 'name_two_id', 'name_one_id',
                                   'name_two_name_name', 'name_one_name_name',
                                   'name_one_qualifier_qualifier_name_name',
                                   'name_two_qualifier_qualifier_name_name',
                                   'reference_id','reference_year','reference_title', 
                                   'database_origin']]
    res_rels_RN_rw.columns = ['id', 'name_one_id', 'name_two_id',
                                   'name_one_name_name', 'name_two_name_name',
                                   'name_one_qualifier_qualifier_name_name',
                                   'name_two_qualifier_qualifier_name_name',
                                   'reference_id','reference_year','reference_title', 
                                   'database_origin']
    res_rels_RN_tw = pd.concat([res_rels_RN, res_rels_RN_rw], axis=0)

    ###################
    #download structured names from RNames API
    # res_sn_raw = download_structured_names_from_api()

    #print(res_sn_raw.keys())
    res_sn = res_sn_raw[['id', 'name_name', 'qualifier_qualifier_name_name','location_name',
                               'reference_first_author', 'reference_year','reference_id', 'remarks']]

    ###################
    # filter for structured names that relate to "not specified" within reference
    # these get exempted from binning
    not_spec = res_sn[res_sn['name_name']== 'not specified']
    not_spec = not_spec[['id']]

    ###################
    ## read time scales
    # this should be via API as soon as functional
    # see my email
    # ts_names = pd.read_csv ('ts_names.csv')
    # t_scales = pd.read_csv ('time_scales.csv')

    ###################
    # define time scale scheme
    # this should be via input form on frontend,
    # before implementing it into frontent can you test if the script runs
    # with these three
    # examples: 'Ordovician time bins (Webby et al., 2004)'
    # 'Periods (ICS, 2020)'
    # 'Stages (ICS, 2020)'
    # binning_scheme = 'Ordovician time bins (Webby et al., 2004)'# this is input
    # binning_scheme = 'Periods (ICS, 2020)'
    # binning_scheme = 'Stages (ICS, 2020)'
    #print(binning_scheme)
    #print(t_scales)
    #print(ts_names)

    ###################
    # define binning algorithm
    # this should be via input form on frontend
    # example: 'combined'
    binning_algorithm = 'combined' # this is input

    ###################
    ###################
    ## binning of structured names imported from PBDB without reference
    res_rels_RN_PBDB = res_rels_RN_raw[res_rels_RN_raw['database_origin'] == 2]
    print('##### Now we are searching for binnings within',res_rels_RN_PBDB.shape[0],' PBDB entries:')
    PBDB_names_binned = binning_fun_PBDB.bin_fun_PBDB(c_rels = res_rels_RN_PBDB,
                               binning_scheme = binning_scheme, ts_names = ts_names, t_scales = t_scales)
    #print("###### PBDB_binned:", PBDB_names_binned.shape[0])
    print("###### PBDB_binned:", PBDB_names_binned)
    
    
    ###################
    ###################
    ## binning of structured names imported from macrostrat without reference
    res_rels_RN_MS = res_rels_RN_raw[res_rels_RN_raw['database_origin'] == 3]
    print('##### Now we are searching for binnings within',res_rels_RN_MS.shape[0],' Macrostrat entries:')
    MS_names_binned = binning_fun_macrostrat.bin_fun_macrostrat(c_rels = res_rels_RN_MS,
                               binning_scheme = binning_scheme, ts_names = ts_names, t_scales = t_scales)

    ###################
    ###################
    ## binning of RNames structured names
    res_rels_RN_RN = res_rels_RN_raw[res_rels_RN_raw['database_origin'] == 1]
    print('##### Now we are searching for binnings within',res_rels_RN_RN.shape[0],'RNames entries:')
    RN_names_binned = binning_fun_id.bin_fun(c_rels = res_rels_RN_RN, binning_algorithm = binning_algorithm,
                               binning_scheme = binning_scheme, ts_names = ts_names,
                               t_scales = t_scales, not_spec = not_spec)
    print('######## RNames binned',RN_names_binned)
    
    ###################
    ###################
    ## binning via absolute ages (except PBDB and Macrostrat)
    print('##### Now we are searching for binnings within', res_rels_RN_raw.shape[0],' entries for absolute time relations:')
    abs_names_binned_full = binning_fun_abs_time.bin_fun_abs(c_rels = res_rels_RN_raw,
                               binning_scheme = binning_scheme, ts_names = ts_names, 
                               t_scales = t_scales, not_spec = not_spec)
    binned_yet = pd.concat([RN_names_binned['name'], PBDB_names_binned['name'], MS_names_binned['name']], axis=0) 
    binned_yet = binned_yet.drop_duplicates()
    #print("###### binned_yet:", binned_yet)
    abs_names_binned = abs_names_binned_full[~abs_names_binned_full['name'].isin(binned_yet)] # only the names which are not binned yet
    print("###### of which", abs_names_binned.shape[0],'were not binned yet')
    
    
    ###################
    ###################
    ## binning of remaining names (rule 9)
    # res_rels_RN_tw
    binned_raw_rule9 = pd.concat([RN_names_binned, PBDB_names_binned, MS_names_binned, abs_names_binned], axis=0)
    binned_yet = pd.concat([RN_names_binned['name'], PBDB_names_binned['name'], MS_names_binned['name'], 
                           abs_names_binned['name']], axis=0) 
    binned_yet = binned_yet.drop_duplicates()
    not_yet_binned = res_rels_RN_raw[~res_rels_RN_raw['name_one_id'].isin(binned_yet)]
    r9_names_binned = binning_fun_rule9.bin_fun_rule9(c_rels = not_yet_binned, already_binned = binned_raw_rule9,
                               binning_scheme = binning_scheme, ts_names = ts_names, t_scales = t_scales,
                               not_spec = not_spec, binning_algorithm = binning_algorithm)
    #print("###### r9_names_binned:", r9_names_binned)


    ###################
    ###################
    ## preparation of output
    # there will be two output tables
    # resi_binned: gives binning of each individual structured name with relations
    # binned_generalised: gives binning of identical names

    #make results readable
    binned_raw = pd.concat([RN_names_binned, PBDB_names_binned, MS_names_binned, 
                            abs_names_binned, r9_names_binned], axis=0)
    binned_raw = binned_raw.drop_duplicates()
    # name readable name
    binned_raw = pd.merge(binned_raw, res_sn, left_on="name", right_on="id")
    binned_raw.rename(columns={'id':'name_id', 'name': 'name_a', 'name_name': 'name',
                                'qualifier_qualifier_name_name': 'qualifier_name'},inplace = True)   
    binned_raw = binned_raw[['name_id', 'name', 'qualifier_name','oldest',
                               'youngest', 'refs', 'rule']]
    print('##### binned_raw1:', binned_raw)
    # oldest readable names
    binned_raw = pd.merge(binned_raw, res_sn, left_on="oldest", right_on="id")
    binned_raw.rename(columns={'id':'oldest_id', 'name_name': 'oldest_name'},inplace = True)
    binned_raw = binned_raw[['name_id', 'name', 'qualifier_name','oldest_id', 'oldest_name',
                               'youngest', 'refs', 'rule']]
    print('##### binned_raw2:', binned_raw)
    # youngest readable names
    binned_raw = pd.merge(binned_raw, res_sn, left_on="youngest", right_on="id")
    binned_raw.rename(columns={'id':'youngest_id', 'name_name': 'youngest_name'},inplace = True)
    binned_raw = binned_raw[['name_id', 'name', 'qualifier_name','oldest_id', 'oldest_name',
                               'youngest_id', 'youngest_name', 'refs', 'rule']]
   
    print('##### binned_raw3:', binned_raw)
    print('##### binning_scheme:', binning_scheme.drop_duplicates())
    bs = binning_scheme.drop_duplicates()
    binned_raw['binning_scheme'] = bs.values[0]

    ###################
    ###################
    # output 1:
    # all structural names with distinct ids
    # binned to binning scheme
    binned_raw = binned_raw.drop_duplicates()
    print('########### binned raw', binned_raw)

    ###################
    ###################
    # generate generalised binning
    # unique names without absolute time
    uni_binned = binned_raw[binned_raw['qualifier_name'] !='mya']
    uni_binned = uni_binned[['name', 'qualifier_name']]
    uni_binned = uni_binned.drop_duplicates()
    print('##### uni_binned:', uni_binned)

    # get time bins
    x_names = ts_names[ts_names['ts_name']==binning_scheme]
    print('##### x_names:', x_names)
    time_slices = t_scales[t_scales['ts_name_id']==x_names['id'].values[0]]
    time_slices = time_slices[['structured_name_id', 'sequence']]
    time_slices.rename(columns={'structured_name_id':'ts', 'sequence':'ts_index'},inplace = True)
    print('##### time_slices:', time_slices)

    ##loop through uni_binned and collect for each name the youngest and oldest time bin
    print('##### Now we are searching for generalised bins:')
    bnu = uni_binned.index
    bnurange = np.arange(0,len(bnu),1)
    binned_generalised_ids = pd.DataFrame([] * 3, columns=["name", "oldest_id", "youngest_id"])
    
    #test
    uni_binned_x = uni_binned.iloc[4]
    print('##### uni_binned_x:', uni_binned_x)
    resi_binned_sub = binned_raw[(binned_raw["name"]==uni_binned_x['name'])
                                   & (binned_raw["qualifier_name"]==uni_binned_x['qualifier_name'])]
    print('##### resi_binned_sub:', resi_binned_sub)
    ts_tot_oldest = time_slices[time_slices["ts"].isin(resi_binned_sub['oldest_id'])]
    print('##### ts_tot_oldest:', ts_tot_oldest)
    ts_tot_youngest = time_slices[time_slices["ts"].isin(resi_binned_sub['youngest_id'])]
    ts_youngest = time_slices.loc[(time_slices['ts_index']==max(ts_tot_youngest['ts_index']))]
    ts_oldest = time_slices.loc[(time_slices['ts_index']==min(ts_tot_oldest['ts_index']))]
    print('##### ts_oldest:', ts_oldest)
    #test end
    
    for i in bnurange:
        uni_binned_x = uni_binned.iloc[i]
        resi_binned_sub = binned_raw.loc[(binned_raw["name"]==uni_binned_x['name'])
                                       & (binned_raw["qualifier_name"]==uni_binned_x['qualifier_name'])]
        ts_tot_oldest = time_slices[time_slices["ts"].isin(resi_binned_sub['oldest_id'])]
        ts_tot_youngest = time_slices[time_slices["ts"].isin(resi_binned_sub['youngest_id'])]
        ts_youngest = time_slices.loc[(time_slices['ts_index']==max(ts_tot_youngest['ts_index']))]
        ts_oldest = time_slices.loc[(time_slices['ts_index']==min(ts_tot_oldest['ts_index']))]

        combi = pd.DataFrame([{'name': uni_binned_x['name'], 'oldest_id': ts_oldest['ts'].iloc[0],
                               'youngest_id': ts_youngest['ts'].iloc[0]}])

        binned_generalised_ids = pd.concat([binned_generalised_ids, combi], axis=0)

    #print(binned_generalised_ids)

    #make results readable
    binned_generalised = pd.merge(binned_generalised_ids, res_sn, left_on="oldest_id", right_on="id")
    binned_generalised.rename(columns={'name_name': 'oldest'},inplace = True)
    binned_generalised = binned_generalised[['name', 'oldest', 'youngest_id']]
    binned_generalised = pd.merge(binned_generalised, res_sn, left_on="youngest_id", right_on="id")
    binned_generalised.rename(columns={'name_name': 'youngest'},inplace = True)
    binned_generalised['binning_scheme'] = binning_scheme.drop_duplicates()

    ###################
    ###################
    # output 2:
    # all structural names with identical name and qualifier name
    # binned to binning scheme
    # we could call this "simplified binning"
    binned_generalised = binned_generalised[['name', 'oldest', 'youngest', 'binning_scheme']]
    #print(binned_generalised)

    ## adding absolute ages to the binnings
    # Two options are available:
    # + adding the age constraints used in the PBDB: 'PBDB_ages'
    # + adding the age constraints of own RNames entries: 'RN_ages'
    # define age constraints
    agecon = 'RN_ages'

    xbinned = pd.concat([binned_raw['youngest_id'], binned_raw['oldest_id']], ignore_index=True).drop_duplicates()
    xage_res_rels = res_rels_RN_tw[(res_rels_RN_tw['name_one_id'].isin(xbinned))  &
                     (res_rels_RN_tw['name_two_qualifier_qualifier_name_name']=='mya')]

    def agebinbin (xage_res_rels,agecon):
        if agecon== 'PBDB_ages':
            xage_res_rels_x = xage_res_rels.loc[(xage_res_rels["reference_title"]=="Paleobiology Database")]
        if agecon== 'RN_ages':
            xage_res_rels_x = xage_res_rels.loc[~(xage_res_rels["reference_title"]=="Paleobiology Database")]
        if (xage_res_rels_x.shape[0]==0):
            print('No absolute time scale exists for binning approach.')
        if (xage_res_rels_x.shape[0]>0):
                xage_res_rels_x = xage_res_rels_x[['name_one_id','name_two_name_name','reference_id']]
                agerange = xage_res_rels_x['name_one_id'].drop_duplicates()
                binned_ages = pd.DataFrame([] * 4, columns=['name_id','oldest_age', 'youngest_age', 'ref_age'])
                for i in range(0,len(agerange)):
                    xage_x = xage_res_rels_x[xage_res_rels_x['name_one_id'] == agerange.iloc[i]]
                    oldest = max(pd.to_numeric(xage_x['name_two_name_name']))
                    youngest = min(pd.to_numeric(xage_x['name_two_name_name']))
                    combi = pd.DataFrame([{'name_id' : xage_x['name_one_id'].iloc[0],
                                            'oldest_age' : oldest, 'youngest_age' : youngest,
                                            'ref_age' : xage_x['reference_id'].iloc[0]}])
                    binned_ages = pd.concat([binned_ages, combi], axis=0)

                binned_ages_o = pd.merge(binned_raw, binned_ages, left_on="oldest_id", right_on="name_id")
                binned_ages_o = binned_ages_o.drop(['youngest_age','ref_age'], axis=1)
                binned_ages = pd.merge(binned_ages_o, binned_ages, left_on="youngest_id", right_on="name_id")
                binned_ages = binned_ages.drop(['oldest_age_y', 'name_id_y','name_id'], axis=1)
                binned_ages.rename(columns={'oldest_age_x':'oldest_age', 'name_id_x': 'name_id'},inplace = True)
                return (binned_ages)
        return pd.DataFrame()
    print('##### Now we are adding for absolute times to binned names.')
    binned_with_abs_ages = agebinbin(xage_res_rels = xage_res_rels,agecon = agecon)
    print('##### These are the binning with absolute time:', binned_with_abs_ages)

    ###################
    ###################
    # output 3:
    # all structural names with distinct ids
    # binned to binning scheme and with absolute ages
    binned_with_abs_ages['binning_scheme'] = binning_scheme
    binned_with_abs_ages['age_constraints'] = agecon
    
    binned_raw.to_csv('binning.csv')
    binned_generalised.to_csv('generalised.csv')
    binned_with_abs_ages.to_csv('absolute_ages.csv')

    return {
        'binning': binned_raw,
        'generalised': binned_generalised,
        'absolute_ages': binned_with_abs_ages,
    }


