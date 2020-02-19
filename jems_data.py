"""
Utilities for retrieving and managing the JEMS data from the MSSQL database.
"""

import pyodbc
import pandas as pd

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
        retrieving timeseries data from MSSQL
        results is stored into self.df pandas dataframe
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
        retrieving timeseries data between start_date and end_date from MSSQL
        results is stored into self.df pandas dataframe
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
