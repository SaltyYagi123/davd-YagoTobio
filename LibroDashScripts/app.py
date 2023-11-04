from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"], 
    "Amount": [4,1,2,2,4,5], 
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

app = Dash(__name__)


fig = px.bar(df, x="Fruit", y = "Amount", color = "City", barmode = "group")


app.layout = html.Div(children=[
    html.H1(children='Hello Dash'), 
    html.Div(children='''
        Dash: A web application framework for your data. 
    '''), 
    dcc.Graph(
        id='example-graph', 
        figure=fig
    )
])

#@callback(
#    Output('graph-content', 'figure'),
#    Input('dropdown-selection', 'value')
#)
#def update_graph(value):
#    dff = df[df.country==value]
#    return px.line(dff, x='year', y='pop')

if __name__ == '__main__':
    app.run(debug=True)
