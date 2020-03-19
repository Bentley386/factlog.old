"""
Utilities for retrieving and managing the JEMS data from the MSSQL database.
"""

import pyodbc
import pandas as pd
import numpy as np

class DieselDs:
    """Class for retrieving the JEMS data from the database."""
    def __init__(self, password):
        self.c = self.connectToMSSQL(password)
        self.sensors()

    def connectToMSSQL(self, password):
        """connect to MSSQL DB"""
        return pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};"
                              "Server=localhost;"
                              "Database=TracHistorian;"
                              "UID=SA;"
                              "PWD=" + password)

    def load(self, sensorId, type="raw"):
        """
        Retrieve values of sensor with sensorId from MSSQL.
        The 'type' argument determines the frequency type of the data:
            - raw: all values
            - min: minutely values
            - hour: hourly values
            - day: daily values
        Return results in self.df pandas dataframe - schema as in DB.
        """

        # selecting the correct table
        typeTable = "sensor_values";
        if (type == "min"):
            typeTable = "sensor_values_minute"
        elif (type == "hour"):
            typeTable = "sensor_values_hour"
        elif (type == "day"):
            typeTable = "sensor_values_day"

        # retrieving the data
        self.df = pd.read_sql_query('SELECT * FROM {} WHERE sensors_id = {} ORDER BY timestamp ASC'.format(typeTable, sensorId), self.c)

        # also returning df
        return self.df

    def load_range(self, start_date, end_date, type="raw"):
        """
        Retrieve sensor values of all sensors between start_date and end_date from MSSQL.
        The 'type' argument determines the frequency type of the data (details
        in docstring of load above).
        Return results in self.df pandas dataframe - schema as in DB.
        """

        # selecting the correct table
        typeTable = "sensor_values";
        if (type == "min"):
            typeTable = "sensor_values_minute"
        elif (type == "hour"):
            typeTable = "sensor_values_hour"
        elif (type == "day"):
            typeTable = "sensor_values_day"

        # retrieving the data
        self.df = pd.read_sql_query("SELECT * FROM {} WHERE '{}' <= timestamp AND timestamp < '{}'\
                                    ORDER BY timestamp ASC".format(typeTable, start_date, end_date), self.c)

        # also returning df
        return self.df

    def sensors(self):
        """
        retrieving the data from sensors
        result is stored into self.sdf pandas dataframe
        """
        SQL = " \
        SELECT \
            sensors.id as sensorid, \
            sensors.name as name, \
            sensors.description as description, \
            sensors.enabled as enabled, \
            sensor_groups.scan_rate as scan_rate, \
            sensor_groups.description as group_description, \
            datatype.name as datatype, \
            measure_unit.name as measure_unit, \
            measure_unit_type.name as measure_unit_type \
        FROM \
            sensors, \
            sensor_groups, \
            datatype, \
            measure_unit, \
            measure_unit_type \
        WHERE \
            sensor_groups_id = sensor_groups.id AND \
            datatype_id = datatype.id AND \
            measure_unit_id = measure_unit.id AND \
            measure_unit_type_id = measure_unit_type.id"

        self.sdf = pd.read_sql_query(SQL, self.c)

    def searchSensor(self, id):
        """
        Searches for a sensor name in the dataframe of all sensors.
        """
        return self.sdf[self.sdf['name'].str.contains(id) == True]


def reshape_sensor_data(input_df):
    """
    Reshape a dataframe with sensor values in schema as in the DB into a data
    frame with one row per timestamp and one column per sensor.
    """
    def sensor_value_to_table(sensor_row, table):
        """Write a sensor value to the reshaped table."""
        print(f'Row: {sensor_row.name}')
        table.at[sensor_row['timestamp'], sensor_row['sensors_id']] = sensor_row['value']

    print('Preparing empty dataframe')
    # prepare the reshaped table
    output_df = pd.DataFrame(
        index = np.sort(input_df["timestamp"].unique()),
        columns = np.sort(input_df["sensors_id"].unique()))
    # copy individual sensor values
    print('Applying function')
    input_df.apply(lambda row: sensor_value_to_table(row, output_df), axis=1)
    return output_df
