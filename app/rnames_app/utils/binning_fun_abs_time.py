#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import time

###################
# binning based on relations to absolute time
# excluding the PBDB ages (bin_fun_PBDB bins via PBDB ages)


def bin_fun_abs (c_rels, binning_scheme, ts_names, t_scales):
    
    
    t_scheme = binning_scheme
    x_names = ts_names[ts_names['ts_name']==t_scheme]
    used_ts = t_scales[t_scales['ts_name_id']==x_names['id'].values[0]]
    # rename columns in order to make compatible with following code
    used_ts = used_ts[['structured_name_id', 'sequence']]
    used_ts.rename(columns={'structured_name_id':'ts', 'sequence': 'ts_index'},inplace = True)
    #print('####### used TS:', used_ts.shape[0])
    
    # this object give the PDBD upload id(s)
    ref_id = c_rels[["reference_id"]]
    if ref_id.shape[0]>0:
        ref_id = ref_id.drop_duplicates()
    #print('####### ref_id:', ref_id)

    # makes c_rels two-sided
    c_rels = c_rels[['id', 'name_one_id', 'name_two_id','name_one_qualifier_qualifier_name_name', 
                              'name_two_qualifier_qualifier_name_name', 
                              'name_one_remarks','name_two_remarks','reference_id', 'reference_year']]
    c_rels.rename(columns={'name_one_id': 'name_1', 'name_two_id':'name_2', 
                         'name_one_qualifier_qualifier_name_name': 'strat_qualifier_1',
                         'name_two_qualifier_qualifier_name_name': 'strat_qualifier_2'},inplace = True) # rename to fit following code
    # make c_rels two-sided
    c_relsx = c_rels[['id', 'name_2','strat_qualifier_2','name_1', 'strat_qualifier_1', 
                      'name_one_remarks','name_two_remarks','reference_id', 'reference_year']]
    c_relsx.columns = ['id', 'name_1','strat_qualifier_1','name_2', 'strat_qualifier_2',
                       'name_one_remarks','name_two_remarks','reference_id', 'reference_year']
    c_rels = pd.concat([c_rels.reset_index(drop=False), c_relsx.reset_index(drop=False)], axis=0)
    c_rels = c_rels.reset_index(drop=True)  
    #print('####### c_rels two sided:', c_rels.shape[0])
    
    # some PBDB downloaded structured names have only relations to Absolute time
    # these are ignored by binning-fun_id.binning_fun()
    # here we bin them according to their PBDB absolute age:

    # get absolute ages of ts   
    c_rels_abs = c_rels[c_rels['strat_qualifier_2'] =='mya'] # all absolute ages of ts
    #print('####### c_rels abs 1:',c_rels_abs.shape[0])
    abs_ts = c_rels_abs[c_rels_abs['name_1'].isin(used_ts['ts'])]
    #print('####### abs_ts:',abs_ts)
   
    # if ts with ages exist:
    if abs_ts.shape[0]==0:     
        abs_names_binned = pd.DataFrame([] * 6, columns=['name', 'oldest','youngest', 'ts_count', 'refs', 'rule'])
        print('No absolute ages in binning scheme. Empty data frame returned.')

    if abs_ts.shape[0]>0:
        start = time.time()
    
        abs_ts_binned = pd.DataFrame([] * 6, columns=['name', 'oldest','youngest', 'ts_count', 'refs', 'rule'])
        abs_ts_binned_abs = pd.DataFrame([] * 6, columns=['name', 'oldest','youngest', 'ts_count', 'refs', 'rule'])
        for i in range(0,len(used_ts)):
            x_abs_ts = abs_ts[abs_ts['name_1'] == used_ts['ts'].iloc[i]];
            if x_abs_ts.shape[0] > 0:
                oldest = max(pd.to_numeric(x_abs_ts['name_2']))
                youngest = min(pd.to_numeric(x_abs_ts['name_2']))
                x_youngest = x_abs_ts[x_abs_ts['name_2'] == youngest]
                x_oldest = x_abs_ts[x_abs_ts['name_2'] == oldest]
                combi = pd.DataFrame([{'name': used_ts['ts'].iloc[i],
                                   'oldest': x_oldest['name_1'].iloc[0], 'youngest': x_youngest['name_1'].iloc[0],
                                   'ts_count': 0,'refs':ref_id['reference_id'].iloc[0], 'rule': 8.0}])
                combi_abs = pd.DataFrame([{'name': used_ts['ts'].iloc[i],
                                   'oldest': oldest, 'youngest': youngest,
                                   'ts_count': 0,'refs':ref_id['reference_id'].iloc[0], 'rule': 8.0}])
                abs_ts_binned = pd.concat([abs_ts_binned, combi], axis=0)
                abs_ts_binned_abs = pd.concat([abs_ts_binned_abs, combi_abs], axis=0)
            
        # get all other absolute ages
        c_rels_abs = c_rels_abs[~c_rels_abs['name_1'].isin(used_ts['ts'])]   
        names_with_abs_age = c_rels_abs['name_1'].drop_duplicates()
        names_with_abs_age = names_with_abs_age.to_frame()
    
        abs_names_binned = pd.DataFrame([] * 6, columns=['name', 'oldest','youngest', 'ts_count', 'refs', 'rule'])
        for i in range(0,len(names_with_abs_age)):
            x_c_rels_abs = c_rels_abs[c_rels_abs['name_1'] == names_with_abs_age['name_1'].iloc[i]]
            ## here filter for youngest 'reference_year'
            max_year = max(pd.to_numeric(x_c_rels_abs['reference_year']))
            x_c_rels_abs = c_rels_abs[c_rels_abs['reference_year'] == max_year]
            if x_c_rels_abs.shape[0]>0:
                oldest = max(pd.to_numeric(x_c_rels_abs['name_2']))   
                youngest = min(pd.to_numeric(x_c_rels_abs['name_2']))
                x_strat_oldest = abs_ts_binned_abs[(abs_ts_binned_abs['youngest']<=oldest) & (abs_ts_binned_abs['oldest']>=oldest)]
                x_strat_youngest = abs_ts_binned_abs[(abs_ts_binned_abs['youngest']<=youngest) & (abs_ts_binned_abs['oldest']>=youngest)]
                if (x_strat_oldest.shape[0]>0) & (x_strat_youngest.shape[0]>0):
                    yts = used_ts[used_ts['ts']==x_strat_youngest['name'].iloc[0]]
                    ots = used_ts[used_ts['ts']==x_strat_oldest['name'].iloc[0]]
                    combi = pd.DataFrame([{'name': names_with_abs_age['name_1'].iloc[i],
                                       'oldest': x_strat_oldest['name'].iloc[0], 'youngest': x_strat_youngest['name'].iloc[0],
                                       'ts_count': yts['ts_index'].iloc[0]-ots['ts_index'].iloc[0],
                                       'refs':ref_id['reference_id'].iloc[0], 'rule': 8.1}])
                    abs_names_binned = pd.concat([abs_names_binned, combi], axis=0)
        end = time.time()
        dura = (end - start)/60
    
        print("############################################")
        print("We find",len(abs_names_binned),"binned names with absolute age. It took", round(dura, 2), "minutes")
        print("############################################")
     
    return abs_names_binned  
