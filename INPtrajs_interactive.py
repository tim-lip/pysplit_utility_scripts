import os
import pickle5 as pickle
import pandas as pd
import cartopy
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import pysplit_utils as utils

# Define interactive plot rule
def on_click(event):
    ind = event.ind[0]
    datetime = pine_data.index[ind]
    
    # Get trajectory group in specific time interval
    interval = pd.Timedelta('3 hours')
    start = datetime-interval
    end = datetime+interval
    traj_group = utils.extract_trajectories_timeinterval(utils.traj_path, start, end)
    traj_group = utils.filter_trajectories(traj_group, 0.2)
    
    projection = cartopy.crs.AzimuthalEquidistant(78.924444, 11.928611)
    fig, ax = plt.subplots(figsize=(16,9), 
                           subplot_kw={'projection': projection})

    for traj in traj_group:  
            x = traj.path.xy[0]
            y = traj.path.xy[1]
            z = [coord[2] for coord in traj.path.coords]
            
            threshold = 500
            x_low, y_low, z_low, x_high, y_high, z_high = utils.get_high_and_low_coords(x,y,z,threshold)
            
            if traj.data['DateTime'][0] <= datetime:
                color = 'red'
            if traj.data['DateTime'][0] > datetime:
                color = 'blue'
            ax.plot(x_high, y_high, transform=cartopy.crs.PlateCarree(), 
                    color=color, linestyle='--')
            ax.plot(x_low, y_low, transform=cartopy.crs.PlateCarree(), 
                    color=color, linestyle='-')
        
    patch1 = mpatches.Patch(color='red', label='before expansion')
    patch2 = mpatches.Patch(color='blue', label='after expansion')
    line1 = mlines.Line2D([], [], color='black', 
                          linestyle='--', label=f'Above {threshold}m')
    line2 = mlines.Line2D([], [], color='black', 
                          linestyle='-', label=f'Below {threshold}m')
    ax.legend(handles=[patch1, patch2, line1, line2])
    ax.coastlines()
    ax.gridlines() 
    
#%% Script starts here

# Load Pine Data
with open(utils.pine_path, 'rb') as handle:
    pine_data = pickle.load(handle)

# Plotting
fig, ax = plt.subplots(figsize=(16, 9), constrained_layout=True)
c = ax.scatter(x=pine_data.index,
               y=pine_data['INP_cn / stdL-1'],
               c=pine_data['T_min / °C'],
               picker=True)
fig.colorbar(c, ax=ax, label='$T$ / °C')

locator = mdates.AutoDateLocator()
formatter = mdates.ConciseDateFormatter(locator)

ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(formatter)
ax.set_yscale('log')
ax.grid()
ax.set_xlabel('Date UTC')
ax.set_ylabel(r'$c_\mathrm{INP}$ / l$_\mathrm{std}^{-1}$')

fig.canvas.mpl_connect('pick_event', on_click)