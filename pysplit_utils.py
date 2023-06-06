import os
import re
import numpy as np
import pandas as pd
import pysplit

# paths 
working_dir = os.getcwd()
parent = os.path.abspath(os.path.join(working_dir, os.pardir))
traj_path = parent+r'/Data/trajectories/NyAlesund'
pine_path = parent+r'/Data/Pine/timeseries_filtered_PINE-04-02_ExINP_GVB.pickle'
plot_path = parent+r'/Plots/PySplit/'

# Helper function to extract date from pysplit trajectory filename
def extract_date(filename: str):
    match = re.search(r'(\d{10})', filename)
    if match:
        date = pd.to_datetime(match.group(1), format='%Y%m%d%H')
        return date
    return None

# Extract all trajectories in time interval and return trajectory group
# Pass same start and endtime to get specific trajectory
def extract_trajectories_timeinterval(path, start: pd.Timestamp, 
                                      end: pd.Timestamp):    
    # Get all the filenames in the directory
    filenames = os.listdir(path)

    # Filter filenames based on the interval
    filtered_filenames = []
    for filename in filenames:
        date = extract_date(filename)
        if date is not None and start <= date <= end:
            filtered_filenames.append(os.path.join(path, filename))

    # Build trajectory group build on filtered filenames
    traj_group = pysplit.make_trajectorygroup(filtered_filenames)
    
    
    return traj_group

# Sorts coordinates in groups above and below an altitude threshold
def get_high_and_low_coords(x,y,z, treshold):
    low_ind = [i for i in range(len(x)) if z[i] < treshold]
    x_low = [x[i] for i in low_ind]
    y_low = [y[i] for i in low_ind]
    z_low = [z[i] for i in low_ind]

    high_ind = [i for i in range(len(x)) if z[i] >= treshold]
    x_high = [x[i] for i in high_ind]
    y_high = [y[i] for i in high_ind]
    z_high = [z[i] for i in high_ind]

    return x_low, y_low, z_low, x_high, y_high, z_high

# filter out trajectories above a certain integration error threshold
def filter_trajectories(traj_group, threshold):
    for traj in traj_group:
        traj.load_reversetraj()
        traj.calculate_integrationerr()
        if traj.integration_error <= threshold:
            traj_group.pop(trajid=traj.trajid)
    return traj_group

def distance_between2pts(coord0, coord1, in_xy=False):
    """
    Calculate distance between two sets of coordinates.
    Parameters
    ----------
    coord0 : tuple of floats
        Coordinate pair in degrees
    coord1 : tuple of floats
        Coordinate pair in degrees
    in_xy : Boolean
        Default False.  If True, the pair is in (lon, lat)
        rather than (lat, lon)
    Returns
    -------
    distance : float
        Great circle distance in meters.
    """
    coord0 = np.radians(coord0)
    coord1 = np.radians(coord1)

    coord_order = {False: [0, 1],
                   True: [1, 0]}

    a, b = coord_order[in_xy]

    distance = (np.arccos(np.sin(coord1[a]) * np.sin(coord0[a]) +
                          np.cos(coord1[a]) * np.cos(coord0[a]) *
                          np.cos(coord0[b] - coord1[b])) * 6371) * 1000

    return distance
