import dash_bootstrap_components as dbc
from pandas_datareader import wb # Import World Bank dataset 
import pandas as pd

countries = wb.get_countries()
print(countries.head(10)[['name']])
countries["capitalCity"].replace({"":None}, inplace=True)
countries.dropna(subset=["capitalCity"], inplace=True)
countries = countries[["name", "iso3c"]]
countries = countries[countries["name"] != "Kosovo"]
countries = countries.rename(columns={"name":"country"})


# Hace esto en caso de que cambie el valor de la columna de la API. Smort
df = wb.get_indicators()[['id','name']]
df = df[df.name == 'CO2 emissions (kt)']
print(df)

#Indiv using the Internet (%age of the population) -> IT.NET.USER.ZS
#Proportion of seats held by women in national parliaments (%) -> SG.GEN.PARL.ZS
#CO2 emissions (kt) -> EN.ATM.CO2E.KT