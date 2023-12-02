from dash import Output, Input, State
import plotly.express as px
from data_processing import categorize_major
# Import other necessary modules


def astronaut_callbacks(app, df_astronauts):
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
        filtered_df = df_astronauts[
            (df_astronauts["Year"] >= selected_year_range[0]) & (df_astronauts["Year"] <= selected_year_range[1])
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

def mission_time_series_callback(app, df_space_missions):
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
        return fig

def mission_3d_scatter_callback(app, df_space_missions):
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

