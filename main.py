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

persons, houses, ask_df, bid_df = initialize()
heatmap_data = [[
    round(houses.iloc[i + j * 10]['last_updated'], 2) for i in range(10)
] for j in range(10)]
# heatmap_data=[list(df.iloc[i]) for i in range(len(df))][::-1]

content = [
    dcc.Graph(
        id='live-update-graph',
        figure=go.Figure(
            data=go.Heatmap(
                z=heatmap_data,
                y=[i for i in range(10)],
                x=[i for i in range(10)],
                colorscale=[[0, "rgb(166,206,227)"], [0.25, "rgb(31,120,180)"],
                            [0.45,
                             "rgb(178,223,138)"], [0.65, "rgb(51,160,44)"],
                            [0.85, "rgb(251,154,153)"], [1, "rgb(227,26,28)"]]),
            layout=go.Layout(title='Market Prices')),
        style={'height': 1000},
        config={'displayModeBar': False}),
    dcc.Interval(
        id='interval-component',
        interval=4 * 1000,  # in milliseconds
        n_intervals=0)
]

app.layout = html.Div(content)


@app.callback(
    Output('live-update-graph', 'figure'),
    [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    simulate(persons, houses, ask_df, bid_df)
    heatmap_data = [[
        round(houses.iloc[i + j * 10]['last_updated'], 2) for i in range(10)
    ] for j in range(10)]
    return {
        'data': [
            go.Heatmap(
                z=heatmap_data,
                y=[i for i in range(10)],
                x=[i for i in range(10)],
                colorscale=[[0, "rgb(166,206,227)"], [0.25, "rgb(31,120,180)"],
                            [0.45,
                             "rgb(178,223,138)"], [0.65, "rgb(51,160,44)"],
                            [0.85, "rgb(251,154,153)"], [1, "rgb(227,26,28)"]])
        ]
    }


if __name__ == "__main__":
    app.run_server(debug=True)
