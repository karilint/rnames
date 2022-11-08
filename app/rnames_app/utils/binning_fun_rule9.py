#!/usr/bin/env python
# coding: utf-8

import time
import pandas as pd
import numpy as np

def bin_fun_rule9 (c_rels, already_binned, binning_scheme, binning_algorithm, ts_names, t_scales, not_spec):
  
    not_spec = not_spec
        
    print("Binning via rule 9 runs.")
    print("This takes a few minutes....")
    start = time.time()
  
    # Prepare binning scheme
    
    t_scheme = binning_scheme
    x_names = ts_names[ts_names['ts_name']==t_scheme]
    used_ts = t_scales[t_scales['ts_name_id']==x_names['id'].values[0]]
    # rename columns in order to make compatible with following code
    used_ts = used_ts[['structured_name_id', 'sequence']]
    used_ts.rename(columns={'structured_name_id':'ts', 'sequence': 'ts_index'},inplace = True)
    
    # Prepare c_rels
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
    
    # exclude not specified relations (check for improvement, needs evtl placed somewhere else)
    not_spec_x = c_rels[c_rels['name_1'].isin(not_spec['id'])]
    not_spec_ref = not_spec_x[['reference_id']]
    not_spec_sn = not_spec_x[['name_2']]
    c_rels = c_rels[~(c_rels['reference_id'].isin(not_spec_ref['reference_id']) & 
                     c_rels['name_2'].isin(not_spec_sn['name_2']))]

    ##############################################################
    ##############################################################
    # the first tier has three binning rules and is based on direct relations

    c_rels_combined = pd.merge(already_binned, c_rels, how= 'inner', left_on="name", right_on="name_2")

    ##############################################################
    ##############################################################
    
    bnu = c_rels_combined["name"]
    bnu = bnu.drop_duplicates()
    bnurange = np.arange(0,len(bnu),1)
    r9_names_binned = pd.DataFrame([] * 6, columns=['name', 'oldest','youngest', 'ts_count', 'refs', 'rule'])
    for i in bnurange:
        x_name = bnu.iloc[i]
        xrels = c_rels_combined[c_rels_combined['name']==x_name]
        if xrels.shape[0]>0:
            xrels = xrels[xrels['ts_count']== min(xrels['ts_count'])] # filter for shortest range
            bins_o = xrels['oldest'].drop_duplicates()
            bins_y = xrels['youngest'].drop_duplicates()
            mbins_o = pd.merge(bins_o, used_ts, how = 'inner', left_on = "oldest", right_on="ts")
            mbins_y = pd.merge(bins_y, used_ts, how = 'inner', left_on = "youngest", right_on="ts")
            if ((mbins_o.shape[0]>0)& (mbins_y.shape[0]>0)):
                new_oldest = mbins_o[mbins_o['ts_index'] == min(mbins_o['ts_index'])]
                new_youngest = mbins_y[mbins_y['ts_index'] == max(mbins_y['ts_index'])]
                refs = xrels['reference_id'].drop_duplicates()
                if (refs.shape[0]==1):
                    refs = xrels['reference_id'].iloc[0]           
                elif (refs.shape[0]>1):
                    refs = pd.DataFrame(refs)
                    refs = ','.join(map(str, refs["reference_id"]))                     
                combi = pd.DataFrame([{'name': x_name,
                                       'oldest': new_oldest['ts'].iloc[0], 'youngest': new_youngest['ts'].iloc[0],
                                       'ts_count': new_youngest['ts_index'].iloc[0]-new_oldest['ts_index'].iloc[0],
                                       'refs':refs, 'rule': 9.0}])
                r9_names_binned = pd.concat([r9_names_binned, combi], axis=0)

    end = time.time()
    #info.update()
    dura = (end - start)/60
    print('###########################################')
    print("We find", len(r9_names_binned),
          "binned names via rule 9.0. It took ", round(dura, 2),  "minutes.")
    print('###########################################')
    return r9_names_binned

