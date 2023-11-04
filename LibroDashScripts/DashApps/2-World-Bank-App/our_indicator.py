import pandas as pd
from pandas_datareader import wb

# Hace esto en caso de que cambie el valor de la columna de la API. Smort
df = wb.get_indicators()[['id','name']]
df = df[df.name == 'CO2 emissions (kt)']
print(df)

#Indiv using the Internet (%age of the population) -> IT.NET.USER.ZS
#Proportion of seats held by women in national parliaments (%) -> SG.GEN.PARL.ZS
#CO2 emissions (kt) -> EN.ATM.CO2E.KT