import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table
from figures import (
    create_choropleth_figure,
    create_sunburst,
    create_scatterplot_major,
    create_group_bar_chart,
    company_sunburst,
    company_success_bar_chart,
    treemap_success,
    failed_missions_calendar,
    average_mission_cost,
    average_mission_cost_countries,
    average_mission_cost_companies,
    xgboost_importance_factors,
)
from data_processing import (
    load_and_preprocess_data_astronauts,
    load_and_preprocess_data_missions,
    generate_wordcloud,
    load_mission_success,
    process_mission_success
)


# Load and preprocess the data
df_space_missions, missions_per_country, grouped_df = load_and_preprocess_data_missions(
    "assets/space_missions.csv"
)
df_astronauts, major_counts, state_counts = load_and_preprocess_data_astronauts(
    "assets/astronauts.csv"
)
df_mission_success = load_mission_success("assets/Space_Corrected.csv")

df_ms = process_mission_success(df_mission_success)
wordcloud_image = generate_wordcloud(df_astronauts)

spacex_image = html.Img(
    src="assets/spacex.jpeg",
    style={
        "display": "block",
        "margin-left": "auto",
        "margin-right": "auto",
        "width": "75%",
    },
)

success_rate_image = html.Img(
    src="assets/SuccessRate.png",
    style={
        "display": "block",
        "margin-left": "auto",
        "margin-right": "auto",
        "width": "100%",
    },
)

table_country_image = html.Img(
    src="assets/tableCountryMission.png",
    style={
        "display": "block",
        "margin-left": "auto",
        "margin-right": "auto",
        "width": "100%",
    },
)


def create_learn_card():
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
    return dbc.Card(
        [
            dbc.CardHeader("Una Introducción al dashboard."),
            dbc.CardBody(learn_text),
        ],
        className="mt-4",
    )


def create_astronaut_card(df_astronauts, state_counts, major_counts, wordcloud_image):
    astronaut_card = dbc.CardBody(
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3("Status Selector"),
                        dcc.Checklist(
                            id="status-selector",
                            options=[
                                {"label": s, "value": s}
                                for s in df_astronauts["Status"].unique()
                            ],
                            value=df_astronauts["Status"].unique().tolist(),
                            inline=False,
                        ),
                        html.H3("Gender Selector"),
                        dcc.Checklist(
                            id="gender-selector",
                            options=[
                                {"label": g, "value": g}
                                for g in df_astronauts["Gender"].unique()
                            ],
                            value=df_astronauts["Gender"].unique().tolist(),
                            inline=True,
                        ),
                    ],
                    width=2,
                ),
                dbc.Col(
                    [
                        html.H3("Year Range Slider"),
                        dcc.RangeSlider(
                            id="year-range-slider",
                            min=df_astronauts["Year"].min(),
                            max=df_astronauts["Year"].max(),
                            value=[
                                df_astronauts["Year"].min(),
                                df_astronauts["Year"].max(),
                            ],
                            marks={
                                str(year): str(year)
                                for year in range(
                                    df_astronauts["Year"].min(),
                                    df_astronauts["Year"].max() + 1,
                                )
                                if year % 5 == 0
                            },
                            allowCross=False,
                        ),
                        dcc.Graph(id="bar-chart"),
                        dcc.Graph(
                            id="us-map",
                            figure=create_choropleth_figure(
                                state_counts,
                                "Number of Astronauts by US State",
                                "State",
                                "USA-states",
                                "Astronaut Count",
                                "usa",
                            ),
                        ),
                        dcc.Graph(
                            id="major-bubble-chart",
                            figure=create_scatterplot_major(
                                major_counts,
                                "Undergraduate Major",
                                "Major Category",
                                "Number of Astronauts",
                                "Major Category",
                                "Astronaut by Major: Typical vs. Unusual",
                            ),
                        ),
                        html.H3("Word Soup de las misiones espaciales"),
                        wordcloud_image,
                    ],
                    width=10,
                ),
            ]
        ),
        className="mt-4",
    )

    return astronaut_card


def create_missions_card(missions_per_country, grouped_df, df_space_missions):
    missions_card = dbc.Card(
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id="missions-map",
                        figure=create_choropleth_figure(
                            missions_per_country,
                            "Number of Space Missions by Country",
                            "Country",
                            "country names",
                            "Number of Missions",
                        ),
                    ),
                    width=6,
                ),
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
                    dcc.Graph(
                        id="nested-pie-chart",
                        figure=create_sunburst(
                            grouped_df,
                            "Company",
                            "MissionStatus",
                            "Space Missions: Companies and Mission Success Rates",
                        ),
                    ),
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
                        dcc.Graph(id="3d-scatter-plot"),
                    ],
                    width=6,
                ),
            ]
        )
    )
    return missions_card


def create_failure_explanation_card(spacex_image):
    return dbc.Card(
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        html.H2("¿Porque fallan las misiones espaciales?"),
                        spacex_image,
                        html.Hr(),
                    ],
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Markdown(
                                """
                                    Observamos que nuestra base de datos tiene 7 columnas distintas: 
                                     + **Nombre de la Compañía** (Company Name) - Nombre de la compañía que fundó la misión. 
                                     + **Ubicación (Location)** - La ubicación del despegue. 
                                     + **Tiempo y hora del despegue** (Datum) 
                                     + **Status Rocket** - El estado actual del cohete. 
                                     + **Rocket** - El coste en milliones de dolares de la misión.
                                     + **Status Mission** - El estado, exitoso o fallo del despegue. 
                                     """
                            ),
                            width=5,
                        ),
                        dbc.Col(
                            dash_table.DataTable(
                                id="success_table",
                                columns=[
                                    {"name": i, "id": i}
                                    for i in df_mission_success.columns
                                ],
                                data=df_mission_success.to_dict("records"),
                                style_table={
                                    "overflowX": "auto",  # Horizontal scroll
                                    "maxHeight": "300px",  # Maximum table height
                                },
                                style_cell={
                                    "textAlign": "left",
                                    "backgroundColor": "white",
                                    "color": "black",
                                    "fontSize": 14,
                                    "font-family": "sans-serif",
                                },
                                style_header={
                                    "backgroundColor": "lightgrey",
                                    "fontWeight": "bold",
                                },
                                style_data={"whiteSpace": "normal", "height": "auto"},
                                fixed_rows={"headers": True},
                            ),
                            width=7,
                        ),
                        html.Hr(),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Markdown(
                                """
                        Ya que estamos analizando la razón por las cuales fallan las misiones espaciales, 
                        vamos a primero observar el status de las misiones. 
                                         
                        Podemos observar que un **89.71%** de las misiones espaciales son **exitosas**, y un 
                        **7.84% no lo son.** Esta segunda cifra van a ser las misiones más importantes para nuestro analisis.
                                """
                            ),
                            width=4,
                        ),  # Adjust the width as needed
                        dbc.Col(success_rate_image, width=4),
                        dbc.Col(
                            dcc.Graph(id="company-success-sunburst", figure=company_sunburst(df_ms), style={
                                "width": "450px",
                                "height": "325px",
                                "margin": "auto",
                            },)
                            ,width=4),
                        html.Hr(),
                    ]
                ),
                dbc.Row(
                    [
                        html.H4("Analizando el efecto de la ubicación de despegue:"),
                        dbc.Col(
                            dcc.Markdown(
                                """
                                    Observamos que un gran número de las misiones espaciales salen desde Rusia y Estados Unidos. Una de las razones de más peso es debido a la carrera espacial de ambos países:

                                    > La carrera espacial fue una pugna entre Estados Unidos y la Unión Soviética por la conquista del espacio que duró aproximadamente de 1955 a 1988.  
                                    > Supuso el esfuerzo paralelo de ambos países de explorar el espacio exterior con satélites artificiales y de enviar humanos al espacio y a la superficie lunar.  
                                    > Aunque el conflicto se remonta a las primeras tecnologías de cohetes y a las tensiones internacionales tras la Segunda Guerra Mundial, el inicio de la carrera espacial se hizo efectivo con el lanzamiento soviético del Sputnik 1 el 4 de octubre de 1957.  
                                    > El término se acuñó de forma análoga al de la carrera armamentística. La carrera espacial constituyó uno de los ejes principales de rivalidad cultural y tecnológica entre la URSS y los Estados Unidos durante la Guerra Fría. La tecnología espacial se convirtió en una arena particularmente importante en este conflicto, tanto por sus potenciales aplicaciones militares como por sus efectos sobre la opinión pública de uno y otro país.
                                """
                            ),
                            width=8,
                        ),
                        dbc.Col(table_country_image, width=4),
                        html.Hr(),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [dcc.Markdown("""**Ahora vamos a observar la tasa de éxito y fallo de las misiones espaciales para cada uno de estos paises, asumiendo que la ubicación de despegue esta relacionado al país detrás de dicha misión. Es decir, que si la ubicación es en India, vamos a declarar que la operación espacial y todo lo relacionado de operaciones fue Indu.**"""),
                             html.H3("Que vemos en porcentaje de éxito:"),
                             dcc.Markdown(""" 
                                + Kenia ocupa el primer lugar con un porcentaje de éxito del 100%. Kenia ha realizado 9 misiones espaciales y todas ellas han tenido éxito.
                                + Francia, con 303 misiones espaciales, ocupa el segundo lugar con un porcentaje de éxito del 94%.
                                + Rusia, con 1398 misiones espaciales, ocupa el tercer puesto con un porcentaje de éxito del 93,34%. Esto ya es algo. 
                                + En comparación con los lanzamientos que tienen lugar en Estados Unidos, Rusia sale mejor parada, ya que las misiones estadounidenses tienen una tasa de éxito de alrededor del 88%.
                                """),
                             html.H3("Que vemos en porcentaje de fallo:"), 
                             dcc.Markdown(""" 
                                + Brasil y Corea del Sur tienen una tasa de fracaso similar del 66,67%, es decir, dos tercios de sus misiones espaciales fracasan.
                                + Cabe señalar que Corea del Sur tiene una tasa de éxito del 33%, mientras que Brasil aún no ha realizado ninguna misión espacial con éxito.
                                + Estos resultados no son desalentadores, ya que tanto Corea del Sur como Brasil sólo han realizado 3 intentos de misión espacial.
                                + A continuación tenemos a Corea del Norte, con una tasa de fracaso del 60% en sus 5 misiones espaciales.
                                + Irán tiene una tasa de fracaso del 57%. Sin embargo, sólo ha realizado 14 misiones espaciales.
                                """)], width = 4),

                        dbc.Col(dcc.Graph(
                                id="mission-success-per-country",
                                figure=create_group_bar_chart(df_ms),
                        ),width=8),   
                    ]
                ), 
                dbc.Row(
                    [
                        html.H2("Analizando el efecto de una compañía"),
                        dbc.Col(
                            dcc.Markdown(
                                """
                                        Medimos la tasa de exito y fallo de cada compañía:

                                        #### Compañías exitosas destacables:
                                        Compañías como ASI, Blue Origin, Douglas, IRGC, i-Space, Yuzhmash y otras tienen un 100% de tasa de exito. 

                                        #### Compañías fallidas destacables: 
                                        Compañías como EER, Landscape, OneSpace, Sandia y Virgin Orbit tienen un 100% de tasa de fallo. Nunca han tenido una misión exitosa. 
                                        """
                            ),
                            width=3,
                        ),
                        dbc.Col(
                            dcc.Graph(
                                id="company-bar-chart",
                                figure=(company_success_bar_chart(df_ms)),
                            ),
                            width=9,
                        ),
                        html.Hr(),
                        html.H3(
                            "Gráfica recopilatoria de las tasas de éxito entre paises y sus respectivas compañías:"
                        ),
                        dcc.Graph(
                            id="tree-map",
                            figure=(treemap_success(df_ms)),
                        ),
                        html.Hr(),
                    ]
                ),
                dbc.Row(
                    [
                        html.H2("Analizando el efecto de la hora y día del despegue:"), 
                        dbc.Col(dcc.Markdown(
                            """
                        + El porcentaje global de misiones fallidas se ha reducido con los años. Mientras que en los primeros años tuvimos tasas de fracaso de hasta el 60-70%, la tasa de fracaso en 2018 es solo de alrededor del 1,7% y en 2019 es de alrededor del 5,5%.
                        
                        + Está claro que a medida que el campo de la Exploración Espacial ha evolucionado y que disponemos de tecnologías más nuevas y avanzadas, las probabilidades de fallo se han reducido.
                        
                        + La tasa media de fallos en este periodo es del 9,6%.
                        
                        + Repasando las tendencias mensuales de fracasos, vemos que las misiones espaciales lanzadas en noviembre tienen la mayor probabilidad de fracasar, seguidas de las de febrero.
                        
                        + Diciembre tiene la menor tasa de fracaso con un 5,78%.
                        
                        + Aunque la tendencia semanal no tiene sentido (a menos que se sea supersticioso), es interesante ver que el miércoles es el día más seguro de la semana en cuanto a lanzamientos de misiones espaciales.
                            """), width = 4), 
                        dbc.Col(dcc.Graph(
                            id = "calendar-graph", 
                            figure = failed_missions_calendar(df_ms)
                        ), width = 8),
                        html.Hr()
                    ]
                ), 
                dbc.Row(
                    [
                        dbc.Col(dcc.Markdown(
                            """ 
                            Vemos que, con el tiempo, el coste medio de las misiones ha disminuido desde 1987. Sin embargo, como se ha visto anteriormente, la tasa de fracaso de las misiones espaciales ha disminuido con el tiempo. Por lo tanto, una cosa está clara, a medida que la tecnología ha avanzado, hemos sido capaces de hacer misiones espaciales a un menor coste y con menores tasas de fracaso.
                            La razón por la que vemos un pico muy alto en 1987 es por una Misión Espacial de la RVSN URSS que tiene un coste estimado de 5000 millones de dólares. Eso sí que es mucho dinero. 
                            Esto distorsionó mucho los datos, ya que la mayoría de las demás misiones espaciales de ese año no tenían ningún coste de misión en el conjunto de datos.
                            """), width = 4),
                        dbc.Col(dcc.Graph(
                            id = "average-mission-cost", 
                            figure = average_mission_cost(df_ms)
                        ), width = 8),
                        html.Hr(),
                    ]
                ),
                dbc.Row(
                    [
                        html.H3("Análisis de los costes de las misiones en países y compañías"), 
                        dcc.Markdown("""
                        + Una tendencia importante que observamos es que Estados Unidos ha conseguido reducir el coste de sus misiones espaciales con el paso del tiempo.
                        + El resultado anterior de que EE.UU. redujo el coste medio de las misiones a lo largo de los años también se confirma aquí a partir de los resultados mostrados por la NASA.
                        + Otra cosa que me ha parecido especialmente interesante es que las primeras misiones de SpaceX no tuvieron éxito y su coste era notablemente inferior al de sus misiones espaciales posteriores. Por tanto, aumentar el presupuesto que asignan a cada misión espacial les ayudó a tener más éxito."""),
                        dbc.Col(
                            dcc.Graph(
                                id="country-cost-evolution", 
                                figure = average_mission_cost_countries(df_ms)
                            ),width = 6
                        ), 
                        dbc.Col(
                            dcc.Graph(
                                id = "company-cost-evolution", 
                                figure = average_mission_cost_companies(df_ms)
                            ), width = 6
                        ), 
                    ]
                ), 
                dbc.Row(
                    [
                        html.Hr(),
                        html.H2("Modelo de Machine Learning para determinar los factores del exito de una misión"), 
                        dbc.Col(dcc.Markdown("""
                        ### Rendimiento del modelo XGBoost:
                        Sin ningún ajuste de hiperparámetros, entreno el modelo utilizando las siguientes características :

                        + Nombre de la empresa
                        + Lugar de lanzamiento
                        + Cohete, es decir, coste de la misión
                        + País
                        + Año de lanzamiento
                        + Mes de lanzamiento
                        + Día de la semana de lanzamiento
                        
                        El objetivo es predecir la columna objetivo, que en este caso es el Estado de la Misión. 
                        Hay que tener en cuenta que, para facilitar las cosas, considero cualquier misión que no haya sido un éxito como un fracaso, es decir, los fracasos parciales y los fracasos previos al lanzamiento son sólo fracasos a nuestros ojos.

                        ##### El modelo de XGBoost nos da **una precisión del 93% en el dataset de entreno, y un 89% en el de testeo.**

                        ##### Como se observa en este gráfico de importancia de características, vemos que el Año en que se lanzó la misión espacial tiene el mayor impacto a la hora de predecir el estado de la misión. Le sigue el mes de lanzamiento de la misión.
                        """), width = 6), 
                        dbc.Col(
                            dcc.Graph(
                                id = "xgboost-importance-factors", 
                                figure = xgboost_importance_factors(df_ms)
                            ), width = 6
                        ),
                        html.Hr(),
                    ]
                ),

            ]
        )
    )


def create_tabs(
    df_astronauts,
    df_space_missions,
    state_counts,
    major_counts,
    wordcloud_image,
    missions_per_country,
    grouped_df,
):
    learn_card = create_learn_card()
    astronaut_card = create_astronaut_card(
        df_astronauts, state_counts, major_counts, wordcloud_image
    )
    missions_card = create_missions_card(
        missions_per_country, grouped_df, df_space_missions
    )
    failure_explanation_card = create_failure_explanation_card(spacex_image)

    return dbc.Tabs(
        [
            dbc.Tab(learn_card, tab_id="tab-1", label="Learn"),
            dbc.Tab(astronaut_card, tab_id="tab-2", label="Astronautas"),
            dbc.Tab(missions_card, tab_id="tab-3", label="Misiones"),
            dbc.Tab(
                failure_explanation_card,
                tab_id="tab-4",
                label="¿Porque fallan las misiones espaciales?",
            ),
        ],
        id="tabs",
        active_tab="tab-1",
        className="mt-2",
    )


def create_layout(
    df_astronauts,
    df_space_missions,
    state_counts,
    major_counts,
    wordcloud_image,
    missions_per_country,
    grouped_df,
):
    footer = html.Div(
        dcc.Markdown(
            """
            Desarrollado por Yago Tobio Souto. 5º GITT + BA.\n
            Datasets utilizados:\n
            1. Nasa Astronauts (1959 - Present) _https://www.kaggle.com/datasets/nasa/astronaut-yearbook_\n
            2. All Space Missions since 1950 _https://www.kaggle.com/datasets/agirlcoding/all-space-missions-from-1957_\n
            3. Space Missions from 1957 _https://www.kaggle.com/datasets/agirlcoding/all-space-missions-from-1957_\n
            _Special thanks to Aayush Jain_
            """
        ),
        className="p-2 mt-5 bg-primary text-white small",
    )

    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    html.H1(
                        "La Odisea de los astronautas y sus misiones espaciales",
                        className="text-center bg-primary text-white p-2",
                    )
                )
            ),
            dbc.Row(
                dbc.Col(
                    create_tabs(
                        df_astronauts,
                        df_space_missions,
                        state_counts,
                        major_counts,
                        wordcloud_image,
                        missions_per_country,
                        grouped_df,
                    ),
                    width=12,
                    className="mt-4 border",
                )
            ),
            # Assume footer is defined elsewhere
            dbc.Row(dbc.Col(footer)),
        ],
        fluid=True,
    )
