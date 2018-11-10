import os
import pandas as pd
import numpy as np
import pyodbc
import requests
import base64
from sqlalchemy import create_engine

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

from Settings import *
from Queries import *

pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 500)


app = dash.Dash()
server = app.server
app.scripts.config.serve_locally = True
dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-finance-1.28.0.min.js'


# Establish database connection to Write Records
def SQLServerConnection(config):
    conn_str = (
        'DRIVER={driver};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}')

    conn = pyodbc.connect(
        conn_str.format(**config)
    )

    return conn


def loadData(query):
    sqlData = []
    conn = SQLServerConnection(sqlconfig)

    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    for row in rows:
        sqlData.append(list(row))

    df = pd.DataFrame(sqlData)

    return df


def parseTeams(df):
    teamdict = {}
    cols = df['TeamId'].unique()

    for team in cols:
        teamdict[team] = np.array(
            df.loc[df['TeamId'] == team, 'PlayerId'])

    teamdf = pd.DataFrame(dict([(k, pd.Series(v))
                                for k, v in teamdict.items()]))
    teamdf = teamdf.fillna('')

    return teamdf


COLORS = [
    {'background': '#42a059', 'text': 'seagreen'},
    {'background': '#febe2c', 'text': 'goldenrod'},
    {'background': '#e32931', 'text': 'crimson'},
    {'background': '#4990e7', 'text': 'cornflowerblue'},
    {'background': '#d9d9d9', 'text': 'gainsboro'}]


headerstyle = {'align': 'center',
               'width': '300px',
               'background-color': '#0f6db5',
               'text-align': 'center',
               'font-size': '22px',
               'padding': '5px',
               'color': '#ffffff'}

tablestyle = {'display': 'table',
              'border-cllapse': 'separate',
              'font': '15px Open Sans, Arial, sans-serif',
              'font-weight': '30',
              'border-collapse': 'separate'}

rowstyle = {'color': 'black',
            'align': 'center',
            'text-align': 'center',
            'font-size': '40px'}

tabs_styles = {
    'height': '50px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '5px',
    'font-size': '18px'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'fontWeight': 'bold',
    'color': 'white',
    'padding': '5px',
    'font-size': '22px'
}

def localImg(image):
    encoded_image = base64.b64encode(
        open(os.getcwd() + '/TeamLogos/' + image, 'rb').read())
    return 'data:image/png;base64,{}'.format(encoded_image)


def getPlayerImage(player):
    if player != '':
        img = teams.loc[teams['PlayerId'] == player, 'PlayerImg'].iloc[0]
        name = teams.loc[teams['PlayerId'] == player, 'FullName'].iloc[0]

        return html.Div(children=[
            html.Img(src=str(img), style={'height': '100px'}),
            html.Div(html.H4(str(name),
                             style={'font-size': '20px',
                                    'text-align': 'center'}))
        ])


def getTeamImage(team):
    img = teams.loc[teams['TeamId'] == team, 'TeamLogo'].iloc[0]

    return html.Div(children=[
        html.Img(src=str(img), style={'height': '90px'})
    ])


def get_data_object(df):
    rows = []
    for i in range(len(df)):
        row = []
        for col in df.columns:
            value = getPlayerImage(df.iloc[i][col])
            style = {'align': 'center', 'padding': '7px',
                     'text-align': 'center', 'font-size': '25px'}
            row.append(html.Td(value, style=style))

            if i % 2 == 0 and 'background-color' not in style:
                style['background-color'] = '#f2f2f2'

        rows.append(html.Tr(row))

    return html.Table(
        [html.Tr([html.Th(getTeamImage(col), style=headerstyle) for col in df.columns])] + rows, style=tablestyle)


# Atlantic = ['BOS', 'BKN', 'NYK', 'PHI', 'TOR']
# Central = ['CHI', 'CLE', 'DET', 'IND', 'MIL']
# Southeast = ['ATL', 'CHA', 'MIA', 'ORL', 'WAS']
# Northwest = ['DEN', 'MIN', 'OKC', 'POR', 'UTA']
# Pacific = ['GSW', 'LAC', 'LAL', 'PHX', 'SAC']
# Southwest = ['DAL', 'HO', 'MEM', 'NOP', 'SAS']

teamsQuery = 'SELECT * FROM TeamRosters2018'
teams = loadData(teamsQuery)
teams.columns = ['PlayerId', 'TeamId', 'TeamCode', 'FirstName', 'LastName', 'FullName', 'TeamLogo', 'PlayerImg', 'Division', 'Conference']
teamdf = parseTeams(teams)
get_data_object(teamdf)


latestGame = loadData(latestGameQuery)
latestGame.columns = ['LatestDate', 'Venue', 'TeamID', 'PlayerID', 'FullName', 'JerseyNum', 'Pos', 'Min', 'Pts', 'Ast', 'Blk', 'Reb', 'Fga', 'Fgm', 'Fta', 'Ftm', 'Stl', 'Tov', 'Pf', 'Pip', 'Pipa', 'Pipm']



def update_layout():
    return html.Div(children=[
        html.Div([
            html.Img(src=localImg('nba.png'),
                     style={
                         'height': '145px',
                         'float': 'left'},
                     ),
        ]),

        html.H1("NBA League Analysis",
                style={'text-align': 'center',
                       'padding': '10px'}),

        html.P('This is some text', style={'text-align': 'center',
                                           'padding': '10px'}),

        dcc.Tabs(id="div-tabs", value='Atlantic', children=[
            dcc.Tab(label='ATLANTIC', value='Atlantic', style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='CENTRAL', value='Central', style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='SOUTHEAST', value='Southeast', style=tab_style, selected_style=tab_selected_style),

            dcc.Tab(label='NORTHWEST', value='Northwest', style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='PACIFIC', value='Pacific', style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='SOUTHWEST', value='Southwest', style=tab_style, selected_style=tab_selected_style),
        ], style=tabs_styles),

        # html.Button('Refresh Dashboard', id='my-button'),

        html.Div(
            id='table-container'
        )

    ])


app.layout = update_layout()


@app.callback(
    Output('table-container', 'children'),
    [Input('div-tabs', 'value')])

def update_graph(value):
    teams = loadData(teamsQuery)
    teams.columns = ['PlayerId', 'TeamId', 'TeamCode', 'FirstName', 'LastName', 'FullName', 'TeamLogo', 'PlayerImg', 'Division', 'Conference']
    teams = teams[teams['Division'] == value]
    teamdf = parseTeams(teams)

    return get_data_object(teamdf)


external_css = [
    "https://codepen.io/chriddyp/pen/bWLwgP.css",
    "https://codepen.io/chriddyp/pen/brPBPO.css",
    "https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i"
]

for css in external_css:
    app.css.append_css({"external_url": css})


if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })


if __name__ == '__main__':
    app.run_server(debug=True)
