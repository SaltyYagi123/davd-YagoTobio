import plotly.express as px 

def create_choropleth_figure(df, title, locations, locationmode, color, scope=None):
    """
    Create a choropleth figure using Plotly Express.

    Parameters:
    df (DataFrame): The data frame to use for the plot.
    title (str): The title of the plot.
    locations (str): The column in DataFrame to be used as locations.
    locationmode (str): The mode for the locations.
    color (str): The column in DataFrame to define the color of the plot.
    scope (str, optional): The scope of the choropleth. Default is None.

    Returns:
    plotly.graph_objs._figure.Figure: The choropleth figure.
    """
    fig = px.choropleth(
        df,
        locations=locations,
        locationmode=locationmode,
        color=color,
        title=title,
        scope=scope,
    )

    return fig

def create_sunburst(df,inner_circle,outer_circle, title):
    """
    Create a sunburst figure using Plotly Express.

    Parameters:
    df (DataFrame): The data frame to use for the plot.
    inner_circle (str): The column for the inner circle of the sunburst.
    outer_circle (str): The column for the outer circle of the sunburst.
    title (str): The title of the plot.

    Returns:
    plotly.graph_objs._figure.Figure: The sunburst figure.

    """
    fig = px.sunburst( 
        df, 
        path=[inner_circle, outer_circle], 
        values = "Count", 
        title=title, 
        custom_data=["Percentage"],
    )

    # Update hovertemplate to show percentages
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{customdata[0]:.2f}%"
    )

    return fig

def create_scatter_3d(df, x, y, z, color, title):
    """
    Create a 3D scatter plot using Plotly Express.

    Parameters:
    df (DataFrame): The data frame to use for the plot.
    x, y, z (str): The columns in DataFrame for the x, y, and z axes.
    color (str): The column in DataFrame to define the color of the points.
    title (str): The title of the plot.

    Returns:
    plotly.graph_objs._figure.Figure: The 3D scatter plot figure.
    """

    fig = px.scatter_3d(
        df,
        x=x,
        y=y,  # You might need to map this to a numerical scale
        z=z,  # Same as above
        color=color,  # Could be another categorical variable
        title=title,
    )
    return fig

def create_scatterplot_major(df,x,y,size,color,title):
    """
    Create a scatter plot for major categories using Plotly Express.

    Parameters:
    df (DataFrame): The data frame to use for the plot.
    x, y (str): The columns in DataFrame for the x and y axes.
    size (str): The column in DataFrame to define the size of the points.
    color (str): The column in DataFrame to define the color of the points.
    title (str): The title of the plot.

    Returns:
    plotly.graph_objs._figure.Figure: The scatter plot figure.
    """
    fig = px.scatter(
        df, 
        x = x, 
        y = y, 
        size = size, 
        color = color, 
        title = title
    )

    fig.update_layout(xaxis_tickangle=-45)
    fig.update_traces(
        marker=dict(opacity=0.7)
    )  # Adjust opacity for better visualization

    return fig
