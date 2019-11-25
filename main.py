from modules.m_initialization import initialize
from simulation import simulate

import dash
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import dash_daq as daq
import numpy as np
from dash.exceptions import PreventUpdate
import pandas as pd
from dash.dependencies import Input, Output
import plotly.express as px

# from layouts.dash_layout import create_tabs, main, create_cards_horizontal, create_card, create_tab_content, create_navbar

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

k = 0
persons, houses, ask_df, bid_df = initialize()
heatmap_data = [[
    round(houses.iloc[i + j * 10]['last_updated'], 2) for i in range(10)
] for j in range(10)]
# heatmap_data=[list(df.iloc[i]) for i in range(len(df))][::-1]

content = [
    dbc.Button("Simulate!", id="start-button", className="mr-2"),
    html.Span(id="sim-count", style={"vertical-align": "middle"}),
    dcc.Graph(
        id='live-update-graph',
        figure=go.Figure(
            data=go.Heatmap(
                z=heatmap_data,
                y=[i for i in range(10)],
                x=[i for i in range(10)]),
            layout=go.Layout(title='Market Prices')),
        style={'height': 1000},
        config={'displayModeBar': False}),
    dcc.Interval(
        id='interval-component',
        interval=5 * 1000,  # in milliseconds
        n_intervals=0),
]

app.layout = html.Div(content)


@app.callback(
    Output('live-update-graph', 'figure'),
    [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    heatmap_data = [[
        round(houses.iloc[i + j * 10]['market_price'], 2) for i in range(10)
    ] for j in range(10)]
    return {
        'data': [
            go.Heatmap(
                z=heatmap_data,
                y=[i for i in range(10)],
                x=[i for i in range(10)])
        ]
    }


@app.callback(
    Output("sim-count", "children"), [Input('start-button', 'n_clicks')])
def update_sim_count(n):
    global k
    print(n)
    mean_price = houses['market_price'].mean()
    if (n is not None):
        while True:
            if (n % 2 == 0):
                break
            k += 1
            simulate(persons, houses, ask_df, bid_df)
        print('loop exited')
        return f"No. of Sims: {k} {mean_price}"


if __name__ == "__main__":
    app.run_server(debug=True)
