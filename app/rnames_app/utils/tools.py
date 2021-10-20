import pandas as pd
import multiprocessing as mp
import time
import pandas as pd
import numpy as np

def get_cron_relations():
    url = "http://karilint.pythonanywhere.com/rnames/api/relations/?format=json"
    start = time.time()
    cron_relations = pd.read_json(url)
    #cron_relations = pd.read_csv("view_cron_relations.csv") # from file
    end = time.time()
    print("Downloaded ", len(cron_relations), "relations. Download time: ", end - start, "seconds")
    cron_relations.to_csv("cron_relations.csv", index = False, header=True)
    return (cron_relations, end - start)

def get_time_slices():
    csv_folder = 'rnames_app/utils/csv/'

    rassm_ts = pd.read_csv(csv_folder+"binning_rass.csv", header=None)
    cnr = np.arange(0,len(rassm_ts),1)
    rassm_ts = pd.DataFrame(rassm_ts, index=cnr)
    rassm_ts.columns = ["ts"]
    rassm_ts['ts_index'] = rassm_ts.index
    rassm_ts = rassm_ts.append({'ts' : 'not specified' , 'ts_index' : len(rassm_ts)} , ignore_index=True)

    berg_ts = pd.read_csv(csv_folder+"binning_bergst.csv", header=None)
    cnr = np.arange(0,len(berg_ts),1)
    berg_ts = pd.DataFrame(berg_ts, index=cnr)
    berg_ts.columns = ["ts"]
    berg_ts['ts_index'] = berg_ts.index
    berg_ts = berg_ts.append({'ts' : 'not specified' , 'index_1' : len(berg_ts)} , ignore_index=True)


    webby_ts = pd.read_csv(csv_folder+"binning_webby.csv", header=None)
    cnr = np.arange(0,len(webby_ts),1)
    webby_ts = pd.DataFrame(webby_ts, index=cnr)
    webby_ts.columns = ["ts"]
    webby_ts['ts_index'] = webby_ts.index
    webby_ts = webby_ts.append({'ts' : 'not specified' , 'ts_index' : len(webby_ts)} , ignore_index=True)


    stages_ts = pd.read_csv(csv_folder+"binning_stages.csv", header=None)
    cnr = np.arange(0,len(stages_ts),1)
    stages_ts = pd.DataFrame(stages_ts, index=cnr)
    stages_ts.columns = ["ts"]
    stages_ts['ts_index'] = stages_ts.index
    stages_ts = stages_ts.append({'ts' : 'not specified' , 'ts_index' : len(stages_ts)} , ignore_index=True)

    periods_ts = pd.read_csv(csv_folder+"binning_periods.csv", header=None)
    cnr = np.arange(0,len(periods_ts),1)
    periods_ts = pd.DataFrame(periods_ts, index=cnr)
    periods_ts.columns = ["ts"]
    periods_ts['ts_index'] = periods_ts.index
    periods_ts = periods_ts.append({'ts' : 'not specified' , 'ts_index' : len(periods_ts)} , ignore_index=True)


    epochs_ts = pd.read_csv(csv_folder+"binning_epoch.csv", header=None)
    cnr = np.arange(0,len(epochs_ts),1)
    epochs_ts = pd.DataFrame(epochs_ts, index=cnr)
    epochs_ts.columns = ["ts"]
    epochs_ts['ts_index'] = epochs_ts.index
    epochs_ts = epochs_ts.append({'ts' : 'not specified' , 'ts_index' : len(epochs_ts)} , ignore_index=True)


    eras_ts = pd.read_csv(csv_folder+"binning_era.csv", header=None)
    cnr = np.arange(0,len(eras_ts),1)
    eras_ts = pd.DataFrame(eras_ts, index=cnr)
    eras_ts.columns = ["ts"]
    eras_ts['ts_index'] = eras_ts.index
    eras_ts = eras_ts.append({'ts' : 'not specified' , 'ts_index' : len(eras_ts)} , ignore_index=True)

    eons_ts = pd.read_csv(csv_folder+"binning_eon.csv", header=None)
    cnr = np.arange(0,len(eons_ts),1)
    eons_ts = pd.DataFrame(eons_ts, index=cnr)
    eons_ts.columns = ["ts"]
    eons_ts['ts_index'] = eons_ts.index
    eons_ts = eons_ts.append({'ts' : 'not specified' , 'ts_index' : len(eons_ts)} , ignore_index=True)

    return {
        'rassm': rassm_ts,
        'berg': berg_ts,
        'webby': webby_ts,
        'stages': stages_ts,
        'periods': periods_ts,
        'epochs': epochs_ts,
        'eras': eras_ts,
        'eons': eons_ts
    }

def binning_outputs_equal(a, b):
    fa = pd.read_csv(a)
    fb = pd.read_csv(b)
    cols = list(fa.columns.values)

    def sort_refs(row):
        row = row.split(", ")
        row = map(int, row)
        row = sorted(row)
        row = map(str, row)
        concatenator = ', '
        return concatenator.join(row)
    fa.loc[:,'refs'] = fa['refs'].apply(sort_refs)
    fb.loc[:, 'refs'] = fb['refs'].apply(sort_refs)
    fa.sort_values(by=cols, inplace=True, ignore_index=True)
    fb.sort_values(by=cols, inplace=True, ignore_index=True)

    df = fa.merge(fb, how='outer', indicator=True)
    only2 = df[df['_merge'] == 'right_only']
    if len(only2) > 0:
        print(a)
        print(only2)

    pd.testing.assert_frame_equal(fa, fb)

class Task:
    def func(self):
        self.queue.put(self.target(**self.args))

    def __init__(self, target, args):
        self.target = target
        self.args = args
        self.queue = mp.Queue()
        self.handle = mp.Process(target=self.func)
        self.handle.start()

    def join(self):
        ret = self.queue.get()
        self.handle.join()
        return ret
