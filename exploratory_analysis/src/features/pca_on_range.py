"""
A script for performing PCA on a time range of JEMS sensor data and dumping the
results to disk.

You can set start_date(-s), end_date(-e) and save_location(-l) with arguments.

First it queries sensor values from the database. Then data is transformed to
the correct format and missing values are replaced with mean value. Results
before and after replacing are saved as csv. Next, PCA is applied, components_
and singular_values_ are saved as npy.

For 1 year of data, the script runs a few minutes.
"""

import os
import pyodbc
import argparse
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from dotenv import load_dotenv

# get settings from .env file
if os.path.exists("../.env"):
    load_dotenv()
else:
    raise RuntimeError("Expecting .env file with settings.")

from src.data.jems_data import DieselDs

def write_to_table(row, table):
    """Write a sensor row to a table."""
    table.loc[row['timestamp'], row['sensors_id']] = row['value']


if __name__ == "__main__":
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
    dt = DieselDs(os.getenv("DB_PASSWORD"))

    # get sensor values for each hour between start and end date
    values = dt.load_range(args.start_date, args.end_date, "hour")

    # create dataframe where each column represents one sensor
    table = pd.DataFrame(index = values["timestamp"].unique(), columns = values["sensors_id"].unique())
    values.apply(lambda row: write_to_table(row, table) , axis=1)
    table.to_csv(os.path.join(args.save_location, 'sensor_values.csv'))

    # create dataframe where NaN are replaced by mean value of a column
    imp_mean = SimpleImputer(missing_values=np.nan, strategy='mean')
    new_table = pd.DataFrame(data = imp_mean.fit_transform(table),
                            index = values["timestamp"].unique(),
                            columns = values["sensors_id"].unique())
    new_table.to_csv(os.path.join(args.save_location, 'sensor_values_without_nan.csv'))

    # standardize the data
    new_table = pd.DataFrame(data = StandardScaler().fit_transform(new_table),
                                index = new_table.index, columns = new_table.columns)

    # PCA
    pca = PCA()
    principal_components = pca.fit_transform(new_table)
    principal_components = pd.DataFrame(principal_components)

    # save components and singular values
    np.save(os.path.join(args.save_location, 'components'), pca.components_)
    np.save(os.path.join(args.save_location, 'singular_values'), pca.singular_values_)

    # print information about the sensor which has the biggest absolute value of coefficient
    # in vector that points in direction of the biggest variance
    sensor = table.columns[np.argmax(np.abs(pca.components_[0]))]
    print("Sensor with the biggest coefficient:")
    print(dt.sdf[dt.sdf.sensorid == sensor].to_string())

    # create list of sensor ids from most important sensor to the least important one
    sensor_importance = []
    for component in pca.components_:
        sensor_importance.append(table.columns[np.argmax(np.abs(component))])
    np.save(os.path.join(args.save_location, 'sensor_importance'), sensor_importance)