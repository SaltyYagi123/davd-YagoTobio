from dash import Dash, html, dcc, Input, Output, State
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO
from collections import Counter


import base64
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# Dataframe
df = pd.read_csv("assets/astronauts.csv")

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
typical_majors_keywords = ['Engineering', 'Science', 'Physics', 'Mathematics', 'Chemistry', 'Biology', 'Astronomy', 'Aeronautics']

# Function to categorize majors based on keywords
def categorize_major(major):
    major = str(major)  # Ensure the major is a string
    for keyword in typical_majors_keywords:
        if keyword in major:
            return 'Typical'
    return 'Wacky/Unusual'

# Apply this function to the 'Undergraduate Major' column
df['Major Category'] = df['Undergraduate Major'].apply(categorize_major)

# Count the number of astronauts in each categorized major
major_counts = df.groupby(['Major Category', 'Undergraduate Major']).size().reset_index(name='Number of Astronauts')

# Count the number of astronauts per state
state_counts = df["State"].value_counts().reset_index()
state_counts.columns = ["State", "Astronaut Count"]

#! - Word Count Bubble for the Space Missions 
# Split the 'Missions' column into individual missions and count them
mission_list = df['Missions'].dropna().str.split(', ').sum()
mission_counts = Counter(mission_list)

# Generate the word cloud from frequencies
wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(mission_counts)

# Convert the word cloud image to a string of base64 to display in Dash
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
img = BytesIO()
plt.savefig(img, format='png', bbox_inches='tight', pad_inches=0)
img.seek(0)
wordcloud_string = base64.b64encode(img.getvalue()).decode()

wordcloud_image = html.Img(src='data:image/png;base64,{}'.format(wordcloud_string), style={'width': '100%', 'height': 'auto'})


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
    x='Undergraduate Major', 
    y='Major Category', 
    size='Number of Astronauts',
    color='Major Category', 
    title='Astronauts by Major: Typical vs. Wacky/Unusual'
)

# Improve readability
fig_education.update_layout(xaxis_tickangle=-45)
fig_education.update_traces(marker=dict(opacity=0.7))  # Adjust opacity for better visualization

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
                            marks={str(year): str(year) for year in range(df['Year'].min(), df['Year'].max() + 1) if year % 5 == 0},
                            allowCross=False,
                        ),
                        dcc.Graph(id="bar-chart"),
                        dcc.Graph(id="us-map", figure=fig_choropleth),
                        dcc.Graph(id='major-bubble-chart', figure=fig_education),
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
    [Output("bar-chart", "figure"), Output("us-map", "figure"), Output("major-bubble-chart", "figure")],
    [
        Input("year-range-slider", "value"),
        Input("status-selector", "value"),
        Input("gender-selector", "value"),
    ],
)
def update_visualizations(selected_year_range, selected_status, selected_gender):
    
    filtered_df = df[(df['Year'] >= selected_year_range[0]) & (df['Year'] <= selected_year_range[1])]
    if selected_status:
        filtered_df = filtered_df[filtered_df['Status'].isin(selected_status)]
    if selected_gender:
        filtered_df = filtered_df[filtered_df['Gender'].isin(selected_gender)]

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
    major_counts = filtered_df['Undergraduate Major'].value_counts().reset_index()
    major_counts.columns = ['Undergraduate Major', 'Number of Astronauts']
    major_counts['Major Category'] = major_counts['Undergraduate Major'].apply(categorize_major)

    # Create the bubble chart
    bubble_fig = px.scatter(
        major_counts,
        x='Undergraduate Major',
        y='Major Category',
        size='Number of Astronauts',
        color='Major Category',
        title='Astronauts by Major: Typical vs. Wacky/Unusual'
    )

    # Adjust layout for the bubble chart
    bubble_fig.update_layout(xaxis_tickangle=-45)
    bubble_fig.update_traces(marker=dict(opacity=0.7))

    # Return all the figures
    return bar_fig, map_fig, bubble_fig


if __name__ == "__main__":
    app.run_server(debug=True)
