from modules.m_initialization import initialize
from layouts.dash_layout import create_tabs, main, create_cards_horizontal, create_card, create_tab_content, create_navbar
from initialization_params import params as init_params
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

params = init_params

persons, houses, ask_df, bid_df = None, None, None, None
k = 1000

params_content = [
    html.H5('Initialization Wealth Mean'),
    dcc.Slider(
        id='init-wealth-mean-slider',
        min=100,
        max=400,
        step=50,
        value=300,
    ),
    html.Div(id='init-wealth-mean-slider-output'),
    html.H5('Initialization Wealth Sigma'),
    dcc.Slider(
        id='init-wealth-sigma-slider',
        min=1,
        max=20,
        step=1,
        value=10,
    ),
    html.Div(id='init-wealth-sigma-slider-output'),
    html.H5('Initialization House Price Mean'),
    dcc.Slider(
        id='init-price-mean-slider',
        min=100,
        max=400,
        step=50,
        value=300,
    ),
    html.Div(id='init-price-mean-slider-output'),
    html.H5('Initialization House Price Sigma'),
    dcc.Slider(
        id='init-price-sigma-slider',
        min=1,
        max=20,
        step=1,
        value=10,
    ),
    html.Div(id='init-price-sigma-slider-output'),
    dbc.Button("Set Parameters!", id="set-params-button", className="mr-2"),
]

main_content = [
    dcc.Graph(
        id='live-update-graph',
        figure=go.Figure(
            data=go.Heatmap(
                z=None, y=[i for i in range(10)], x=[i for i in range(10)]),
            layout=go.Layout(title='Market Prices')),
        style={'height': 1000},
        config={'displayModeBar': False}),
    dcc.Interval(
        id='interval-component',
        disabled=True,
        interval=500,  # in milliseconds
        n_intervals=0),
]

main_header = [
    dbc.Button("Start sequence!", id="start-button", className="mr-2"),
    html.Span(id="sim-count", style={"vertical-align": "middle"}),
]

main_tab = create_tab_content([main_content], [], header=main_header)
params_tab = create_tab_content([params_content], [])
output_tab = create_tab_content([], [])

tabs = create_tabs([params_tab, main_tab, output_tab],
                   ['Set Parameters', 'Main', 'Outputs'])
navbar = create_navbar()
app.layout = html.Div([navbar, tabs])


@app.callback(
    dash.dependencies.Output('init-wealth-mean-slider-output', 'children'),
    [dash.dependencies.Input('init-wealth-mean-slider', 'value')])
def update_wealth_mu(value):
    global params
    params['wealth_mu'] = value
    return f'{value}'


@app.callback(
    dash.dependencies.Output('init-wealth-sigma-slider-output', 'children'),
    [dash.dependencies.Input('init-wealth-sigma-slider', 'value')])
def update_wealth_sigma(value):
    global params
    params['wealth_sigma'] = value
    return f'{value}'


@app.callback(
    dash.dependencies.Output('init-price-mean-slider-output', 'children'),
    [dash.dependencies.Input('init-price-mean-slider', 'value')])
def update_price_mu(value):
    global params
    params['initialization_price_mu'] = value
    return f'{value}'


@app.callback(
    dash.dependencies.Output('init-price-sigma-slider-output', 'children'),
    [dash.dependencies.Input('init-price-sigma-slider', 'value')])
def update_price_sigma(value):
    global params
    params['initialization_price_sigma'] = value
    return f'{value}'


@app.callback(
    Output('live-update-graph', 'figure'),
    [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    heatmap_data = [[
        round(houses.iloc[i + j * 10]['last_updated'], 2) for i in range(10)
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
    Output('interval-component', 'disabled'),
    [Input('set-params-button', 'n_clicks')])
def set_params(n):
    global persons, houses, ask_df, bid_df
    persons, houses, ask_df, bid_df = initialize(params)
    return False


@app.callback(
    Output("sim-count", "children"), [Input('start-button', 'n_clicks')])
def start_sim(n):
    global k
    global params
    if (n is not None):
        for i in range(10):
            k += 1
            simulate(params, persons, houses, ask_df, bid_df)
        return f"Sequence ended at {k} simulations"


if __name__ == "__main__":
    app.run_server(debug=True)
