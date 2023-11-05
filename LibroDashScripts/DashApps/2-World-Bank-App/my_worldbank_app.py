from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
from pandas_datareader import wb

# In the app we use 3 Bootstrap components (dbc) -> Label, RadioItems, Button.

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP]) 
# En caso de que no quieras activar las funciones de actualizacion, puedes hacer el prevent_initial_callbacks=True

# ---------------------- DATA PRE-PROCESSING -----------------------

countries = wb.get_countries()
# print(countries.head(10)[['name']])
countries["capitalCity"].replace({"": None}, inplace=True)
countries.dropna(subset=["capitalCity"], inplace=True)
countries = countries[["name", "iso3c"]]
countries = countries[countries["name"] != "Kosovo"]
countries = countries.rename(columns={"name": "country"})

# Get the indicators
df = wb.get_indicators()[["id", "name"]]
df = df[df.name == "CO2 emissions (kt)"]
# print(df)

# Indiv using the Internet (%age of the population) -> IT.NET.USER.ZS
# Proportion of seats held by women in national parliaments (%) -> SG.GEN.PARL.ZS
# CO2 emissions (kt) -> EN.ATM.CO2E.KT

indicators = {
    "IT.NET.USER.ZS": "Individuals using the Internet (% of population)",
    "SG.GEN.PARL.ZS": "Proportion of seats held by women in national parliaments (%)",
    "EN.ATM.CO2E.KT": "CO2 emissions (kt)",
}


def update_wb_data():
    # Retrieve specific world bank data from the API
    df = wb.download(
        indicator=(list(indicators)), country=countries["iso3c"], start=2005, end=2016
    )  # Columns: Country, Year, IT.NET.USER.ZS, SG.GEN.PARL, EN.ATM, !! No ISO3
    #print(df.head())
    #print(df.info())
    #print(df.describe())
    df = (
        df.reset_index()
    )  # We reset the index so that country and year, which are part of the index, become new columns, and we have a dedicated index column with nothing but integers, which will help with filtering later.
    df.year = df.year.astype(int)  # So we can filter with pandas.

    # Add country ISO3 ID to main df so we can plot it on the visual graph
    df = pd.merge(df, countries, on="country")
    df = df.rename(
        columns=indicators
    )  # We pass a dictionary so it know what to search for, instead of hardcoding a dict.
    return df


# --------------------    APP LAYOUT  --------------------------------

app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                [
                    html.H1(
                        "Comparison of World Bank Country Data", 
                        style={"textAlign":"center"},
                    ),
                    dcc.Graph(id="my-choropleth", figure={})],
                width=12,
            )
        ),
        # Okay so here the structure is that each element within the col is a row, but you work outwards.
        dbc.Row(
            dbc.Col(
                [
                    dbc.Label(
                        "Select Data Set:", 
                        className = "fw-bold", 
                        style={"textDecoration":"underline", "fontSize": 20},
                    ),
                    dbc.RadioItems(
                        id="radio-indicator",
                        options=[{"label": i, "value": i} for i in indicators.values()],
                        value=list(indicators.values())[0],  # Registra el valor seleccionado por el usuario. Pero ponemos el default, que es el [0]
                        input_class_name="me-2",  # Margin end 2
                    ),
                ],
                width=4,
            )
        ),
        dbc.Row(  # So here it would be 3 rows in one column that's 6 columns-wide.
            [
                dbc.Col(
                    [
                        dbc.Label(
                            "Select Years:", 
                            className = "fw-bold", 
                            style={"textDecoration":"underline", "fontSize":20},
                        ),
                        dcc.RangeSlider(
                            id="years-range",
                            min=2005,
                            max=2016,
                            step=1,
                            value=[2005, 2006],
                            marks={
                                year: str(year)
                                if year == 2005 or year == 2016
                                else f"'{str(year)[-2:]}"
                                for year in range(2005, 2017)
                            },
                            allowCross=True,
                        ),
                        dbc.Button(
                            id="my-button",  # Component id for the callback
                            children="Submit",  # Text displayed on the button
                            n_clicks=0,  # Num times it's been clicked by the user. States
                            color="primary",  # secondary -> gray, success -> green.
                            className="mt-4 fw-bold",  # Full bootstrap -> mt-4 Margin top 4 units of space. Font weight bold
                        ),
                    ],
                    width=6,
                ),
            ]
        ),
        dcc.Interval(id="timer", interval=1000 * 60, n_intervals=0), # You can have a max intervals parameter, which will let you limit the number of updates. 
        dcc.Store(id="storage", storage_type="session", data={}),  # Save dashboard data in memory of the browser for quick re-call.
        # Storage type can be session, local and memory.
    ]
)

# --------------------- Callback Structure + Callback Functions --------------
#* Callback 1 - First callback is responsible for retrieving data from the world bank. 
@app.callback(
    Output("storage", "data"), 
    Input("timer", "n_intervals")) 
# Component id, component property. 
# ? - Input es el timer interval, que cuando se resetee, se activa la función
# ? - La función devuelve la base de datos actualizada como output, la cual se mete en el session storage, y se pasa a data
def store_data(_): #One parameter, because one input
    dataframe = update_wb_data()
    return dataframe.to_dict("records") # Because we have one output, if it had multiple, then return multiple. 

#* Callback 2 - Second callback is responsible for creating and displaying the choropleth map on the app. 
# ? - Callback ordering -> If callbacks don't depend on each other, the order won't matter. For callbacks that do, the trigger should be written before any other callback. 
@app.callback(
    Output("my-choropleth","figure"),   # La figura que vamos a generar
    Input("my-button", "n_clicks"),     # 'Todos los parametros de entrada. -> No vamos a permitir que se actualice hasta que se pulse el botón porque es un input. 
    Input("storage", "data"), 
    State("years-range", "value"),      # Cambios de estado. Makes a note of users selection. Esto es mucho de React. 
    State("radio-indicator", "value")
)

def update_graph(n_clicks, stored_dataframe, years_chosen, indct_chosen):
    dff = pd.DataFrame.from_records(stored_dataframe) #Obten la última versión del dataset de memoria. 
    print(years_chosen)

    # Filter the DataFrame based on years_chosen
    if years_chosen[0] != years_chosen[1]:
        dff = dff[dff.year.between(years_chosen[0], years_chosen[1])]
        dff = dff.groupby(["iso3c", "country"])[indct_chosen].mean()
    else:
        dff = dff[dff["year"].isin(years_chosen)]

    # Reset the index if needed
    dff = dff.reset_index()
    print(dff)
    # Define labels for the plot
    labels = {
        indicators["SG.GEN.PARL.ZS"]: "% parliament women", 
        indicators["IT.NET.USER.ZS"]: "pop. % using internet"
    }

    # Create the choropleth plot
    fig = px.choropleth(
        data_frame=dff, 
        locations="iso3c", 
        color=indct_chosen, 
        scope="world", 
        hover_data={"iso3c": False, "country": True}, 
        labels=labels
    )
    
    fig.update_layout(
        geo={"projection":{"type": "natural earth"}}, 
        margin=dict(l=50, r=50, t=50, b=50)
    )
    return fig

if __name__ == "__main__":
    app.run_server(debug = True)