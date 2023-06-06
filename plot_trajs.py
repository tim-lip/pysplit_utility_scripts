import os
import pandas as pd
import cartopy
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pysplit_utils as utils

# set parameters
threshold = 500 # set threshold in m to color lower parts of trajectory red
start = pd.to_datetime('2023-03-17 10:00')
end = pd.to_datetime('2023-03-19 10:00')

# set paths
working_dir = os.getcwd()
parent = os.path.abspath(os.path.join(working_dir, os.pardir))
traj_path = parent+r'/HySplit/trajectories/NyAlesund/'


traj_group = utils.extract_trajectories_timeinterval(traj_path, start, end)
traj_group = utils.filter_trajectories(traj_group, 2)
print("Trajectory group created and filtered")

projection = cartopy.crs.NorthPolarStereo()

#%% plot all trajectories combined

# only take every third trajectory
traj_group_filtered = [traj for traj in traj_group if traj.data['DateTime'][0].hour % 3 == 0]
traj_group_filtered = traj_group #turned off

# Colormap for time passed
all_trajec_times = [traj.data['DateTime'][0] for traj in traj_group_filtered]
min_time, max_time = min(all_trajec_times), max(all_trajec_times)
norm = mcolors.Normalize(vmin=0, vmax=(max_time - min_time).total_seconds())
#cmap = plt.get_cmap('viridis')
cmap_colors = [(0, 'lightcoral'), (0.5, 'red'), (1, 'yellow')]

# Create the colormap
cmap = mcolors.LinearSegmentedColormap.from_list("my_cmap", cmap_colors)
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])

fig, ax = plt.subplots(figsize=(12,8), 
                       subplot_kw={'projection': projection})

for traj in traj_group_filtered: 
    print('Doing '+ str(traj.data['DateTime'][0]))
    x = traj.path.xy[0]
    y = traj.path.xy[1]

    #[min_longitude, max_longitude, min_latitude, max_latitude]
    #ax.set_extent([-150, 150, 60, 90], crs=cartopy.crs.PlateCarree())
    
    start_time = (traj.data['DateTime'][0] - min_time).total_seconds()
    
    ax.plot(x, y, transform=cartopy.crs.PlateCarree(), 
            color=cmap(norm(start_time)))
    
    ax.set_title(f'Trajectories from time interval {start} - {end}')
    ax.coastlines()
    ax.gridlines()   

cb = plt.colorbar(sm, orientation='vertical')
date_format = "%Y-%m-%d"
date_labels = pd.date_range(min_time, max_time, freq='D')
cb.set_ticks((date_labels - min_time).total_seconds())
cb.set_ticklabels([i.strftime(date_format) for i in date_labels])

fig.tight_layout()   

print('Saving Plot!')
start_str = start.strftime('%d-%m-%Y')
end_str = end.strftime('%d-%m-%Y')
filename = 'Plots/Combinedtrajects_'+start_str+'-'+end_str+'.png'
fig.savefig(filename)

#%% plot single trajectories
for traj in traj_group:
    fig, ax = plt.subplots(figsize=(16,9), 
                           subplot_kw={'projection': projection})
    
    traj.load_reversetraj()
    traj.calculate_integrationerr()
    datetime = traj.data['DateTime'][0]
    
    z = [coord[2] for coord in traj.path.coords]
    x = traj.path.xy[0]
    y = traj.path.xy[1]
    
    x_rev = traj.path_r.xy[0]
    y_rev = traj.path_r.xy[1]
    
    x_low, y_low, z_low, x_high, y_high, z_high = utils.get_high_and_low_coords(x,y,z,200)

    x_w = np.concatenate((x,x_rev)) #longitude
    y_w = np.concatenate((y,y_rev)) #latitude
    #[min_longitude, max_longitude, min_latitude, max_latitude]
    ax.set_extent([np.min(x)-10, np.max(x)+10, np.min(y)-1, np.max(y)+1], 
                  crs=cartopy.crs.PlateCarree())

    ax.plot(x_high, y_high, color='blue', ls='', marker='o', 
            transform=cartopy.crs.PlateCarree(), 
            label=f'high (>{threshold}m)')
    ax.plot(x_low, y_low, color='red', ls='', marker='o', 
            transform=cartopy.crs.PlateCarree(),
            label=f'low (<{threshold}m)')
    ax.plot(x_rev, y_rev, color='green', ls='', marker='x', 
            transform=cartopy.crs.PlateCarree(), 
            label='reverse')
    
    ax.set_title(f'{datetime}, Integration error: {traj.integration_error:3f}')
    ax.coastlines()
    ax.gridlines()   
    plt.legend()
    plt.close()
    
    filename = f'Plots/Single_Trajectories/trajec{datetime}'[:-3].replace(' ', '_').replace(':', '')+'.png'
    fig.savefig(filename)
    print(datetime)
    
