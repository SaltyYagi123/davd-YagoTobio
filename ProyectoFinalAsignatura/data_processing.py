import pandas as pd 
import plotly.express as px 

df = pd.read_csv("assets/astronauts.csv")

df = df[df['Year'].notna()]
df['Year'] = df['Year'].astype(int)

# Create 5-year bins 
df['Year Interval'] = pd.cut(df['Year'], bins=range(df['Year'].min(), df['Year'].max() + 5, 5), right=False)

df['Year Interval'] = df['Year Interval'].astype(str)
# Group by Year and Status + Count in each group 
grouped_df = df.groupby(['Year Interval', 'Status']).size().reset_index(name='Count')

fig = px.bar(grouped_df, x='Year Interval', y='Count', color='Status', barmode = 'group', 
             title= "Number of Astronauts over the year by Status")

fig.show()