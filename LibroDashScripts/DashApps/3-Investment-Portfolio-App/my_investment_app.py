# Library Imports
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go  # Instead of plotly express
import pandas as pd

# * Stylesheet and app name
app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB, dbc.icons.FONT_AWESOME])

# Returns of three types:
# 1. 3-month US Treasury Bill
# 2. The 10-year US Treasury Bond
# 3. S&P 500
# 4. BAA Corp bond
# 5. Inflation

df = pd.read_csv("assets/historic.csv")
print(df.head())

MAX_YR = df.Year.max()  # Graph ranges - Global Variables
MIN_YR = df.Year.min()
START_YR = 2007

COLORS = { #Dictionary for component stocks
    "cash": "#3cb521",
    "bonds": "#fd7e14",
    "stocks": "#446e9b",
    "inflation": "#cd0200",
    "background": "whitesmoke",
}

# * Components
# * Aqui tenemos que pensar de manera inversa. Bottom-up approach. 
# ? - 1. Tabs - 3 tab structure. Learn, play, results. Each contains their display, id and label

# ! - Markdown Components: 
datasource_text = dcc.Markdown(
    """
    [Data source:](http://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html)
    Historical Returns on Stocks, Bonds and Bills from NYU Stern School of
    Business
    """
)

asset_allocation_text = dcc.Markdown(
    """
> **Asset allocation** is one of the main factors that drive portfolio risk and returns.   Play with the app and see for yourself!

> Change the allocation to cash, bonds and stocks on the sliders and see how your portfolio performs over time in the graph.
  Try entering different time periods and dollar amounts too.
"""
)

learn_text = dcc.Markdown(
    """
    Past performance certainly does not determine future results, but you can still
    learn a lot by reviewing how various asset classes have performed over time.

    Use the sliders to change the asset allocation (how much you invest in cash vs
    bonds vs stock) and see how this affects your returns.

    Note that the results shown in "My Portfolio" assumes rebalancing was done at
    the beginning of every year.  Also, this information is based on the S&P 500 index
    as a proxy for "stocks", the 10 year US Treasury Bond for "bonds" and the 3 month
    US Treasury Bill for "cash."  Your results of course,  would be different based
    on your actual holdings.

    This is intended to help you determine your investment philosophy and understand
    what sort of risks and returns you might see for each asset category.

    The  data is from [Aswath Damodaran](http://people.stern.nyu.edu/adamodar/New_Home_Page/home.htm)
    who teaches  corporate finance and valuation at the Stern School of Business
    at New York University.

    Check out his excellent on-line course in
    [Investment Philosophies.](http://people.stern.nyu.edu/adamodar/New_Home_Page/webcastinvphil.htm)
    """
)

cagr_text = dcc.Markdown(
    """
    (CAGR) is the compound annual growth rate.  It measures the rate of return for an investment over a period of time, 
    such as 5 or 10 years. The CAGR is also called a "smoothed" rate of return because it measures the growth of
     an investment as if it had grown at a steady rate on an annually compounded basis.
    """
)

footer = html.Div(
    dcc.Markdown(
        """
         This information is intended solely as general information for educational
        and entertainment purposes only and is not a substitute for professional advice and
        services from qualified financial services providers familiar with your financial
        situation.    
        """
    ),
    className="p-2 mt-5 bg-primary text-white small",
)

# ! C1: Tab 1 
learn_card = dbc.Card(
    [
        dbc.CardHeader("An Introduction to Asset Allocation"),
        dbc.CardBody(learn_text),
    ], className="mt-4"
)

# ! C1: Tab 2
# * C1: Play Tab - 2. Sliders
slider_card = dbc.Card(
    [
        html.H4("First set cash allocation %:", className="card-title"),
        dcc.Slider(
            id="cash", 
            marks = {i:f"{i}%" for i in range(0,101, 10)},
            min = 0, 
            max = 100, 
            step = 5, # ! What this mean? 
            value = 10, # Default value
            included = False, # ! What this mean?
        ), 
        html.H4("Then set stock allocation %:", className="card-title mt-3",),
        html.Div("(The rest will be left as bonds)", className="card-title"),
        dcc.Slider(
            id = "stock_bond", 
            marks = {i:f"{i}" for i in range(0, 91, 10)}, 
            min = 0,
            max = 90, 
            step = 5, 
            value = 50, 
            included = False, # Specify the discrete value not a range. 
        ),
    ], 
    body = True, 
    className = "mt-4",
)

# * C1: Play Tab - 3. Inputs 
start_amount = dbc.InputGroup(
    [
        dbc.InputGroupText("Start Amount $"),
        dbc.Input(
            id="starting_amount",
            placeholder="Min $10",
            type="number",
            min=10,
            value=10000,
        ),
    ],
    className="mb-3",
)
start_year = dbc.InputGroup(
    [
        dbc.InputGroupText("Start Year"), 
        dbc.Input(
            id = "start_yr", 
            placeholder = f"min {MIN_YR} max {MAX_YR}", 
            type =  "number", 
            min = MIN_YR, 
            max = MAX_YR, 
            value = START_YR 
        )
    ], className="mb-3"
)
number_of_years = dbc.InputGroup(
    [
        dbc.InputGroupText("Number of Years:"),
        dbc.Input(
            id="planning_time",
            placeholder="# yrs",
            type="number",
            min=1,
            value=MAX_YR - START_YR + 1,
        ),
    ],
    className="mb-3",
)
end_amount = dbc.InputGroup(
    [
        dbc.InputGroupText("Ending Amount"),
        dbc.Input(id = "ending_amount", disabled = True, className = "text-black"),
    ],
    className="mb-3",
)
# Includes the hover tool tips component
rate_of_return = dbc.InputGroup(
    [
        dbc.InputGroupText(
            "Rate of Return(CAGR)",
            id="tooltip_target",
            className="text-decoration-underline",
        ),
        dbc.Input(id="cagr", disabled=True, className="text-black"),
        dbc.Tooltip(cagr_text, target="tooltip_target"),
    ],
    className="mb-3",
)

# * C1: Play Tab - 4. Select key time periods
time_period_data = [
    {
        "label": f"2007-2008: Great Financial Crisis to {MAX_YR}",
        "start_yr": 2007,
        "planning_time": MAX_YR - START_YR + 1,
    },
    {
        "label": "1999-2010: The decade including 2000 Dotcom Bubble peak",
        "start_yr": 1999,
        "planning_time": 10,
    },
    {
        "label": "1969-1979:  The 1970s Energy Crisis",
        "start_yr": 1970,
        "planning_time": 10,
    },
    {
        "label": "1929-1948:  The 20 years following the start of the Great Depression",
        "start_yr": 1929,
        "planning_time": 20,
    },
    {
        "label": f"{MIN_YR}-{MAX_YR}",
        "start_yr": "1928",
        "planning_time": MAX_YR - MIN_YR + 1,
    },
    {
        "label": f"2020 - {MAX_YR}: COVID-19 Pandemic", 
        "start_yr": "2020", 
        "planning_time": MAX_YR - 2020,
    }
]

time_period_card = dbc.Card(
    [
        html.H4(
            "Or select a time period:",
            className="card-title",
        ),
        dbc.RadioItems(
            id="time_period",
            options=[
                {"label": period["label"], "value": i}
                for i, period in enumerate(time_period_data)
            ],
            value=0,
            labelClassName="mb-2",
        ),
    ],
    body = True,
    className = "mt-4",
)

# * C1: Play Tab Structure
input_groups = html.Div(
    [start_amount, start_year, number_of_years, end_amount, rate_of_return], 
    className="mt-4 p-4",
)

# ! C1: Tab 3
# No incluimos aqui los datos porque se cambiarán en el callback function 
total_returns_table = dash_table.DataTable(
    id="total_returns", 
    columns = [{"id":"Year", "name":"Year", "type":"text"}] + [{"id":col, "name":col, "type":"numeric", "format":{"specifier":"$,.0f"}} for col in ["Cash", "Bonds", "Stocks", "Total"]],
    page_size=15, 
    style_table={"overflowX":"scroll"}, 
)

# En cambio aquí son datos fijos
annual_returns_pct_table = dash_table.DataTable(
    id="annual_returns_pct",
    columns=(
        [{"id": "Year", "name": "Year", "type": "text"}]
        + [
            {"id": col, "name": col, "type": "numeric", "format": {"specifier": ".1%"}}
            for col in df.columns[1:] # in order to exclude the year. 
        ]
    ),
    data=df.to_dict("records"), #This transforms it into a dict. But why this does not go into the other?
    sort_action="native",
    page_size=15,
    style_table={"overflowX": "scroll"},
)

# * C1: Tab 3 Structure defined in tabs
results_card = dbc.Card(
    [
        dbc.CardHeader("My Portfolio Returns - Rebalanced Annually"),
        html.Div(total_returns_table),
    ],
    className="mt-4",
)

data_source_card = dbc.Card(
    [
        dbc.CardHeader("Source Data: Annual Total Returns"),
        html.Div(annual_returns_pct_table),
    ],
    className="mt-4",
)

# ! C1: Tabs Structure
tabs = dbc.Tabs(
    [
        dbc.Tab(learn_card, tab_id="tab-1", label = "Learn"), 
        dbc.Tab(
            [asset_allocation_text, slider_card, input_groups, time_period_card],
            tab_id="tab-2", 
            label="Play", 
            className="pb-4",
        ),
        dbc.Tab([results_card, data_source_card], tab_id="tab-3", label="Results"),
    ],
    id = "tabs", 
    active_tab = "tab-2", #? - Enseña cual es la primera pestaña en abrirse. 
)

# ! C2 -  Graph layouts 
# * Pie chart
# Using normal Plotly not express 
def make_pie(slider_input, title):
    fig = go.Figure(
        data=[
            go.Pie(
                labels = ["Cash", "Bonds", "Stocks"], 
                values = slider_input, 
                textinfo= "label+percent", 
                textposition= "inside", 
                marker={"colors": [COLORS["cash"], COLORS["bonds"], COLORS["stocks"]]}, 
                sort = False, # We want the colour for each asset to stay the same, that's why we set it as false. 
                hoverinfo="none",
            )
        ]
    )

    # To update in the callback 
    fig.update_layout(
        title_text = title, 
        title_x = 0.5, 
        margin = dict(b=25, t=75, l=35, r=25), 
        height = 325, 
        paper_bgcolor = COLORS["background"],
    )

    return fig 

def make_line_chart(dff):
    start = dff.loc[1,"Year"]
    yrs = dff["Year"].size - 1 

    dtick = 1 if yrs < 16 else 2 if yrs in range(16,30) else 5 # Ajuste de los tiempos 
    # Si el numero de años es menor a 16, dtick = 1, si en cambio si esta entre 16-30 dtick = 2, si ninguno 5. 
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dff["Year"],
            y=dff["all_cash"],
            name="All Cash",
            marker_color=COLORS["cash"],
        )
    )
    fig.add_trace(
        go.Scatter(
            x=dff["Year"],
            y=dff["all_bonds"],
            name="All Bonds (10yr T.Bonds)",
            marker_color=COLORS["bonds"],
        )
    )
    fig.add_trace(
        go.Scatter(
            x=dff["Year"],
            y=dff["all_stocks"],
            name="All Stocks (S&P500)",
            marker_color=COLORS["stocks"],
        )
    )
    fig.add_trace(
        go.Scatter(
            x=dff["Year"],
            y=dff["Total"],
            name="My Portfolio",
            marker_color="black",
            line=dict(width=6, dash="dot"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=dff["Year"],
            y=dff["inflation_only"],
            name="Inflation",
            visible=True,
            marker_color=COLORS["inflation"],
        )
    )
    # Para el callback. Aqui establecemos las partes que no tienen que ver con los datos. 
    fig.update_layout(
        title = f"Returns for {yrs} years staring {start}", 
        template = "none", 
        showlegend = True, 
        legend = dict(x=0.01, y = 0.99), 
        height = 400, 
        margin = dict(l=40, r= 10, t = 60, b = 55), 
        yaxis = dict(tickprefix = "$", fixedrange = True), # No Zoom  
        xaxis = dict(title = "Year Ended", fixedrange = True, dtick = dtick)
    )

# ! - APP LAYOUT 
app.layout = dbc.Container(
    # 1st row - Blue Header Bar [One column that spans the entire width (12)]
    # 2nd row - 2 columns. Left column has the tabs which contain the user input tabs
    #         - Right column has the primary chart outputs. The widths are both set to twelve, for no zoom in on small screens. 
    #         - That's why width is = 12. Then on large screen we have the lg parameters which let us see them side by side. 
    # 3rd row - El footer. Contracts, legal , maps, etc...
    [
        dbc.Row(
            dbc.Col(
                html.H2(
                    "Asset Allocation Visualizer", 
                    className="text-center bg-primary text-white p-2"
                ),
            )
        ),
        dbc.Row(
            [
                dbc.Col(tabs, width=12, lg=5, className="mt-4 border"), 
                dbc.Col(
                    [
                        dcc.Graph(id="allocation_pie_chart", className="mb-2"), 
                        dcc.Graph(id="returns_chart", className="pb-4"), 
                        html.Hr(), 
                        html.Div(id="summary_table"), 
                        html.H6(datasource_text, className="my-2"),
                    ], 
                    width=12, 
                    lg=7, 
                    className="pt-4", 
                ), 
            ], 
            className="ms-1"
        ),
        dbc.Row(
            dbc.Col(footer)
        )
    ],
    fluid = True # Ocupa el area posible. Bueno para responsive design 
)

# ! - Calculation of the investment returns (Backtest) / (CAGR)

def backtest(stocks, cash, start_bal, nper, start_yr):
    """calculates the investment returns for user selected asset allocation,
    rebalanced annually and returns a dataframe
    """

    end_yr = start_yr + nper - 1
    cash_allocation = cash / 100
    stocks_allocation = stocks / 100
    bonds_allocation = (100 - stocks - cash) / 100

    # Select time period - since data is for year end, include year prior
    # for start ie year[0]
    dff = df[(df.Year >= start_yr - 1) & (df.Year <= end_yr)].set_index(
        "Year", drop=False
    )
    dff["Year"] = dff["Year"].astype(int)

    # add columns for My Portfolio returns
    dff["Cash"] = cash_allocation * start_bal
    dff["Bonds"] = bonds_allocation * start_bal
    dff["Stocks"] = stocks_allocation * start_bal
    dff["Total"] = start_bal
    dff["Rebalance"] = True

    # calculate My Portfolio returns
    for yr in dff.Year + 1:
        if yr <= end_yr:
            # Rebalance at the beginning of the period by reallocating
            # last period's total ending balance
            if dff.loc[yr, "Rebalance"]:
                dff.loc[yr, "Cash"] = dff.loc[yr - 1, "Total"] * cash_allocation
                dff.loc[yr, "Stocks"] = dff.loc[yr - 1, "Total"] * stocks_allocation
                dff.loc[yr, "Bonds"] = dff.loc[yr - 1, "Total"] * bonds_allocation

            # calculate this period's  returns
            dff.loc[yr, "Cash"] = dff.loc[yr, "Cash"] * (
                1 + dff.loc[yr, "3-mon T.Bill"]
            )
            dff.loc[yr, "Stocks"] = dff.loc[yr, "Stocks"] * (1 + dff.loc[yr, "S&P 500"])
            dff.loc[yr, "Bonds"] = dff.loc[yr, "Bonds"] * (
                1 + dff.loc[yr, "10yr T.Bond"]
            )
            dff.loc[yr, "Total"] = dff.loc[yr, ["Cash", "Bonds", "Stocks"]].sum()

    dff = dff.reset_index(drop=True)
    columns = ["Cash", "Stocks", "Bonds", "Total"]
    dff[columns] = dff[columns].round(0)

    # create columns for when portfolio is all cash, all bonds or  all stocks,
    #   include inflation too
    #
    # create new df that starts in yr 1 rather than yr 0
    dff1 = (dff[(dff.Year >= start_yr) & (dff.Year <= end_yr)]).copy()
    #
    # calculate the returns in new df:
    columns = ["all_cash", "all_bonds", "all_stocks", "inflation_only"]
    annual_returns = ["3-mon T.Bill", "10yr T.Bond", "S&P 500", "Inflation"]
    for col, return_pct in zip(columns, annual_returns):
        dff1[col] = round(start_bal * (1 + (1 + dff1[return_pct]).cumprod() - 1), 0)
    #
    # select columns in the new df to merge with original
    dff1 = dff1[["Year"] + columns]
    dff = dff.merge(dff1, how="left")
    # fill in the starting balance for year[0]
    dff.loc[0, columns] = start_bal
    return dff


def cagr(dff):
    """calculate Compound Annual Growth Rate for a series and returns a formated string"""

    start_bal = dff.iat[0]
    end_bal = dff.iat[-1]
    planning_time = len(dff) - 1
    cagr_result = ((end_bal / start_bal) ** (1 / planning_time)) - 1
    return f"{cagr_result:.1%}"


def worst(dff, asset):
    """calculate worst returns for asset in selected period returns formated string"""

    worst_yr_loss = min(dff[asset])
    worst_yr = dff.loc[dff[asset] == worst_yr_loss, "Year"].iloc[0]
    return f"{worst_yr_loss:.1%} in {worst_yr}"

def make_summary_table(dff):
    """Make html table to show cagr and  best and worst periods"""

    table_class = "h5 text-body text-nowrap"
    cash = html.Span(
        [html.I(className="fa fa-money-bill-alt"), " Cash"], className=table_class
    )
    bonds = html.Span(
        [html.I(className="fa fa-handshake"), " Bonds"], className=table_class
    )
    stocks = html.Span(
        [html.I(className="fa fa-industry"), " Stocks"], className=table_class
    )
    inflation = html.Span(
        [html.I(className="fa fa-ambulance"), " Inflation"], className=table_class
    )

    start_yr = dff["Year"].iat[0]
    end_yr = dff["Year"].iat[-1]

    df_table = pd.DataFrame(
        {
            "": [cash, bonds, stocks, inflation],
            f"Rate of Return (CAGR) from {start_yr} to {end_yr}": [
                cagr(dff["all_cash"]),
                cagr(dff["all_bonds"]),
                cagr(dff["all_stocks"]),
                cagr(dff["inflation_only"]),
            ],
            f"Worst 1 Year Return": [
                worst(dff, "3-mon T.Bill"),
                worst(dff, "10yr T.Bond"),
                worst(dff, "S&P 500"),
                "",
            ],
        }
    )
    return dbc.Table.from_dataframe(df_table, bordered=True, hover=True)



# ! - CALLBACKS 
# ? - Callback #1 -> Update the pie chart 
@app.callback(
    Output("allocation_pie_chart", "figure"),  # Output -> Pie Chart
    Input("stock_bond", "value"),              # Input -> stock_bond slider 
    Input("cash", "value"),                    # Input -> Cash slider 
)

def update_pie(stocks, cash): 
    bonds = 100 - stocks - cash
    slider_input = [cash, bonds, stocks]

    if stocks >= 70: 
        investment_style = "Aggressive"
    elif stocks <= 30: 
        investment_style = "Conservative"
    else: 
        investment_style = "Moderate"

    figure = make_pie(slider_input, investment_style + " Asset Allocation")
    return figure # Output the new pie chart. 

# ? - Callback #2 -> Change the slider range, so that it doesn't exceed 100% and everything is in sync. 
@app.callback(
    Output("stock_bond", "max"),   # Max allowed for stock
    Output("stock_bond", "marks"), # Readjustment of slider marks
    Output("stock_bond", "value"), # In case of out of range 
    Input("cash", "value"),        # We don't make this a state, because we want real time updates
    State("stock_bond", "value"),  # Stock Value
)

def update_stock_slider(cash, initial_stock_value): 
    max_slider = 100 - int(cash)
    stocks = min(max_slider, initial_stock_value)

    # Format the new slider scale: 
    if max_slider > 50: 
        marks_slider = {i:f"{i}%" for i in range(0, max_slider + 1, 10)}
    elif max_slider <= 15: 
        marks_slider = {i:f"{i}%" for i in range(0, max_slider + 1, 1)}
    else: 
        marks_slider = {i:f"{i}%" for i in range(0, max_slider + 1, 5)}

    return max_slider, marks_slider, stocks

# ? - Callback #3 -> Circular callback and synched componets. Workhorse of the app.
# ? - Slider changes responsible for: Data table, line chart, summary table, ending amount + rate of return. 

@app.callback(
    Output("total_returns", "data"),     # Table of total returns
    Output("returns_chart", "figure"),   # Line graph of total returns 
    Output("summary_table", "children"), # Summary table of ROI
    Output("ending_amount", "value"),    # Final Values
    Output("cagr", "value"),             # Compound Annual Growth Rate
    Input("stock_bond", "value"),        # How much in stock %
    Input("cash", "value"),              # How much in cash %
    Input("starting_amount", "value"),   # Initial Deposit 
    Input("planning_time", "value"),     # Planning time
    Input("start_yr", "value"),          # Yearly expense 
)
#5 inputs
def update_totals(stocks, cash, start_bal, planning_time , start_yr): 
    # Ponemos los defaults para inputs invalidos o los iniciales al arrancar. 
    start_bal = 10 if start_bal is None else start_bal
    planning_time = 1 if planning_time is None else planning_time  
    start_yr = MIN_YR if start_yr is None else int(start_yr)

    # Calculate el tiempo valido desde el start year 
    max_time = MAX_YR + 1 - start_yr
    planning_time = min(max_time, planning_time)
    if start_yr + planning_time > MAX_YR:
        start_yr = min(df.iloc[-planning_time, 0], MAX_YR) # 0  es la columna año. Aqui estamos seleccionando el año más temprano posible. 

    # Creamos una base de datos para el retorno de inversion 
    dff = backtest(stocks, cash, start_bal, planning_time, start_yr)

    # Creata datos para el dataframe 
    data = dff.to_dict("records") 

    fig = make_line_chart(dff)
    summary_table = make_summary_table(dff)

    # Format ending balance
    ending_amount = f"${dff['Total'].iloc[-1]:0,.0f}"

    # Calculo del CAGR 
    ending_cagr = cagr(dff["Total"])

    return data, fig, summary_table, ending_amount, ending_cagr

if __name__ == '__main__':
    app.run_server(debug=True)