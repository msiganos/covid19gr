import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import data


template = 'plotly_white'
# template = 'plotly_dark'

# Functions to create Plotly charts

# Timeline
# Chart type: line chart (Scatter)
# Data: df_daily_stats / df_three_days_stats / df_weekly_stats
# Input: Daily / 3-day average / Weekly average / Running total
def daily_line_chart(input='Daily'):
    options = {
        'Daily': data.df_daily_stats,
        '3-day average': data.df_three_days_stats,
        'Weekly average': data.df_weekly_stats,
        'Running total': data.df_daily_stats
    }
    df = options[input].copy()

    categories = ['cases', 'deceased', 'intubated']
    secondary = ['positivity', 'fatality']

    if input=='Running total':
        df = df[['date', 'calculated_cases_cumsum', 'calculated_deceased_cumsum']].rename(columns={'calculated_cases_cumsum':'cases', 'calculated_deceased_cumsum':'deceased'})
        categories = ['cases', 'deceased']
    
    if input != 'Daily':
        secondary = []

    fig = make_subplots(specs=[[{'secondary_y': True, 'r': -0.05}]])

    for cat in categories:
        fig.add_trace(
            go.Scatter(
                x=df['date'].to_list(),
                y=df[cat].to_list(),
                mode='lines', # +markers
                name=cat.capitalize(),
                legendgroup="group1",
                legendgrouptitle_text="Primary axis",
            ),
            secondary_y=False,
        )

    if input == 'Daily':
        fig.add_trace(
            go.Scatter(
                x=df['date'].to_list(),
                y=df['calculated_tests_total'].to_list(),
                mode='lines', # +markers
                name='Tests',
                visible='legendonly',
                legendgroup="group1",
            ),
            secondary_y=False,
        )

    for item in secondary:
        fig.add_trace(
            go.Scatter(
                x=df['date'].to_list(),
                y=df['calculated_'+item.lower()].to_list(),
                mode='lines', # +markers
                name=item.capitalize() + " (%)",
                line_dash='dot',
                legendgroup="group2",
                legendgrouptitle_text="Secondary axis",
                visible='legendonly'
            ),
            secondary_y=True,
        )

    fig.update_layout({
        'margin': {'l': 0, 'b': 0, 't': 0, 'r': 0},
        'yaxis': {'fixedrange': True, 'hoverformat': ','},
        'yaxis2': {'fixedrange': True, 'hoverformat': '.2f', 'showgrid': False,},
        # 'xaxis': {'fixedrange': True},
        'hovermode': 'x unified',
        'legend': {'x': 0, 'y': 1, 'groupclick': 'toggleitem', 'orientation': 'h', 'bgcolor': 'rgba(0,0,0,0)'},
        'template': template,
    })

    fig.update_yaxes(rangemode='tozero')

    return fig


# Info by gender
# Chart type: Pie chart
# Data: df_total_stats
# Input: Cases / Deceased / Intubated
def info_by_gender_pie_chart(cat):
    df = data.df_total_stats.copy()

    fig = go.Figure(
        data=[
            go.Pie(
                labels=df['gender'].unique().tolist(),
                values=df.groupby(['category', 'gender'])[['value']].sum().loc[cat,'value'].to_list(),
                hole=0.4,
                textinfo='label+percent',
                name='',
                hoverinfo='label+value'
            )
        ]
    )

    fig.update_layout(
        margin = {'l': 0, 'b': 0, 't': 0, 'r': 0},
        template = template,
        showlegend=False,
    )

    series_deceased_by_gender = df[df['category']=='deceased'].groupby('gender')['value'].sum()
    series_cases_by_gender = df[df['category']=='cases'].groupby('gender')['value'].sum()
    series_fatality_by_gender = series_deceased_by_gender / series_cases_by_gender * 100

    if cat=='deceased':
        fig.update_traces(
            hovertext = [f'Fatality: {val:.3f} %' for val in series_fatality_by_gender.to_list()],
            hovertemplate = "%{label}<br>%{value}<br>%{text}<br>"
        )
    
    return fig


# Age groups
# Chart type: Bar chart
# Data: df_total_stats
def age_group_bar_chart():
    df = data.df_total_stats
    age_labels = np.char.replace( df['age'].unique().astype(np.str_), '_', ' to ')
    age_labels = np.char.replace( age_labels, 'plus', '+').tolist()

    categories = ['cases', 'deceased', 'intubated']

    fig = go.Figure()

    for cat in categories:
        fig.add_trace(go.Bar(
            x=age_labels,
            y=df.groupby(['category', 'age'])[['value']].sum().loc[cat,'value'].to_list(),
            name=cat.capitalize(),
        ))

    fig.update_layout({
        'margin': {'l': 30, 'b': 30, 't': 0, 'r': 0},
        'legend': {'x': 0, 'y': 1.0},
        'yaxis': {'fixedrange': True, 'hoverformat': ','},
        'xaxis': {'fixedrange': True},
        'hovermode': 'x unified',
        'template': template
    })

    series_deceased_by_age = df[df['category']=='deceased'].groupby('age')['value'].sum()
    series_cases_by_age = df[df['category']=='cases'].groupby('age')['value'].sum()
    series_fatality_by_age = series_deceased_by_age / series_cases_by_age * 100

    fig.update_traces(
        hovertext = [f'Fatality: {val:.3f} %' for val in series_fatality_by_age.to_list()],
        selector=dict(name="Deceased")
    )

    return fig


# Info by age group and gender
# Chart type: Sunburst chart
# Data: df_total_stats
# Input: Cases / Deceased / Intubated
def info_by_age_group_and_gender_sunburst_chart(cat):
    df = data.df_total_stats.copy()

    series_deceased_by_age = df[df['category']=='deceased'].groupby('age')['value'].sum()
    series_cases_by_age = df[df['category']=='cases'].groupby('age')['value'].sum()
    series_fatality_by_age = series_deceased_by_age / series_cases_by_age * 100

    series_deceased_by_age_and_gender = df[df['category']=='deceased'].groupby(['age', 'gender'])['value'].sum()
    series_cases_by_age_and_gender = df[df['category']=='cases'].groupby(['age', 'gender'])['value'].sum()
    series_fatality_by_age_and_gender = series_deceased_by_age_and_gender / series_cases_by_age_and_gender * 100

    df_fatality_by_age_and_gender = series_fatality_by_age_and_gender.reset_index()
    df_fatality_by_age_and_gender['ids'] = df_fatality_by_age_and_gender['age'] + '/' + df_fatality_by_age_and_gender['gender']
    df_fatality_by_age_and_gender.set_index('ids', inplace=True)

    df = df[df['category']==cat]
    df['age'].replace({'0_17': '0 to 17', '18_39': '18 to 39', '40_64': '40 to 64', '65plus': '65+'}, inplace=True)

    fig_tmp = px.sunburst(df, path=['age', 'gender'], values='value')
    fig_ids = [ item.replace(' to ', '_').replace('+', 'plus') for item in fig_tmp.data[0].ids]

    sunburst_fatality_values = df_fatality_by_age_and_gender.loc[fig_ids[0:-4]]['value'].to_list()
    sunburst_fatality_values.extend(series_fatality_by_age.loc[fig_ids[-4:]].to_list())

    fig = go.Figure()

    fig.add_trace(go.Sunburst(
        ids=fig_tmp.data[0].ids,
        labels= fig_tmp.data[0].labels,
        parents=fig_tmp.data[0].parents,
        values=fig_tmp.data[0].values,
        branchvalues="total",
        name=cat,
    ))

    fig.update_layout(
        margin = dict(t=0, l=0, r=0, b=0),
        template = template
    )

    fig.update_traces(
        textinfo="label+percent parent",
        insidetextorientation='horizontal',
    )

    if cat=='deceased':
        fig.update_traces(
            hovertext = [f'Fatality: {val:.3f} %' for val in sunburst_fatality_values],
        )
    
    return fig