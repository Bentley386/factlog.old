"""
A script for performing PCA on a time range of JEMS sensor data and dumping the
results to disk.

Before running the script, you have to set START_DATE, END_DATE and
SAVE_LOCATION.

First it queries sensor values from the database. Then data is transformed to
the correct format and missing values are replaced with mean value. Results
before and after replacing are saved as csv. Next, PCA is applied, components_
and singular_values_ are saved as npy.

For 1 year of data, the script runs a few minutes.
"""

import os
import pyodbc
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.decomposition import PCA
from dotenv import load_dotenv

# get settings from .env file
if os.path.exists(".env"):
    load_dotenv()
else:
    raise RuntimeError("Expecting .env file with settings.")

from jems_data import DieselDs

# TODO: move parameters to script arguments with argparse
# start and end of interval to analyse
START_DATE = "2017-01-21 00:00:00.0"
END_DATE = "2017-01-22 00:00:00.0"
# where to save results (must end with '/')
SAVE_LOCATION = "./"

def write_to_table(row, table):
    """Write a sensor row to a table."""
    table.loc[row['timestamp'], row['sensors_id']] = row['value']

if __name__ == "__main__":
    # initialize Diesel data source
    dt = DieselDs(os.getenv("DB_PASSWORD"))

    # get sensor values for each hour between START_DATE and END_DATE
    values = dt.load_range(START_DATE, END_DATE, "hour")

    # create dataframe where each column represents one sensor
    table = pd.DataFrame(index = values["timestamp"].unique(), columns = values["sensors_id"].unique())
    values.apply(lambda row: write_to_table(row, table) , axis=1)
    table.to_csv(SAVE_LOCATION + 'sensor_values.csv')

    # create dataframe where NaN are replaced by mean value of a column
    imp_mean = SimpleImputer(missing_values=np.nan, strategy='mean')
    newTable = pd.DataFrame(data = imp_mean.fit_transform(table),
                            index = values["timestamp"].unique(),
                            columns = values["sensors_id"].unique())
    newTable.to_csv(SAVE_LOCATION + 'sensor_values_without_nan.csv')

    # PCA
    pca = PCA()
    pca.fit(newTable)

    # save components and singular values
    np.save(SAVE_LOCATION + 'components', pca.components_)
    np.save(SAVE_LOCATION + 'singular_values', pca.singular_values_)

    # print information about the sensor which has the biggest absolute value of coefficient
    # in vector that points in direction of the biggest variance
    sensor = table.columns[np.argmax(np.abs(pca.components_[0]))]
    print("Sensor with the biggest coefficient:")
    print(dt.sdf[dt.sdf.sensorid == sensor].to_string())
