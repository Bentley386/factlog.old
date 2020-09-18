# CONTINENTAL USE CASE

## Readme
The purpose of this document is to aggregate all the core info about JEMS use case related to JSI's work in order to allow anyone to get an instant and detailed overview of JSI's work progress.

## Partners
Partners involved in CONTINENTAL use case and relevant to JSI's work are:

* Alin Popa
* Andreea Paunescu

### Content of the file
There is no header in the CSV files.
The header has to be set manually, e.g. when loading CSV to Pandas.

```
Id, Timestamp, SerialNumber, Station, StationType, StationNumber, Material, TestDescription, TestValue, TestResult, USL, LSL, Format
```

| Field name | Description |
| ---------- | ----------- |
| Id         | Is the unique id from MS Access DB - not relevant for our project |
| Timestamp  | The date time when the event took place - when the values were stored into our DB (when an unit was at a specific station) |
| SerialNumber| Unique identification for each and every unit produced in our Factory |
| Station    | Name of the station/equipment where the unit was processed |
| StationType | Type of the station, if the station is from Pre-Assembly area of from Final Assembly area |
| StationNumber | The number of the specific station in the production flow (i.e 1st Station from the flow will have the StationNumber=1 and 5th Station  from the flow will have the StationNumber=5) |
| Material | Unique identifier asigned for a specific product that we are producing |
| TestDescription | The name/description of the test step or process parameter - define what we are doing in that step (i.e. measuring a current, angle or a force) |
| TestValue | The value provided/measured by the station/equipment for each test step |
| TestResult | Result of the test after the evaluation with the limits was done. (i.e. If the measured value is between the limits the result will be Pass, if it is outside of the limits the result will be Fail) |
| USL | Lower limit of the test step |
| LSL | Upper limit of the test step |
| Format | Data type of format for the stored/measured values (R6.2 - Real number with 6 digits before the coma and 2 digits after the coma). |

__Author:__ _Alin Popa - Initial work_





