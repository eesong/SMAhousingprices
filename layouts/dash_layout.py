from dash.dependencies import Input, Output
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html


def create_navbar():
    return dbc.NavbarSimple(
        children=[
            html.Div(id='refresh_time', className='mr-3 mt-2 text-muted'),
            dbc.Button(
                "Refresh",
                id='button_refresh',
                color="primary",
                className="mr-1")
        ],
        brand="Jobtech Dashboard",
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


def create_cards_vertical(card_list):
    return dbc.Row([
        dbc.Col(
            dbc.FormGroup([
                dbc.RadioItems(
                    options=[{
                        "value": i
                    } for i in range(len(card_list))],
                    value=0,
                    id="vary-selection",
                    inputClassName='py-5',
                ),
            ]),
            className='text-right',
            style={'max-width': 50}),
        html.Div([dbc.Row([dbc.Col(card)]) for card in card_list],
                 className='d-flex flex-column justify-content-between'),
    ])


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
        style={'width': 400},
        className='m-2')
