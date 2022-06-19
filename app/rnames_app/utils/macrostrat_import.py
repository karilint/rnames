#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 15 21:07:53 2022

@author: bjoernkroeger
"""
from urllib.request import urlopen
#import json, re
import numpy as np
import pandas as pd
import time
import requests
from math import ceil

#import csv evtls needed for saving downloads locally

###################
# download from Macrostrat
###################
def stratseparator (res_sections_MS ,stratlevel, stratstring):   
    sec_mbr = res_sections_MS[res_sections_MS['strat_name'].str.endswith(stratstring)]
    sec_mbr['strat_name'] = sec_mbr['strat_name'].str.replace(stratstring, '')
    sec_mbr['Qualifier_one'] = stratlevel
    sec_mbr['Qualifier_two'] = "mya"
    sec_mbr1 = sec_mbr[['strat_name', 'Qualifier_one','t_age', 'Qualifier_two']]
    sec_mbr2 = sec_mbr[['strat_name', 'Qualifier_one','b_age', 'Qualifier_two']]
    sec_mbr1.rename(columns={"strat_name" : "Name_one", "t_age" :"Name_two"},inplace = True)
    sec_mbr2.rename(columns={"strat_name" : "Name_one", "b_age" :"Name_two"},inplace = True)
    sec_mbra = pd.concat([sec_mbr1, sec_mbr2], axis=0)
    # part two intervals
    sec_mbr4 = pd.merge(sec_mbr, res_intvl_MS, left_on="t_interval", right_on="interval_id")
    sec_mbr5 = pd.merge(sec_mbr, res_intvl_MS, left_on="b_interval", right_on="interval_id")
    sec_mbr4.rename(columns={"strat_name" : "Name_one", "interval_name" :"Name_two","t_interval" :"int_id" },inplace = True)
    sec_mbr5.rename(columns={"strat_name" : "Name_one", "interval_name" :"Name_two","b_interval" :"int_id" },inplace = True)
    sec_mbri = pd.concat([sec_mbr4, sec_mbr5], axis=0)
    # Macrostrat download is agnostic about qualifiers of interval names
    # we merge Macrostrat intervals with indentical names of RNames strat:
    sec_mbria = pd.merge(sec_mbri, res_sn_RNx, left_on="Name_two", right_on="name_name")
    sec_mbria = sec_mbria[['Name_one', 'Qualifier_one', 'name_name', 'qualifier_qualifier_name_name']]
    sec_mbria.rename(columns={"name_name": "Name_two", "qualifier_qualifier_name_name": "Qualifier_two"},inplace = True)
    # all others:
    sec_mbrib = sec_mbri[~sec_mbri["Name_two"].isin(sec_mbria['Name_two'])]
    sec_mbrib = sec_mbrib[['Name_one', 'Qualifier_one', 'Name_two']]
    sec_mbrib['Qualifier_two'] = 'indet Regio_Standard'
    sec_mbr =pd.concat([sec_mbra, sec_mbria, sec_mbrib], axis=0)
    sec_mbr = sec_mbr.drop_duplicates()
    return sec_mbr

def download_sections():
    url = 'https://macrostrat.org/api/sections?all'
    response = requests.get(url)
    return response.json()['success']['data']

def download_intervals():
    sections = download_sections()
    results = []
    n = len(sections)
    d = 1000

    for i in range(0, ceil(n/d)):
        url = 'https://macrostrat.org/api/age_model?section_id={0}'.format(sections[i * d]['section_id'])
        for j in range(i * d + 1, min((i + 1) * d, n)):
            url = url + ',' + str(sections[j]['section_id'])
        response = requests.get(url).json()
        results = results + response['success']['data']

    return pd.DataFrame(results)

def download_map_legends():
    url = 'https://macrostrat.org/api/v2/geologic_units/map/legend?source_id=1'

    for i in range(2, 501): # TODO: valid range should be detected using the api
        url = url + ',' + str(i)

    response = requests.get(url)
    response_json = response.json()
    return pd.json_normalize(response_json['success'], record_path=['data'])


def macrostrat_import(res_sn_raw):
    ###################
    # res_sn_raw contains structured names with inlined relations in RNames
    # needed to match Macrostrat names with RN structured names

    #print(res_sn_raw.keys())
    res_sn_RN = res_sn_raw[['id', 'name_name', 'qualifier_qualifier_name_name','location_name',
                               'reference_first_author', 'reference_year','reference_id']]
    res_sn_RNx = res_sn_RN.drop_duplicates(subset='name_name', keep="first")


    ###################
    # load stratigraphic units
    url = 'https://macrostrat.org/api/units?all&format=json'
    print(url)
    response = requests.get(url)
    response_json = response.json()
    flat_json = pd.json_normalize(response_json['success'], record_path=['data'])
    res_units_MS_raw = pd.DataFrame(flat_json)

    ###################
    # loop through MS sections to get intervals
    # takes a very long time (< 2h)

    res_intvl_MS_raw = download_intervals()
    res_intvl_MS = res_intvl_MS_raw[['interval_id', 'interval_name', 'age_bottom', 'age_top']]
    res_intvl_MS = res_intvl_MS.drop_duplicates()

    ###################
    ###################
    # loop through maps

    res_sections_MS_raw = download_map_legends()
    res_sections_MS = res_sections_MS_raw[res_sections_MS_raw['strat_name'].notnull()]
    res_sections_MS = res_sections_MS[['strat_name', 't_age', 'b_age', 't_interval', 'b_interval']]
    res_sections_MS = res_sections_MS[~res_sections_MS['strat_name'].str.contains(";")]
    res_sections_MS = res_sections_MS.drop_duplicates()

    ###################
    ###################
    ##### prepare stratigraphic units from intervals

    intvx = res_intvl_MS[['interval_name', 'age_bottom', 'age_top']]
    intvx['Qualifier_two'] = "mya"
    intv_rn = pd.merge(intvx, res_sn_RNx, left_on="interval_name", right_on="name_name")
    intv_rn['strat_name'] = intv_rn['qualifier_qualifier_name_name'].str.replace('Group', 'Regio_Stage')
    # !!!use this in stratseparator because this is cleaner / check Ludlow problem
    intv_rn1 = intv_rn[['interval_name', 'age_bottom', 'qualifier_qualifier_name_name', 'Qualifier_two',]]
    intv_rn1.rename(columns={"age_bottom" : "Name_two", "qualifier_qualifier_name_name": "Qualifier_one"},inplace = True)
    intv_rn2 = intv_rn[['interval_name', 'age_top', 'qualifier_qualifier_name_name', 'Qualifier_two',]]
    intv_rn2.rename(columns={"age_top" : "Name_two", "qualifier_qualifier_name_name": "Qualifier_one"},inplace = True)

    intvls =pd.concat([intv_rn1, intv_rn1], axis=0)
    intvls.rename(columns={"interval_name" : "Name_one"},inplace = True)
    intvls['Qualifier_one'] = intvls['Qualifier_one'].str.replace('Group', 'Regio_Stage')
    intvls['Belongs_to'] = 0

    ###################
    ###################
    ##### prepare stratigraphic units from sections



    sec_mbr = stratseparator (res_sections_MS = res_sections_MS, stratstring =" Member", stratlevel = "Member")
    sec_fm = stratseparator (res_sections_MS = res_sections_MS, stratstring =" Formation", stratlevel = "Formation")
    sec_gp = stratseparator (res_sections_MS = res_sections_MS, stratstring =" Group", stratlevel = "Group")
    sec_sgp = stratseparator (res_sections_MS = res_sections_MS, stratstring =" Supergroup", stratlevel = "Supergroup")
    sec_beds = stratseparator (res_sections_MS = res_sections_MS, stratstring =" Beds", stratlevel = "Informal Lithostratigraphy")
    sec_bed = stratseparator (res_sections_MS = res_sections_MS, stratstring =" Bed", stratlevel = "Bed")

    sec_rest = res_sections_MS[(~res_sections_MS['strat_name'].str.endswith(" Member")) &
                                    (~res_sections_MS['strat_name'].str.endswith(" Formation")) &
                                    (~res_sections_MS['strat_name'].str.endswith(" Group")) &
                                    (~res_sections_MS['strat_name'].str.endswith(" Supergroup")) &
                                    (~res_sections_MS['strat_name'].str.endswith(" Beds")) &
                                    (~res_sections_MS['strat_name'].str.endswith(" Bed"))
                                    ]
    sec_rest['Qualifier_one'] = "Informal Lithostratigraphy"
    sec_rest['Qualifier_two'] = "mya"
    sec_rest1 = sec_rest[['strat_name', 'Qualifier_one','t_age', 'Qualifier_two']]
    sec_rest2 = sec_rest[['strat_name', 'Qualifier_one','b_age', 'Qualifier_two']]
    sec_rest1.rename(columns={"strat_name" : "Name_one", "t_age" :"Name_two"},inplace = True)
    sec_rest2.rename(columns={"strat_name" : "Name_one", "b_age" :"Name_two"},inplace = True)
    sec_resta = pd.concat([sec_rest1, sec_rest2], axis=0)

    sec_rest4 = pd.merge(sec_rest, res_intvl_MS, left_on="t_interval", right_on="interval_id")
    sec_rest5 = pd.merge(sec_rest, res_intvl_MS, left_on="b_interval", right_on="interval_id")
    sec_rest4.rename(columns={"strat_name" : "Name_one", "interval_name" :"Name_two","t_interval" :"int_id" },inplace = True)
    sec_rest5.rename(columns={"strat_name" : "Name_one", "interval_name" :"Name_two","b_interval" :"int_id" },inplace = True)
    sec_resti = pd.concat([sec_rest4, sec_rest5], axis=0)
    # Macrostrat download is agnostic about qualifiers of interval names
    # we merge Macrostrat intervals with indentical names of RNames strat:
    sec_restia = pd.merge(sec_resti, res_sn_RNx, left_on="Name_two", right_on="name_name")
    sec_restia = sec_restia[['Name_one', 'Qualifier_one', 'Name_two', 'qualifier_qualifier_name_name']]
    sec_restia.rename(columns={"qualifier_qualifier_name_name": "Qualifier_two"},inplace = True)
    # all others:
    sec_restib = sec_resti[~sec_resti["Name_two"].isin(sec_restia['Name_two'])]
    sec_restib = sec_restib[['Name_one', 'Qualifier_one', 'Name_two']]
    sec_restib['Qualifier_two'] = 'indet Regio_Standard'
    sec_rest =pd.concat([sec_resta, sec_restia, sec_restib], axis=0)
    sec_rest = sec_rest.drop_duplicates()

    ### relations from sections
    secs = pd.concat([sec_rest, sec_mbr, sec_gp, sec_sgp, sec_beds, sec_bed], axis=0)
    secs['Belongs_to'] = 0
    secs = secs.drop_duplicates()
    ##############################

    ###################
    ###################
    #prepare MS stratigraphic units from units

    res_units_MS = res_units_MS_raw[res_units_MS_raw['strat_name_id'].notnull()]
    res_units_MS = res_units_MS[['unit_id', 'unit_name', 'strat_name_id', 'Mbr', 'Fm', 'Gp', 'SGp', 't_age', 'b_age']]
    res_units_MS['Mbr'] = res_units_MS['Mbr'].replace(r'^\s*$', np.NaN, regex=True)
    res_units_MS['Fm'] = res_units_MS['Fm'].replace(r'^\s*$', np.NaN, regex=True)
    res_units_MS['Gp'] = res_units_MS['Gp'].replace(r'^\s*$', np.NaN, regex=True)
    res_units_MS['SGp'] = res_units_MS['SGp'].replace(r'^\s*$', np.NaN, regex=True)

    ums_mbr_fm = res_units_MS[['unit_id', 'unit_name', 'strat_name_id', 'Mbr', 'Fm', 't_age', 'b_age']]
    ums_mbr_fm = ums_mbr_fm.dropna(subset=['Mbr', 'Fm'])
    ums_mbr_fm['Qualifier_one'] = "Member"
    ums_mbr_fm['Qualifier_two'] = "Formation"
    ums_mbr_fm['Belongs_to'] = 1
    ums_mbr_fm.rename(columns={"Mbr": "Name_one", "Fm":"Name_two"},inplace = True)
    ums_mbr_fm = ums_mbr_fm[["Name_one", "Name_two", "Qualifier_one", "Qualifier_two", "Belongs_to",
                             't_age', 'b_age']]

    ums_fm_gp = res_units_MS[['unit_id', 'unit_name', 'strat_name_id', 'Fm', 'Gp', 't_age', 'b_age']]
    ums_fm_gp = ums_fm_gp.dropna(subset=['Fm', 'Gp'])
    ums_fm_gp['Qualifier_one'] = "Formation"
    ums_fm_gp['Qualifier_two'] = "Group"
    ums_fm_gp['Belongs_to'] = 1
    ums_fm_gp.rename(columns={"Fm": "Name_one", "Gp":"Name_two"},inplace = True)
    ums_fm_gp = ums_fm_gp[["Name_one", "Name_two", "Qualifier_one", "Qualifier_two", "Belongs_to",
                           't_age', 'b_age']]

    ums_gp_sgp = res_units_MS[['unit_id', 'unit_name', 'strat_name_id', 'Gp', 'SGp', 't_age', 'b_age']]
    ums_gp_sgp = ums_gp_sgp.dropna(subset=['Gp', 'SGp'])
    ums_gp_sgp['Qualifier_one'] = "Group"
    ums_gp_sgp['Qualifier_two'] = "Supergroup"
    ums_gp_sgp['Belongs_to'] = 1
    ums_gp_sgp.rename(columns={"Gp": "Name_one", "SGp":"Name_two"},inplace = True)
    ums_gp_sgp = ums_gp_sgp[["Name_one", "Name_two", "Qualifier_one", "Qualifier_two", "Belongs_to",
                             't_age', 'b_age']]

    res_rel_MS1 = pd.concat([ums_mbr_fm, ums_fm_gp, ums_gp_sgp], axis=0)

    res_units_MS2 = res_rel_MS1[['Name_one', 'Qualifier_one', 't_age']]
    res_units_MS2['Qualifier_two'] = "mya"
    res_units_MS2['Belongs_to'] = 0
    res_units_MS2.rename(columns={"t_age": "Name_two"},inplace = True)


    res_units_MS3 = res_rel_MS1[['Name_one', 'Qualifier_one', 'b_age']]
    res_units_MS3['Qualifier_two'] = "mya"
    res_units_MS3['Belongs_to'] = 0
    res_units_MS3.rename(columns={"b_age": "Name_two"},inplace = True)

    res_rel_MS = pd.concat([res_rel_MS1, res_units_MS2, res_units_MS3], axis=0)
    res_rel_MS = res_rel_MS[['Name_one', 'Name_two', 'Qualifier_one', 'Qualifier_two', "Belongs_to"]]

    ### relations from units
    res_rel_MS = res_rel_MS.drop_duplicates()
    ##############################

    ###### add location and additional columns
    relations_MS = pd.concat([res_rel_MS, secs, intvls], axis=0)
    relations_MS = relations_MS.drop_duplicates()
    data = ['Era', 'Eon', 'Epoch', 'Period', 'Stage', 'Sytem', 'Substage']
    dfx = pd.DataFrame(data, columns=['Chrono_global'])
    dfx['Location']= 'Global'
    relations_MS = pd.merge(relations_MS, dfx, left_on='Qualifier_one', right_on= 'Chrono_global', how='outer')
    relations_MS = relations_MS.drop('Chrono_global', axis=1)
    relations_MS['Name_one_remarks'] ='Autogenerated by PBDB importer.'
    relations_MS['Name_two_remarks'] ='Autogenerated by PBDB importer.'
    relations_MS = relations_MS.dropna(subset=['Qualifier_one'])

    ###### MS structural names
    sn_MS = relations_MS[['Name_one',  'Qualifier_one', 'Location']]

    ################################
    #### output#####################
    #### structural names out out
    sn_MS = relations_MS[['Name_one',  'Qualifier_one', 'Location']]
    sn_MS = sn_MS.drop_duplicates()
    #### relations out
    relations_MS = relations_MS.drop('Location', axis=1)
    ################################

    return {'relations': relations_MS, 'structured_names': sn_MS}

