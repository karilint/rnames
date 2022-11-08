#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import time

###################
# binning based on relations to absolute time
# excluding the PBDB ages (bin_fun_PBDB bins via PBDB ages)


def bin_fun_abs (c_rels, binning_scheme, ts_names, t_scales, not_spec):
     
    t_scheme = binning_scheme
    x_names = ts_names[ts_names['ts_name']==t_scheme]
    used_ts = t_scales[t_scales['ts_name_id']==x_names['id'].values[0]]
    # rename columns in order to make compatible with following code
    used_ts = used_ts[['structured_name_id', 'sequence']]
    used_ts.rename(columns={'structured_name_id':'ts', 'sequence': 'ts_index'},inplace = True)
    
    # this object give the PDBD upload id(s)
    ref_id = c_rels[["reference_id"]]
    if ref_id.shape[0]>0:
        ref_id = ref_id.drop_duplicates()

    # makes c_rels two-sided
    c_rels = c_rels[['id', 
                     'name_one_id', 'name_two_id',
                     'name_one_name_name','name_two_name_name',
                     'name_one_qualifier_qualifier_name_name', 'name_two_qualifier_qualifier_name_name', 
                     'name_one_remarks','name_two_remarks','reference_id', 'reference_year']]
    c_rels.rename(columns={'name_one_id': 'name_1', 'name_two_id':'name_2',
                           'name_one_name_name' : 'struct_name_1', 'name_two_name_name' : 'struct_name_2',
                         'name_one_qualifier_qualifier_name_name': 'strat_qualifier_1',
                         'name_two_qualifier_qualifier_name_name': 'strat_qualifier_2'},inplace = True) # rename to fit following code
    # make c_rels two-sided
    c_relsx = c_rels[['id', 
                      'name_2','name_1',
                      'struct_name_2', 'struct_name_1',
                      'strat_qualifier_2', 'strat_qualifier_1', 
                      'name_two_remarks','name_one_remarks','reference_id', 'reference_year']]
    c_relsx.columns = ['id', 
                       'name_1', 'name_2',
                       'struct_name_1', 'struct_name_2',
                       'strat_qualifier_1','strat_qualifier_2',
                       'name_one_remarks','name_two_remarks','reference_id', 'reference_year']
    c_rels = pd.concat([c_rels.reset_index(drop=False), c_relsx.reset_index(drop=False)], axis=0)
    c_rels = c_rels.reset_index(drop=True)  
    
    # exclude not specified relations (check for improvement, needs evtl placed somewhere else)
    not_spec_x = c_rels[c_rels['name_1'].isin(not_spec['id'])]
    not_spec_ref = not_spec_x[['reference_id']]
    not_spec_sn = not_spec_x[['name_2']]
    c_rels = c_rels[~(c_rels['reference_id'].isin(not_spec_ref['reference_id']) & 
                     c_rels['name_2'].isin(not_spec_sn['name_2']))]

    
    # some PBDB downloaded structured names have only relations to Absolute time
    # these are ignored by binning-fun_id.binning_fun()
    # here we bin them according to their PBDB absolute age:

    # get absolute ages of ts   
    c_rels_abs = c_rels[c_rels['strat_qualifier_2'] =='mya'] # all absolute ages of ts
    #print('####### c_rels abs 1:',c_rels_abs.shape[0])
    abs_ts = c_rels_abs[c_rels_abs['name_1'].isin(used_ts['ts'])]
   
    # if ts with ages exist:
    if abs_ts.shape[0]==0:     
        abs_names_binned = pd.DataFrame([] * 6, columns=['name', 'oldest','youngest', 'ts_count', 'refs', 'rule'])
        print('No absolute ages in binning scheme. Empty data frame returned.')

    if abs_ts.shape[0]>0:
        start = time.time()
    
        abs_ts_binned = pd.DataFrame([] * 6, columns=['name', 'oldest','youngest', 'ts_count', 'refs', 'rule'])
        abs_ts_binned_abs = pd.DataFrame([] * 6, columns=['name', 'oldest_abs','youngest_abs', 
                                                          'oldest_id','youngest_id''ts_count', 'refs', 'rule'])
       
        for i in range(0,len(used_ts)):
           x_abs_ts = abs_ts[abs_ts['name_1'] == used_ts['ts'].iloc[i]];
           if x_abs_ts.shape[0] > 0:
                oldest = max((x_abs_ts['struct_name_2'])) # oldest mya
                youngest = min((x_abs_ts['struct_name_2'])) # youngest mya
                x_youngest = abs_ts[abs_ts['struct_name_2'] == youngest]
                x_oldest = abs_ts[abs_ts['struct_name_2'] == oldest]
                if x_oldest.shape[0] > 0:
                   # combi_abs names are struct_names (the actual million years)
                   combi_abs = pd.DataFrame([{'name': used_ts['ts'].iloc[i],
                                   'oldest_abs': oldest, 'youngest_abs': youngest,
                                   'oldest_id': x_oldest['name_2'].iloc[0], 'youngest_id': x_youngest['name_2'].iloc[0],
                                   'ts_count': 0,'refs':ref_id['reference_id'].iloc[0], 'rule': 8.0}])
                   # combi names are id's only
                   combi = pd.DataFrame([{'name': used_ts['ts'].iloc[i],
                                   'oldest': x_oldest['name_2'].iloc[0], 'youngest':  x_youngest['name_2'].iloc[0],
                                   'ts_count': 0,'refs':ref_id['reference_id'].iloc[0], 'rule': 8.0}])
                   abs_ts_binned = pd.concat([abs_ts_binned, combi], axis=0)
                   abs_ts_binned_abs = pd.concat([abs_ts_binned_abs, combi_abs], axis=0)
                
        # get all other absolute ages
        c_rels_abs = c_rels_abs[~c_rels_abs['name_1'].isin(used_ts['ts'])]   
        names_with_abs_age = c_rels_abs['name_1'].drop_duplicates()
        names_with_abs_age = names_with_abs_age.to_frame()
        
        # Convert column data to numeric
        abs_ts_binned_abs['youngest_abs'] = pd.to_numeric(abs_ts_binned_abs['youngest_abs'])
        abs_ts_binned_abs['oldest_abs'] = pd.to_numeric(abs_ts_binned_abs['oldest_abs'])
    
        abs_names_binned = pd.DataFrame([] * 6, columns=['name', 'oldest','youngest', 'ts_count', 'refs', 'rule'])
        for i in range(0,len(names_with_abs_age)):
            x_c_rels_abs = c_rels_abs[c_rels_abs['name_1'] == names_with_abs_age['name_1'].iloc[i]]            
            max_year = max((x_c_rels_abs['reference_year'])) ## here filter for youngest 'reference_year'
            x_c_rels_abs = x_c_rels_abs[x_c_rels_abs['reference_year'] == max_year]
            if x_c_rels_abs.shape[0]>0:
                oldest = max(pd.to_numeric(x_c_rels_abs['struct_name_2']))
                youngest = min(pd.to_numeric(x_c_rels_abs['struct_name_2']))
                x_strat_oldest = abs_ts_binned_abs[(abs_ts_binned_abs['youngest_abs']<=oldest) & 
                                                   (abs_ts_binned_abs['oldest_abs']>=oldest)]
                x_strat_youngest = abs_ts_binned_abs[(abs_ts_binned_abs['youngest_abs']<=youngest) & 
                                                     (abs_ts_binned_abs['oldest_abs']>=youngest)]        
                if (x_strat_oldest.shape[0]>0) & (x_strat_youngest.shape[0]>0):
                    yts = used_ts[used_ts['ts']==x_strat_youngest['name'].iloc[0]]
                    ots = used_ts[used_ts['ts']==x_strat_oldest['name'].iloc[0]]
                    combi = pd.DataFrame([{'name': names_with_abs_age['name_1'].iloc[i],
                                       'oldest': x_strat_oldest['name'].iloc[0], 'youngest': x_strat_youngest['name'].iloc[0],
                                       'ts_count': ots['ts_index'].iloc[0]-yts['ts_index'].iloc[0],
                                       'refs':ref_id['reference_id'].iloc[0], 'rule': 8.0}])
                    abs_names_binned = pd.concat([abs_names_binned, combi], axis=0)

        end = time.time()
        dura = (end - start)/60
    
        print("############################################")
        print("We find",len(abs_names_binned),"binned names with absolute age. It took", round(dura, 2), "minutes")
        print("############################################")
     
    return abs_names_binned  
