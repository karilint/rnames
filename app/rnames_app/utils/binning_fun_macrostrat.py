#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import time

###################
# many Macrostrat structured names refer to absolute ages 
# these ages are coherent with in Macrostrat (Peters et al. 2018)
# to use Macrostrat age grouping a special binning algorithm is needed
# bin_fun_macrostrat is doing this.
#

def bin_fun_macrostrat (c_rels, binning_scheme, ts_names, t_scales):
    
    
    t_scheme = binning_scheme
    x_names = ts_names[ts_names['ts_name']==t_scheme]
    used_ts = t_scales[t_scales['ts_name_id']==x_names['id'].values[0]]
    # rename columns in order to make compatible with following code
    used_ts = used_ts[['structured_name_id', 'sequence']]
    used_ts.rename(columns={'structured_name_id':'ts', 'sequence': 'ts_index'},inplace = True)
    
    # this object gives the Macrostrat upload id(s)
    PBDB_id = c_rels.loc[(c_rels["database_origin"]== 3),["reference_id"]]
    if PBDB_id.shape[0]>0:
        PBDB_id = PBDB_id.drop_duplicates()

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
    
    # many Macrostrat downloaded structured names have only relations to Absolute time
    # these are ignored by binning-fun_id.binning_fun()
    # here we bin them according to their Macrostrat absolute age
    
    # get Macrostrat based absolute ages of ts   
    c_rels_abs = c_rels[c_rels['strat_qualifier_2'] =='mya'] # all absolute ages of ts
    abs_ts = c_rels_abs[c_rels_abs['name_1'].isin(used_ts['ts'])]
    
    # if ts with Macrostrat based ages exist:
    if abs_ts.shape[0]==0:     
        PBDB_names_binned = pd.DataFrame([] * 6, columns=['name', 'oldest','youngest', 'ts_count', 'refs', 'rule'])
        print('No Macrostrat based ages in binning scheme. Empty data frame returned.')

    if abs_ts.shape[0]>0:
        start = time.time()
    
        PBDB_ts_binned = pd.DataFrame([] * 6, columns=['name', 'oldest','youngest', 'ts_count', 'refs', 'rule'])
        PBDB_ts_binned_abs = pd.DataFrame([] * 6, columns=['name', 'oldest_abs','youngest_abs', 
                                                          'oldest_id','youngest_id''ts_count', 'refs', 'rule'])
        
        for i in range(0,len(used_ts)):
            x_abs_ts = abs_ts[abs_ts['name_1'] == used_ts['ts'].iloc[i]];
            if x_abs_ts.shape[0] > 0:
                oldest = max((x_abs_ts['struct_name_2']))
                youngest = min((x_abs_ts['struct_name_2']))
                x_youngest = x_abs_ts[x_abs_ts['struct_name_2'] == youngest]
                x_oldest = x_abs_ts[x_abs_ts['struct_name_2'] == oldest]
                if x_oldest.shape[0] > 0:
                    # combi_abs names are struct_names (the actual million years)
                    combi_abs = pd.DataFrame([{'name': used_ts['ts'].iloc[i],
                                    'oldest_abs': oldest, 'youngest_abs': youngest,
                                    'oldest_id': x_oldest['name_2'].iloc[0], 'youngest_id': x_youngest['name_2'].iloc[0],
                                    'ts_count': 0,'refs':PBDB_id['reference_id'].iloc[0], 'rule': 7.0}])
                    # combi names are id's only
                    combi = pd.DataFrame([{'name': used_ts['ts'].iloc[i],
                                    'oldest': x_oldest['name_2'].iloc[0], 'youngest':  x_youngest['name_2'].iloc[0],
                                    'ts_count': 0,'refs':PBDB_id['reference_id'].iloc[0], 'rule': 7.0}])
                    PBDB_ts_binned = pd.concat([PBDB_ts_binned, combi], axis=0)
                    PBDB_ts_binned_abs = pd.concat([PBDB_ts_binned_abs, combi_abs], axis=0)
            
        # get all other Macrostrat based absolute ages
        c_rels_abs = c_rels_abs[~c_rels_abs['name_1'].isin(used_ts['ts'])]
        
        # Convert column data to numeric
        PBDB_ts_binned_abs['youngest_abs'] = pd.to_numeric(PBDB_ts_binned_abs['youngest_abs'])
        PBDB_ts_binned_abs['oldest_abs'] = pd.to_numeric(PBDB_ts_binned_abs['oldest_abs'])
        
        names_with_PBDB_age = c_rels_abs['name_1'].drop_duplicates()
        names_with_PBDB_age = names_with_PBDB_age.to_frame()
   
        PBDB_names_binned = pd.DataFrame([] * 6, columns=['name', 'oldest','youngest', 'ts_count', 'refs', 'rule'])
        combi = pd.DataFrame([] * 6, columns=['name', 'oldest','youngest', 'ts_count', 'refs', 'rule'])
        for i in range(0,len(names_with_PBDB_age)):
            x_c_rels_abs = c_rels_abs[c_rels_abs['name_1'] == names_with_PBDB_age['name_1'].iloc[i]]
            if x_c_rels_abs.shape[0]>0:
                oldest = max(pd.to_numeric(x_c_rels_abs['struct_name_2']))   
                youngest = min(pd.to_numeric(x_c_rels_abs['struct_name_2']))
                x_strat_oldest = PBDB_ts_binned_abs[(PBDB_ts_binned_abs['youngest_abs']<=oldest) & 
                                                    (PBDB_ts_binned_abs['oldest_abs']>=oldest)]
                x_strat_youngest = PBDB_ts_binned_abs[(PBDB_ts_binned_abs['youngest_abs']<=youngest) & 
                                                      (PBDB_ts_binned_abs['oldest_abs']>=youngest)]
                if (x_strat_oldest.shape[0]>0) & (x_strat_youngest.shape[0]>0):
                    yts = used_ts[used_ts['ts']==x_strat_youngest['name'].iloc[0]] # youngest bin
                    ots = used_ts[used_ts['ts']==x_strat_oldest['name'].iloc[0]] # oldest bin
                    if (x_strat_youngest.shape[0]>1):    # use another condition because yts can be two
                        x_strat_youngest = x_strat_youngest[x_strat_youngest['oldest_abs'] == max(x_strat_youngest['oldest_abs'])] #  base of the top interval
                    if (x_strat_oldest.shape[0]>1):
                        x_strat_oldest = x_strat_oldest[x_strat_oldest['youngest_abs'] == min(x_strat_oldest['youngest_abs'])] # tob of the base interval
                        yts = used_ts[used_ts['ts']==x_strat_youngest['name'].iloc[0]] # youngest bin
                        ots = used_ts[used_ts['ts']==x_strat_oldest['name'].iloc[0]] # oldest bin
                    combi = pd.DataFrame([{'name': names_with_PBDB_age['name_1'].iloc[i],
                                       'oldest': x_strat_oldest['name'].iloc[0], 'youngest': x_strat_youngest['name'].iloc[0],
                                       'ts_count': yts['ts_index'].iloc[0]-ots['ts_index'].iloc[0],
                                       'refs':PBDB_id['reference_id'].iloc[0], 'rule': 7.2}])
                PBDB_names_binned = pd.concat([PBDB_names_binned, combi], axis=0)
        end = time.time()
        dura = (end - start)/60
    
        print("############################################")
        print("The Macrostrat binning took", round(dura, 2), "minutes. We find", len(PBDB_names_binned),"binned names.")
        print("############################################")
    
    return PBDB_names_binned  
