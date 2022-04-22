import dash_bootstrap_components as dbc
from dash import html

# Generate card layout for information cards
def generate_card(header, body, footer=None):
    card = []

    card.append(
        dbc.CardHeader(
            header,
            className="font-weight-bold text-primary")
    )

    card.append(
        dbc.CardBody(body)
    )

    if footer:
        card.append(dbc.CardFooter(footer))

    return dbc.Card(card, className="shadow")

# Generate card layout for cards with graphs
def generate_info_card(title, value, value2, info_type="", icon=None):

    if info_type in (
        'cases-total', 'cases-active', 'cases-critical',
            'cases-deceased', 'cases-recovered'):
        class_title = "text-"+info_type
        class_card_border = "border-left-"+info_type
    else:
        class_title = ""
        class_card_border = ""

    card = dbc.CardBody(
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            title,
                            className="font-weight-bold text-uppercase mb-1 " +
                            class_title #text-xs 
                        ),
                        html.Div(
                            value,
                            className="mb-0 font-weight-bold text-gray-800"),
                        html.Div(
                            value2,
                            className="mb-0 font-weight-bold text-gray-800")
                    ],
                    className="mr-2"
                ),
                dbc.Col(
                    html.I(className="fas fa-2x text-gray-300 "+icon),
                    className="col-auto"
                )
            ],
            className="no-gutters align-items-center"
        )

    )

    return dbc.Card(card, className="shadow "+class_card_border)
