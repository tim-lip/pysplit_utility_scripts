import pandas as pd
import matplotlib.pyplot as plt
import pysplit_utils as utils

datetime = pd.to_datetime('2023031522', format='%Y%m%d%H')
traj_group = utils.extract_trajectories_timeinterval(utils.traj_path, datetime, datetime)

for traj in traj_group:
    traj_datetime = traj.data['DateTime'][0]
    print('Doing '+ str(traj_datetime))
    
    x = traj.path.xy[0]
    y = traj.path.xy[1]
    
    plt.plot(x,y)