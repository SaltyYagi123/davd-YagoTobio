from dash import Dash
import dash_bootstrap_components as dbc
from layout import create_layout
from data_processing import load_and_preprocess_data_astronauts, load_and_preprocess_data_missions, generate_wordcloud
from callbacks import  astronaut_callbacks, mission_time_series_callback, mission_3d_scatter_callback

app = Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO, dbc.icons.FONT_AWESOME])
server = app.server

df_space_missions, missions_per_country, grouped_df = load_and_preprocess_data_missions("assets/space_missions.csv")
df_astronauts, major_counts, state_counts = load_and_preprocess_data_astronauts("assets/astronauts.csv")
wordcloud_image = generate_wordcloud(df_astronauts)
app.layout = create_layout(df_astronauts, df_space_missions, state_counts, major_counts, wordcloud_image, missions_per_country, grouped_df)

astronaut_callbacks(app, df_astronauts)
mission_time_series_callback(app, df_space_missions)
mission_3d_scatter_callback(app, df_space_missions)

if __name__ == "__main__":
    app.run_server(debug=False)
