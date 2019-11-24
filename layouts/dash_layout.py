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


def create_card(value, unit, name, threshold=None):
    if (threshold != None) and (round(float(value)) < threshold):
        styling = 'text-danger'
    else:
        styling = 'text-success'
    return dbc.Card(
        dbc.CardBody([
            html.H3(
                str(round(float(value))) + unit,
                className=f"card-title {styling}"),
            html.H6(name, className="small"),
        ],
                     className="align-items-center"),
        className="text-center",
    )


def create_tab_content(content_list, card_list, footer=[]):
    return dbc.Card(
        dbc.CardBody([
            create_cards_horizontal(card_list),
            main(content_list),
            main(footer)
        ]),
        className="mt-3",
    )


def main(content_list):
    if len(content_list) == 0:
        return html.Div()
    content1 = content_list.pop(0)
    return html.Div([
        dbc.Row([dbc.Col(content1, md=5)] +
                [dbc.Col(content) for content in content_list])
    ],)


def create_cards_horizontal(card_list):
    return html.Div([
        dbc.Row([dbc.Col(card) for card in card_list]),
    ])


def create_tabs(tab_content_list, tab_name_list):
    tabs = zip(tab_content_list, tab_name_list)
    return dbc.Container(
        [dbc.Tabs([dbc.Tab(content, label=name) for content, name in tabs])],
        className="mt-4")
