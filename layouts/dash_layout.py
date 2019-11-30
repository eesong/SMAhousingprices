from dash.dependencies import Input, Output
import pandas as pd
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from common import func2str


def create_navbar():
    return dbc.NavbarSimple(
        children=[
            html.Div(id='refresh_time', className='mr-3 mt-2 text-muted'),
            # dbc.Button(
            #     "Refresh",
            #     id='button_refresh',
            #     color="primary",
            #     className="mr-1")
        ],
        brand="Housing Prices Simulation",
        brand_href="#",
        sticky="top",
    )


def create_card(id, value, unit, name, threshold=None):
    if (threshold != None) and (round(float(value)) >= threshold):
        styling = 'text-success'
    else:
        styling = ''
    return dbc.Card(
        dbc.CardBody([
            html.H3(
                str(round(float(value))) + unit,
                id=id,
                className=f"card-title {styling}"),
            html.H6(name, className="small"),
        ],
            className="align-items-center"),
        className="text-center",
    )


def params_card(params_dict):

    table_header = [
        html.Thead(html.Tr([html.Th("Parameter"), html.Th("Value")]))
    ]

    rows = []
    for key, value in params_dict.items():
        if callable(value):
            value = func2str(value)
        row = html.Tr([html.Td(str(key)), html.Td(str(value))])
        rows.append(row)

    table_body = [html.Tbody(rows)]

    table = dbc.Table(
        table_header + table_body,
        bordered=True,
        hover=True,
        responsive=True,
        striped=True,
        className='small',
    )
    return table


def create_tab_content(content_list, card_list, header=[], footer=[]):
    return dbc.Card(
        dbc.CardBody([
            main(header),
            create_cards_horizontal(card_list),
            main(content_list),
            main(footer)
        ]),
        className="mt-3",
    )


def main(content_list):
    return html.Div([dbc.Row([dbc.Col(content) for content in content_list])],)


def create_cards_horizontal(card_list):
    return html.Div([
        dbc.Row([dbc.Col(card) for card in card_list]),
    ])


def create_radio(card_list):
    return dbc.Row([
        dbc.Col(
            dbc.FormGroup([
                dbc.RadioItems(
                    options=[{
                        "value": i
                    } for i in range(len(card_list))],
                    value=0,
                    id="vary-selection",
                    inputClassName='py-5 my-3',
                    # className='d-flex flex-column justify-content-between'
                ),
            ]),
            style={'max-width': 50},
            align="center",
        ),
        dbc.Col(
            html.Div([html.Div(card) for card in card_list],
                     className='d-flex flex-column justify-content-between')
        ),
    ])


def create_cards_vertical(card_list):
    return html.Div([
        html.Div(card) for card in card_list])


def create_tabs(tab_content_list, tab_name_list):
    tabs = zip(tab_content_list, tab_name_list)
    return dbc.Container(
        [dbc.Tabs([dbc.Tab(content, label=name) for content, name in tabs])],
        className="mt-4")


def create_slider(label, name, values):
    min, max, step, value = values
    return dbc.Card(
        dbc.CardBody([
            html.Div(label),
            dcc.Slider(
                id=name + '-slider',
                min=min,
                max=max,
                step=step,
                value=value,
            ),
            html.Div(id=name + '-slider-output', className='text-right small'),
        ]),
        style={'width': 500},
        className='m-2')
