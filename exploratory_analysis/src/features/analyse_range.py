"""
A script for performing analyses on a time range of JEMS sensor data.
"""

import os
import pyodbc
import pdb
import argparse
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from dotenv import load_dotenv
from collections import Counter
from sklearn.cluster import KMeans

# get settings from .env file
if os.path.exists("../.env"):
    load_dotenv()
else:
    raise RuntimeError("Expecting .env file with settings.")

from src.data import jems_data
# import src.data.stateGraph

def load_DB_and_reshape():
    # read arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start-date', default="2017-01-21", help="Start of interval to analyse. \
                        Date must be given as 'YYYY-MM-DD hh:mm:ss' or as any prefix of it.", metavar='S')
    parser.add_argument('-e', '--end-date', default="2017-01-22", help="End of interval to analyse. \
                        Date must be given as 'YYYY-MM-DD hh:mm:ss' or as any prefix of it.", metavar='E')
    parser.add_argument('-l', '--save-location', default="results/", help="Location for saving results", metavar='L')
    args = parser.parse_args()

    # check if save location is a valid path
    if not os.path.exists(args.save_location):
        raise RuntimeError("Save location must be a valid path.")

    # initialize Diesel data source
    dt = jems_data.DieselDs(os.getenv("DB_PASSWORD"))

    # get sensor values for each hour between start and end date
    print(f'Loading data in time range: {args.start_date} - {args.end_date}')
    values = dt.load_range(args.start_date, args.end_date, "hour")

    print(f'Loaded')

    # create dataframe where each column represents one sensor
    print('Reshaping data')
    sensor_values = jems_data.reshape_sensor_data(values)
    sensor_values.to_csv(os.path.join(args.save_location, 'sensor_values.csv'))


def join_sensor_descriptions():
    # read arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-csv', help="Path to input csv with sensor values in columns.")
    parser.add_argument('-sd', '--sensor-description', help="Path to input csv with sensor descriptions.")
    parser.add_argument('-o', '--output-csv', help="Path to output csv with full sensor data.")
    args = parser.parse_args()

    print('Reading sensor values from', args.input_csv)
    sensor_values = pd.read_csv(open(args.input_csv))
    print(f'Read {sensor_values.shape[0]} rows and {sensor_values.shape[1]} columns')

    print('Reading sensor descriptions from', args.sensor_description)
    sensor_description = pd.read_csv(open(args.sensor_description), index_col='sensorid')
    print(f'Read {sensor_description.shape[0]} rows and {sensor_description.shape[1]} columns')
    # change sensor name type to string to match index in sensor_val_stats below
    sensor_description.index = sensor_description.index.map(str)

    sensor_val_stats = sensor_values.describe(include='all').transpose()
    sensor_val_stats.index.name = 'sensorid'

    sensor_data = sensor_description.join(sensor_val_stats, how='inner')
    sensor_data.to_csv(args.output_csv)


# sensors per component
component_sensors = {
    "B100" : ['50','53','62','63','64','65','97','98'] # removed due to sparsity: '96'
}

def normalize_timestamp(timestamp_series):
    """
    Convert timestamp to milliseconds.
    Assumes the series is sorted in ascending order!
    """
    # convert datetime strings into milliseconds from epoch
    times = pd.to_datetime(timestamp_series, format='%Y-%m-%d %H:%M:%S').astype(np.int64) // int(1e6)
    return times

def prepare_streamstory_input():
    # read arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-csv', help="Path to input csv with sensor values in columns.")
    parser.add_argument('-sd', '--sensor-description', default=None, help="[OPTIONAL] Path to input csv with sensor descriptions. If given, sensor descriptions will be used instead of IDs.")
    parser.add_argument('-o', '--output-csv', help="Path to output csv with sensor data formatted for StreamStory.")
    args = parser.parse_args()

    print('Reading sensor values from', args.input_csv)
    sensor_values = pd.read_csv(open(args.input_csv))
    print(f'Read {sensor_values.shape[0]} rows and {sensor_values.shape[1]} columns')

    if args.sensor_description is not None:
        print('Reading sensor descriptions from', args.sensor_description)
        sensor_description = pd.read_csv(open(args.sensor_description), index_col='sensorid')
        print(f'Read {sensor_description.shape[0]} rows and {sensor_description.shape[1]} columns')

        # go over all column ids except `timestamp` at 0 and prepare
        col_rename = {}
        for col_id in sensor_values.columns[1:]:
            col_rename[col_id] = sensor_description.loc[int(col_id)]['description'].replace(' ', '_')

    target_component = "B100"
    # collect just the relevant sensor values and the timestamp
    component_data = sensor_values.filter(['timestamp'] + component_sensors[target_component])
    if args.sensor_description is not None:
        component_data = component_data.rename(columns=col_rename)
    component_data['timestamp'] = normalize_timestamp(component_data['timestamp'])
    component_data = component_data.set_index('timestamp')

    component_data.to_csv(args.output_csv)


if __name__ == "__main__":
    # prepare_streamstory_input()
    graph = stateGraph.StateGraph(5)
