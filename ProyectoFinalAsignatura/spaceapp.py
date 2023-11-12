from dash import Dash, html, dcc, Input, Output, State
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
                    )],
                    width=2,
                ),  # Adjust width as needed
                dbc.Col(dcc.Graph(id="bar-chart"), width=10),  # Adjust width as needed
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


@app.callback(Output("bar-chart", "figure"), [Input("status-selector", "value"), Input("gender-selector", "value")])
def update_chart(selected_status, selected_gender):
    filtered_df = df[df["Status"].isin(selected_status)]
    filtered_df = filtered_df[filtered_df["Gender"].isin(selected_gender)]
    
    grouped_df = (
        filtered_df.groupby(["Year Interval", "Status"])
        .size()
        .reset_index(name="Count")
    )
    fig = px.bar(
        grouped_df,
        x="Year Interval",
        y="Count",
        color="Status",
        barmode="group",
        title="Numero de Astronautas por rango a través de los años",
    )
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
