"""
A script for building StreamStory input csv files for JEMS data.
"""

import pandas as pd
import argparse

import numpy as np

# sensors per component
COMPONENT_SENSORS = {
    "B100" : ['50','53','55','62','63','64','65','97','98'], # removed due to sparsity: '96'
    "B200" : ['6','7','8','9','10','11','12','13','17','31','32','33','34','35','39','49','52','56','58','66','67','68',
                '69','70','71','72','73','74','75','76'], # removed due to sparsity: '36'
    "B300" : ['14','15','16','40','48','51','57','77','78','79','80','81'], # removed due to sparsity: '61'
    "B102" : ['19','20','85'], # Water tank 1 (removed due to sparsity: '117')
    "turbine" : ['105','106','107'],
    "B201" : ['21','22','86'], # Water tank 2 (removed due to sparsity: '125')
    "B202" : ['23','24','25','87'], # Diesel tank (removed due to sparsity: '126')
    # Catalyst tank (D103), lime tank (D104), mixer (D500) are not included because all sensors are too rare
    # B200-extended are sensors from B200 with sensors from subcomponents: water tank 2, diesel tank and turbine
    "B200-extended" : ['6','7','8','9','10','11','12','13','17','31','32','33','34','35','39','49','52','56','58','66','67',
                        '68','69','70','71','72','73','74','75','76','21','22','86','23','24','25','87','105','106','107'],
}

def normalize_timestamp(timestamp_series):
    """
    Convert timestamp to milliseconds.
    Assumes the series is sorted in ascending order!
    """
    # convert datetime strings into milliseconds from epoch
    times = pd.to_datetime(timestamp_series, format='%Y-%m-%d %H:%M:%S').astype(np.int64) // int(1e6)
    return times


if __name__ == "__main__":
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
    component_data = sensor_values.filter(['timestamp'] + COMPONENT_SENSORS[target_component])
    if args.sensor_description is not None:
        component_data = component_data.rename(columns=col_rename)
    component_data['timestamp'] = normalize_timestamp(component_data['timestamp'])
    component_data = component_data.set_index('timestamp')

    component_data.to_csv(args.output_csv)