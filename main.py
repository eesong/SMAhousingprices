from modules.m_initialization import initialize
from layouts.dash_layout import create_tabs, main, create_cards_horizontal, create_card, create_tab_content, create_navbar, create_slider
from initialization_params import params as init_params
from simulation import simulate, update_history

from collections import defaultdict

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
history = defaultdict(list)

persons, houses, ask_df, bid_df = None, None, None, None
k = 1000

params_content = [
    create_slider('Initialization Wealth Mean', 'init-wealth',
                  (100, 400, 50, 300)),
    create_slider('Initialization House Price', 'init-price',
                  (100, 400, 50, 300)),
    create_slider('Amenities Coef', 'amen-coef', (100, 1000, 100, 500)),
    create_slider('Location Coef', 'loc-coef', (100, 1000, 100, 500)),
    create_slider('Number of People Born', 'no-born', (10, 40, 1, 10)),
    dbc.Button("Set Parameters!", id="set-params-button", className="mr-2"),
]

main_content = [
    dcc.Graph(
        id='heatmap-graph',
        figure=go.Figure(
            data=go.Heatmap(
                z=None, y=[i for i in range(10)], x=[i for i in range(10)]),
            layout=go.Layout(title='Market Prices')),
        style={'height': 800},
        config={'displayModeBar': False}),
    dcc.Interval(
        id='interval-component',
        max_intervals=0,
        interval=2000,  # in milliseconds
        n_intervals=0),
]

ouput_content = [
    dcc.Graph(id='house-status-graph',),
    dcc.Graph(id='persons-status-graph',),
]

main_header = [
    dbc.Button("Start sequence!", id="start-button", className="mr-2"),
    html.Span(id="sim-count", style={"vertical-align": "middle"}),
]

main_tab = create_tab_content([main_content], [], header=main_header)
params_tab = create_tab_content([params_content], [])
output_tab = create_tab_content([ouput_content], [])

tabs = create_tabs([params_tab, main_tab, output_tab],
                   ['Set Parameters', 'Main', 'Outputs'])
navbar = create_navbar()
app.layout = html.Div([navbar, tabs])

###################################### Params ######################################


@app.callback(
    dash.dependencies.Output('init-wealth-slider-output', 'children'),
    [dash.dependencies.Input('init-wealth-slider', 'value')])
def update_init_wealth(value):
    global params
    params['INITIAL_WEALTH'] = lambda: value + 100 * np.random.uniform()
    return f'{value}'


@app.callback(
    dash.dependencies.Output('init-price-slider-output', 'children'),
    [dash.dependencies.Input('init-price-slider', 'value')])
def update_init_price(value):
    global params
    params['INITIAL_PRICE'] = lambda: value + 100 * np.random.uniform()
    return f'{value}'


@app.callback(
    dash.dependencies.Output('amen-coef-slider-output', 'children'),
    [dash.dependencies.Input('amen-coef-slider', 'value')])
def update_amen_coef(value):
    global params
    params['INITIAL_WEALTH'] = value
    return f'{value}'


@app.callback(
    dash.dependencies.Output('loc-coef-slider-output', 'children'),
    [dash.dependencies.Input('loc-coef-slider', 'value')])
def update_loc_coef(value):
    global params
    params['INITIAL_PRICE'] = value
    return f'{value}'


@app.callback(
    dash.dependencies.Output('no-born-slider-output', 'children'),
    [dash.dependencies.Input('no-born-slider', 'value')])
def update_no_born(value):
    global params
    params['NUM_BORN'] = lambda: np.random.binomial(value, 0.5)
    return f'{value}'


###################################### Graph ######################################


@app.callback(
    Output('heatmap-graph', 'figure'),
    [Input('interval-component', 'n_intervals')])
def update_heatmap_graph(n):
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
    Output('house-status-graph', 'figure'),
    [Input('interval-component', 'n_intervals')])
def update_house_status_graph(n):
    Y = history["total_houses_occupied"]
    Y1 = history["total_houses_empty"]
    Y2 = history["total_houses_selling"]
    if not Y:
        return {}
    else:
        X = [i for i in range(len(Y))]
        data = go.Scatter(x=X, y=Y, name='total_houses_occupied')
        data1 = go.Scatter(x=X, y=Y1, name='total_houses_empty')
        data2 = go.Scatter(x=X, y=Y2, name='total_houses_selling')
        return {
            'data': [data, data1, data2],
            'layout':
                go.Layout(
                    xaxis=dict(range=[min(X), max(X)]),
                    yaxis=dict(
                        range=[min(Y + Y1 +
                                   Y2), max(Y + Y1 + Y2)]),
                )
        }


@app.callback(
    Output('persons-status-graph', 'figure'),
    [Input('interval-component', 'n_intervals')])
def update_population_status_graph(n):
    Y = history["popn_with_zero_house"]
    Y1 = history["popn_with_one_house"]
    Y2 = history["popn_with_two_house"]
    if not Y:
        return {}
    else:
        X = [i for i in range(len(Y))]
        data = go.Scatter(x=X, y=Y, name='popn_with_zero_house')
        data1 = go.Scatter(x=X, y=Y1, name='popn_with_one_house')
        data2 = go.Scatter(x=X, y=Y2, name='popn_with_two_house')
        return {
            'data': [data, data1, data2],
            'layout':
                go.Layout(
                    xaxis=dict(range=[min(X), max(X)]),
                    yaxis=dict(
                        range=[min(Y + Y1 +
                                   Y2), max(Y + Y1 + Y2)]),
                )
        }


###################################### Commands ######################################


@app.callback(
    Output('interval-component', 'max_intervals'),
    [Input('set-params-button', 'n_clicks')])
def set_params(n):
    if n and (n > 0):
        global persons, houses, ask_df, bid_df
        persons, houses, ask_df, bid_df = initialize(params)
        return -1
    else:
        return 0


@app.callback(
    Output("sim-count", "children"), [Input('start-button', 'n_clicks')])
def start_sim(n):
    global k, history
    global params, persons, houses, ask_df, bid_df
    if (n is not None):
        for i in range(10):
            k += 1
            simulate(params, persons, houses, ask_df, bid_df)
            update_history(history, persons, houses)
        print('\n\n\n\n', houses, '\n\n\n\n', persons)
        return f"Sequence ended at {k} simulations"


if __name__ == "__main__":
    app.run_server(debug=True)
    pass