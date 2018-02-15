import os
import sys
import requests
import json
import pandas as pd
import numpy as np
import pyodbc
from sqlalchemy import create_engine


# get today's date, for use later when getting Id's
import time
from datetime import datetime, timedelta

now = datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d")
yesterday = datetime.today() - timedelta(days=1)
yesterday = datetime.strptime(yesterday.strftime("%Y-%m-%d"), "%Y-%m-%d")


# Connection to ms sql using pyodbc
driver = 'ODBC DRIVER 13 for SQL Server'
server = 's'
database = 'd'
username = 'u'
password = 'p'
conn  = pyodbc.connect(r'DRIVER={ODBC DRIVER 13 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)


# Request a cursor from the connection that can be used for queries
cursor= conn.cursor() 


# Create dataframe from sql table in database
Players = pd.read_sql("select * from [dbo].[Players]", conn)
Teams = pd.read_sql("select * from [dbo].[Teams]", conn)

PlayerId = Players['PlayerID']

TeamsId = []
for i in Teams['TeamID']:
    if int(len(str(i))) == 10:
        TeamsId.append(i)

headers = {'user-agent': 'python'}

# --------------------------- Player stats by season ---------------------------


playercareerstats = 'http://'
playerStats = []
for i in PlayerId:
    try:
        playerStatsRequest = requests.get(playercareerstats + str(i), headers=headers)
        print(str(i) + ' - ' + str(playerStatsRequest.status_code))
    #    playerStatsRequest.raise_for_status()
        playerStatsRequest = playerStatsRequest.json()
        playerStats.append(playerStatsRequest)
        pass
    except ValueError as e:
        print(str(i) + ' ' + str(e))


def seasonStats(resultName, summaries, resultList, headersList):
    for i in summaries:
        for j in i['resultSets']:
            for rows in j['rowSet']:
                if len(j['rowSet']) > 0 and j['name'] == resultName:
                    resultList.append(rows)
                    headersList.append(j['headers'])


# ------------------------ establish database connection for use later ------------------------


engine = create_engine('mssql+pyodbc://uid:pwd@dbname')


def parseWrite(dbTableName):
    resultList = []
    headersList = []
    seasonStats(dbTableName, playerStats, resultList, headersList)
    resultList = pd.DataFrame(resultList)
    resultList.columns = [headersList[0]]
    resultList.to_sql(dbTableName, engine, flavor=None, schema='dbo', if_exists='replace', index=None, chunksize=1000)

parseWrite('SeasonTotalsRegularSeason')
parseWrite('CareerTotalsRegularSeason')

parseWrite('SeasonTotalsPostSeason')
parseWrite('CareerTotalsPostSeason')

parseWrite('SeasonTotalsAllStarSeason')
parseWrite('CareerTotalsAllStarSeason')

parseWrite('SeasonTotalsCollegeSeason')
parseWrite('CareerTotalsCollegeSeason')


# --------------------------- Team stats by season ---------------------------


teamcareerStats = 'http://'
teamStats = []
for i in TeamsId:
    try:
        teamStatsRequest = requests.get(teamcareerStats + str(i), headers=headers)
        print(str(i) + ' - ' + str(teamStatsRequest.status_code))
        #teamStatsRequest.raise_for_status()
        teamStatsRequest = teamStatsRequest.json()
        teamStats.append(teamStatsRequest)
        pass
    except ValueError

TeamSeasons = []
teamSeason_headers = []
seasonStats('TeamStats', teamStats, TeamSeasons, teamSeason_headers)
teamSeason_headers = teamSeason_headers[0]
TeamSeasons = pd.DataFrame(TeamSeasons)
TeamSeasons.columns = [teamSeason_headers]
TeamSeasons.to_sql('TeamLegacyStats', engine, flavor=None, schema='dbo', if_exists='replace', index=None, chunksize=1000)
