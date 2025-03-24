# -*- coding: utf-8 -*-
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import os
import numpy as np
# TODO: issue: line graph only shows when i press the "raw" tab. i want it to display all the time, like the bar chart.
# TODO: start ammount is not displayed from the year-- opps
# TODO: somewhere in here there is a divide by 0 error...
# TODO: currently, the percentages on the bar chart are the selected number out of the total income. it needs to be selected number out of the income-housing/12

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.LUX, dbc.icons.FONT_AWESOME],
)

# Load datasets
income_df = pd.read_csv("data/income.csv")
house_df = pd.read_csv("data/house.csv")
chicken_df = pd.read_csv("data/chicken.csv")
gas_df = pd.read_csv("data/gas.csv")
dfs = [income_df, house_df, chicken_df, gas_df]
print(income_df.columns)

# Convert 'observation_date' to 'year' and drop 'observation_date' while keeping 'year'
for df in dfs:
    if "observation_date" in df.columns:
        df["observation_date"] = pd.to_datetime(df["observation_date"])
        df["year"] = df["observation_date"].dt.year
        df.drop(columns=["observation_date"], inplace=True)  # Drop to prevent merge conflicts

# Merge all datasets on 'year', keeping 'year' in the final DataFrame
df = income_df.merge(chicken_df, on="year", how="inner") \
             .merge(house_df, on="year", how="inner") \
             .merge(gas_df, on="year", how="inner")
print(df.head())

# Convert to Dash DataTable format
data_records = df.to_dict("records")

MAX_YR = gas_df.year.max()
MIN_YR = gas_df.year.min()

COLORS = {
    "income": "#3cb521",
    "house": "#fd7e14",
    "chicken": "#446e9b",
    "gas": "#cd0200",
}

"""
==========================================================================
Helper functions to calculate saving results and stuff
"""

def get_starting_amount(selected_year):

    value = income_df.loc[income_df["year"] == selected_year, "Income"]
    if not value.empty:
        print("yearly income", value.iloc[0])

        print("STARTING AMMOUNT",value.iloc[0] / 12 )
        return value.iloc[0] / 12

    else:
        return 0

# Implement cost_per_mile function
def cost_per_mile(selected_year):
    cost = gas_df.loc[gas_df["year"] == selected_year, "GASREGCOVW"]
    if not cost.empty:
        print("cost per mile", cost)
        return cost.iloc[0] / 25  # Average MPG is 25

    else:
        return 0

# Implement cost_per_meal function
def cost_per_meal(selected_year):
    cost = chicken_df.loc[chicken_df["year"] == selected_year, "chicken"]
    if not cost.empty:
        return cost.iloc[0] / 3  # Average meal is 1/3 of the total cost
    else:
        return 0

"""
==========================================================================
Markdown Text
"""
datasource_text = dcc.Markdown(
    """
    [Data source:](https://fred.stlouisfed.org/)
    30 years of data showing the average household income, price of a home, price of chicken, and cost of gas per gallon. 
    """
)

income_allocation_text = dcc.Markdown(
    """
> **Income allocation** is a way to explore, given the average income, what someone can afford.   Play with the app and see for yourself!

> Change the allocation of chicken and gas on the sliders and see how your income supports you over time in the graph.
  Try entering different time periods and dollar amounts too.
"""
)

learn_text = dcc.Markdown(
    """
    This data is not seasonally adjusted, so that is a factor in the differences over time. Because it's constant throughout all the data being used, it should be fine. 

    Past cost of living does not necessarily determine future results, but you can still
    learn a lot by reviewing how different components have changed over time, and make general assumptions of where the trend will go in the future. 

    Use the sliders to change the income allocation (how much you spend on gas or chicken) 
    and see how much income you have leftover-- if any.

    This is intended to help you understand how the average income in the US has been able to support the average household over time. 

    The data is from FRED, more details can be found in the README section of this project. 
    """
)

footer = html.Div(
    dcc.Markdown(
        """
         This information is intended solely as general information for educational
        and entertainment purposes only and is not a substitute for professional advice and
        services from qualified government services providers familiar with your financial
        situation.
        """
    ),
    className="p-2 mt-5 bg-primary text-white small",
)

"""
==========================================================================
Tables
"""
# Define Dash DataTable
income_table = dash_table.DataTable(
    id="income_table",
    columns=[{"id": "year", "name": "year", "type": "numeric"}]  # Year column
    + [
        {"id": col, "name": col, "type": "numeric", "format": {"specifier": "$,.0f"}}
        for col in ["Income", "house", "chicken", "gas"]
    ],  # Money formatting
    data=data_records,  # Insert processed data
    page_size=15,
    style_table={"overflowX": "scroll"},
)

"""
==========================================================================
Figures
"""

def make_bar(slider_input, title):
    sorted_indices = sorted(range(len(slider_input)), key=lambda k: slider_input[k], reverse=True)
    sorted_slider_input = [slider_input[i] for i in sorted_indices]
    sorted_labels = ["Chicken (lbs)", "Gas (gallons)", "Savings"]
    sorted_labels = [sorted_labels[i] for i in sorted_indices]

    total = sum(sorted_slider_input) # TODO: this should not be the sorted slider input. it should be the yearly income
    percentages = [(value / total) * 100 for value in sorted_slider_input]

    shades_of_blue = ["#1f77b4", "#4d88ff", "#a6c6ff"]

    fig = go.Figure()

    for i, label in enumerate(sorted_labels):
        fig.add_trace(go.Bar(
            y=["Budget Allocation"],
            x=[sorted_slider_input[i]],
            orientation="h",
            name=label,
            marker={"color": shades_of_blue[i]},
            textfont=dict(color="white"),
            text=[f'    {percentages[i]:.1f}%'],
            textposition="inside",
            hoverinfo="none"
        ))

    fig.update_layout(
        title_text=title,
        title_x=0.5,
        barmode="stack",
        margin=dict(b=25, t=75, l=35, r=25),
        height=325,
    )
    return fig

# Add graph showing normalized log of USD for income, gas, chicken, and house costs
# TODO: i want this to show ALL of the time, not just when the "raw" is selected
def make_time_series_graph(df):
    fig = go.Figure()
    for col in ["Income", "house", "chicken", "gas"]:
        fig.add_trace(go.Scatter(
            x=df["year"],
            y=np.log(df[col]),  # Normalize using log scale
            mode="lines",
            name=col,
        ))
    fig.update_layout(
        title="Normalized Log of USD Over Time",
        xaxis_title="Year",
        yaxis_title="Log of USD",
        legend_title="Category",
    )
    return fig

"""
==========================================================================
Make Tabs
"""
income_allocation_card = dbc.Card(income_allocation_text, className="mt-2")

slider_card = dbc.Card(
    [
        html.H4("First select how many miles you want to drive: ", className="card-title"),
        html.Div("(calculated on the average car having 25mpg gas mileage)", className="card-title"),
        dcc.Slider(
            id="gas",
            marks={i: f"{i}" for i in range(0, 101, 10)},
            min=0,
            max=100,
            step=5,
            value=10,
            included=False,
        ),
        html.H4(
            "Then choose how many meals you want to eat (with chicken): ",
            className="card-title mt-3",
        ),
        html.Div("(calculated on the average meal including about 5 ounces of chicken)", className="card-title"),
        dcc.Slider(
            id="chicken",
            marks={i: f"{i}" for i in range(0, 91, 10)},
            min=0,
            max=90,
            step=5,
            value=50,
            included=False,
        ),
    ],
    body=True,
    className="mt-4",
)

start_amount = dbc.InputGroup(
    [
        dbc.InputGroupText("Start Amount $"),
        html.Div(
            id="starting_amount",
            children=f"${get_starting_amount(MAX_YR):,.2f}", # TODO: this should be the start ammount for the selected year, not the max year
            style={"padding": "0.375rem 0.75rem"}
        ),
    ],
    className="mb-3",
)

year = dbc.InputGroup(
    [
        dbc.InputGroupText("Year"),
        dbc.Input(
            id="year",
            placeholder=f"min {MIN_YR}   max {MAX_YR}",
            type="number",
            min=MIN_YR,
            max=MAX_YR,
            value=MAX_YR,
        ),
    ],
    className="mb-3",
)


end_amount = dbc.InputGroup(
    [
        dbc.InputGroupText("Ending Amount"),
        dbc.Input(id="ending_amount", disabled=True, className="text-black"),
    ],
    className="mb-3",
)

input_groups = html.Div(
    [start_amount, year, end_amount],
    className="mt-4 p-4",
)

overall_card = dbc.Card(
    [
        dbc.CardHeader("Here you can see how the cost of all factors has changed over time"),
        html.Div(income_table),  # Add the raw data table here
    ],
    className="mt-4",
)

learn_card = dbc.Card(
    [
        dbc.CardHeader("An Introduction to Income Allocation and Living Wages in the US"),
        dbc.CardBody(learn_text),
    ],
    className="mt-4",
)

tabs = dbc.Tabs(
    [
        dbc.Tab(learn_card, tab_id="tab1", label="Learn"),
        dbc.Tab(
            [income_allocation_text, slider_card, input_groups],
            tab_id="tab-2",
            label="Play",
            className="pb-4",
        ),
        dbc.Tab([overall_card], tab_id="tab-3", label="Raw"),
    ],
    id="tabs",
    active_tab="tab-2",
    className="mt-2",
)

"""
===========================================================================
Main Layout
"""
app.layout = dbc.Container(
    [
        html.Div(
            [
                html.H2(
                    "Discover the Cost of Living in the US",
                    className="text-center text-white py-3 mb-0",
                ),
                html.H5(
                    "Allie Peterson, Westmont College, Community Action Computing (CS-150)",
                    className="text-center text-white mt-2 mb-0",
                ),
            ],
            className="bg-primary w-100",
        ),
        dbc.Row(
            [
                dbc.Col(tabs, width=12, lg=5, className="mt-4 border"),
                dbc.Col(
                    [
                        dcc.Graph(id="allocation_bar_chart", className="mb-2"),
                        dcc.Graph(id="time_series_graph", className="pb-4"),  # Add the time series graph
                        html.Hr(),
                        html.Div(id="summary_table"),
                        html.H6(datasource_text, className="my-2"),
                    ],
                    width=12,
                    lg=7,
                    className="pt-4",
                ),
            ],
            className="ms-1",
        ),
        dbc.Row(dbc.Col(footer)),
    ],
    fluid=True,
)

"""
==========================================================================
Callbacks
"""

@app.callback(
    Output("allocation_bar_chart", "figure"),
    Input("chicken", "value"),
    Input("gas", "value"),
    Input("year", "value"),
)
def update_bar(chicken_lbs, gas_gallons, year):
# TODO: this should subtract the housing from the income. then that is the income for the month.
    monthly_income = get_starting_amount(year) #
    print("monthly income in updae bar:", monthly_income)

    # Prices per unit
    price_per_lb_chicken = chicken_df.loc[chicken_df["year"] == year, "chicken"].iloc[0]
    print("price per lb cjhicken ",price_per_lb_chicken )
    price_per_gallon_gas = gas_df.loc[gas_df["year"] == year, "gas"].iloc[0]
    print("price_per_gallon_gas ", price_per_gallon_gas)

    # Calculate total expenses
    total_expense = (chicken_lbs * price_per_lb_chicken) + (gas_gallons * price_per_gallon_gas)
    print("total expense: ",total_expense)

    # Calculate remaining savings
    savings = max(0, monthly_income - total_expense)

    # Convert to percentage of total income
    expense_percent = min(100, (total_expense / monthly_income) * 100)
    savings_percent = max(0, 100 - expense_percent)

    slider_input = [expense_percent, savings_percent]
    sorted_labels = ["Expenses", "Savings"]

    figure = make_bar(slider_input, "Monthly Budget Breakdown")
    return figure

# Add callback for the time series graph
@app.callback(
    Output("time_series_graph", "figure"),
    Input("tabs", "active_tab"),
)
def update_time_series_graph(active_tab):
    if active_tab == "tab-3":
        return make_time_series_graph(df)
    return go.Figure()

if __name__ == "__main__":
    app.run(debug=True)