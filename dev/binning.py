import requests
import time
import json
import sys
import pandas as pd
sys.path.append('../')

from app.rnames_app.utils.root_binning_ids import main_binning_fun

relations_file = 'relations.csv'
time_scales_file = 'time_scales.csv'
structured_names_file = 'structured_names.csv'

def download_paginated(url):
    start = time.time()
    response = requests.get(url)
    response_json = response.json()
    flat_json = pd.json_normalize(response_json['results'], sep='_')
    df = pd.DataFrame(flat_json)

    while True:
        url = response_json['next']
        if url == None:
            # There is no next page to download
            break

        print(url)
        response = requests.get(url)
        response_json = response.json()
        flat_json = pd.json_normalize(response_json['results'], sep='_')
        df = pd.concat([df, pd.DataFrame(flat_json)])

    ende = time.time()
    print("download took: ", (ende - start)/60, "mins")
    return df

def download_relations(base_url):
    print ('Downloading relations...')
    start = time.time()
    url = base_url + "relations/?format=json&inline=true&page_size=1000"
    return download_paginated(url)

def download_structured_names(base_url):
    print ('Downloading structured names...')
    url = base_url + "structured-names/?inline=true&format=json&page_size=1000"
    return download_paginated(url)

def download_time_scales(base_url):
    print ('Downloading time scales...')
    start = time.time()
    url = base_url + "time-scale-names/?inline=true&format=json&page_size=1000"
    return download_paginated(url)

def confirm_redownload(file_name):
    try:
        with open(file_name, "r") as f:
            while True:
                response = input('Redownload ' + file_name + '? (y/n): ')
                if response == 'y':
                    return True
                elif response == 'n':
                    return False
    except IOError:
        pass

    return True

def download_data(config):
    url = config.get('url')

    if confirm_redownload(relations_file):
        relations = download_relations(url)
        relations.to_csv(relations_file)

    if confirm_redownload(structured_names_file):
        snames = download_structured_names(url)
        snames.to_csv(structured_names_file)

    if confirm_redownload(time_scales_file):
        scales = download_time_scales(url)
        scales.to_csv(time_scales_file)

def save_config(config):
    with open("config.json", "w") as f:
        json.dump(config, f)

def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except IOError:
        with open("config.json", "x") as f:
            json.dump({}, f)
            return dict()

def select_time_scale(config):
    df = pd.read_csv(time_scales_file)
    df = df[['ts_name_id', 'ts_name_ts_name']]
    df = df.drop_duplicates()

    print('Available time scales:')
    for index, row in df.iterrows():
        print('\t[' + str(row['ts_name_id']) + '] ' + str(row['ts_name_ts_name']))

    try:
        return int(input('Enter a time scale ID: '))
    except:
        return -1

def run_binning(config):
    ts_id = select_time_scale(config)
    time_scale = pd.read_csv(time_scales_file)
    time_scale = time_scale[time_scale['ts_name_id'] == ts_id]
    time_scale = time_scale.sort_values(by='sequence', ascending=True)

    if time_scale.shape[0] == 0:
        print('Invalid time scale ID')
        return True

    sequence = time_scale.copy()

    time_scale = time_scale[['ts_name_id', 'ts_name_ts_name']]
    time_scale.rename(inplace=True, columns={'ts_name_ts_name': 'ts_name', 'ts_name_id': 'id'})

    relations = pd.read_csv(relations_file)
    structured_names = pd.read_csv(structured_names_file)

    time_scale_name = time_scale['ts_name']
    main_binning_fun(time_scale_name, time_scale, sequence, relations, structured_names)
    return False

def change_config(config):
    url = input('Enter API url: ')
    if url != '':
        config['url'] = url

def show_menu(config):
    # pd.set_option('display.max_rows', 999)
    pd.set_option('display.max_columns', 999)

    print('Please select an action by inputting a number')
    print('\t[1] Run binning')
    print('\t[2] Change API url')
    print('\t[3] Download data')
    print('\t[4] Exit')

    try:
        opt = int(input())
    except:
        print('Please enter a number')
        return True

    if opt == 1:
        return run_binning(config)
    elif opt == 2:
        change_config(config)
    elif opt == 3:
        download_data(config)
    elif opt == 4:
        return False

    return True

def main():
    config = load_config()
    if config.get('url') == None:
        config['url'] = input('Enter API url: ')

    while show_menu(config):
        pass

    save_config(config)

main()
