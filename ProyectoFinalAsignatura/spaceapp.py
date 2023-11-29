from dash import Dash, html, dcc, Input, Output, State
from wordcloud import WordCloud
from collections import Counter
from io import BytesIO
import dash_leaflet as dl


import base64
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt

# Dataframe
df = pd.read_csv("assets/astronauts.csv")
df_space_missions = pd.read_csv("assets/space_missions.csv", encoding="ISO-8859-1")
df_space_missions_failure = pd.read_csv("assets/Space_Corrected.csv", encoding="ISO-8859-1")

# * Data pre-processing
df = df[df["Year"].notna()]
df["Year"] = df["Year"].astype(int)
# Create 5-year bins
df["Year Interval"] = pd.cut(
    df["Year"], bins=range(df["Year"].min(), df["Year"].max() + 5, 5), right=False
)
df["Year Interval"] = df["Year Interval"].astype(str)

# Extract state from 'Birth Place'
df["State"] = df["Birth Place"].str.split(",").str[-1].str.strip()

# Define lists of majors you consider 'Typical'
typical_majors_keywords = [
    "Engineering",
    "Science",
    "Physics",
    "Mathematics",
    "Chemistry",
    "Biology",
    "Astronomy",
    "Aeronautics",
]


# Function to categorize majors based on keywords
def categorize_major(major):
    major = str(major)  # Ensure the major is a string
    for keyword in typical_majors_keywords:
        if keyword in major:
            return "Typical"
    return "Wacky/Unusual"


# Apply this function to the 'Undergraduate Major' column
df["Major Category"] = df["Undergraduate Major"].apply(categorize_major)

# Count the number of astronauts in each categorized major
major_counts = (
    df.groupby(["Major Category", "Undergraduate Major"])
    .size()
    .reset_index(name="Number of Astronauts")
)

# Count the number of astronauts per state
state_counts = df["State"].value_counts().reset_index()
state_counts.columns = ["State", "Astronaut Count"]

#! - Word Count Bubble for the Space Missions
# Split the 'Missions' column into individual missions and count them
mission_list = df["Missions"].dropna().str.split(", ").sum()
mission_counts = Counter(mission_list)

# Generate the word cloud from frequencies
wordcloud = WordCloud(
    width=800, height=400, background_color="white"
).generate_from_frequencies(mission_counts)

# Convert the word cloud image to a string of base64 to display in Dash
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
img = BytesIO()
plt.savefig(img, format="png", bbox_inches="tight", pad_inches=0)
img.seek(0)
wordcloud_string = base64.b64encode(img.getvalue()).decode()

wordcloud_image = html.Img(
    src="data:image/png;base64,{}".format(wordcloud_string),
    style={"width": "100%", "height": "auto"},
)


"""
DATA PRE-PROCESSING FOR THE SPACE MISSIONS:
======================================================
"""
# * Data pre-processing for the space missions:
# Convert 'Date' to datetime and extract the year
df_space_missions["Date"] = pd.to_datetime(df_space_missions["Date"])
df_space_missions["Year"] = df_space_missions["Date"].dt.year
# Group by year and count the number of missions
missions_per_year = (
    df_space_missions.groupby("Year").size().reset_index(name="Number of Missions")
)

# Extract country name from 'Location'
df_space_missions["Country"] = (
    df_space_missions["Location"].str.split(",").str[-1].str.strip()
)
# Count the number of missions per country
missions_per_country = df_space_missions["Country"].value_counts().reset_index()
missions_per_country.columns = ["Country", "Number of Missions"]

# Group by company and mission status
grouped_df = (
    df_space_missions.groupby(["Company", "MissionStatus"])
    .size()
    .reset_index(name="Count")
)
# Calculate the total missions for each company
total_missions_per_company = (
    grouped_df.groupby("Company")["Count"].sum().reset_index(name="TotalMissions")
)
# Merge to get total missions alongside status counts
grouped_df = pd.merge(grouped_df, total_missions_per_company, on="Company")
# Calculate total missions
total_missions = grouped_df["Count"].sum()
# Calculate the percentage for each company
grouped_df["Percentage"] = grouped_df["Count"] / total_missions * 100


# Create the choropleth map
fig_missions_map = px.choropleth(
    missions_per_country,
    locations="Country",
    locationmode="country names",
    color="Number of Missions",
    title="Number of Space Missions by Country",
)

fig_sunburst = px.sunburst(
    grouped_df,
    path=["Company", "MissionStatus"],
    values="Count",
    title="Space Missions: Companies and Mission Success Rates",
    custom_data=["Percentage"],
)
# Update hovertemplate to show percentages
fig_sunburst.update_traces(
    hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{customdata[0]:.2f}%"
)

fig_3d = px.scatter_3d(
    df_space_missions,
    x="Year",
    y="MissionStatus",  # You might need to map this to a numerical scale
    z="Price",  # Same as above
    color="Company",  # Could be another categorical variable
    title="3D Scatter Plot of Space Missions",
)

"""
FIGURES
========================================================================================
"""
# You might need a mapping from state names to codes

# Create the choropleth map
fig_choropleth = px.choropleth(
    state_counts,
    locations="State",
    locationmode="USA-states",
    color="Astronaut Count",
    scope="usa",
    title="Number of Astronauts by US State",
)

# Adjust layout if needed
fig_choropleth.update_layout(geo=dict(bgcolor="rgba(0,0,0,0)"))

fig_education = px.scatter(
    major_counts,
    x="Undergraduate Major",
    y="Major Category",
    size="Number of Astronauts",
    color="Major Category",
    title="Astronauts by Major: Typical vs. Wacky/Unusual",
)

# Improve readability
fig_education.update_layout(xaxis_tickangle=-45)
fig_education.update_traces(
    marker=dict(opacity=0.7)
)  # Adjust opacity for better visualization

app = Dash(
    __name__, external_stylesheets=[dbc.themes.SUPERHERO, dbc.icons.FONT_AWESOME]
)

"""
EXPLICATIVE TEXT
==========================================================================================
"""

learn_text = dcc.Markdown(
    """
    Bienvenidos a 'Odisea Astronauta: Un Viaje A través del Espacio y Tiempo'
    En esta primera sección de nuestro innovador tablero de control, se embarcarán en un fascinante recorrido por la historia y los logros de los astronautas a lo largo de los años. Descubrirán patrones intrigantes y datos reveladores sobre quienes han sido estos exploradores del espacio, sus orígenes, y las misiones que han llevado a cabo.

    ¿Qué aprenderán?

    **1. Evolución en el Tiempo:** Visualicen cómo ha cambiado el número y el estado de los astronautas (activos, retirados, fallecidos) a lo largo de los años.

    **2. Diversidad de Género:** Conozcan la distribución de género entre los astronautas y cómo esto ha ido transformándose.

    **3. Orígenes Globales:** Explorarán el mapa interactivo para descubrir de dónde vienen estos héroes del espacio, destacando la diversidad de sus lugares de nacimiento.

    **4. Desarrollo de Misiones:** Observarán cómo han evolucionado las horas de vuelo en el espacio a lo largo del tiempo, reflejando los avances en las misiones espaciales.

    **5. Trayectoria y Experiencia:** Estudiarán la relación entre la edad de los astronautas en su primer vuelo y sus horas totales de vuelo, revelando patrones de carrera.

    **6. Más Allá de la Tierra:** A través de un gráfico de burbujas, verán la interacción entre el número de vuelos espaciales, caminatas espaciales y horas en el espacio.

    **7. Impacto del Rango Militar:** Analizarán cómo el rango militar se relaciona con las horas de vuelo en el espacio.

    **8. Interconexión de Datos:** Finalmente, una matriz de correlación les mostrará cómo se relacionan entre sí diferentes variables numéricas, como vuelos espaciales y caminatas espaciales.

    Cada gráfico está diseñado para ser interactivo, permitiéndoles sumergirse profundamente en los datos y descubrir historias ocultas detrás de los números. Prepárense para un viaje informativo y visualmente estimulante por el universo de los astronautas.
    """
)


footer = html.Div(
    dcc.Markdown(
        """
        Desarrollado por Yago Tobio Souto. 5º GITT + BA. 
        Datasets utilizados: 
        1. Nasa Astronauts (1959 - Present) _https://www.kaggle.com/datasets/nasa/astronaut-yearbook_
        """
    ),
    className="p-2 mt-5 bg-primary text-white small",
)

"""
CARDS
===============================
"""
learn_card = dbc.Card(
    [
        dbc.CardHeader("An Introduction to the dashboard"),
        dbc.CardBody(learn_text),
    ],
    className="mt-4",
)

missions_card = dbc.Card(
    dbc.CardBody(
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="missions-map", figure=fig_missions_map), width=6),
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id="mission-status-dropdown",
                            options=[
                                {"label": status, "value": status}
                                for status in df_space_missions[
                                    "MissionStatus"
                                ].unique()
                            ],
                            value="Success",  # Default value
                            clearable=False,
                        ),
                        dcc.Graph(id="missions-time-series"),
                    ],
                    width=6,
                ),
                dbc.Col(
                    dcc.Graph(id="nested-pie-chart", figure=fig_sunburst),
                    width=6,
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id="company-filter",
                            options=[
                                {"label": company, "value": company}
                                for company in df_space_missions["Company"].unique()
                            ],
                            value=None,
                            multi=True,
                            placeholder="Select Company",
                        ),
                        # Other filters as needed...
                        dcc.Graph(id="3d-scatter-plot"),
                    ],width=6,
                ),
            ]
        )
    )
)

astronaut_card = dbc.Card(
    dbc.CardBody(
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3("Status Selector"),
                        dcc.Checklist(
                            id="status-selector",
                            options=[
                                {"label": s, "value": s} for s in df["Status"].unique()
                            ],
                            value=df["Status"].unique().tolist(),
                            inline=False,
                        ),
                        html.H3("Gender Selector"),
                        dcc.Checklist(
                            id="gender-selector",
                            options=[
                                {"label": g, "value": g} for g in df["Gender"].unique()
                            ],
                            value=df["Gender"].unique().tolist(),
                            inline=True,
                        ),
                    ],
                    width=2,
                ),  # Adjust width as needed
                dbc.Col(
                    [
                        html.H3("Year Range Slider"),
                        dcc.RangeSlider(
                            id="year-range-slider",
                            min=df["Year"].min(),
                            max=df["Year"].max(),
                            value=[df["Year"].min(), df["Year"].max()],
                            marks={
                                str(year): str(year)
                                for year in range(
                                    df["Year"].min(), df["Year"].max() + 1
                                )
                                if year % 5 == 0
                            },
                            allowCross=False,
                        ),
                        dcc.Graph(id="bar-chart"),
                        dcc.Graph(id="us-map", figure=fig_choropleth),
                        dcc.Graph(id="major-bubble-chart", figure=fig_education),
                        html.H3("Word Soup de las misiones espaciales"),
                        wordcloud_image,
                    ],
                    width=10,
                ),
                # Adjust width as needed
            ]
        )
    ),
    className="mt-4",
)

failure_explanation_card = dbc.Card(
    dbc.CardBody(

    )
)

"""
COMPONENTS
"""

# Tab organisation
tabs = dbc.Tabs(
    [
        dbc.Tab(learn_card, tab_id="tab-1", label="Learn"),
        dbc.Tab(
            astronaut_card,
            tab_id="tab-2",
            label="Astronauts",
            className="pb-4",
        ),
        dbc.Tab(missions_card, tab_id="tab-3", label="Missions", className="pb-4"),
    ],
    id="tabs",
    active_tab="tab-1",
    className="mt-2",
)


"""
MAIN LAYOUT 
=========================================================================================
"""

app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1(
                    "La Odisea de los astronautas: un viaje por el tiempo y el espacio",
                    className="text-center bg-primary text-white p-2",
                ),
            )
        ),
        dbc.Row(
            dbc.Col(tabs, width=12, className="mt-4 border"),
        ),
        dbc.Row(dbc.Col(footer)),
    ],
    fluid=True,
)

"""
CALLBACKS 
============================================================
"""


@app.callback(
    [
        Output("bar-chart", "figure"),
        Output("us-map", "figure"),
        Output("major-bubble-chart", "figure"),
    ],
    [
        Input("year-range-slider", "value"),
        Input("status-selector", "value"),
        Input("gender-selector", "value"),
    ],
)
def update_visualizations(selected_year_range, selected_status, selected_gender):
    filtered_df = df[
        (df["Year"] >= selected_year_range[0]) & (df["Year"] <= selected_year_range[1])
    ]
    if selected_status:
        filtered_df = filtered_df[filtered_df["Status"].isin(selected_status)]
    if selected_gender:
        filtered_df = filtered_df[filtered_df["Gender"].isin(selected_gender)]

    grouped_df = (
        filtered_df.groupby(["Year Interval", "Status"])
        .size()
        .reset_index(name="Count")
    )

    bar_fig = px.bar(
        grouped_df,
        x="Year Interval",
        y="Count",
        color="Status",
        barmode="group",
        title="Numero de Astronautas por rango a través de los años",
    )

    state_counts = filtered_df["State"].value_counts().reset_index()
    state_counts.columns = ["State", "Astronaut Count"]

    map_fig = px.choropleth(
        state_counts,
        locations="State",
        locationmode="USA-states",
        color="Astronaut Count",
        scope="usa",
        title="Number of Astronauts by US State",
    )
    map_fig.update_layout(geo=dict(bgcolor="rgba(0,0,0,0)"))

    # Prepare data for the bubble chart
    major_counts = filtered_df["Undergraduate Major"].value_counts().reset_index()
    major_counts.columns = ["Undergraduate Major", "Number of Astronauts"]
    major_counts["Major Category"] = major_counts["Undergraduate Major"].apply(
        categorize_major
    )

    # Create the bubble chart
    bubble_fig = px.scatter(
        major_counts,
        x="Undergraduate Major",
        y="Major Category",
        size="Number of Astronauts",
        color="Major Category",
        title="Astronauts by Major: Typical vs. Wacky/Unusual",
    )

    # Adjust layout for the bubble chart
    bubble_fig.update_layout(xaxis_tickangle=-45)
    bubble_fig.update_traces(marker=dict(opacity=0.7))

    # Return all the figures
    return bar_fig, map_fig, bubble_fig


@app.callback(
    Output("missions-time-series", "figure"),
    [Input("mission-status-dropdown", "value")],
)
def update_mission_time_series(selected_status):
    filtered_df = df_space_missions[
        df_space_missions["MissionStatus"] == selected_status
    ]
    missions_per_year = (
        filtered_df.groupby("Year").size().reset_index(name="Number of Missions")
    )

    fig = px.line(
        missions_per_year,
        x="Year",
        y="Number of Missions",
        title="Number of Space Missions Over Time",
        markers=True,
    )

    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(count=5, label="5y", step="year", stepmode="backward"),
                        dict(step="all"),
                    ]
                )
            ),
            rangeslider=dict(visible=True),
            type="date",
        )
    )
    # Add range slider configuration here...

    return fig


@app.callback(
    Output("3d-scatter-plot", "figure"),
    [Input("company-filter", "value")],  # Add other inputs as needed
)
def update_3d_scatter(selected_companies):
    filtered_df = df_space_missions
    if selected_companies:
        filtered_df = filtered_df[df_space_missions["Company"].isin(selected_companies)]

    # Update 3D scatter plot with filtered data
    fig = px.scatter_3d(
        filtered_df,
        x="Year",
        y="MissionStatus",  # Adjust mapping to numerical scale if needed
        z="Price",  # Same as above
        color="Company",  # Or another categorical variable
        title="3D Scatter Plot of Space Missions",
    )
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
