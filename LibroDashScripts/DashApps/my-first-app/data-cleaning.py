import pandas as pd
import plotly.express as px


df = pd.read_csv("tweets.csv")
print(df.info())
print(df.describe)

df["name"] = pd.Series(df["name"]).str.lower()
print(df["date_time"].head())

# Specify the correct date format
df["date_time"] = pd.to_datetime(df["date_time"], format="%d/%m/%Y %H:%M", errors='coerce')

df = (
    df.groupby([df["date_time"].dt.date, "name"])[ # Group by day, without the hour, and by name. 
        ["number_of_likes", "number_of_shares"]    
    ] #This basically means that we want to group the number of likes and the number of shares by date and by user. 
    .mean()
    .astype(int)
)

df = df.reset_index() #Sort

print(df.head())