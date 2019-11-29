from modules.m_initialization import initialize
from layouts.dash_layout import create_tabs, main, create_cards_horizontal, create_card, create_tab_content, create_navbar, create_slider, create_cards_vertical
from initialization_params import params as init_params
from common import generate_min_max
from simulation import simulate, update_history

from collections import defaultdict
import copy

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
run_history = {}

scatter_data = [[]]

runs = {'params': params}
persons, houses, ask_df, bid_df = initialize(params)
run_counter = 0
sim_t = 0

param_ids = ['init-wealth', 'init-price', 'amen-coef', 'loc-coef', 'no-born']
param_names = [
    'INITIAL_WEALTH', 'INITIAL_PRICE', 'AMENITIES_COEF', 'LOC_COEF', 'NUM_BORN'
]
params_lambdas = lambda value: [
    lambda: value + 100 * np.random.uniform(), lambda: value + 100 * np.random.
    uniform(), value, value, lambda: np.random.binomial(value, 0.5)
]
param_min_max = [
    generate_min_max(100, 50),
    generate_min_max(100, 50),
    generate_min_max(100, 100),
    generate_min_max(100, 100),
    generate_min_max(10, 2)
]
slider_labels = [
    'Initialization Wealth Mean', 'Initialization House Price',
    'Amenities Coef', 'Location Coef', 'Number of People Born'
]
output_metrics = {
    'Mean Market Price': 'mean_market_price',
    'Occupancy Rate': 'occupancy_rate',
}

params_content = [
    create_cards_vertical([
        create_slider(slider_labels[i], param_ids[i], param_min_max[i])
        for i in range(len(param_names))
    ]),
    dbc.Button("Set Parameters!", id="set-params-button", className="mr-2"),
]

main_content = [
    dcc.Graph(
        id='heatmap-graph',
        figure=go.Figure(
            data=go.Heatmap(
                z=[[]], y=[i for i in range(10)], x=[i for i in range(10)]),
            layout=go.Layout(title='Market Prices')),
        style={'height': 800},
        config={'displayModeBar': False}),
    dcc.Interval(
        id='interval-component',
        max_intervals=0,
        interval=1000,  # in milliseconds
        n_intervals=0),
]

ouput_content = [
    dbc.Select(
        id="output-metric-select",
        options=[{
            'label': key,
            'value': value
        } for key, value in output_metrics.items()],
        disabled=True),
    dcc.Graph(id='output-graph', style={'height': 800}),
]

main_header = [
    dbc.Button(
        "Start Simulation!", id="start-button", disabled=True,
        className="mr-2"),
]

main_cards = [
    create_card('run-count-text', run_counter, '/10', '# Runs', 10),
    create_card('sim-count-text', sim_t, '', 'Years passed in run'),
    create_card('sim-completion-text', 0, '', 'Simulation complete', 1),
]

main_tab = create_tab_content([main_content], main_cards, header=main_header)
params_tab = create_tab_content([params_content], [])
output_tab = create_tab_content([ouput_content], [])

tabs = create_tabs([params_tab, main_tab, output_tab],
                   ['Set Parameters', 'Start Simulation', 'Generate Outputs'])
navbar = create_navbar()
app.layout = html.Div([navbar, tabs])

###################################### Params ######################################


@app.callback([Output(name + '-slider', 'disabled') for name in param_ids],
              [Input('vary-selection', 'value')])
def disable_inputs(selected_index):
    output = [False, False, False, False, False]
    output[selected_index] = True
    output = tuple(output)
    return output


@app.callback(
    [Output(name + '-slider-output', 'children') for name in param_ids],
    [Input(name + '-slider', 'value') for name in param_ids])
def update_slider_value(*args):
    global params
    output = []
    for index, value in enumerate(args):
        name = param_names[index]
        params[name] = params_lambdas(value)[index]
        output.append(value)
    return tuple(output)


# @app.callback(
#     Output('init-wealth-slider-output', 'children'),
#     [Input('init-wealth-slider', 'value')])
# def update_init_wealth(value):
#     global params
#     params['INITIAL_WEALTH'] = lambda: value + 100 * np.random.uniform()
#     return f'{value}'

# @app.callback(
#     Output('init-price-slider-output', 'children'),
#     [Input('init-price-slider', 'value')])
# def update_init_price(value):
#     global params
#     params['INITIAL_PRICE'] = lambda: value + 100 * np.random.uniform()
#     return f'{value}'

# @app.callback(
#     Output('amen-coef-slider-output', 'children'),
#     [Input('amen-coef-slider', 'value')])
# def update_amen_coef(value):
#     global params
#     params['INITIAL_WEALTH'] = value
#     return f'{value}'

# @app.callback(
#     Output('loc-coef-slider-output', 'children'),
#     [Input('loc-coef-slider', 'value')])
# def update_loc_coef(value):
#     global params
#     params['INITIAL_PRICE'] = value
#     return f'{value}'

# @app.callback(
#     Output('no-born-slider-output', 'children'),
#     [Input('no-born-slider', 'value')])
# def update_no_born(value):
#     global params
#     params['NUM_BORN'] = lambda: np.random.binomial(value, 0.5)
#     return f'{value}'

###################################### Graph ######################################


@app.callback(
    Output('heatmap-graph', 'figure'),
    [Input('interval-component', 'n_intervals')])
def update_heatmap_graph(n):
    global heatmap_data
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


@app.callback([
    Output('run-count-text', 'children'),
    Output('sim-count-text', 'children')
], [Input('interval-component', 'n_intervals')])
def update_run_count(n):
    return run_counter, sim_t


@app.callback(
    Output('output-graph', 'figure'), [Input('output-metric-select', 'value')])
def gen_market_price_graph(metric_key):
    global scatter_data
    X = [
        i for i in range(
            len(run_history[list(run_history.keys())[0]][metric_key]))
    ]
    scatter_data = [
        go.Scatter(x=X, y=Y[metric_key], name=key)
        for key, Y in run_history.items()
    ]
    return {
        'data':
            scatter_data,
        'layout':
            go.Layout(
                xaxis=dict(range=[min(X), max(X)]),
                yaxis=dict(range=[
                    min([min(Y[metric_key]) for key, Y in run_history.items()]),
                    max([max(Y[metric_key]) for key, Y in run_history.items()])
                ]),
            )
    }


###################################### Buttons ######################################


@app.callback([
    Output('interval-component', 'max_intervals'),
    Output('start-button', 'disabled')
], [Input('set-params-button', 'n_clicks'),
    Input('vary-selection', 'value')])
def set_params(n, selected_index):
    if n and (n > 0):
        global runs, persons, houses, ask_df, bid_df
        runs = {}
        param_to_vary = param_names[selected_index]
        param_to_vary_vals = [
            param_min_max[selected_index][0] +
            i * param_min_max[selected_index][2] for i in range(10)
        ]
        for val in param_to_vary_vals:
            params[param_to_vary] = params_lambdas(val)[selected_index]
            runs[str(param_to_vary) + ' = ' + str(val)] = params
        return -1, False
    else:
        return 0, True


@app.callback([
    Output("sim-completion-text", "children"),
    Output('output-metric-select', 'disabled')
], [Input('start-button', 'n_clicks')])
def start_sim(n):
    global sim_t, run_counter, run_history
    global persons, houses, ask_df, bid_df
    if (n is not None):
        run_counter = 0
        for key, params in runs.items():
            print('A0')
            history = defaultdict(list)
            persons, houses, ask_df, bid_df = initialize(params)
            sim_t = 0
            print('A1')
            for i in range(params['NUM_FRAMES']):
                sim_t += 1
                print('B0')
                persons, houses, ask_df, bid_df = simulate(
                    params, persons, houses, ask_df, bid_df)
                print('B1')
                update_history(history, persons, houses)
                print('B2')
                print(run_counter, sim_t)
            print('A2')
            run_history[key] = history
            run_counter += 1
        print(run_history)
        return 1, False
    return 0, True


if __name__ == "__main__":
    app.run_server(debug=True)
    pass