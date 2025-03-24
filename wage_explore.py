# -*- coding: utf-8 -*-
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import os

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.LUX, dbc.icons.FONT_AWESOME],
)

# Loading in data
income_df = pd.read_csv("data/income.csv")
house_df = pd.read_csv("data/house.csv")
chicken_df = pd.read_csv("data/chicken.csv")
gas_df = pd.read_csv("data/gas.csv")

# Applying datetime conversion and extract the year
dfs = [income_df, house_df, chicken_df, gas_df]

for df in dfs:
    if "observation_date" in df.columns:
        df["observation_date"] = pd.to_datetime(df["observation_date"])
        df["year"] = df["observation_date"].dt.year

MAX_YR = gas_df.year.max()
MIN_YR = gas_df.year.min()

COLORS = { # TODO: fix the colors on this
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
    value = income_df.loc[income_df["year"] == selected_year, "MEHOINUSA672N"]
    if not value.empty:
        return value.iloc[0] / 12
    else:
        return 0

# TODO: im plement function calculating milage cost
# average mile per gallon is 25.
def cost_per_mile(selected_year):
    cost = gas_df.loc[gas_df["year"] == selected_year, "GASREGCOVW"]
    if not cost.empty:
        return cost.iloc[0] / 25
    else:
        return 0

# TODO: implement function calculating averge cost per meal
def cost_per_meal(selected_year):
    # average meal is 1/3
    cost = gas_df.loc[gas_df["year"] == selected_year, "APU0000706111"]
    if not cost.empty:
        return cost.iloc[0] / 3
    else:
        return 0


"""
==========================================================================
Markdown Text 
"""
# TODO: fix data source
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
Figures
"""


def make_bar(slider_input, title):
    # TODO: update so it accuratly shows the resulting number subtracting based on the slider preferences.
    sorted_indices = sorted(range(len(slider_input)), key=lambda k: slider_input[k], reverse=True)
    sorted_slider_input = [slider_input[i] for i in sorted_indices]
    sorted_labels = ["Chicken (lbs)", "Gas (gallons)", "Savings"]
    sorted_labels = [sorted_labels[i] for i in sorted_indices]

    total = sum(sorted_slider_input)
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
        # paper_bgcolor=COLORS["background"],
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
        html.Div("(calculated on the average car having 25mpg gas milage)", className="card-title"),
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
            # TODO: call cost_per_meal in how much is take from the total.
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
            children=f"${get_starting_amount(MAX_YR):,.2f}",
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

number_of_years = dbc.InputGroup(
    [
        dbc.InputGroupText("Number of Years:"),
        dbc.Input(
            id="planning_time",
            placeholder="# yrs",
            type="number",
            min=1,
            value=MAX_YR - MIN_YR + 1,
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
    [start_amount, year, number_of_years, end_amount],
    className="mt-4 p-4",
)

overall_card = dbc.Card(
    [
        dbc.CardHeader("Here you can see how the cost of all factors has changed over time"),
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
            [income_allocation_text, slider_card, input_groups],  # Removed the button
            tab_id="tab-2",
            label="Play",
            className="pb-4",
        ),
        dbc.Tab([overall_card], tab_id="tab-3", label="Results"),
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
                    "Cost of Living in the US Exploration",
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
    monthly_income = get_starting_amount(year)

    # Prices per unit (assumed values, can be adjusted)
    price_per_lb_chicken = chicken_df.loc[chicken_df["year"] == year, "APU0000706111"].iloc[0]
    price_per_gallon_gas = gas_df.loc[gas_df["year"] == year, "GASREGCOVW"].iloc[0]

    # Calculate total expenses
    total_expense = (chicken_lbs * price_per_lb_chicken) + (gas_gallons * price_per_gallon_gas)

    # Calculate remaining savings
    savings = max(0, monthly_income - total_expense)

    # Convert to percentage of total income
    expense_percent = min(100, (total_expense / monthly_income) * 100)
    savings_percent = max(0, 100 - expense_percent)

    slider_input = [expense_percent, savings_percent]
    sorted_labels = ["Expenses", "Savings"]

    figure = make_bar(slider_input, "Monthly Budget Breakdown")
    return figure


if __name__ == "__main__":
    app.run(debug=True)