import os, math, cartopy
import pickle5 as pickle
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pysplit_utils as utils

# Set parameters
T_pine = -32 #in celsius
max_integration_error = 1 #in percent
pine_time = ['2023-03-15', '2023-04-10'] #default

# Load Pine Data and filter for single temperature
with open(utils.pine_path, 'rb') as handle:
    pine_data = pickle.load(handle)
pine_data = pine_data[(pine_data['T_min / °C'] > T_pine-1) &
                      (pine_data['T_min / °C'] < T_pine+1)]
pine_data = pine_data.loc[pine_time[0]:pine_time[1], :]

# Get corresponding trajectories
start = pine_data.index.min()
end = pine_data.index.max()
traj_group = utils.extract_trajectories_timeinterval(utils.traj_path, start, end)
traj_group = utils.filter_trajectories(traj_group, max_integration_error)

# determine colormap and get order in which to draw in
INP_list = []
for traj in traj_group:
    datetime = traj.data['DateTime'][0]
    stoptime = datetime+pd.Timedelta('30 minutes')
    INP_traj = pine_data.loc[datetime:stoptime, :]
    INP_traj = INP_traj['INP_cn / stdL-1'].mean()
    if not math.isnan(INP_traj):
        INP_list.append(INP_traj)

cmap = plt.get_cmap('YlOrRd')
norm = mcolors.Normalize(vmin=min(INP_list), vmax=max(INP_list))

order_INP = [i for i, v in sorted(enumerate(INP_list), key=lambda x: x[1])]

# Plotting
projection = cartopy.crs.AzimuthalEquidistant(78.924444, 11.928611)
fig, ax = plt.subplots(figsize=(10,8), 
                       subplot_kw={'projection': projection})
        
#for position in order_INP:
for traj in traj_group:
   # traj = traj_group[position]

    datetime = traj.data['DateTime'][0]
    stoptime = datetime+pd.Timedelta('30 minutes')
    INP_traj = pine_data.loc[datetime:stoptime, :]['INP_cn / stdL-1'].mean()
    if not math.isnan(INP_traj):
        #z = [coord[2] for coord in traj.path.coords]
        x = traj.path.xy[0]
        y = traj.path.xy[1]
        
        # for better display purposes play around with alpha and linewidth
        alpha = 1
        if norm(INP_traj)<0.3:
            alpha = norm(INP_traj)
        ax.plot(x, y, transform=cartopy.crs.PlateCarree(),
                color=cmap(norm(INP_traj)), linewidth=max(5*norm(INP_traj), 1),
                alpha = alpha)
      
fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), 
             label='$c_\mathrm{INP}$ / l$_\mathrm{std}^{-1}$')
ax.coastlines()
ax.gridlines()
ax.set_title(f'Tpine = {T_pine} °C')
fig.tight_layout()
if pine_time[0] == '2023-03-15' and pine_time[1] =='2023-04-10':
    fig.savefig(utils.plot_path+f'trajectories_INPcolored_Tpine{T_pine}.png')
else:
    fig.savefig(utils.plot_path+f'trajectories_INPcolored_Tpine{T_pine}_time{pine_time[0]}to{pine_time[1]}.png')
        
    