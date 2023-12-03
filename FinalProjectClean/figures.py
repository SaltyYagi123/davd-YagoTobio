import plotly.express as px 
import plotly.graph_objs as go
import pandas as pd
from plotly.subplots import make_subplots
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import xgboost as xgb

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

def create_group_bar_chart(df):
    encoder = LabelEncoder()
    encoder.fit(df['Status Mission'])
    colors = {0 : 'red', 1 : 'Orange', 2 : 'Yellow', 3 : 'Green'}
    fig = make_subplots(rows = 4 ,cols = 4,subplot_titles=df['Country'].unique())

    for i, country in enumerate(df['Country'].unique()):
        counts = df[df['Country'] == country]['Status Mission'].value_counts(normalize = True) * 100
        color = [colors[x] for x in encoder.transform(counts.index)]
        trace = go.Bar(x = counts.index, y = counts.values, name = country,showlegend=False,marker={'color' : color})
        fig.add_trace(trace, row = (i//4)+1, col = (i%4)+1)
    
    fig.update_layout(margin=dict(l=80, r=80, t=50, b=10),
                    title = { 'text' : '<b>Countries and Mission Status</b>', 'x' : 0.5},title_font_color= '#cacaca',
                    height = 800,
                    width = 850)
                    
    for i in range(1,5):
        fig.update_yaxes(title_text = 'Percentage',row = i, col = 1)
    
    return fig

def company_sunburst(df):

    fig = px.sunburst(df, path = ['Status Mission', 'Country'])
    fig.update_layout(title = { 'text' : '<b>Countries and Mission Status</b>', 'x' : 0.5})
    return fig

def company_success_bar_chart(df):
    # Ensure the Series is of type float to accommodate percentage values
    successPerc = df[df['Status Mission'] == 'Success'].groupby('Company Name')['Status Mission'].count().astype(float)
    total_missions = df.groupby('Company Name')['Status Mission'].count()
    
    # Calculate the success percentage
    successPerc = (successPerc / total_missions) * 100
    successPerc = successPerc.sort_index()
    
    # Do the same for failure percentage
    FailurePerc = df[df['Status Mission'] == 'Failure'].groupby('Company Name')['Status Mission'].count().astype(float)
    FailurePerc = (FailurePerc / total_missions) * 100
    FailurePerc = FailurePerc.sort_index()

    # Plotting code remains the same
    trace1 = go.Bar(x=successPerc.index, y=successPerc.values, name='Success Rate of Companies', opacity=0.7)
    trace2 = go.Bar(x=FailurePerc.index, y=FailurePerc.values, name='Failure Rate of Companies', opacity=0.7)
    fig = go.Figure([trace1, trace2])
    fig.update_layout(template='plotly_white', margin=dict(l=80, r=80, t=25, b=10),
                      title={'text': '<b>Success and Failure Rates of Companies</b>', 'x': 0.5}, width=1000,
                      yaxis_title='<b>Percentage</b>', xaxis_title='<b>Companies</b>',
                      legend=dict(
                          yanchor="top",
                          y=0.99,
                          xanchor="left",
                          x=0.01
                      ))

    return fig


def treemap_success(df):
    fig = px.treemap(df,path = ['Status Mission','Country','Company Name'])
    fig.update_layout(template = 'ggplot2',margin=dict(l=80, r=80, t=50, b=10),
                    title = { 'text' : '<b>Mission Status,Countries and Companies</b>', 'x' : 0.5})
    return fig

def rocket_effect(df):
    # creating a single list containing the names of the Launch Vehicles
    details = []
    for detail in df.Detail.values:
        d = [x.strip() for x in detail.split('|')]
        for ele in d:
            if('Cosmos' in ele):
                details.append('Cosmos')
            elif('Vostok' in ele):
                details.append('Vostok')
            elif('Tsyklon' in ele):
                details.append('Tsyklon')
            elif('Ariane' in ele):
                details.append('Ariane')
            elif('Atlas' in ele):
                details.append('Atlas')
            elif('Soyuz' in ele):
                details.append('Soyuz')
            elif('Delta' in ele):
                details.append('Delta')
            elif('Titan' in ele):
                details.append('Titan')
            elif('Molniya' in ele):
                details.append('Molniya')
            elif('Zenit' in ele):
                details.append('Zenit')
            elif('Falcon' in ele):
                details.append('Falcon')
            elif('Long March' in ele):
                details.append('Long March')
            elif('PSLV' in ele):
                details.append('PSLV')
            elif('GSLV' in ele):
                details.append('GSLV')
            elif('Thor' in ele):
                details.append('Thor')
            else:
                details.append('Other')
    counts = dict(pd.Series(details).value_counts(sort = True))
    fig = go.Figure(go.Bar(x = list(counts.keys()), y = list(counts.values())))
    fig.update_layout(template = 'ggplot2',margin=dict(l=80, r=80, t=50, b=10),
                    title = { 'text' : '<b>Number of Missions in each type of Launch Vehicle</b>', 'x' : 0.5},
                    yaxis_title = '<b>Number of Missions</b>',xaxis_title = '<b>Launch Vehicle</b>',)
    
    return fig

def failed_missions_calendar(df):
    fig = make_subplots(rows = 3, cols = 1)
    for i, period in enumerate(['year', 'month', 'weekday']):
        data = df[df['Status Mission'] == 'Failure'][period].value_counts().sort_index()
        data = dict((data / df[period].value_counts().sort_index())*100.0)
        mean = sum(data.values()) / len(data)
        if(period == 'year'):
            x = list(data.keys())
        elif(period == 'month'):
            x = ['January', 'February', 'March', 'April', 'May','June', 'July', 'August','September','October', 'November', 'December']
        else:
            x = ['Monday', 'Tuesday', 'Wednesday','Thursday','Friday','Saturday','Sunday']
        trace1 = go.Scatter(x = x, y = list(data.values()),mode = 'lines',text = list(data.keys()),name = f'Failures in each {period}',connectgaps = False)
        trace2 = go.Scatter(x = x, y = [mean]*len(data), mode = 'lines',showlegend=False,name = f'Mean failures over the {period}s',line = {'dash':'dash','color':
                                                                                                                                        'grey'})
        fig.append_trace(trace1, row = i+1, col = 1)
        fig.append_trace(trace2, row = i+1, col = 1)
    fig.update_layout(template = 'simple_white',height = 600,
                    title = { 'text' : '<b>Failed Missions as a percentage of total missions in that period</b>', 'x' : 0.5})
    for i in range(1,4):
        fig.update_yaxes(title_text = '<b>Percentage</b>',row = i, col = 1)
    
    return fig

def average_mission_cost(df):
    df[' Rocket'] = df[' Rocket'].apply(lambda x: str(x).replace(',',''))
    df[' Rocket'] = df[' Rocket'].astype('float64')
    df[' Rocket'] = df[' Rocket'].fillna(0)

    costDict = dict(df[df[' Rocket'] > 0].groupby('year')[' Rocket'].mean())
    fig = go.Figure(go.Scatter(x = list(costDict.keys()), y = list(costDict.values()), yaxis = 'y2',mode = 'lines',showlegend=False,name = 'Average Mission Cost Over the years'))
    fig.update_layout(margin=dict(l=80, r=80, t=50, b=10),
                    title = { 'text' : '<b>Average Mission Cost Over the years</b>', 'x' : 0.5},
                    yaxis_title = '<b>Cost of Mission in Million Dollars</b>',xaxis_title = '<b>Year of Launch</b>',)
    return fig

def average_mission_cost_countries(df):
    fig = px.scatter(df[df[' Rocket'].between(1,4999)],x = 'year', y = 'Country', color = 'Status Mission',size = ' Rocket', size_max=30)
    fig.update_layout(template = 'simple_white',margin=dict(l=80, r=80, t=50, b=10),
                    title = { 'text' : '<b>Average Mission Cost Over the years For Various Countries</b>', 'x' : 0.5})

    return fig 

def average_mission_cost_companies(df):
    fig = px.scatter(df[df[' Rocket'].between(1,4999)],x = 'year', y = 'Company Name',color = 'Status Mission',size = ' Rocket',size_max = 30)
    fig.update_layout(template = 'simple_white',margin=dict(l=80, r=80, t=50, b=10),
                    title = { 'text' : '<b>Average Mission Cost Over the years For Various Companies</b>', 'x' : 0.5})

    return fig

def xgboost_importance_factors(df):
    # Assuming 'df' is your DataFrame
    df['Target'] = (~(df['Status Mission'] == 'Success')).astype('int32')
    # Select features and target
    X = df[['Company Name', 'Country', 'year', 'month', 'weekday']]  # Assuming ' Rocket' is either dropped or correctly processed elsewhere
    y = df['Target']

    # Initialize the LabelEncoder
    encoder = LabelEncoder()

    # Apply the encoder to each categorical column
    X['Company Name'] = encoder.fit_transform(df['Company Name'])
    X['Country'] = encoder.fit_transform(df['Country'])

    # Splitting the dataset into the Training set and Test set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)

    # Initialize the classifier
    classifier_xgb = xgb.XGBClassifier(random_state=0, n_jobs=-1, max_depth=5)

    # Fit the classifier to the training data
    classifier_xgb.fit(X_train, y_train)

    feature_importance_xgb = classifier_xgb.get_booster().get_fscore()

    trace = go.Bar(x = list(feature_importance_xgb.values()), y = list(feature_importance_xgb.keys()),orientation='h')
    fig = go.Figure([trace])
    fig.update_layout(template = 'simple_white',margin=dict(l=80, r=80, t=50, b=10),
                    title = { 'text' : '<b>Feature Importance</b>', 'x' : 0.5},
                    yaxis_title = '<b>Features</b>',xaxis_title = '<b>F Score</b>')

    return fig