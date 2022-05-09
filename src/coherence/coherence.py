import os
from os.path import join, exists, basename, dirname, expanduser
from glob import glob
import numpy as np
import pandas as pd
import rasterio as rio
from tqdm import tqdm, tqdm_notebook
import matplotlib.pyplot as plt
import pickle

data_dir = '/bsuscratch/zacharykeskinen/data/uavsar/images'
fig_dir = expanduser('~/uavsar/figures/coherence_collections/')
pol_cols = {'VV':'red', 'VH':'green','HV':'aqua','HH':'blue'}
np.random.seed(20220503)

res = pd.DataFrame()

for dir in glob(join(data_dir, '*')):
    pairs = glob(join(dir, '*'))
    pairs = [pair for pair in pairs if basename(pair) != 'tmp']
    for pair in tqdm(pairs, desc = basename(dir)):
        coh_fps = glob(join(pair, '*cor.grd.tiff'))
        for coh_fp in coh_fps:
            dic = {}
            desc = pd.read_csv(glob(join(pair, '*.csv'))[0], index_col = 0)
            dic['first_dt'] = pd.to_datetime(desc.loc['value', 'start time of acquisition for pass 1'])
            dic['second_dt'] = pd.to_datetime(desc.loc['value', 'start time of acquisition for pass 2'])
            dic['heading'] = desc.loc['value', 'peg heading']
            dic['pol'] = basename(coh_fp).split('_')[6][4:]
            with rio.open(coh_fp) as src:
                arr = src.read(1)
                dic['coh_25'], dic['coh_75'] = np.nanquantile(arr, [0.25, 0.75])
                dic['median_coh'] = np.nanmedian(arr)
            res = pd.concat([res, pd.DataFrame.from_records([dic])])
res['diff_dt'] = (res['second_dt'] - res['first_dt']).astype('timedelta64[D]')
with open(expanduser('~/uavsar/results/time_coh/res_df_full'), 'wb') as f:
    pickle.dump(res, f)

from meso_extract import meso_notebook_extract

res = pd.DataFrame()

for dir in glob(join(data_dir, '*')):
    pairs = glob(join(dir, '*'))
    pairs = [pair for pair in pairs if basename(pair) != 'tmp']
    for pair in tqdm(pairs, desc = basename(dir)):
        coh_fps = glob(join(pair, '*cor.grd.tiff'))
        for coh_fp in coh_fps:
            dic = {}
            csv_fp = glob(join(pair, '*.csv'))[0]
            desc = pd.read_csv(csv_fp, index_col = 0)
            dic['first_dt'] = pd.to_datetime(desc.loc['value', 'start time of acquisition for pass 1'])
            dic['second_dt'] = pd.to_datetime(desc.loc['value', 'start time of acquisition for pass 2'])
            dic['heading'] = desc.loc['value', 'peg heading']
            dic['pol'] = basename(coh_fp).split('_')[6][4:]
            dic['meso_result'] = meso_notebook_extract(img_fp=coh_fp, ann_csv = csv_fp, col_in = 'snow_depth_set_1', box_side=10)
            res = pd.concat([res, pd.DataFrame.from_records([dic])])
res['diff_dt'] = (res['second_dt'] - res['first_dt']).astype('timedelta64[D]')
with open(expanduser(f'~/uavsar/results/coh_snotel_sd/res_df_full'), 'wb') as f:
    pickle.dump(res, f)