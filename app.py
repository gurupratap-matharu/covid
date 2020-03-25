import glob
import io
import re
from datetime import date, timedelta

# Using plotly + cufflinks in offline mode
import cufflinks
import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
# Standard plotly imports
import plotly.graph_objects as go
import requests
from dash.dependencies import Input, Output
from plotly.offline import init_notebook_mode, iplot

cufflinks.go_offline(connected=True)
init_notebook_mode(connected=True)


app = dash.Dash(__name__)
server = app.server
app.config.suppress_callback_exceptions = True
app.title = 'COVID-19'

data = pd.read_csv('dashboard_data.csv')
data['date'] = pd.to_datetime(data['date'])

geo_us = pd.read_csv('geo_us.csv')

colors = {
    'background': '#FFFFFF',
    'text': '#2b2b2b',
    'grid': '#d3d8d6',
    'red': '#ef493e'
}

available_countries = sorted(data['Country/Region'].unique())

states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California',
          'Colorado', 'Connecticut', 'Delaware', 'District of Columbia', 'Florida',
          'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky',
          'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi',
          'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico',
          'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania',
          'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
          'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']

eu = ['Albania', 'Andorra', 'Austria', 'Belarus', 'Belgium', 'Bosnia and Herzegovina',
      'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France',
      'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy', 'Kosovo', 'Latvia', 'Liechtenstein',
      'Lithuania', 'Luxembourg', 'Malta', 'Moldova', 'Monaco', 'Montenegro', 'Netherlands', 'North Macedonia', 'Norway',
      'Poland', 'Portugal', 'Romania', 'San Marino', 'Serbia', 'Slovakia', 'Slovenia', 'Spain', 'Sweden',
      'Switzerland', 'Turkey', 'Ukraine', 'United Kingdom', 'Vatican City']

region_options = {'Worldwide': available_countries, 'United States': states, 'Europe': eu}

df_us = data[data['Province/State'].isin(states)]
df_eu = data[data['Country/Region'].isin(eu)]
df_eu = df_eu.append(pd.DataFrame({'date': [pd.to_datetime('2020-01-22'), pd.to_datetime('2020-01-23')],
                                   'Country/Region': ['France', 'France'],
                                   'Province/State': [np.nan, np.nan],
                                   'Confirmed': [0, 0],
                                   'Deaths': [0, 0],
                                   'Recovered': [0, 0],
                                   'Latitude': [np.nan, np.nan],
                                   'Longitude': [np.nan, np.nan],
                                   'Active': [0, 0]})).sort_index()

df_us.drop('Country/Region', axis=1, inplace=True)
df_us.rename(columns={'Province/State': 'Country/Region'}, inplace=True)


@app.callback(
    Output('confirmed_ind', 'figure'),
    [Input('global_format', 'value')])
def confirmed(view):
    if view == 'Worldwide':
        df = data
    elif view == 'United States':
        df = df_us
    elif view == 'Europe':
        df = df_eu
    else:
        df = data

    value = df[df['date'] == df['date'].iloc[-1]]['Confirmed'].sum()
    delta = df[df['date'] == df['date'].unique()[-2]]['Confirmed'].sum()
    return {
        'data': [{'type': 'indicator',
                  'mode': 'number+delta',
                  'value': value,
                  'delta': {'reference': delta,
                            'valueformat': '.2%',
                            'relative': True,
                            'font': {'size': 25}},
                  'number': {'valueformat': ',',
                             'font': {'size': 50}},
                  'domain': {'y': [0, 1], 'x': [0, 1]}}],
        'layout': go.Layout(
            title={'text': "CUMULATIVE CONFIRMED"},
            font=dict(color=colors['red']),
            paper_bgcolor=colors['background'],
            plot_bgcolor=colors['background'],
            height=200
        )
    }


@app.callback(
    Output('active_ind', 'figure'),
    [Input('global_format', 'value')])
def active(view):
    if view == 'Worldwide':
        df = data
    elif view == 'United States':
        df = df_us
    elif view == 'Europe':
        df = df_eu
    else:
        df = data

    value = df[df['date'] == df['date'].iloc[-1]]['Active'].sum()
    delta = df[df['date'] == df['date'].unique()[-2]]['Active'].sum()
    return {
        'data': [{'type': 'indicator',
                  'mode': 'number+delta',
                  'value': value,
                  'delta': {'reference': delta,
                            'valueformat': '.2%',
                            'relative': True,
                            'font': {'size': 25}},
                  'number': {'valueformat': ',',
                             'font': {'size': 50}},
                  'domain': {'y': [0, 1], 'x': [0, 1]}}],
        'layout': go.Layout(
            title={'text': "CURRENTLY ACTIVE"},
            font=dict(color=colors['red']),
            paper_bgcolor=colors['background'],
            plot_bgcolor=colors['background'],
            height=200
        )
    }


@app.callback(
    Output('recovered_ind', 'figure'),
    [Input('global_format', 'value')])
def recovered(view):
    if view == 'Worldwide':
        df = data
    elif view == 'United States':
        df = df_us
    elif view == 'Europe':
        df = df_eu
    else:
        df = data

    value = df[df['date'] == df['date'].iloc[-1]]['Recovered'].sum()
    delta = df[df['date'] == df['date'].unique()[-2]]['Recovered'].sum()
    return {
        'data': [{'type': 'indicator',
                  'mode': 'number+delta',
                  'value': value,
                  'delta': {'reference': delta,
                            'valueformat': '.2%',
                            'relative': True,
                            'font': {'size': 25}},
                  'number': {'valueformat': ',',
                             'font': {'size': 50}},
                  'domain': {'y': [0, 1], 'x': [0, 1]}}],
        'layout': go.Layout(
            title={'text': "RECOVERED CASES"},
            font=dict(color=colors['red']),
            paper_bgcolor=colors['background'],
            plot_bgcolor=colors['background'],
            height=200
        )
    }


@app.callback(
    Output('deaths_ind', 'figure'),
    [Input('global_format', 'value')])
def deaths(view):
    if view == 'Worldwide':
        df = data
    elif view == 'United States':
        df = df_us
    elif view == 'Europe':
        df = df_eu
    else:
        df = data

    value = df[df['date'] == df['date'].iloc[-1]]['Deaths'].sum()
    delta = df[df['date'] == df['date'].unique()[-2]]['Deaths'].sum()
    return {
        'data': [{'type': 'indicator',
                  'mode': 'number+delta',
                  'value': value,
                  'delta': {'reference': delta,
                            'valueformat': '.2%',
                            'relative': True,
                            'font': {'size': 25}},
                  'number': {'valueformat': ',',
                             'font': {'size': 50}},
                  'domain': {'y': [0, 1], 'x': [0, 1]}}],
        'layout': go.Layout(
            title={'text': "DEATHS TO DATE"},
            font=dict(color=colors['red']),
            paper_bgcolor=colors['background'],
            plot_bgcolor=colors['background'],
            height=200
        )
    }


@app.callback(
    Output('worldwide_trend', 'figure'),
    [Input('global_format', 'value')])
def worldwide_trend(view):
    if view == 'Worldwide':
        df = data
    elif view == 'United States':
        df = df_us
    elif view == 'Europe':
        df = df_eu
    else:
        df = data

    traces = [go.Scatter(
        x=df.groupby('date')['date'].first(),
        y=df.groupby('date')['Confirmed'].sum(),
        name="Confirmed",
        mode='lines'),
        go.Scatter(
        x=df.groupby('date')['date'].first(),
        y=df.groupby('date')['Active'].sum(),
        name="Active",
        mode='lines'),
        go.Scatter(
        x=df.groupby('date')['date'].first(),
        y=df.groupby('date')['Recovered'].sum(),
        name="Recovered",
        mode='lines'),
        go.Scatter(
        x=df.groupby('date')['date'].first(),
        y=df.groupby('date')['Deaths'].sum(),
        name="Deaths",
        mode='lines')]
    return {
        'data': traces,
        'layout': go.Layout(
            title="{} Infectados".format(view),
            xaxis_title="Date",
            yaxis_title="Cantidad de Personas",
            font=dict(color=colors['text']),
            paper_bgcolor=colors['background'],
            plot_bgcolor=colors['background'],
            xaxis=dict(gridcolor=colors['grid']),
            yaxis=dict(gridcolor=colors['grid'])
        )
    }


@app.callback(
    Output('country_select', 'options'),
    [Input('global_format', 'value')])
def set_active_options(selected_view):
    return [{'label': i, 'value': i} for i in region_options[selected_view]]


@app.callback(
    Output('country_select', 'value'),
    [Input('global_format', 'value'),
     Input('country_select', 'options')])
def set_countries_value(view, available_options):
    if view == 'Worldwide':
        return ['China', 'Italy', 'South Korea', 'US', 'Spain', 'France', 'Germany']
    elif view == 'United States':
        return ['New York', 'Washington', 'California', 'Florida', 'Texas']
    elif view == 'Europe':
        return ['France', 'Germany', 'Italy', 'Spain', 'United Kingdom']
    else:
        return ['China', 'Italy', 'South Korea', 'US', 'Spain', 'France', 'Germany']


@app.callback(
    Output('active_countries', 'figure'),
    [Input('global_format', 'value'),
     Input('country_select', 'value')])
def active_countries(view, countries):
    if view == 'Worldwide':
        df = data
    elif view == 'United States':
        df = df_us
    elif view == 'Europe':
        df = df_eu
    else:
        df = data

    traces = []
    for country in countries:
        traces.append(go.Scatter(
            x=df[df['Country/Region'] == country].groupby('date')['date'].first(),
            y=df[df['Country/Region'] == country].groupby('date')['Active'].sum(),
            name=country,
            mode='lines'))
    return {
        'data': traces,
        'layout': go.Layout(
            title="Casos activos por región",
            xaxis_title="Fecha",
            yaxis_title="Cantidad de Personas",
            font=dict(color=colors['text']),
            paper_bgcolor=colors['background'],
            plot_bgcolor=colors['background'],
            xaxis=dict(gridcolor=colors['grid']),
            yaxis=dict(gridcolor=colors['grid']),
            hovermode='closest'
        )
    }


@app.callback(
    Output('stacked_active', 'figure'),
    [Input('global_format', 'value'),
     Input('column_select', 'value')])
def stacked_active(view, column):
    if view == 'Worldwide':
        df = data
        scope = 1000
    elif view == 'United States':
        df = df_us
        scope = 20
    elif view == 'Europe':
        df = df_eu
        scope = 1000
    else:
        df = data
        scope = 1000

    traces = []
    for region in df['Country/Region'].unique():
        if df[(df['date'] == df['date'].iloc[-1]) & (df['Country/Region'] == region)]['Confirmed'].sum() > scope:
            traces.append(go.Scatter(
                x=df[df['Country/Region'] == region].groupby('date')['date'].first(),
                y=df[df['Country/Region'] == region].groupby('date')[column].sum(),
                name=region,
                hoverinfo='x+y+name',
                stackgroup='one',
                mode='none'))
    return {
        'data': traces,
        'layout': go.Layout(
            title="{} Casos {}<br>(Regiónes con mas de {} casos confirmados)".format(column, view, scope),
            xaxis_title="Fecha",
            yaxis_title="Cantidad de Personas",
            font=dict(color=colors['text']),
            paper_bgcolor=colors['background'],
            plot_bgcolor=colors['background'],
            xaxis=dict(gridcolor=colors['grid']),
            yaxis=dict(gridcolor=colors['grid']),
            hovermode='closest'
        )
    }


@app.callback(
    Output('world_map_active', 'figure'),
    [Input('global_format', 'value'),
     Input('date_slider', 'value')])
def world_map_active(view, date_index):
    if view == 'Worldwide':
        df = data
        scope = 'world'
        projection_type = 'natural earth'
    elif view == 'United States':
        df = df_us
        scope = 'usa'
        projection_type = 'albers usa'
    elif view == 'Europe':
        df = df_eu
        scope = 'europe'
        projection_type = 'natural earth'
    else:
        df = data
        scope = 'world'
        projection_type = 'natural earth',

    # World map
    date = df['date'].unique()[date_index]

    df_world_map = df[df['date'] == date].groupby('Country/Region').agg({'Confirmed': 'sum',
                                                                         'Longitude': 'mean',
                                                                         'Latitude': 'mean',
                                                                         'Country/Region': 'first'})

    if date_index > 7:
        idx7 = date_index - 7
    else:
        idx7 = 0

    df_world_map['share_of_last_week'] = ((df[df['date'] == date].groupby('Country/Region')['Confirmed'].sum() -
                                           df[df['date'] == df['date'].unique()[idx7]].groupby('Country/Region')['Confirmed'].sum()) /
                                          df[df['date'] == date].groupby('Country/Region')['Confirmed'].sum()) * 100

    df_world_map['percentage'] = df_world_map['share_of_last_week'].fillna(0).apply(lambda x: '{:.1f}'.format(x))

    # Manually change some country centroids which are mislocated due to far off colonies
    df_world_map.loc[df_world_map['Country/Region'] == 'US', 'Latitude'] = 39.810489
    df_world_map.loc[df_world_map['Country/Region'] == 'US', 'Longitude'] = -98.555759

    df_world_map.loc[df_world_map['Country/Region'] == 'France', 'Latitude'] = 46.2276
    df_world_map.loc[df_world_map['Country/Region'] == 'France', 'Longitude'] = -3.4360

    df_world_map.loc[df_world_map['Country/Region'] == 'United Kingdom', 'Latitude'] = 55.3781
    df_world_map.loc[df_world_map['Country/Region'] == 'United Kingdom', 'Longitude'] = 2.2137

    df_world_map.loc[df_world_map['Country/Region'] == 'Denmark', 'Latitude'] = 56.2639
    df_world_map.loc[df_world_map['Country/Region'] == 'Denmark', 'Longitude'] = 9.5018

    df_world_map.loc[df_world_map['Country/Region'] == 'Netherlands', 'Latitude'] = 52.1326
    df_world_map.loc[df_world_map['Country/Region'] == 'Netherlands', 'Longitude'] = 5.2913

    df_world_map.loc[df_world_map['Country/Region'] == 'Canada', 'Latitude'] = 59.050000
    df_world_map.loc[df_world_map['Country/Region'] == 'Canada', 'Longitude'] = -112.833333

    if pd.to_datetime(date).strftime('%Y-%m-%d') > '2020-03-22' and view == 'United States':
        df_world_map = df_world_map[['Confirmed', 'share_of_last_week', 'percentage']].merge(
            geo_us, left_on='Country/Region', right_on='Province/State')
        df_world_map['Country/Region'] = df_world_map['Province/State']

    df_world_map = df_world_map[df_world_map['Country/Region'] != 'Cruise Ship']

    return {
        'data': [
            go.Scattergeo(
                lon=df_world_map['Longitude'],
                lat=df_world_map['Latitude'],
                text=df_world_map['Country/Region'] + ': ' +
                ['{:,}'.format(i) for i in df_world_map['Confirmed']] +
                ' total cases, ' + df_world_map['percentage'] +
                '% from previous week',
                hoverinfo='text',
                mode='markers',
                marker=dict(reversescale=False,
                            autocolorscale=False,
                            symbol='circle',
                            size=np.sqrt(df_world_map['Confirmed'] / 5),
                            sizeref=1,
                            sizemin=0,
                            line=dict(width=.5, color='rgba(0, 0, 0)'),
                            colorscale='Reds',
                            cmin=0,
                            color=df_world_map['share_of_last_week'],
                            cmax=100,
                            colorbar=dict(
                                title="Percentage of<br>cases occurring in<br>the previous week",
                                thickness=30)
                            )
            )
        ],
        'layout': go.Layout(
            title='Number of cumulative confirmed cases (size of marker)<br>and share of new cases from the previous week (color)',
            geo=dict(scope=scope,
                     projection_type=projection_type,
                     showland=True,
                     landcolor="rgb(100, 125, 100)",
                     showocean=True,
                     oceancolor="rgb(80, 150, 250)",
                     showcountries=True,
                     showlakes=True),
            font=dict(color=colors['text']),
            paper_bgcolor=colors['background'],
            plot_bgcolor=colors['background']
        )
    }


app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(children='COVID-19',
            style={
                'textAlign': 'center',
                'color': colors['text'],
                'padding': 20,
            }
            ),

    html.Hr(),

    html.Div(
        dcc.RadioItems(
            id='global_format',
            options=[{'label': i, 'value': i} for i in ['Worldwide', 'United States', 'Europe']],
            value='Worldwide',
            labelStyle={'float': 'center', 'display': 'inline-block', 'padding-right': 100, }
        ),
        style={'textAlign': 'center',
               'color': colors['text'],
               'width': '100%',
               'float': 'center',
               'display': 'inline-block',
               }
    ),
    html.Div(
        dcc.Graph(id='confirmed_ind'),
        style={
            'textAlign': 'center',
            'color': colors['red'],
            'width': '25%',
            'float': 'left',
            'display': 'inline-block'
        }
    ),
    html.Div(
        dcc.Graph(id='active_ind'),
        style={
            'textAlign': 'center',
            'color': colors['red'],
            'width': '25%',
            'float': 'left',
            'display': 'inline-block'
        }
    ),

    html.Div(
        dcc.Graph(id='deaths_ind'),
        style={
            'textAlign': 'center',
            'color': colors['red'],
            'width': '25%',
            'float': 'left',
            'display': 'inline-block'
        }
    ),

    html.Div(
        dcc.Graph(id='recovered_ind'),
        style={
            'textAlign': 'center',
            'color': colors['red'],
            'width': '25%',
            'float': 'left',
            'display': 'inline-block'
        }
    ),
    html.Hr(),

    html.Div([
        html.Div(
            dcc.Graph(id='worldwide_trend'),
            style={'width': '50%', 'float': 'left', 'display': 'inline-block'}
        ),

        html.Div([
            dcc.Graph(id='stacked_active'),
            html.Div(dcc.RadioItems(
                id='column_select',
                options=[{'label': k, 'value': v} for k, v in dict([('Confirmados', 'Confirmed'), ('Activos', 'Active'),
                                                                    ('Recuperados', 'Recovered'), ('Muertos', 'Deaths')]).items()],
                value='Active',
                labelStyle={'float': 'center', 'display': 'inline-block'},
                style={'textAlign': 'center',
                       'color': colors['text'],
                       'width': '100%',
                       'float': 'center',
                       'display': 'inline-block'
                       }),
                     style={'width': '100%', 'float': 'center', 'display': 'inline-block'})
        ],
            style={'width': '50%', 'float': 'right', 'vertical-align': 'bottom'}
        )],
        style={'width': '98%', 'float': 'center', 'vertical-align': 'bottom'}
    ),

    html.Div([
        dcc.Graph(id='world_map_active'),
        dcc.Slider(
            id='date_slider',
            min=list(range(len(data['date'].unique())))[0],
            max=list(range(len(data['date'].unique())))[-1],
            value=list(range(len(data['date'].unique())))[-1],
            marks={(idx): (date if idx % 7 == 0 else '') for idx, date in
                   enumerate(sorted(set([item.strftime("%m-%d-%Y") for
                                         item in data['date']])))},
            step=None,
            vertical=False,
            updatemode='mouseup')],
        style={'width': '50%',
               'display': 'inline-block'}
    ),

    html.Div([
        dcc.Graph(id='active_countries'),
        dcc.Dropdown(
            id='country_select',
            multi=True,
            style={'width': '95%', 'float': 'center'}
        )],
        style={'width': '50%',
               'float': 'right',
               'display': 'inline-block'}),

    html.Div(
        dcc.Markdown(' '),
        style={
            'textAlign': 'center',
            'color': '#FEFEFE',
            'width': '100%',
            'float': 'center',
            'display': 'inline-block'}),

    html.Div(
        dcc.Markdown('''
            Built by [Greg Rafferty](https://www.linkedin.com/in/gregrafferty/)  
            Source data: [Johns Hopkins CSSE](https://github.com/CSSEGISandData/COVID-19)
            '''),
        style={
            'textAlign': 'center',
            'color': '#FEFEFE',
            'width': '100%',
            'float': 'center',
            'display': 'inline-block'}
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
