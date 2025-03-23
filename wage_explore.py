# -*- coding: utf-8 -*-
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import os
#
print("Current working directory:", os.getcwd())
# app = Dash(
#     __name__,
#     external_stylesheets=[dbc.themes.LUX, dbc.icons.FONT_AWESOME],
# )
#
# #  make dataframe from  spreadsheet:
# all in floats
income_df = pd.read_csv("data/income.csv")
house_df = pd.read_csv("data/house.csv")
chicken_df = pd.read_csv("data/chicken.csv") # float
gas_df = pd.read_csv("data/gas.csv")

## Apply datetime conversion and extract the year
dfs = [income_df, house_df, chicken_df, gas_df]

for df in dfs:
    if "observation_date" in df.columns:  # Ensure the column exists
        df["observation_date"] = pd.to_datetime(df["observation_date"])  # Convert to datetime
        df["year"] = df["observation_date"].dt.year  # Extract the year


#
MAX_YR = gas_df.year.max()
MIN_YR = gas_df.year.min()
# history_df = pd.DataFrame(columns=["Timestamp", "Stocks", "Cash", "Bonds", "Investment Style", "Start Amount", "Start Year", "Planning Time"])

COLORS = { # theese will change
    "income": "#3cb521",
    "house": "#fd7e14",
    "chicken": "#446e9b",
    "gas": "#cd0200",
}

"""
==========================================================================
Markdown Text
"""

datasource_text = dcc.Markdown(
    """
    [WRONGnData sources:](http://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html)
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
    This data is not seasonally adjusted, so that is a factor in the differences over time. Becuase it's constand throught all the data being used, it should be fine. 
    
    
    Past cost of living does not necissarily determine future results, but you can still
    learn a lot by reviewing how different components have changed over time, and make general assumptions of where the trend will go in the future. 

    Use the sliders to change the income allocation (how much you spend on gas or chicken) 
    and see how much income you have leftover-- if any.

    This is intended to help you understand how the average income in the US has been able to support the average household over time. 

    The  data is from FRED, more details can be found in the README section of this project. 


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

# """
# ==========================================================================
# Tables
# """
#
# total_returns_table = dash_table.DataTable(
#     id="total_returns",
#     columns=[{"id": "Year", "name": "Year", "type": "text"}]
#     + [
#         {"id": col, "name": col, "type": "numeric", "format": {"specifier": "$,.0f"}}
#         for col in ["Cash", "Bonds", "Stocks", "Total"]
#     ],
#     page_size=15,
#     style_table={"overflowX": "scroll"},
# )
#
# annual_returns_pct_table = dash_table.DataTable(
#     id="annual_returns_pct",
#     columns=(
#         [{"id": "Year", "name": "Year", "type": "text"}]
#         + [
#             {"id": col, "name": col, "type": "numeric", "format": {"specifier": ".1%"}}
#             for col in df.columns[1:]
#         ]
#     ),
#     data=df.to_dict("records"),
#     sort_action="native",
#     page_size=15,
#     style_table={"overflowX": "scroll"},
# )
#
# # not a callack, just a helper function
# def make_summary_table(dff):
#     """Make html table to show cagr and  best and worst periods"""
#
#     table_class = "h5 text-body text-nowrap"
#     cash = html.Span(
#         [html.I(className="fa fa-money-bill-alt"), " Cash"], className=table_class
#     )
#     bonds = html.Span(
#         [html.I(className="fa fa-handshake"), " Bonds"], className=table_class
#     )
#     stocks = html.Span(
#         [html.I(className="fa fa-industry"), " Stocks"], className=table_class
#     )
#     inflation = html.Span(
#         [html.I(className="fa fa-ambulance"), " Inflation"], className=table_class
#     )
#
#     start_yr = dff["Year"].iat[0]
#     end_yr = dff["Year"].iat[-1]
#
#     df_table = pd.DataFrame(
#         {
#             "": [cash, bonds, stocks, inflation],
#             f"Rate of Return (CAGR) from {start_yr} to {end_yr}": [
#                 cagr(dff["all_cash"]),
#                 cagr(dff["all_bonds"]),
#                 cagr(dff["all_stocks"]),
#                 cagr(dff["inflation_only"]),
#             ],
#             f"Worst 1 Year Return": [
#                 worst(dff, "3-mon T.Bill"),
#                 worst(dff, "10yr T.Bond"),
#                 worst(dff, "S&P 500"),
#                 "",
#             ],
#         }
#     )
#     return dbc.Table.from_dataframe(df_table, bordered=True, hover=True)
#
#
# """
# ==========================================================================
# Figures
# """
#
# # again, not a callback. just puts visual together. The callback is simpler with this.
# def make_pie(slider_input, title):
#     # Find the index of the highest value
#     sorted_indices = sorted(range(len(slider_input)), key=lambda k: slider_input[k], reverse=True)
#
#     # Reorder slider_input values and labels based on sorted indices
#     sorted_slider_input = [slider_input[i] for i in sorted_indices]
#     sorted_labels = ["Cash", "Bonds", "Stocks"]
#     sorted_labels = [sorted_labels[i] for i in sorted_indices]
#
#     # Calculate total sum to compute percentage
#     total = sum(sorted_slider_input)
#     percentages = [(value / total) * 100 for value in sorted_slider_input]
#
#     # Shades of blue (light to dark)
#     shades_of_blue = ["#1f77b4", "#4d88ff", "#a6c6ff"]  # Light, medium, dark blue a6c6ff
#
#     # Create a stacked bar chart with horizontal bars
#     fig = go.Figure()
#
#     # Add bars in sorted order with different shades of blue
#     for i, label in enumerate(sorted_labels):
#         fig.add_trace(go.Bar(
#             y=["Portfolio"],
#             x=[sorted_slider_input[i]],  # Use sorted values
#             orientation="h",  # Horizontal bar chart
#             name=label,  # Add the corresponding label
#             marker={"color": shades_of_blue[i]},  # Use different shades of blue
#             #             marker={"colors": [COLORS["cash"], COLORS["bonds"], COLORS["stocks"]]},
#             textfont=dict(color="white"),  # Set text color to white
#
#             text=[f'    {percentages[i]:.1f}%'],  # Display label and percentage
#             textposition="inside",  # Position the text inside the bar
#             hoverinfo="none"  # Hide hover info to make the text clearer
#         ))
#
#     fig.update_layout(
#         title_text=title,
#         title_x=0.5,
#         barmode="stack",  # Stack the bars on top of each other
#         margin=dict(b=25, t=75, l=35, r=25),
#         height=325,
#         paper_bgcolor=COLORS["background"],
#     )
#     #     data=[
#     #         go.Pie(
#     #             labels=["Cash", "Bonds", "Stocks"],
#     #             values=slider_input,
#     #             textinfo="label+percent",
#     #             textposition="inside",
#     #             marker={"colors": [COLORS["cash"], COLORS["bonds"], COLORS["stocks"]]},
#     #             sort=False,
#     #             hoverinfo="none",
#     #         )
#     #     ]
#     # )
#     # fig.update_layout(
#     #     title_text=title,
#     #     title_x=0.5,
#     #     margin=dict(b=25, t=75, l=35, r=25),
#     #     height=325,
#     #     paper_bgcolor=COLORS["background"],
#     # )
#     return fig
#
#
# def make_line_chart(dff):
#     start = dff.loc[1, "Year"]
#     yrs = dff["Year"].size - 1
#     dtick = 1 if yrs < 16 else 2 if yrs in range(16, 30) else 5
#
#     fig = go.Figure()
#     fig.add_trace(
#         go.Scatter(
#             x=dff["Year"],
#             y=dff["all_cash"],
#             name="All Cash",
#             marker_color=COLORS["cash"],
#         )
#     )
#     fig.add_trace(
#         go.Scatter(
#             x=dff["Year"],
#             y=dff["all_bonds"],
#             name="All Bonds (10yr T.Bonds)",
#             marker_color=COLORS["bonds"],
#         )
#     )
#     fig.add_trace(
#         go.Scatter(
#             x=dff["Year"],
#             y=dff["all_stocks"],
#             name="All Stocks (S&P500)",
#             marker_color=COLORS["stocks"],
#         )
#     )
#     fig.add_trace(
#         go.Scatter(
#             x=dff["Year"],
#             y=dff["Total"],
#             name="My Portfolio",
#             marker_color="black",
#             line=dict(width=6, dash="dot"),
#         )
#     )
#     fig.add_trace(
#         go.Scatter(
#             x=dff["Year"],
#             y=dff["inflation_only"],
#             name="Inflation",
#             visible=True,
#             marker_color=COLORS["inflation"],
#         )
#     )
#     fig.update_layout(
#         title=f"Returns for {yrs} years starting {start}",
#         template="none",
#         showlegend=True,
#         legend=dict(x=0.01, y=0.99),
#         height=400,
#         margin=dict(l=40, r=10, t=60, b=55),
#         yaxis=dict(tickprefix="$", fixedrange=True),
#         xaxis=dict(title="Year Ended", fixedrange=True, dtick=dtick),
#     )
#     return fig
#
#
# def make_bonds_chart(slider_input):
#     # The input should be [cash, bonds, stocks]
#     bonds_value = slider_input[1]  # This is the bonds allocation
#     remaining_value = 100 - bonds_value  # This is the remaining value (100% - bonds)
#
#     # Create a horizontal bar chart for bonds allocation
#     fig = go.Figure()
#
#     # Add the bonds value as a horizontal bar
#     fig.add_trace(go.Bar(
#         y=["Bonds"],
#         x=[bonds_value],  # Only display the bonds value
#         orientation="h",  # Horizontal bar chart
#         name="Bonds",  # Label the bar
#         marker={"color": "#1f77b4"},  # Use a blue color for bonds
#         textfont=dict(color="white"),  # Set text color to white
#         text=[f'{bonds_value:.1f}%'],  # Display the percentage
#         textposition="inside",  # Position the text inside the bar
#         hoverinfo="none",  # Hide hover info
#         showlegend=False
#     ))
#     # remaining value as a lighter blue bar stacked on top of the bonds bar
#     fig.add_trace(go.Bar(
#         y=["Bonds"],
#         x=[remaining_value],  # Remaining value (100% - bonds)
#         orientation="h",  # Horizontal bar chart
#         marker={"color": "#a6c6ff"},  # Light blue for the remaining value
#         hoverinfo="none",  # Hide hover info
#         showlegend=False
#     ))
#
#     # Update layout for the chart
#     fig.update_layout(
#         title="Bonds Allocation",
#         title_x=0.5,
#         height=200,
#         margin=dict(b=25, t=50, l=35, r=25),
#         paper_bgcolor=COLORS["background"],  # Adjust background color
#         barmode="stack",  # Stack the bars on top of each other
#     )
#
#     return fig
#
#
# """
# ==========================================================================
# Make Tabs
# """
#
# # =======Play tab components
#
# asset_allocation_card = dbc.Card(asset_allocation_text, className="mt-2")
#
# slider_card = dbc.Card(
#     [
#         html.H4("First set cash allocation %:", className="card-title"),
#         dcc.Slider(
#             id="cash",
#             marks={i: f"{i}%" for i in range(0, 101, 10)},
#             min=0,
#             max=100,
#             step=5,
#             value=10,
#             included=False,
#         ),
#         html.H4(
#             "Then set stock allocation % ",
#             className="card-title mt-3",
#         ),
#         html.Div("(The rest will be bonds)", className="card-title"),
#         dcc.Slider(
#             id="stock_bond",
#             marks={i: f"{i}%" for i in range(0, 91, 10)},
#             min=0,
#             max=90,
#             step=5,
#             value=50,
#             included=False,
#         ),
#     ],
#     body=True,
#     className="mt-4",
# )
#
#
# time_period_data = [
#     {
#         "label": f"2007-2008: Great Financial Crisis to {MAX_YR}",
#         "start_yr": 2007,
#         "planning_time": MAX_YR - START_YR + 1,
#     },
#     {
#         "label": "1999-2010: The decade including 2000 Dotcom Bubble peak",
#         "start_yr": 1999,
#         "planning_time": 10,
#     },
#     {
#         "label": "1969-1979:  The 1970s Energy Crisis",
#         "start_yr": 1970,
#         "planning_time": 10,
#     },
#     {
#         "label": "1929-1948:  The 20 years following the start of the Great Depression",
#         "start_yr": 1929,
#         "planning_time": 20,
#     },
#     {
#         "label": f"{MIN_YR}-{MAX_YR}",
#         "start_yr": "1928",
#         "planning_time": MAX_YR - MIN_YR + 1,
#     },
# ]
#
#
# time_period_card = dbc.Card(
#     [
#         html.H4(
#             "Or select a time period:",
#             className="card-title",
#         ),
#         dbc.RadioItems(
#             id="time_period",
#             options=[
#                 {"label": period["label"], "value": i}
#                 for i, period in enumerate(time_period_data)
#             ],
#             value=0,
#             labelClassName="mb-2",
#         ),
#     ],
#     body=True,
#     className="mt-4",
# )
#
# # ======= InputGroup components
#
# start_amount = dbc.InputGroup(
#     [
#         dbc.InputGroupText("Start Amount $"),
#         dbc.Input(
#             id="starting_amount",
#             placeholder="Min $10",
#             type="number",
#             min=10,
#             value=10000,
#         ),
#     ],
#     className="mb-3",
# )
# start_year = dbc.InputGroup(
#     [
#         dbc.InputGroupText("Start Year"),
#         dbc.Input(
#             id="start_yr",
#             placeholder=f"min {MIN_YR}   max {MAX_YR}",
#             type="number",
#             min=MIN_YR,
#             max=MAX_YR,
#             value=START_YR,
#         ),
#     ],
#     className="mb-3",
# )
# number_of_years = dbc.InputGroup(
#     [
#         dbc.InputGroupText("Number of Years:"),
#         dbc.Input(
#             id="planning_time",
#             placeholder="# yrs",
#             type="number",
#             min=1,
#             value=MAX_YR - START_YR + 1,
#         ),
#     ],
#     className="mb-3",
# )
# end_amount = dbc.InputGroup(
#     [
#         dbc.InputGroupText("Ending Amount"),
#         dbc.Input(id="ending_amount", disabled=True, className="text-black"),
#     ],
#     className="mb-3",
# )
# rate_of_return = dbc.InputGroup(
#     [
#         dbc.InputGroupText(
#             "Rate of Return(CAGR)",
#             id="tooltip_target",
#             className="text-decoration-underline",
#         ),
#         dbc.Input(id="cagr", disabled=True, className="text-black"),
#         dbc.Tooltip(cagr_text, target="tooltip_target"),
#     ],
#     className="mb-3",
# )
#
# input_groups = html.Div(
#     [start_amount, start_year, number_of_years, end_amount, rate_of_return],
#     className="mt-4 p-4",
# )
#
#
# # =====  Results Tab components
#
# results_card = dbc.Card(
#     [
#         dbc.CardHeader("My Portfolio Returns - Rebalanced Annually"),
#         html.Div(total_returns_table),
#     ],
#     className="mt-4",
# )
#
#
# data_source_card = dbc.Card(
#     [
#         dbc.CardHeader("Source Data: Annual Total Returns"),
#         html.Div(annual_returns_pct_table),
#     ],
#     className="mt-4",
# )
#
#
# # ========= Learn Tab  Components
# learn_card = dbc.Card(
#     [
#         dbc.CardHeader("An Introduction to Asset Allocation"),
#         dbc.CardBody(learn_text),
#     ],
#     className="mt-4",
# )
#
#
# # ========= Build tabs
# tabs = dbc.Tabs(
#     [
#         dbc.Tab(learn_card, tab_id="tab1", label="Learn"),
#         dbc.Tab(
#             [asset_allocation_text, slider_card, input_groups, time_period_card, dbc.Button("Previous Setting", id="previous-setting", className="mt-4")],
#             tab_id="tab-2",
#             label="Play",
#             className="pb-4",
#         ),
#         dbc.Tab([results_card, data_source_card], tab_id="tab-3", label="Results"),
#         dbc.Tab(
#             dash_table.DataTable(
#                 id="history-table",
#                 columns=[{"name": col, "id": col} for col in history_df.columns],
#                 data=history_df.to_dict("records"),
#                 page_size=15,
#                 style_table={"overflowX": "scroll"},
#             ),
#             tab_id="tab-4",
#             label="History",
#         ),
#     ],
#     id="tabs",
#     active_tab="tab-2",
#     className="mt-2",
# )
#
# """
# ==========================================================================
# Helper functions to calculate investment results, cagr and worst periods
# """
#
#
# def backtest(stocks, cash, start_bal, nper, start_yr):
#     """calculates the investment returns for user selected asset allocation,
#     rebalanced annually and returns a dataframe
#     """
#
#     end_yr = start_yr + nper - 1
#     cash_allocation = cash / 100
#     stocks_allocation = stocks / 100
#     bonds_allocation = (100 - stocks - cash) / 100
#
#     # Select time period - since data is for year end, include year prior
#     # for start ie year[0]
#     dff = df[(df.Year >= start_yr - 1) & (df.Year <= end_yr)].set_index(
#         "Year", drop=False
#     )
#     dff["Year"] = dff["Year"].astype(int)
#
#     # add columns for My Portfolio returns
#     dff["Cash"] = cash_allocation * start_bal
#     dff["Bonds"] = bonds_allocation * start_bal
#     dff["Stocks"] = stocks_allocation * start_bal
#     dff["Total"] = start_bal
#     dff["Rebalance"] = True
#
#     # calculate My Portfolio returns
#     for yr in dff.Year + 1:
#         if yr <= end_yr:
#             # Rebalance at the beginning of the period by reallocating
#             # last period's total ending balance
#             if dff.loc[yr, "Rebalance"]:
#                 dff.loc[yr, "Cash"] = dff.loc[yr - 1, "Total"] * cash_allocation
#                 dff.loc[yr, "Stocks"] = dff.loc[yr - 1, "Total"] * stocks_allocation
#                 dff.loc[yr, "Bonds"] = dff.loc[yr - 1, "Total"] * bonds_allocation
#
#             # calculate this period's  returns
#             dff.loc[yr, "Cash"] = dff.loc[yr, "Cash"] * (
#                 1 + dff.loc[yr, "3-mon T.Bill"]
#             )
#             dff.loc[yr, "Stocks"] = dff.loc[yr, "Stocks"] * (1 + dff.loc[yr, "S&P 500"])
#             dff.loc[yr, "Bonds"] = dff.loc[yr, "Bonds"] * (
#                 1 + dff.loc[yr, "10yr T.Bond"]
#             )
#             # dff.loc[yr, "Total"] = dff[["Cash", "Bonds", "Stocks"]].sum(axis=1) # updated issue
#             dff.loc[yr, "Total"] = int(dff.loc[yr, ["Cash", "Bonds", "Stocks"]].sum())
#
#
#     dff = dff.reset_index(drop=True)
#     columns = ["Cash", "Stocks", "Bonds", "Total"]
#     dff[columns] = dff[columns].round(0)
#
#     # create columns for when portfolio is all cash, all bonds or  all stocks,
#     #   include inflation too
#     #
#     # create new df that starts in yr 1 rather than yr 0
#     dff1 = (dff[(dff.Year >= start_yr) & (dff.Year <= end_yr)]).copy()
#     #
#     # calculate the returns in new df:
#     columns = ["all_cash", "all_bonds", "all_stocks", "inflation_only"]
#     annual_returns = ["3-mon T.Bill", "10yr T.Bond", "S&P 500", "Inflation"]
#     for col, return_pct in zip(columns, annual_returns):
#         dff1[col] = round(start_bal * (1 + (1 + dff1[return_pct]).cumprod() - 1), 0)
#     #
#     # select columns in the new df to merge with original
#     dff1 = dff1[["Year"] + columns]
#     dff = dff.merge(dff1, how="left")
#     # fill in the starting balance for year[0]
#     dff.loc[0, columns] = start_bal
#     return dff
#
#
# def cagr(dff):
#     """calculate Compound Annual Growth Rate for a series and returns a formated string"""
#
#     start_bal = dff.iat[0]
#     end_bal = dff.iat[-1]
#     planning_time = len(dff) - 1
#     cagr_result = ((end_bal / start_bal) ** (1 / planning_time)) - 1
#     return f"{cagr_result:.1%}"
#
#
# def worst(dff, asset):
#     """calculate worst returns for asset in selected period returns formated string"""
#
#     worst_yr_loss = min(dff[asset])
#     worst_yr = dff.loc[dff[asset] == worst_yr_loss, "Year"].iloc[0]
#     return f"{worst_yr_loss:.1%} in {worst_yr}"
#
#
# """
# ===========================================================================
# Main Layout
# """
#
# app.layout = dbc.Container(
#     [
#         html.Div(
#             [
#                 html.H2(
#                     "Asset Allocation Visualizer",
#                     className="text-center text-white py-3 mb-0",
#                 ),
#                 html.H5(
#                     "Allie Peterson, Westmont College, Community Action Computing (CS-150)",
#                     className="text-center text-white mt-2 mb-0",  # Added margin-bottom here
#                 ),
#             ],
#             className="bg-primary w-100",  # Full width background color
#         ),
#         dbc.Row(
#             [
#                 dbc.Col(tabs, width=12, lg=5, className="mt-4 border"),
#                 dbc.Col(
#                     [
#                         dcc.Graph(id="allocation_pie_chart", className="mb-2"),
#                         dcc.Graph(id="returns_chart", className="pb-4"),
#                         html.Hr(),
#                         html.Div(id="summary_table"),
#                         html.H6(datasource_text, className="my-2"),
#                     ],
#                     width=12,
#                     lg=7,
#                     className="pt-4",
#                 ),
#             ],
#             className="ms-1",
#         ),
#         dbc.Row(
#             dbc.Col(
#                 [
#                     html.H3("Bonds Allocation", className="text-center mt-4 mb-3"),
#                     dcc.Graph(id="bonds_chart", className="pb-4"),  # New chart for Bonds Allocation
#                 ],
#                 width=12,
#             ),
#             className="ms-1 mt-4",  # Add margin-top to give space between rows
#         ),
#
#         dbc.Row(dbc.Col(footer)),
#     ],
#     fluid=True,
# )
#
#
# """
# ==========================================================================
# Callbacks
# """
#
# @app.callback(
#     Output("allocation_pie_chart", "figure"),
#     Input("stock_bond", "value"),
#     Input("cash", "value"),
# )
# def update_pie(stocks, cash):
#     bonds = 100 - stocks - cash
#     slider_input = [cash, bonds, stocks]
#
#     if stocks >= 70:
#         investment_style = "Aggressive"
#     elif stocks <= 30:
#         investment_style = "Conservative"
#     else:
#         investment_style = "Moderate"
#     figure = make_pie(slider_input, investment_style + " Asset Allocation")
#     return figure
#
#
# @app.callback(
#     Output("stock_bond", "max"),
#     Output("stock_bond", "marks"),
#     Output("stock_bond", "value"),
#     Input("cash", "value"),
#     State("stock_bond", "value"),
# )
# def update_stock_slider(cash, initial_stock_value):
#     max_slider = 100 - int(cash)
#     stocks = min(max_slider, initial_stock_value)
#
#     # formats the slider scale
#     if max_slider > 50:
#         marks_slider = {i: f"{i}%" for i in range(0, max_slider + 1, 10)}
#     elif max_slider <= 15:
#         marks_slider = {i: f"{i}%" for i in range(0, max_slider + 1, 1)}
#     else:
#         marks_slider = {i: f"{i}%" for i in range(0, max_slider + 1, 5)}
#     return max_slider, marks_slider, stocks
#
#
# @app.callback(
#     Output("planning_time", "value"),
#     Output("start_yr", "value"),
#     Output("time_period", "value"),
#     Input("planning_time", "value"),
#     Input("start_yr", "value"),
#     Input("time_period", "value"),
# )
# def update_time_period(planning_time, start_yr, period_number):
#     """syncs inputs and selected time periods"""
#     ctx = callback_context
#     input_id = ctx.triggered[0]["prop_id"].split(".")[0]
#
#     if input_id == "time_period":
#         planning_time = time_period_data[period_number]["planning_time"]
#         start_yr = time_period_data[period_number]["start_yr"]
#
#     if input_id in ["planning_time", "start_yr"]:
#         period_number = None
#
#     return planning_time, start_yr, period_number
#
#
# @app.callback(
#     Output("total_returns", "data"),
#     Output("returns_chart", "figure"),
#     Output("summary_table", "children"),
#     Output("ending_amount", "value"),
#     Output("cagr", "value"),
#     Input("stock_bond", "value"),
#     Input("cash", "value"),
#     Input("starting_amount", "value"),
#     Input("planning_time", "value"),
#     Input("start_yr", "value"),
# )
# def update_totals(stocks, cash, start_bal, planning_time, start_yr):
#     # set defaults for invalid inputs
#     start_bal = 10 if start_bal is None else start_bal
#     planning_time = 1 if planning_time is None else planning_time
#     start_yr = MIN_YR if start_yr is None else int(start_yr)
#
#     # calculate valid planning time start yr
#     max_time = MAX_YR + 1 - start_yr
#     planning_time = min(max_time, planning_time)
#     # planning_time = int(planning_time)
#     print("Planning time type: ", type(planning_time))  # Should be <class 'int'>
#     print("max_time type: ", type(max_time))
#
#
#     if start_yr + planning_time > MAX_YR:
#         # start_yr = min(df.iloc[-int(planning_time), 0], MAX_YR)  # 0 is Year column
#         start_yr = min(df.iloc[-int(planning_time), 0], MAX_YR)
#     # create investment returns dataframe
#     dff = backtest(stocks, cash, start_bal, planning_time, start_yr)
#
#     # create data for DataTable
#     data = dff.to_dict("records")
#
#     # create the line chart
#     fig = make_line_chart(dff)
#
#     summary_table = make_summary_table(dff)
#
#     # format ending balance
#     ending_amount = f"${dff['Total'].iloc[-1]:0,.0f}"
#
#     # calcluate cagr
#     ending_cagr = cagr(dff["Total"])
#
#     return data, fig, summary_table, ending_amount, ending_cagr
#
# @app.callback(
#     Output("bonds_chart", "figure"),  # Update the bonds chart
#     Input("stock_bond", "value"),
#     Input("cash", "value"),
# )
# def update_bonds_chart(stocks, cash):
#     # Calculate the bond allocation
#     bonds = 100 - stocks - cash
#     slider_input = [cash, bonds, stocks]
#
#     # Call the function to generate the bonds chart
#     return make_bonds_chart(slider_input)  # Pass only slider_input
#
# @app.callback(
#     Output("history-table", "data"),
#     Output("previous-setting", "disabled"),
#     Input("stock_bond", "value"),
#     Input("cash", "value"),
#     Input("starting_amount", "value"),
#     Input("planning_time", "value"),
#     Input("start_yr", "value"),
#     State("history-table", "data"),
# )
# def update_history(stocks, cash, start_bal, planning_time, start_yr, history_data):
#     if start_bal is None or planning_time is None or start_yr is None:
#         return history_data, len(history_data) == 0
#
#     new_entry = {
#         "Timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "Stocks": stocks,
#         "Cash": cash,
#         "Bonds": 100 - stocks - cash,
#         "Investment Style": "Aggressive" if stocks >= 70 else "Conservative" if stocks <= 30 else "Moderate",
#         "Start Amount": start_bal,
#         "Start Year": start_yr,
#         "Planning Time": planning_time,
#     }
#
#     history_data.append(new_entry)
#     return history_data, len(history_data) == 0
#
# if __name__ == "__main__":
#     app.run(debug=True)
