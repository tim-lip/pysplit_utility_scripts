import pysplit_utils as utils
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pickle5 as pickle

#%% calculate distances from trajectories and save them in pickle file
pickle_file = 'trajectory_endpoint_distances.pickle'

starttime = pd.to_datetime('2023-03-17 10:00')
endtime = pd.to_datetime('2023-04-10 10:00')

traj_group = utils.extract_trajectories_timeinterval(utils.traj_path, 
                                                     starttime, endtime)

len_traj_group = 0
for traj in traj_group:
    len_traj_group += 1

distances_trajs = []
times_trajs = []
for i in range(1, len_traj_group):
    end_traj = (traj_group[i].path.xy[0][-1], traj_group[i].path.xy[1][-1])
    end_previous_traj = (traj_group[i-1].path.xy[0][-1], traj_group[i-1].path.xy[1][-1])
    
    distance = utils.distance_between2pts(end_traj, end_previous_traj)
    distances_trajs.append(distance)
    
    time_traj = traj_group[i].data['DateTime'][0]
    times_trajs.append(time_traj)
    
with open(pickle_file, 'wb') as handle:
    pickle.dump((times_trajs, distances_trajs), handle, protocol=pickle.HIGHEST_PROTOCOL)


#%% plot comparison with pine data 

campaign = 'ExINP_GVB'
with open(utils.pine_path, 'rb') as handle:
    pine_data = pickle.load(handle)

T_pine = -32
pine_data = pine_data[(pine_data['T_min / °C'] > T_pine-1) &
                      (pine_data['T_min / °C'] < T_pine+1)]

with open(pickle_file, 'rb') as handle:
    times_trajs, distances_trajs = pickle.load(handle)

fig, ax = plt.subplots(figsize=(16, 9))

scatter = ax.scatter(x=pine_data.index,
                     y=pine_data['INP_cn / stdL-1'])
                    # c=pine_data['T_min / °C'], label='Pine')
#cbar = fig.colorbar(scatter, ax=ax, label='$T_\mathrm{Pine}$ / °C')
#cbar.ax.invert_yaxis()
locator = mdates.AutoDateLocator()
formatter = mdates.ConciseDateFormatter(locator)
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(formatter)
ax.set_yscale('log')
ax.grid(axis='both')
ax.set_xlabel('Date UTC')
ax.set_ylabel(r'$c_\mathrm{INP}$ / l$_\mathrm{std}^{-1}$')


ax2 = ax.twinx()
ax2.plot(times_trajs, distances_trajs, color='black')

ax.set_title(f'T_pine = {T_pine}')
    