from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import graphs
import data
import cards
from flask_caching import Cache
import datetime
import os


meta_tags = [
    {
        "name": "description",
        "content": "COVID-19 - Greece analytics"
    },
    {
        "name": "viewport",
        "content": "width=device-width, initial-scale=1.0"
    },
    {
        "name": "author",
        "content": "Marios Siganos"
    },
    {
        "name": "keywords",
        "content": "covid19, covid-19, coronavirus, python, dash, plotly, \
                    bootstrap, data, analytics, visualizations"
    }
]


app = Dash(__name__,  assets_ignore='.*ignored.*', meta_tags=meta_tags)
app.title = "COVID 19 - GREECE ANALYTICS"
server = app.server

cache = Cache(app.server, config={
    'CACHE_TYPE': os.environ.get('APP_CACHE_TYPE', 'FileSystemCache'),
    'CACHE_DIR': 'cache-directory',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', '')
})

# App layout elements
layout_navbar = dbc.Navbar(
    [
        html.Div([
            html.I(className="fas fa-chart-pie"),
            " COVID 19 - GREECE ANALYTICS ",
        ],
        className="navbar-brand"
        ),
    ],
    fixed="top",
    color="primary",
    dark=True,
    class_name="font-weight-bold bg-gradient-primary"
)

layout_footer = dbc.Navbar(
    [
        html.Div([
            "Created by ",
            html.A(
                "msiganos",
                href="https://about.me/msiganos",
                target="_blank",
                className="text-danger"
            ),
            " using Plotly Dash",
        ]),
        html.Div(
            dbc.Button(
                html.I(className="fas fa-info-circle"),
                id="open-info-modal",
                color="danger",
                class_name="btn-circle btn-sm text-white"
            ),

            className="ml-md-auto"
        )
    ],
    fixed="bottom",
    color="primary",
    dark=True,
    class_name="font-weight-bold text-white bg-gradient-primary"
)

layout_modal = dbc.Modal(
    [
        dbc.ModalHeader("About"),
        dbc.ModalBody(
            dcc.Markdown(
                """
                ### COVID 19 - GREECE ANALYTICS

                A simple data analytics app about COVID-19 in Greece.

                Created using [plotly Dash](https://dash.plotly.com).
                
                Inspired by [covid19-live-analytics by gov.gr](https://covid19.gov.gr/covid19-live-analytics) ([innews](https://covid19.innews.gr/en)).

                **Technology**:
                - Dash (based on Flask, Plotly.js and React.js)
                - Bootstrap and Dash Bootstrap Components
                - Deployed on Heroku
                
                **Data sources**: [NPHO](https://eody.gov.gr/en) (same data as the apps above)

                **Creator**: [Marios Siganos](https://about.me/msiganos)
                
                **Contact**: [E-mail](mailto:marios.siganos@gmail.com)
                """
            )
        )
    ],
    id="info-modal"
)


# App layout
@cache.memoize(timeout=300)  # in seconds
def create_layout():
    data.load_new_data(save=True)
    return html.Div([
        layout_navbar,

        dbc.Container(
            [
                dbc.Row(
                    [
                        html.H2("Dashboard"),
                        html.Div(
                            f"Last updated: ({data.df_daily_stats.iloc[-1]['date']})",
                            className="text-xs align-self-end mb-2"
                        )
                    ],
                    class_name="text-primary"
                ),
                dbc.Row(
                        [
                            dbc.Col(
                                cards.generate_info_card(
                                    "Cases",
                                    html.Div([
                                        f"{data.df_daily_stats.iloc[-1]['cases']:,} ",
                                        html.Span(
                                            f"{data.df_daily_stats.iloc[-1]['intubated']} INTUBATED",
                                            className="badge badge-pill badge-cases-critical text-xs"
                                        )
                                    ]),
                                    html.Div([
                                        f"Total: {data.df_daily_stats.iloc[-1]['total_cases']:,}",
                                    ]),
                                    "cases-total",
                                    "fa-plus-square"
                                ),
                                # lg=3,
                                sm=6,
                                class_name="mb-4"
                            ),
                            dbc.Col(
                                cards.generate_info_card(
                                    "Deaths",
                                    html.Div([
                                        f"{data.df_daily_stats.iloc[-1]['deceased']:,}",
                                    ]),
                                    html.Div([
                                        f"Total: {data.df_daily_stats.iloc[-1]['total_deceased']:,}",
                                        html.Span(
                                            f" ({data.df_daily_stats.iloc[-1]['total_deceased']/data.df_daily_stats.iloc[-1]['total_cases'] * 100:.2f}%)",
                                            className="text-xs"
                                        ),
                                    ]),
                                    "cases-deceased",
                                    "fa-skull-crossbones"
                                ),
                                # lg=3,
                                sm=6,
                                class_name="mb-4"
                            ),
                        ]
                    ),
        
                    dbc.Row(
                            [
                                dbc.Col(
                                    cards.generate_card(
                                        "Timeline",
                                        html.Div([
                                            dcc.RadioItems(['Daily', '3-day average', 'Weekly average', 'Running total'], 'Daily', id='input-line'),
                                            dcc.Graph(
                                                id='graph-daily',
                                                figure=graphs.daily_line_chart(),
                                                config = {'toImageButtonOptions': {'scale': 3}}
                                            )
                                        ])
                                    ),
                                    class_name="mb-4"
                                ),
                            ]
                    ),
                    dbc.Row(
                            [
                                dbc.Col(
                                    cards.generate_card(
                                        "Age groups",
                                        dcc.Graph(
                                            id='graph-age-group',
                                            figure=graphs.age_group_bar_chart(),
                                            config={
                                                'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
                                                'toImageButtonOptions': {'scale': 3}
                                            }
                                        ),
                                    ),
                                    class_name="mb-4"
                                ),
                            ]
                    ),
                    dbc.Row(
                            [
                                dbc.Col(
                                    cards.generate_card(
                                        "Info per gender",
                                        html.Div([
                                            dcc.RadioItems(['Cases', 'Deceased', 'Intubated'], 'Cases', id='input-gender-pie'),
                                            dcc.Graph(
                                                id='graph-info-by-gender',
                                                figure=graphs.info_by_gender_pie_chart('cases'),
                                                config = {'toImageButtonOptions': {'scale': 3}}
                                            )
                                        ])
                                    ),
                                    md=6,
                                    class_name="mb-4"
                                ),
                                dbc.Col(
                                    cards.generate_card(
                                        "Info per age group and gender",
                                        html.Div([
                                            dcc.RadioItems(['Cases', 'Deceased', 'Intubated'], 'Cases', id='input-sunburst'),
                                            dcc.Graph(
                                                id='graph-info-by-age-group-and-gender',
                                                figure=graphs.info_by_age_group_and_gender_sunburst_chart('cases'),
                                                config = {'toImageButtonOptions': {'scale': 3}}
                                            )
                                        ])
                                    ),
                                    md=6,
                                    class_name="mb-4"
                                ),
                            ]
                    ),
            ],
            fluid=True,
            class_name="main"
        ),

        layout_footer,
        layout_modal,
    ])

app.layout = create_layout

# Callbacks

# Callback for daily line chart radio buttons
@app.callback(
    Output(component_id='graph-daily', component_property='figure'),
    Input(component_id='input-line', component_property='value'),
    prevent_initial_call=True
)
def update_output_div(input_value):
    return graphs.daily_line_chart(input_value)

# Callback for gender pie chart radio buttons
@app.callback(
    Output(component_id='graph-info-by-gender', component_property='figure'),
    Input(component_id='input-gender-pie', component_property='value'),
    prevent_initial_call=True
)
def update_output_div(input_value):
    return graphs.info_by_gender_pie_chart(input_value.lower())


# Callback for sunburst
@app.callback(
    Output(component_id='graph-info-by-age-group-and-gender', component_property='figure'),
    Input(component_id='input-sunburst', component_property='value'),
    prevent_initial_call=True
)
def update_output_div(input_value):
    return graphs.info_by_age_group_and_gender_sunburst_chart(input_value.lower())


# Callback for modal
@app.callback(
    Output("info-modal", "is_open"),
    [Input("open-info-modal", "n_clicks")],
    [State("info-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open


if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0")
