import pysplit
import os
import pysplit_utils as utils

# enter name of campaign
base_name = r'NyAlesund'

# set additional paths
hysplit_dir = r'C:/hysplit/exec'
storage_dir = utils.traj_path
meteo_dir = parent+r'/Data/gdas'

# set parameters for trajectories
years = [2023]
months = [4]
hours = list(range(24))
altitudes = [0]
location = (78.924444, 11.928611)
runtime = -(24 * 3)

pysplit.generate_bulktraj(base_name, hysplit_dir, storage_dir, meteo_dir,
                          years, months, hours, altitudes, location, runtime,
                          monthslice=slice(10, 14), get_reverse=True,
                          get_clipped=False, hysplit='C:/hysplit/exec/hyts_std')
