# -*- coding: utf-8 -*-
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import os
import numpy as np

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

def get_monthly(selected_year):
    value = income_df.loc[income_df["year"] == selected_year, "Income"]
    if not value.empty:
        return (income_df.iloc[0] - house_df.iloc[0]) / 12  # Subtract housing cost first

    else:
        return 0

# Implement cost_per_mile function
def cost_per_mile(selected_year):
    cost = gas_df.loc[gas_df["year"] == selected_year, "gas"]
    if not cost.empty:
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
> **Disposable income allocation** is a way to explore, given the average income, what someone can afford.

Play with the app and see for yourself!

> Change the allocation of chicken and gas on the sliders and see how your income supports you in the graph.
  Try entering different time periods too.
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
    sorted_labels = ["Gas", "Food", "Savings"]  # Removed Housing
    sorted_labels = [sorted_labels[i] for i in sorted_indices]

    total = 100  # Total is always 100% of disposable income
    percentages = [(value / total) * 100 for value in sorted_slider_input]

    colors = ["#008000", "#FFFF00", "#FFA500"]  # Only for Gas, Food, and Savings

    fig = go.Figure()

    for i, label in enumerate(sorted_labels):
        fig.add_trace(go.Bar(
            y=["Budget Allocation"],
            x=[sorted_slider_input[i]],
            orientation="h",
            name=label,
            marker={"color": colors[i]},
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
def make_time_series_graph(df):
    fig = go.Figure()

    for col in ["Income", "house", "chicken", "gas"]:
        log_values = np.log(df[col])  # Apply log
        scaled_values = (log_values - log_values.min()) / (log_values.max() - log_values.min())  # Normalize

        fig.add_trace(go.Scatter(
            x=df["year"],
            y=scaled_values,  # Use normalized values
            mode="lines",
            name=col,
        ))

    fig.update_layout(
        title="Normalized Log of USD Over Time",
        xaxis_title="Year",
        yaxis_title="Normalized Log of USD (0 to 1)",
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

# Dropdown for selecting year
year_dropdown = dcc.Dropdown(
    id="year_selector",
    options=[{"label": str(year), "value": year} for year in sorted(df["year"].unique())],
    value=df["year"].max(),  # Default to max year
    clearable=False,
    style={"width": "200px"},
)

# Input group to display start amount
start_amount = dbc.InputGroup(
    [
        dbc.InputGroupText("Start Amount $"),
        html.Div(
            id="starting_amount",
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


input_groups = html.Div(
    [start_amount, year],
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
def update_bar(chicken_meals, gas_miles, year):
    # Get yearly income and convert to monthly
    income_value = income_df.loc[income_df["year"] == year, "Income"]
    if not income_value.empty and income_value.iloc[0] > 0:
        monthly_income = income_value.iloc[0] / 12
    else:
        return make_bar([0, 0], "Monthly Budget Breakdown")  # Return empty chart if no income data

    # Get monthly housing cost
    house_value = house_df.loc[house_df["year"] == year, "house"]
    if not house_value.empty:
        monthly_housing = (((house_value.iloc[0]) * 0.85) / 30) / 12
    else:
        monthly_housing = 0

    # **Define disposable income**
    disposable_income = monthly_income - monthly_housing
    if disposable_income <= 0:
        return make_bar([0, 0], "No Disposable Income")  # Prevent division errors

    # Calculate gas and food costs
    gas_cost = gas_miles * cost_per_mile(year)
    food_cost = chicken_meals * cost_per_meal(year)

    # Total expenses (excluding housing)
    total_expense = gas_cost + food_cost

    # Calculate percentages based on disposable income
    gas_percent = (gas_cost / disposable_income) * 100
    food_percent = (food_cost / disposable_income) * 100
    savings_percent = max(0, 100 - (gas_percent + food_percent))

    # Values for stacked bar
    slider_input = [gas_percent, food_percent, savings_percent]
    sorted_labels = ["Gas", "Food", "Savings"]

    figure = make_bar(slider_input, "Monthly Budget Breakdown")
    return figure

@app.callback(
    Output("time_series_graph", "figure"),
    Input("year", "value"),
)
def update_time_series_graph(year):
    return make_time_series_graph(df)

@app.callback(
    Output("starting_amount", "children"),
    Input("year", "value")
)

def update_starting_amount(year):
    income_value = income_df.loc[income_df["year"] == year, "Income"]
    if not income_value.empty:
        starting_amt = (income_value.iloc[0] / 12)
    else:
        starting_amt = 0  # Default value if the year is missing
    return starting_amt


if __name__ == "__main__":
    app.run(debug=True)