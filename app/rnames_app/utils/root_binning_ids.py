#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import requests
import time
import binning_fun_id # to be changedx
import binning_fun_PBDB # to be changedx


###################
###################
# first we download and create all objects needed for binning

###################
#download relations from RNames API
# this takes c. 0.5h
# any possibility to speed this up?
start = time.time()
url = "https://rnames-staging.it.helsinki.fi/api/relations/?format=json&inline=true&page_size=10000"
print(url)
response = requests.get(url)
response_json = response.json()
flat_json = pd.json_normalize(response_json['results'], sep='_')
res_rels_RN_raw = pd.DataFrame(flat_json)

while True:
	url = response_json['next']
	if url == None:
		# There is no next page to download
		break

	#print(url)
	response = requests.get(url)
	response_json = response.json()
	flat_json = pd.json_normalize(response_json['results'], sep='_')
	res_rels_RN_raw = pd.concat([res_rels_RN_raw, pd.DataFrame(flat_json)])
    
#print(res_rels_RN)
ende = time.time()

print("download took:",(ende - start)/60, "mins")



res_rels_RN = res_rels_RN_raw[['id', 'name_one_id', 'name_two_id','name_one_qualifier_stratigraphic_qualifier_name', 
                           'name_two_qualifier_stratigraphic_qualifier_name', 'reference_id','reference_year',
                               'reference_title']]
print(res_rels_RN_raw.keys())



###################
#download structured names from RNames API
# this takes c. 1 min
# any possibility to speed this up?

start = time.time()
url = "https://rnames-staging.it.helsinki.fi/api/structured-names/?inline=true&format=json&page_size=10000"
print(url)
response = requests.get(url)
response_json = response.json()
flat_json = pd.json_normalize(response_json['results'], sep='_')
res_sn_raw = pd.DataFrame(flat_json)

while True:
	url = response_json['next']
	if url == None:
		# There is no next page to download
		break

	#print(url)
	response = requests.get(url)
	response_json = response.json()
	flat_json = pd.json_normalize(response_json['results'], sep='_')
	res_sn_raw = pd.concat([res_sn_raw, pd.DataFrame(flat_json)])
    
#print(res_rels_RN)
ende = time.time()

print("download took:",(ende - start)/60, "mins")

res_sn = res_sn_raw[['id', 'name_name', 'qualifier_qualifier_name_name','location_name', 
                           'reference_first_author', 'reference_year','reference_id']]
#print(res_sn_raw.keys())

###################
# object with all structured names with name 'not specified'
# this is also needed for binning

not_spec = res_sn[res_sn['name_name']== 'not specified']
not_spec = not_spec[['id']]
#print(not_spec)


###################
## read time scales
# this should be via API as soon as functional
# see my email

ts_names = pd.read_csv ('ts_names.csv')
t_scales = pd.read_csv ('time_scales.csv')

###################
# define time scale scheme
# this should be via input form on frontend
# examples: 'Ordovician time bins (Webby et al., 2004)'
# 'Periods (ICS, 2020)'
binning_scheme = 'Ordovician time slices (Bergström et al., 2009)' # this is input


###################
# define binning algorithm
# this should be via input form on frontend
# example: 'combined'
binning_algorithm = 'combined' # this is input

###################
###################
## binning of structured names imported from PBDB
PBDB_names_binned= binning_fun_PBDB.bin_fun_PBDB(c_rels = res_rels_RN_raw, c_strat= res_sn_raw,
                           binning_scheme = binning_scheme, ts_names = ts_names, 
                           t_scales = t_scales, not_spec = not_spec)

###################
###################
## binning of all other strucured names
resi_binned_raw = binning_fun_id.bin_fun(c_rels = res_rels_RN, binning_algorithm = binning_algorithm, 
                           binning_scheme = binning_scheme, ts_names = ts_names, 
                           t_scales = t_scales, not_spec = not_spec)
#print(resi_binned_raw)


###################
###################
## preparation of output
# there will be two output tables
# resi_binned: gives binning of each individual structured name with relations
# binned_generalised: gives binning of identical names

#make results readable
binned_raw = pd.concat([resi_binned_raw, PBDB_names_binned], axis=0)
binned_raw = binned_raw. drop_duplicates()
binned_raw = pd.merge(binned_raw, res_sn, left_on="name", right_on="id")
binned_raw.rename(columns={'name':'name_id', 'name_name': 'name', 
                            'qualifier_qualifier_name_name': 'qualifier_name'},inplace = True)
binned_raw = binned_raw[['name_id', 'name', 'qualifier_name','oldest', 
                           'youngest', 'refs']]
binned_raw = pd.merge(binned_raw, res_sn, left_on="oldest", right_on="id")
binned_raw.rename(columns={'oldest':'oldest_id', 'name_name': 'oldest_name'},inplace = True)
binned_raw = binned_raw[['name_id', 'name', 'qualifier_name','oldest_id', 'oldest_name',
                           'youngest', 'refs']]
binned_raw = pd.merge(binned_raw, res_sn, left_on="youngest", right_on="id")
binned_raw.rename(columns={'youngest':'youngest_id', 'name_name': 'youngest_name'},inplace = True)
binned_raw = binned_raw[['name_id', 'name', 'qualifier_name','oldest_id', 'oldest_name',
                           'youngest_id', 'youngest_name', 'refs']]

#print(resi_binned)

# produce generalised binning
# unique names
uni_binned = binned_raw[['name', 'qualifier_name']]
uni_binned = uni_binned.drop_duplicates()

# get time bins
x_names = ts_names[ts_names['ts_name']==binning_scheme]
time_slices = t_scales[t_scales['ts_name_id']==x_names['id'].values[0]]
time_slices = time_slices[['structured_name_id', 'sequence']]
time_slices.rename(columns={'structured_name_id':'ts', 'sequence': 'ts_index'},inplace = True)


##loop through uni_binned and collect for each name the youngest and oldest time bin
bnu = uni_binned.index
bnurange = np.arange(0,len(bnu),1)
binned_generalised_ids = pd.DataFrame([] * 3, columns=["name", "oldest_id", "youngest_id"])
for i in bnurange:
    uni_binned_x = uni_binned.iloc[i]
    resi_binned_sub = binned_raw.loc[(binned_raw["name"]==uni_binned_x['name'])
                                   & (binned_raw["qualifier_name"]==uni_binned_x['qualifier_name'])]
    resi_binned_sub_oldest = resi_binned_sub['oldest_id']
    resi_binned_sub_youngest = resi_binned_sub['youngest_id']
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
binned_generalised = binned_generalised[['name', 'oldest', 'youngest']]
#print(binned_generalised) 
