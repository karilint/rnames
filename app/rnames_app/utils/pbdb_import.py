#!/usr/bin/env python
# coding: utf-8

from urllib.request import urlopen
import json, re
import numpy as np
import pandas as pd
import time
import csv

def download_data():
    # access data from PBDB
    start = time.time()
    # strata
    url = 'https://paleobiodb.org/data1.2/occs/strata.json?interval=Phanerozoic&textresult'
    r = urlopen(url)
    result= r.read().decode('utf-8')
    data_strata = json.loads(result)
    # intervals (chronostratigraphic)
    url = 'https://paleobiodb.org/data1.2/intervals/list.json?all_records'
    r = urlopen(url)
    # This should put the response from API in a Dict
    result= r.read().decode('utf-8')
    data_intvl = json.loads(result)
    ende = time.time()
    print("download took:",(ende - start)/60, "mins")
    return {'strata': data_strata, 'intervals': data_intvl}

def download_references(data_intvl):
    # create a list of reference ids for PBDB URL
    start = time.time()
    def get_vals(nested, key):
        result = []
        if isinstance(nested, list) and nested != []:   #non-empty list
            for lis in nested:
                result.extend(get_vals(lis, key))
        elif isinstance(nested, dict) and nested != {}:   #non-empty dict
            for val in nested.values():
                if isinstance(val, (list, dict)):   #(list or dict) in dict
                    result.extend(get_vals(val, key))
            if key in nested.keys():   #key found in dict
                result.append(nested[key])
        return result

    refids=get_vals(data_intvl, 'rid') # list in form 
    refids = sum(refids, [])# list in form "ref:12345"
    new_refids=[]
    #print(refids)
    for string in refids:
        new_string = string.replace("ref:", "")
        new_refids.append(new_string)
    new_refids = [int(i) for i in new_refids] # list of reference id's as integers
    #print(new_refids)

    # add reference ids to URL string
    url_raw="https://paleobiodb.org/data1.2/refs/list.json?ref_id="
    refids_string = ' '.join([str(elem) for elem in new_refids])
    refids_string = refids_string.replace(" ", ",")
    url1=url_raw+refids_string
    #print(url)

    # access PBDB references
    r = urlopen(url1)
    # This should put the response from API in a Dict
    result= r.read().decode('utf-8')
    data_PB_refs = json.loads(result)

    # prepare PBDB references for RNames
    # transfer to pandas dataframes
    res_refs_PB = pd.DataFrame(data_PB_refs['records'])
    res_refs_PB['first_author']=res_refs_PB['al1'].astype(str)+', '+res_refs_PB['ai1']
    res_refs_PB = res_refs_PB[['oid', 'first_author', 'pby', 'tit', 'doi']]
    res_refs_PB.rename(columns={"oid": "id", "pby": "year", "tit": "title"}, inplace=True)
    ende = time.time()
    print("download took:",(ende - start)/60, "mins")
    return res_refs_PB

def pbdb_import(cc2):
    downloaded_data = download_data()
    data_strata = downloaded_data['strata']
    data_intvl = downloaded_data['intervals']

    res_refs_PB = download_references(data_intvl)
    # print(res_refs_PB)

    #########################################
    # prepare PBDB download as structured names
    # transfer to pandas dataframes
    res_strat_PB = pd.DataFrame(data_strata['records'])
    res_intvl_PB = pd.DataFrame(data_intvl['records'])

    #translate country codes of PBDB into Location code of RNames
    # cc2 = pd.read_csv('country_codes_s.csv')
    #cc2['ISO3166-1-Alpha-2'].loc[(cc2['ISO3166-1-Alpha-2'] == NA)] = 'NAx'
    cc2['ISO3166-1-Alpha-2'] = cc2['ISO3166-1-Alpha-2'].fillna('NAx') # Nambibia problem
    res_strat_PB["cc2"] = res_strat_PB["cc2"].fillna('NAx') # Nambibia problem
    res_strat_PB["cc2"] = res_strat_PB["cc2"].replace("NA", "NAx")
    res_strat_PB.reset_index(inplace=True)
    xcc = res_strat_PB[['index','cc2']]
    xcc['cc2'] = xcc.cc2.str.split(',')
    xccx =xcc.explode(['cc2'])
    # print(cc2.iloc[90])

    # replace country codes
    c_country = pd.DataFrame(columns = ['index', 'Location'])
    for i in xcc['index']:
        x_xccx = xccx[xccx['index']==i]
        if x_xccx.shape[0]==None:
            c_country.loc[len(c_country)] = [i, 'NaN']
        if x_xccx.shape[0]==1:
            x_cc2 = cc2[cc2["ISO3166-1-Alpha-2"].isin(x_xccx['cc2'])]
            if x_cc2.shape[0]>0:
                c_country.loc[len(c_country)] = [i, x_cc2['official_name_en'].iloc[0]]
                if x_cc2.shape[0]==None:
                    c_country.loc[len(c_country)] = [i, 'NaN']
        if x_xccx.shape[0]>1:
            m_cc2 = pd.merge(x_xccx, cc2, left_on="cc2", right_on="ISO3166-1-Alpha-2")
            m_cc2 = m_cc2[['index', 'Region Name']]
            m_cc2 = m_cc2.drop_duplicates()
            if m_cc2.shape[0]==1:
                c_country.loc[len(c_country)] = [i, m_cc2['Region Name'].iloc[0]]
            if m_cc2.shape[0]>1:
                c_country.loc[len(c_country)] = [i, 'Global']
           
    #print(c_country)

    #testdf = res_strat_PB[~res_strat_PB["index"].isin(c_country['index'])]
    #print(testdf) 

    res_strat_PB = pd.merge(res_strat_PB, c_country, left_on="index", right_on="index")
    res_strat_PB = res_strat_PB[['sgr', 'sfm', 'smb', 'eag', "lag",'Location']]
    res_intvl_PB = res_intvl_PB[['lvl','nam', 'eag', 'lag', 'rid']]

    # time relations to strata
    strat_gr = res_strat_PB[['sgr', 'eag','Location']]
    strat_gr['Qualifier_one'] = "Group"
    strat_gr1 = res_strat_PB[['sgr', "lag"]]
    strat_gr1['Qualifier_one'] = "Group"
    strat_gr1.rename(columns={'lag': 'eag'},inplace = True)
    strat_gr = pd.concat([strat_gr, strat_gr1], axis=0)

    strat_fm = res_strat_PB[['sfm', 'eag','Location']]
    strat_fm['Qualifier_one'] = "Formation"
    strat_fm1 = res_strat_PB[['sfm', "lag"]]
    strat_fm1['Qualifier_one'] = "Formation"
    strat_fm1.rename(columns={'lag': 'eag'},inplace = True)
    strat_fm = pd.concat([strat_fm, strat_fm1], axis=0)

    strat_mbr = res_strat_PB[['smb', 'eag']]
    strat_mbr['Qualifier_one'] = "Member" 
    strat_mbr1 = res_strat_PB[['smb', "lag"]]
    strat_mbr1['Qualifier_one'] = "Member"
    strat_mbr1.rename(columns={'lag': 'eag'},inplace = True)
    strat_mbr = pd.concat([strat_mbr, strat_mbr1], axis=0)

    strat_gr.rename(columns={"sgr": "Name_one"},inplace = True)
    strat_fm.rename(columns={"sfm": "Name_one"},inplace = True)
    strat_mbr.rename(columns={"smb": "Name_one"},inplace = True)
    res_strat_PB1 = pd.concat([strat_gr, strat_fm, strat_mbr], axis=0)
    #print(res_strat_PB1)

    res_strat_PB1.rename(columns={'eag': 'Name_two', 'Location':'Location_one'},inplace = True)
    res_strat_PB1 = res_strat_PB1.dropna()
    res_strat_PB1["Name_one"] = res_strat_PB1["Name_one"].str.strip('"')
    res_strat_PB1['Qualifier_two'] = "absolute Time"
    res_strat_PB1['Location_two'] = "Global" 
    res_strat_PB1['Reference'] = 'PBDB'
    res_strat_PB1['Relation'] = "relates to"

    #print(res_strat_PB1)

    # 'belongs to' relations of strata
    gr_strat_PB = res_strat_PB[['sgr', 'sfm', 'Location']]
    gr_strat_PB.rename(columns={"sgr": "Name_one", "sfm":"Name_two"},inplace = True)
    gr_strat_PB['Qualifier_one']= 'Group'
    gr_strat_PB['Qualifier_two']= 'Formation'

    fm_strat_PB = res_strat_PB[['sfm', 'smb', 'Location']]
    fm_strat_PB['Qualifier_one']= 'Formation'
    fm_strat_PB['Qualifier_two']= 'Member'
    fm_strat_PB.rename(columns={"sfm": "Name_one", "smb":"Name_two"},inplace = True)
    res_strat_PB2 = pd.concat([gr_strat_PB, fm_strat_PB], axis=0)
    res_strat_PB2 = res_strat_PB2.dropna()
    res_strat_PB2.rename(columns={"Location": "Location_one"},inplace = True)
    res_strat_PB2['Location_two'] = res_strat_PB2['Location_one']
    res_strat_PB2['Reference'] = 'PBDB'
    res_strat_PB2['Relation'] = "belongs to"
    res_strat_PB2 = res_strat_PB2[['Name_one', 'Qualifier_one','Location_one' ,'Name_two', 'Qualifier_two', 
                                   'Location_two','Reference', 'Relation']]
    #print(res_strat_PB2)
    #print(res_intvl_PB)

    # time relations to intervals
    intvl_eon = res_intvl_PB[res_intvl_PB['lvl']==1.0]
    intvl_era = res_intvl_PB[res_intvl_PB['lvl']==2.0]
    intvl_period = res_intvl_PB[res_intvl_PB['lvl']==3.0]
    intvl_epoch = res_intvl_PB[res_intvl_PB['lvl']==4.0]
    intvl_age = res_intvl_PB[res_intvl_PB['lvl']==5.0]
    intvl_age_r = res_intvl_PB[res_intvl_PB['lvl'].isnull()]

    intvl_eon['lvl'] = "Eon" 
    intvl_era['lvl'] = "Era"
    intvl_period['lvl'] = "Period"
    intvl_epoch['lvl'] = "Epoch"
    intvl_age['lvl'] = "Stage"
    intvl_age_r['lvl'] = "Regio_Stage" 

    res_intvl_PB = pd.concat([intvl_eon, intvl_era, intvl_period,
                             intvl_epoch, intvl_age, intvl_age_r], axis=0)
    res_intvl_PB = res_intvl_PB.dropna()
    res_intvl_PB.rename(columns={"nam": "Name_one", "lvl":"Qualifier_one", "rid":"Reference"},inplace = True)

    res_intvl_PB1 = res_intvl_PB[['Name_one', 'Qualifier_one', 'eag', 'Reference']]
    res_intvl_PB1.rename(columns={'eag':'Name_two'},inplace = True)
    res_intvl_PB2 = res_intvl_PB[['Name_one', 'Qualifier_one', 'lag', 'Reference']]
    res_intvl_PB2.rename(columns={'lag':'Name_two'},inplace = True)
    res_intvl_PB = pd.concat([res_intvl_PB1, res_intvl_PB2])
    res_intvl_PB['Qualifier_two'] = 'absolute time'
    res_intvl_PB['Relation'] = 'relates to'
    res_intvl_PB['Location_one'] = 'Global'
    res_intvl_PB['Location_two'] = 'Global'

    res_intvl_PB = res_intvl_PB[['Name_one', 'Qualifier_one', 'Location_one','Name_two', 'Qualifier_two', 
                                'Location_two','Reference', 'Relation']]
    relations_PBDB = pd.concat([res_intvl_PB, res_strat_PB1, res_strat_PB2])

    #######################################################
    # relations_PBDB_final should be upladed to relations in RNames
    relations_PBDB_final = res_intvl_PB[['Name_one', 'Qualifier_one', 'Location_one', 'Name_two', 'Qualifier_two',
                                'Location_two', 'Reference', 'Relation']]
    print(relations_PBDB_final)
    #######################################################

    # preparation of input to structured names
    struct_name_a = relations_PBDB[['Name_one', 'Qualifier_one','Location_one']]
    struct_name_b = relations_PBDB[['Name_two', 'Qualifier_two','Location_two']]
    struct_name_a.rename(columns={'Name_one':'name', 'Qualifier_one':'qualifier_name', 
                                 'Location_one': 'location'},inplace = True)
    struct_name_b.rename(columns={'Name_two':'name', 'Qualifier_two':'qualifier_name',
                                 'Location_two':'location'},inplace = True)
    struct_names_PBDB = pd.concat([struct_name_a, struct_name_b])
    struct_names_PBDB = struct_names_PBDB.drop_duplicates()

    #######################################################
    # struct_names_PBDB should be upladed to structured names in RNames
    print(struct_names_PBDB)
    #######################################################

    return {'references': res_refs_PB, 'relations': relations_PBDB_final, 'structured_names': struct_names_PBDB}
