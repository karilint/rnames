#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
from . import binning_fun_id 
from . import binning_fun_PBDB
from . import binning_fun_macrostrat
from . import binning_fun_abs_time
from . import binning_fun_rule9

def main_binning_fun(binning_scheme, ts_names = None, t_scales = None, res_rels_RN_raw = None, res_sn_raw = None, info = None):
    ###################
    ###################
    # first we download and create all objects needed for binning
    # res_rels_RN_raw = download_relations_from_api()

    # make relations two sided
    res_rels_RN = res_rels_RN_raw[['id', 
                   'name_one_id', 'name_two_id',
                   'name_one_name_name','name_two_name_name',
                   'name_one_qualifier_qualifier_name_name', 
                   'name_two_qualifier_qualifier_name_name', 
                   'name_one_remarks','name_two_remarks',
                   'reference_id', 'reference_year', 'database_origin']]
    res_rels_RN.rename(columns={'name_one_id': 'name_1', 'name_two_id':'name_2',
                         'name_one_name_name' : 'struct_name_1', 'name_two_name_name' : 'struct_name_2',
                       'name_one_qualifier_qualifier_name_name': 'strat_qualifier_1',
                       'name_two_qualifier_qualifier_name_name': 'strat_qualifier_2'},inplace = True) # rename to fit following code
    res_rels_RN_rw = res_rels_RN[['id', 
                    'name_2','name_1',
                    'struct_name_2', 'struct_name_1',
                    'strat_qualifier_2', 'strat_qualifier_1', 
                    'name_two_remarks','name_one_remarks',
                    'reference_id', 'reference_year', 'database_origin']]
    res_rels_RN_rw.columns = ['id', 
                     'name_1', 'name_2',
                     'struct_name_1', 'struct_name_2',
                     'strat_qualifier_1','strat_qualifier_2',
                     'name_one_remarks','name_two_remarks','reference_id', 'reference_year', 'database_origin']
    res_rels_RN_tw = pd.concat([res_rels_RN.reset_index(drop=False), res_rels_RN_rw.reset_index(drop=False)], axis=0)
    res_rels_RN_tw = res_rels_RN_tw.reset_index(drop=True)
    res_rels_RN_tw.rename(columns={'name_1': 'name_one_id', 'name_2': 'name_two_id',
                         'struct_name_1':'name_one_name_name', 'struct_name_2':'name_two_name_name',
                       'strat_qualifier_1':'name_one_qualifier_qualifier_name_name',
                       'strat_qualifier_2':'name_two_qualifier_qualifier_name_name'},inplace = True) # rename to fit following code
    

    ###################
    #download structured names from RNames API
    # res_sn_raw = download_structured_names_from_api()

    res_sn = res_sn_raw[['id', 'name_name', 'qualifier_qualifier_name_name','qualifier_qualifier_name_id','location_name',
                               'reference_first_author', 'reference_year','reference_id', 'remarks']]

    ###################
    # filter for structured names that relate to "not specified" within reference
    # these get exempted from binning
    not_spec = res_sn[res_sn['name_name']== 'not specified']
    not_spec = not_spec[['id']]
    
    ####################
    # Early/Lower & Late/Upper problem:
    # PBDB and Macrostrat use Early and Upper instead of Lower and Upper used in stratigraphy.org chart
    # here we provisionally replace Early and Late structured names with Lower and Upper
    xr = res_sn[res_sn['qualifier_qualifier_name_id'] == 
                t_scales['structured_name_qualifier_id'].iloc[1]] # this is just to identify 'qualifier_qualifier_name_name'
    x_ts = res_rels_RN_tw[res_rels_RN_tw['name_one_qualifier_qualifier_name_name'] == 
                          xr['qualifier_qualifier_name_name'].iloc[0]] # all structured names with 'qualifier_qualifier_name_name'
    xx_ts = x_ts[~x_ts['name_one_id'].isin(t_scales['structured_name_id'])]
    xts_e = xx_ts.loc[xx_ts['name_one_name_name'].str.contains("Early ", case=True)]
    xts_l = xx_ts.loc[xx_ts['name_one_name_name'].str.contains("Late ", case=True)]
    xts_e['name_one_name_rpl'] = xts_e['name_one_name_name'].replace('Early ','Lower ', regex=True)   
    xts_l['name_one_name_rpl'] = xts_l['name_one_name_name'].replace('Late ','Upper ', regex=True)
    xts = pd.concat([xts_e[['name_one_id', 'name_one_name_rpl']], 
                     xts_l[['name_one_id', 'name_one_name_rpl']]], axis=0)
    xts.rename(columns={'name_one_id':'name_one_id_orig'},inplace = True)
    xts = pd.merge(xts, xr, left_on="name_one_name_rpl", right_on="name_name",)
    xts.rename(columns={'id':'name_one_id_rpl'},inplace = True)
    xts = xts.drop_duplicates()
    # create df with relations with replacements:
    el_ids = pd.merge(xts, xx_ts, left_on="name_one_id_orig", right_on="name_one_id", how="left")
    el_ids = el_ids.drop_duplicates()
    # this replaces relations in raw
    if (el_ids.shape[0]>0):
        for i in range(0,len(el_ids)):
            xrel = el_ids['id'].iloc[i] # relation to replace
            xel = el_ids[el_ids['id'] == xrel]
            res_rels_RN_raw['name_one_id'] = np.where(res_rels_RN_raw['id'] == xrel, 
                    xel['name_one_id_rpl'].values[0], res_rels_RN_raw['name_one_id'])
 
     # replace ids also in res_rels_RN_tw:
    if (el_ids.shape[0]>0):
        for i in range(0,len(el_ids)):
            xrel = el_ids['id'].iloc[i] # relation to replace
            xel = el_ids[el_ids['id'] == xrel]
            res_rels_RN_tw['name_one_id'] = np.where(res_rels_RN_tw['id'] == xrel, 
                     xel['name_one_id_rpl'].values[0], res_rels_RN_tw['name_one_id'])

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
    ## binning of structured names imported from PBDB (rule 7.1)
    res_rels_RN_PBDB = res_rels_RN_raw[res_rels_RN_raw['database_origin'] == 2]
    print('##### Now we are searching for binnings within',res_rels_RN_PBDB.shape[0],' PBDB entries:')
    if info is not None:
        info.update('Binning PBDB entries')
    PBDB_names_binned = binning_fun_PBDB.bin_fun_PBDB(c_rels = res_rels_RN_PBDB,
                               binning_scheme = binning_scheme, ts_names = ts_names, t_scales = t_scales)

    
    
    ###################
    ###################
    ## binning of structured names imported from macrostrat (rule 7.2)
    res_rels_RN_MS = res_rels_RN_raw[res_rels_RN_raw['database_origin'] == 3]
    print('##### Now we are searching for binnings within',res_rels_RN_MS.shape[0],' Macrostrat entries:')
    if info is not None:
        info.update('Binning Macrostrat entries')
    MS_names_binned = binning_fun_macrostrat.bin_fun_macrostrat(c_rels = res_rels_RN_MS,
                               binning_scheme = binning_scheme, ts_names = ts_names, t_scales = t_scales)

    ###################
    ###################
    ## binning of RNames structured names (rules 0-6.9)
    res_rels_RN_RN = res_rels_RN_raw[res_rels_RN_raw['database_origin'] == 1]
    print('##### Now we are searching for binnings within',res_rels_RN_RN.shape[0],'RNames entries:')
    if info is not None:
        info.update('Binning Rnames entries')
    RN_names_binned = binning_fun_id.bin_fun(c_rels = res_rels_RN_RN, binning_algorithm = binning_algorithm,
                               binning_scheme = binning_scheme, ts_names = ts_names,
                               t_scales = t_scales, not_spec = not_spec)
    #print('######## RNames binned',RN_names_binned)
    
    ###################
    ###################
    ## binning via absolute ages (except PBDB and Macrostrat) (rule 8)
    print('##### Now we are searching for RN binnings within', res_rels_RN_RN.shape[0],' entries for absolute time relations:')
    if info is not None:
        info.update('Search for absolute time relations')
    abs_names_binned_full = binning_fun_abs_time.bin_fun_abs(c_rels = res_rels_RN_RN,
                               binning_scheme = binning_scheme, ts_names = ts_names, 
                               t_scales = t_scales, not_spec = not_spec)
    print("###### We find", abs_names_binned_full.shape[0],' binnings')    
    MS_names_binned = MS_names_binned[~MS_names_binned['name'].isin(abs_names_binned_full['name'])] 
    PBDB_names_binned = PBDB_names_binned[~PBDB_names_binned['name'].isin(abs_names_binned_full['name'])] 
    RN_names_binned = RN_names_binned[~RN_names_binned['name'].isin(abs_names_binned_full['name'])] 
    abs_names_binned = abs_names_binned_full
   
    
    ###################
    ###################
    ## binning of remaining names (rule 9)
    ## here we bin as an additional step the remaing based on what is known at this step
    if info is not None:
        info.update('Bin remaining names based on rule 9')
    binned_raw_rule9 = pd.concat([RN_names_binned, PBDB_names_binned, MS_names_binned, abs_names_binned], axis=0)
    binned_yet = pd.concat([RN_names_binned['name'], PBDB_names_binned['name'], MS_names_binned['name'], 
                           abs_names_binned['name']], axis=0) 
    binned_yet = binned_yet.drop_duplicates()
    not_yet_binned = res_rels_RN_raw[~res_rels_RN_raw['name_one_id'].isin(binned_yet)]
    r9_names_binned = binning_fun_rule9.bin_fun_rule9(c_rels = not_yet_binned, already_binned = binned_raw_rule9,
                               binning_scheme = binning_scheme, ts_names = ts_names, t_scales = t_scales,
                               not_spec = not_spec, binning_algorithm = binning_algorithm)


    ###################
    ###################
    ## preparation of output
    # there will be two output tables
    # resi_binned: gives binning of each individual structured name with relations
    # binned_generalised: gives binning of identical names

    if info is not None:
        info.update('Preparing binning output')

    #make results readable
    binned_raw = pd.concat([RN_names_binned, PBDB_names_binned, MS_names_binned, 
                            abs_names_binned, r9_names_binned], axis=0)
    binned_raw = binned_raw.drop_duplicates()
    binned_raw = pd.merge(binned_raw, res_sn, left_on="name", right_on="id")
    binned_raw.rename(columns={'id':'name_id', 'name': 'name_a', 'name_name': 'name',
                                'qualifier_qualifier_name_name': 'qualifier_name'},inplace = True)   
    binned_raw = binned_raw[['name_id', 'name', 'qualifier_name','oldest',
                               'youngest', 'refs', 'rule']]
    # oldest readable names
    binned_raw = pd.merge(binned_raw, res_sn, left_on="oldest", right_on="id")
    binned_raw.rename(columns={'id':'oldest_id', 'name_name': 'oldest_name'},inplace = True)
    binned_raw = binned_raw[['name_id', 'name', 'qualifier_name','oldest_id', 'oldest_name',
                               'youngest', 'refs', 'rule']]
    # youngest readable names
    binned_raw = pd.merge(binned_raw, res_sn, left_on="youngest", right_on="id")
    binned_raw.rename(columns={'id':'youngest_id', 'name_name': 'youngest_name'},inplace = True)
    binned_raw = binned_raw[['name_id', 'name', 'qualifier_name','oldest_id', 'oldest_name',
                               'youngest_id', 'youngest_name', 'refs', 'rule']]
    bs = binning_scheme.drop_duplicates()
    binned_raw['binning_scheme'] = bs.values[0]
    
    # add replaced Early / Late names
    mraw = pd.concat([xts['name_one_id_orig'], xts['name_one_name_rpl'], xts['name_one_name_rpl'],
                      xts['name_one_name_rpl'], xts['name_one_id_rpl'], xts['name_one_id_rpl']],
                     axis=1, ignore_index=True)
    mraw.columns = ['name_id', 'name', 'oldest_name', 'youngest_name', 'oldest_id', 'youngest_id']
    mraw['refs'] = 0
    mraw['rule'] = 0
    mraw['binning_scheme'] = bs.values[0]
    mraw['qualifier_name'] = xr['qualifier_qualifier_name_name'].values[0]
    mraw['name'] = mraw['name'].replace('Lower ','Early ', regex=True)   
    mraw['name'] = mraw['name'].replace('Upper ','Late ', regex=True)
    mraw = mraw[['name_id','name', 'qualifier_name','oldest_id', 'oldest_name',
                 'youngest_id', 'youngest_name', 'refs', 'rule', 'binning_scheme' ]]
    binned_raw = pd.concat([binned_raw, mraw], axis=0)

    ###################
    ###################   
    # delete redudancies and inaccuracies with another loop
    ## through uni_binned and collect for each name the youngest and oldest time bin
    print('##### Now we remove redundancies:')
    
    bnu = binned_raw['name_id'].drop_duplicates()
    bnurange = np.arange(0,len(bnu),1)
    binned_raw_c = pd.DataFrame([] * 10, columns=['name_id', 'name', 'qualifier_name','oldest_id', 'oldest_name',
                               'youngest_id', 'youngest_name', 'refs', 'rule', 'binning_scheme'])
    binned_raw['name_id'] = pd.to_numeric(binned_raw['name_id'])
    for i in bnurange:
        x_bin = binned_raw[binned_raw['name_id']==bnu.iloc[i]]
        xx_bin = x_bin[x_bin['rule']==(min(pd.to_numeric(x_bin['rule'])))]
        binned_raw_c = pd.concat([binned_raw_c, xx_bin], axis=0)
    
    binned_raw = binned_raw_c

    ###################
    ###################
    # output 1:
    # all structural names with distinct ids
    # binned to binning scheme
    binned_raw = binned_raw.drop_duplicates()

    ###################
    ###################
    # generate generalised binning
    # unique names without absolute time
    uni_binned = binned_raw[binned_raw['qualifier_name'] !='mya']
    uni_binned = uni_binned[['name', 'qualifier_name']]
    uni_binned = uni_binned.drop_duplicates()
    #print('##### uni_binned:', uni_binned)

    # get time bins
    x_names = ts_names[ts_names['ts_name']==binning_scheme]
    time_slices = t_scales[t_scales['ts_name_id']==x_names['id'].values[0]]
    time_slices = time_slices[['structured_name_id', 'sequence']]
    time_slices.rename(columns={'structured_name_id':'ts', 'sequence':'ts_index'},inplace = True)

    ##loop through uni_binned and collect for each name the youngest and oldest time bin
    print('##### Now we are searching for generalised bins:')
    bnu = uni_binned.index
    bnurange = np.arange(0,len(bnu),1)
    binned_generalised_ids = pd.DataFrame([] * 3, columns=["name", "oldest_id", "youngest_id"])
    
    for i in bnurange:
        uni_binned_x = uni_binned.iloc[i]
        resi_binned_sub = binned_raw.loc[(binned_raw["name"]==uni_binned_x['name'])
                                       & (binned_raw["qualifier_name"]==uni_binned_x['qualifier_name'])]
        if resi_binned_sub.shape[0]>0:
            ts_tot_oldest = time_slices[time_slices["ts"].isin(resi_binned_sub['oldest_id'])]
            ts_tot_youngest = time_slices[time_slices["ts"].isin(resi_binned_sub['youngest_id'])]
            if ((ts_tot_oldest.shape[0]>0) & (ts_tot_youngest.shape[0]>0)):
                ts_youngest = time_slices.loc[(time_slices['ts_index']==max(ts_tot_youngest['ts_index']))]
                ts_oldest = time_slices.loc[(time_slices['ts_index']==min(ts_tot_oldest['ts_index']))]
        
                combi = pd.DataFrame([{'name': uni_binned_x['name'], 'oldest_id': ts_oldest['ts'].iloc[0],
                                       'youngest_id': ts_youngest['ts'].iloc[0]}])
        
                binned_generalised_ids = pd.concat([binned_generalised_ids, combi], axis=0)

    #make results readable
    binned_generalised = pd.merge(binned_generalised_ids, res_sn, left_on="oldest_id", right_on="id")
    binned_generalised.rename(columns={'name_name': 'oldest'},inplace = True)
    binned_generalised = binned_generalised[['name', 'oldest', 'youngest_id']]
    binned_generalised = pd.merge(binned_generalised, res_sn, left_on="youngest_id", right_on="id")
    binned_generalised.rename(columns={'name_name': 'youngest'},inplace = True)
    binned_generalised['binning_scheme'] = bs.values[0]

    ###################
    ###################
    # output 2:
    # all structural names with identical name and qualifier name
    # binned to binning scheme
    # we could call this "simplified binning"
    binned_generalised = binned_generalised[['name', 'oldest', 'youngest', 'binning_scheme']]
    binned_generalised = binned_generalised.drop_duplicates()


    ## adding absolute ages to the binnings
    # searches for most actual (newest reference) absolute ages of binning intervals
    xbinned = pd.concat([binned_raw['youngest_id'], binned_raw['oldest_id']], ignore_index=True).drop_duplicates()
    xage_res_rels = res_rels_RN_tw[(res_rels_RN_tw['name_one_id'].isin(xbinned))  &
                     (res_rels_RN_tw['name_two_qualifier_qualifier_name_name']=='mya')]
    xage_res_rels['reference_year'] = pd.to_numeric(xage_res_rels['reference_year'])
    xage_res_rels['database_origin'] = pd.to_numeric(xage_res_rels['database_origin'])

    def agebinbin (xage_res_rels):      # ,agecon
        xrefs = xage_res_rels['reference_id'].drop_duplicates()
        agerange = xage_res_rels['name_one_id'].drop_duplicates()
        xage_res_rels_x = xage_res_rels
        # if several absolute time schemes exist
        if (xrefs.shape[0]>1):
            xage_res_rels_x =  xage_res_rels.drop(xage_res_rels.index)# empty container for available time schemes
            print(xage_res_rels_x)
            for i in range(0, len(xrefs)):
                xxage_res_rels = xage_res_rels[xage_res_rels['reference_id'] == xrefs.iloc[i]]
                xxage_res_rels = xxage_res_rels.drop_duplicates()
                # if each ts_name has two ages or more
                if (xxage_res_rels.shape[0] >= agerange.shape[0]*2):
                    xage_res_rels_x = pd.concat([xage_res_rels_x, xxage_res_rels], axis=0)
            # use youngest reference only
            if not xage_res_rels_x.empty:
                xage_res_rels_x = xage_res_rels_x[xage_res_rels_x['reference_year'] == max(xage_res_rels_x['reference_year'])]
                xage_res_rels_x = xage_res_rels_x[xage_res_rels_x['database_origin'] == min(xage_res_rels_x['database_origin'])]

        if (xage_res_rels_x.shape[0]==0):
            print('No absolute time scale exists for binning approach.')
        if (xage_res_rels_x.shape[0]>0):
                xage_res_rels_x = xage_res_rels_x[['name_one_id','name_two_name_name','reference_id']]
                agerange = xage_res_rels_x['name_one_id'].drop_duplicates()
                binned_ages = pd.DataFrame([] * 4, columns=['name_id','oldest_age', 'youngest_age', 'ref_age'])
                for i in range(0, agerange.shape[0]):
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
    
    print('##### Now we are adding absolute times to binned names:')
    if info is not None:
        info.update('Adding absolute times to binned names')
    binned_with_abs_ages = agebinbin(xage_res_rels = xage_res_rels) #,agecon = agecon

    ###################
    ###################
    # output 3:
    # all structural names with distinct ids
    # binned to binning scheme and with absolute ages
    binned_with_abs_ages['binning_scheme'] = bs.values[0]
    #binned_with_abs_ages['age_constraints'] = agecon
    
    #binned_raw.to_csv('binning.csv')
    #binned_generalised.to_csv('generalised.csv')
    #binned_with_abs_ages.to_csv('absolute_ages.csv')

    return {
        'binning': binned_raw,
        'generalised': binned_generalised,
        'absolute_ages': binned_with_abs_ages,
    }


