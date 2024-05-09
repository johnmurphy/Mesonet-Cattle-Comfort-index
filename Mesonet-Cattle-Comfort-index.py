# importing libraries 
import pandas as pd 
import os 
import numpy as np

# for database connection
from sqlalchemy import create_engine

# Set working directory
os.chdir('set working directory')
print(os.getcwd())

# CSV File source : SouixCountyIowa-WeatherData-20211215-20220614.csv
# Example Below : 2021-12-15 Souix County Iowa (42.967830657959, -96.1524963378906) 
# Weather Data Source : https://www.visualcrossing.com/
# Weather Data Source Documentation : https://www.visualcrossing.com/resources/documentation/weather-data/weather-data-documentation/

vFileName = "NameYourFile.csv"
df = pd.read_csv(vFileName) 

# Use to Test Calculation expected results = 37.9
# An example CCI calculation for environmental conditions, represented
# by Ta, RH, WS, and RAD of 30°C, 50%, 1.0 m/s, and 500 W/m2, respectively,
# would be as follows: 30°C + 1.8 (RH adjustment from Eq. [1]) + 0.6
# (WS adjustment from Eq. [2]) + 5.5 (RAD adjustment from Eq. [3] = 37.9.

# Source:: https://content.prod.mesonet.org/learn/ag/tools_documentation/Cattle_Comfort_Description.201605.pdf

# Declare Variables for testing
# Euler's number
#e = 2.71828 

# ambient temperature
#Ta = 47.2000007629395

# relative humidity
#RH = 89.5 

# wind speed
#WS = 39.7000007629395 

# radiation
#RAD = 61.2000007629395


# Calculate RH correction factor
# Euler's number
e = 2.71828 

RHx = (0.00182 * df.RH + 1.8 * pow(10,-5) * df.Ta * df.RH)

RHy = (0.000054 * pow(df.Ta,2) + 0.00192 * df.Ta - 0.0246) * (df.RH - 30)

RHz = pow(e,RHx)

RHCorrFactor = RHz * RHy

#print(RHCorrFactor)
df['RHCorrFactor'] = RHCorrFactor
# Test output 1.8


# Calculate Wind Speed (WS) correction factor
# Needed to replace the math libary with numpy as math has trouble handling pandas dataframe data (series). Needed to put data in numpy array.
WSa = 1/pow((2.26 * df.WS + 0.23),0.45)

WSb = 2.9 + 1.14 * pow(10,-6) * pow(df.WS,2.5) - np.emath.logn(0.3, np.array(pow((2.26 * df.WS + 0.33),-2))) 

WSc = WSa * WSb

WSd = pow(e,WSc)

# The formula in the University of Nebraska document was incorrect. The Mesonet document has the updated corrected calc. by the same author.
WSCorrFactor = (-6.56/WSd) - 0.00566 * pow(df.WS,2) + 3.33 

#print(WSCorrFactor)
df['WSCorrFactor'] = WSCorrFactor
# Test output 0.6


# Calculate RAD correction factor
RADCorrFactor = 0.0076 * df.RAD - 0.00002 * df.RAD * df.Ta + 0.00005 * pow(df.Ta,2) * np.sqrt(df.RAD) + 0.1 * df.Ta - 2 

#print(RADCorrFactor)
df['RADCorrFactor'] = RADCorrFactor
# Test output 5.5


# Calculate the final Cattle Comfort Index (CCI) value.

df['CCI'] = df.Ta + df.RHCorrFactor + df.WSCorrFactor + df.RADCorrFactor
#print(CCI)
# Test output 37.9


# Added feature. Days on Feed (DOF). Thought it would be interesting to add to the final dataset. 
df.insert(0, 'DOF', range(0,len(df)))


# Just take a look to see what it looks like
df.head()


# Windows Authentication

Server = 'ServerName'
Database = 'Database'
Driver = 'ODBC Driver 17 for SQL Server'

#Username =
#Password = 
#DatabaseConn = f'mssql://{Username}:{Password}@{Server}/{Database}?driver={Driver}'

DatabaseConn = f'mssql://@{Server}/{Database}?driver={Driver}'

engine = create_engine(DatabaseConn)
con = engine.connect()


# to_sql funtion creates a new table, index = False does not include index from df, if_exists = 'replace' will replace the entire table
df.to_sql('[TableName]', con = engine, if_exists = 'replace', index = False, chunksize = 50) 
# chunksize not required, but helpful for large amounts of data





