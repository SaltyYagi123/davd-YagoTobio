from dash import html, dcc
from figures import create_choropleth_figure, create_sunburst, create_scatter_3d, create_scatterplot_major
from data_processing import load_and_preprocess_data_astronauts, load_and_preprocess_data_missions, generate_wordcloud
import dash_bootstrap_components as dbc

# Load and preprocess the data
df_space_missions, missions_per_country, grouped_df = load_and_preprocess_data_missions("assets/space_missions.csv")
df_astronauts, major_counts, state_counts = load_and_preprocess_data_astronauts("assets/astronauts.csv")
wordcloud_image = generate_wordcloud(df_astronauts)
spacex_image = html.Img(
    src="assets/spacex.jpeg",
    style={'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto', 'width': '75%'}
)

def create_learn_card(): 
    learn_text = dcc.Markdown("""
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
    """)
    return dbc.Card(
        [
            dbc.CardHeader("Una Introducción al dashboard."), 
            dbc.CardBody(learn_text),
        ],className="mt-4"
    )

def create_astronaut_card(df_astronauts, state_counts, major_counts, wordcloud_image): 
    astronaut_card = dbc.CardBody(
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3("Status Selector"),
                        dcc.Checklist(
                            id = "status-selector", 
                            options=[
                                {"label": s, "value": s} for s in df_astronauts["Status"].unique()
                            ],
                            value=df_astronauts["Status"].unique().tolist(),
                            inline=False,
                        ), 
                        html.H3("Gender Selector"), 
                        dcc.Checklist(
                            id="gender-selector",
                            options=[
                                {"label": g, "value": g} for g in df_astronauts["Gender"].unique()
                            ],
                            value=df_astronauts["Gender"].unique().tolist(),
                            inline=True,
                        ),
                    ], width=2,
                ),
                dbc.Col(
                    [
                        html.H3("Year Range Slider"), 
                        dcc.RangeSlider(
                            id="year-range-slider",
                            min=df_astronauts["Year"].min(),
                            max=df_astronauts["Year"].max(),
                            value=[df_astronauts["Year"].min(), df_astronauts["Year"].max()],
                            marks={
                                str(year): str(year)
                                for year in range(
                                    df_astronauts["Year"].min(), df_astronauts["Year"].max() + 1
                                )
                                if year % 5 == 0
                            },
                            allowCross=False,
                        ),
                        dcc.Graph(id="bar-chart"), 
                        dcc.Graph(id="us-map", figure = create_choropleth_figure(state_counts, "Number of Astronauts by US State", "State", "USA-states", "Astronaut Count", "usa")),
                        dcc.Graph(id = "major-bubble-chart", figure = create_scatterplot_major(major_counts, "Undergraduate Major", "Major Category", "Number of Astronauts", "Major Category", "Astronaut by Major: Typical vs. Unusual")),
                        html.H3("Word Soup de las misiones espaciales"), 
                        wordcloud_image, 
                    ],
                    width = 10, 
                ),
            ]
        ), 
        className="mt-4",
    )
    
    return astronaut_card

def create_missions_card(missions_per_country, grouped_df, df_space_missions):
    missions_card = dbc.Card(
        dbc.Row([
            dbc.Col(
                dcc.Graph(id = "missions-map", figure = create_choropleth_figure(missions_per_country, "Number of Space Missions by Country", "Country", "country names", "Number of Missions")), 
                width = 6
            ),
            dbc.Col(
                [
                    dcc.Dropdown(
                        id = "mission-status-dropdown", 
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
                width = 6, 
            ), 
            dbc.Col(
                dcc.Graph(id="nested-pie-chart", figure = create_sunburst(grouped_df, "Company", "MissionStatus", "Space Missions: Companies and Mission Success Rates")),
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
                    dcc.Graph(id="3d-scatter-plot")
                ], width=6
            ),
        ])
    )
    return missions_card

def create_failure_explanation_card(spacex_image):
    return dbc.Card(
        dbc.CardBody(
            dbc.Row(
                [
                    html.H2("¿Porque fallan las misiones espaciales?"), 
                    spacex_image
                ]
            ),
        )
    )

def create_tabs(df_astronauts, df_space_missions, state_counts, major_counts, wordcloud_image, missions_per_country, grouped_df):
    learn_card = create_learn_card()
    astronaut_card = create_astronaut_card(df_astronauts, state_counts, major_counts, wordcloud_image)
    missions_card = create_missions_card(missions_per_country, grouped_df, df_space_missions)
    failure_explanation_card = create_failure_explanation_card(spacex_image)

    return dbc.Tabs(
        [
            dbc.Tab(learn_card, tab_id="tab-1", label="Learn"),
            dbc.Tab(astronaut_card, tab_id="tab-2", label="Astronautas"),
            dbc.Tab(missions_card, tab_id="tab-3", label="Misiones"),
            dbc.Tab(failure_explanation_card, tab_id="tab-4", label="¿Porque fallan las misiones espaciales?"),
        ],
        id="tabs",
        active_tab="tab-1",
        className="mt-2",
    )

def create_layout(df_astronauts, df_space_missions, state_counts, major_counts, wordcloud_image, missions_per_country, grouped_df):

    footer = html.Div(
        dcc.Markdown(
            """
            Desarrollado por Yago Tobio Souto. 5º GITT + BA.\n
            Datasets utilizados:\n
            1. Nasa Astronauts (1959 - Present) _https://www.kaggle.com/datasets/nasa/astronaut-yearbook_\n
            2. All Space Missions since 1950 _https://www.kaggle.com/datasets/agirlcoding/all-space-missions-from-1957_\n
            """
        ),
        className="p-2 mt-5 bg-primary text-white small",
    )

    return dbc.Container(
        [
            dbc.Row(dbc.Col(html.H1("La Odisea de los astronautas y sus misiones espaciales", className="text-center bg-primary text-white p-2"))),
            dbc.Row(dbc.Col(create_tabs(df_astronauts, df_space_missions, state_counts, major_counts, wordcloud_image, missions_per_country, grouped_df), width=12, className="mt-4 border")),
            # Assume footer is defined elsewhere
            dbc.Row(dbc.Col(footer)), 
        ], 
        fluid=True,
    )
