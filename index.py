from modules.m_initialization import initialize
from layouts.dash_layout import create_tabs, main, create_cards_horizontal, create_card, create_tab_content, create_navbar, create_slider, params_card, create_radio
from initialization_params import params as init_params
from common import generate_min_max, Nmean_to_logNmean
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

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL])
server = app.server

params = init_params
run_history = {}

scatter_data = [[]]

runs = {'params': params}
persons, houses, ask_df, bid_df = initialize(params)
run_counter = 0
sim_t = 0

param_ids = [
    'init-income',
    'init-price',
    'amen-coef',
    'loc-coef',
    'no-born',
    'prob-buy',
]
param_names = [
    'INCOME',
    'INITIAL_PRICE',
    'AMENITIES_COEF',
    'LOC_COEF',
    'NUM_BORN',
    'PROBA_BUY',
]
param_min_max = [
    generate_min_max(20, 5),
    generate_min_max(100, 50),
    generate_min_max(0, .5),
    generate_min_max(0, .5),
    generate_min_max(10, 2),
    generate_min_max(0, .1),
]
slider_labels = [
    'Income Mean ($,000s)',
    'Initialization House Price ($,000s)',
    'WTP $/Unit Amenities ($,000s)',
    'WTP $/Unit Distance ($,000s)',
    'Max Number of People Born',
    'Probability of Buying Intention'
]


def params_lambdas(value): return [
    lambda: np.random.lognormal(
        Nmean_to_logNmean(value*1000, 2109460174/1000), 0.65745)/1000,
    lambda: value + 100 * np.random.uniform(),
    value,
    value,
    lambda: np.random.binomial(value, 0.5),
    value
]


output_metrics = {
    'Mean Market Price of Houses': 'mean_market_price',
    'Occupancy Rate of Houses': 'occupancy_rate',
    'Standard Deviation of Market Price of Houses': 'sd_market_price',
    'Homelessness Rate of Persons': 'homeless_rate',
    'Total Utility of Persons': 'total_utility',
    'Standard Deviation of Utility of Persons': 'sd_utility',
    'Transactions Made': 'transactions_made',
}

params_content = [
    create_radio([
        create_slider(slider_labels[i], param_ids[i], param_min_max[i])
        for i in range(len(param_names))
    ]),
    dbc.Button("Set Parameters!", id="set-params-button", className="mr-2"),
]

main_content = [
    dbc.Button(
        "Start Simulation!", id="start-button", disabled=True,
        className="m-3"),
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
        disabled=False),
    dcc.Graph(id='output-graph', style={'height': 800}),
    html.Div(id='table')
]

main_cards = [
    create_card('run-count-text', run_counter, '/10', '# Runs', 10),
    create_card('sim-count-text', sim_t, '', 'Years passed in run'),
    create_card('sim-completion-text', 0, '', 'Simulation complete', 1),
]

main_tab = create_tab_content([main_content], main_cards)
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
    output = [False for i in range(len(param_names))]
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
        output.append(round(value, 2))
    return tuple(output)

###################################### Graph ######################################


@app.callback(
    Output('heatmap-graph', 'figure'),
    [Input('interval-component', 'n_intervals')])
def update_heatmap_graph(n):
    global heatmap_data
    heatmap_data = [[
        round(houses.iloc[i + j * 10]['last_bought_price'], 2) for i in range(10)
    ] for j in range(10)]
    def text(
        LOC, LBP, A, S): return f'Location: {LOC}<br />Last Bought Price: {LBP}<br />Amenities: {A}<br />Status: {S}'
    text_data = [[
        text(
            str(houses.iloc[i + j * 10]['location']),
            str(round(houses.iloc[i + j * 10]['last_bought_price'], 2)),
            str(round(houses.iloc[i + j * 10]['amenities'], 2)),
            str(houses.iloc[i + j * 10]['status']),
        ) for i in range(10)] for j in range(10)]
    return {
        'data': [
            go.Heatmap(
                z=heatmap_data,
                y=[i for i in range(10)],
                x=[i for i in range(10)],
                hoverinfo='text',
                text=text_data)
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
                    min([min(Y[metric_key])
                         for key, Y in run_history.items()]),
                    max([max(Y[metric_key]) for key, Y in run_history.items()])
                ]),
            )
    }


###################################### Buttons ######################################


@app.callback([
    Output('interval-component', 'max_intervals'),
    Output('start-button', 'disabled'),
    Output('table', 'children'),
], [Input('set-params-button', 'n_clicks'),
    Input('vary-selection', 'value')])
def set_params(n, selected_index):
    global runs, persons, houses, ask_df, bid_df
    table = params_card(runs[list(runs.keys())[0]])
    if n and (n > 0):
        runs = {}
        param_to_vary = param_names[selected_index]
        param_to_vary_vals = [
            param_min_max[selected_index][0] +
            i * param_min_max[selected_index][2] for i in range(10)
        ]
        for val in param_to_vary_vals:
            run_params = copy.deepcopy(params)
            run_params[param_to_vary] = params_lambdas(val)[selected_index]
            runs[str(param_to_vary) + ' = ' + str(val)] = run_params
        return -1, False, table
    else:
        return 0, True, table


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
            # print('A0')
            print('Now running for: ', params)
            history = defaultdict(list)
            persons, houses, ask_df, bid_df = initialize(params)
            sim_t = 0
            # print('A1')
            for i in range(params['NUM_FRAMES']):
                sim_t += 1
                # print('B0')
                persons, houses, ask_df, bid_df, match_df = simulate(
                    params, persons, houses, ask_df, bid_df)
                # print('B1')
                update_history(history, persons, houses, match_df)
                # print('B2')
                print(run_counter, sim_t)
            # print('A2')
            run_history[key] = history
            run_counter += 1
        print(run_history)
        return 1, False
    return 0, True


if __name__ == "__main__":
    app.run_server(debug=True)
    pass
