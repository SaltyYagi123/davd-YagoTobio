import pandas as pd
import plotly.express as px

from dash import Dash, dcc, html, Input, Output

# Preparing data for usage ***************************

df = pd.read_csv("tweets.csv") #GLOBAL VARIABLES SHOULD NEVER BE ALTERED. 
# print(df.info())
# print(df.describe)

df["name"] = pd.Series(df["name"]).str.lower()
# print(df["date_time"].head())

# Specify the correct date format
df["date_time"] = pd.to_datetime(
    df["date_time"], format="%d/%m/%Y %H:%M", errors="coerce"
)

df = (
    df.groupby(
        [df["date_time"].dt.date, "name"]
    )[  # Group by day, without the hour, and by name.
        ["number_of_likes", "number_of_shares"]
    ]  # This basically means that we want to group the number of likes and the number of shares by date and by user.
    .mean()
    .astype(int)
)

df = df.reset_index()  # Sort

fig = px.line(data_frame=df, x="date_time", y="number_of_likes",
 color="name", log_y=True, height=300)

# App Layout *****************************************

stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = Dash(__name__, external_stylesheets=stylesheets)

# Basic three column structure
# app.layout = html.Div([
#    html.Div(dcc.Dropdown(), className="four columns"), # 3 columns which occupy the width of four columns each.
#    html.Div(dcc.Dropdown(), className="four columns"),
#    html.Div(dcc.Dropdown(), className = "four columns"),
# ], className = "row")

app.layout = html.Div(
    [
        html.Div(html.H1("Twitter Likes Analysis of Famous People", 
                         style={"textAlign":"center"}),
                         className="row"),
        html.Div(
            dcc.Graph(id="line-chart", figure=fig, className="row")
        ),
        html.Div(
            dcc.Dropdown(
                id="my-dropdown",
                multi=True,
                options=[{"label": x, "value": x} 
                         for x in sorted(df["name"].unique())],
                value=["taylorswift13", "cristiano", "jtimberlake"],
                style={"color":"green"}
            ),
            className="three columns",
        ), 
        html.Div(
            html.A(
                id="my-link", 
                children="Click here to Visit Twitter", 
                href="https://twitter.com/explore", 
                target="_blank", #Si quieres que se abra en una nueva pestaña, esto debería de ser _blank, en vez de _self
                style={"color":"red", "backgroundColor": "yellow", "fontSize":"40px"}
            ), 
            className="two columns", 
        ),
    ],
    className="row"
)

# Ther is a max of 12 columns

# App Callbacks ----------------------------------------------------------------------------------------------------------------
@app.callback(
    Output(component_id="line-chart", component_property="figure"),
    [Input(component_id="my-dropdown", component_property="value")],
)

def update_graph(chosen_value): #Chosen value se refiere a los valores del dropdown list, que se pasan por el 
                                #Component id del callback. Cada vez que se eliga otra opción, se activa. 
    print(f"Values chosen by user: {chosen_value}")

    # Aqui miramos la cantidad de valores que se le pasa para verificar. 
    if len(chosen_value) == 0: 
        return {}
    else: 
        df_filtered = df[df["name"].isin(chosen_value)]
        fig = px.line(
            data_frame = df_filtered, 
            x="date_time", 
            y= "number_of_likes", 
            color="name", 
            log_y=True, 
            labels={
                "number_of_likes":"Likes", 
                "date_time":"Date", 
                "name": "Celebrity",
            },
        )
        return fig


if __name__ == "__main__":
    app.run_server(debug=True)
