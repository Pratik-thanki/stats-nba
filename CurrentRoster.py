import pandas as pd
import requests 
from Settings import *

teams = ['1610612737', '1610612738', '1610612751', '1610612766', '1610612741', '1610612739', '1610612765', '1610612754', '1610612748', '1610612749', '1610612752', '1610612753', '1610612755', '1610612761', '1610612764', '1610612742', '1610612743', '1610612744', '1610612745', '1610612746', '1610612747', '1610612763', '1610612750', '1610612740', '1610612760', '1610612756', '1610612757', '1610612758', '1610612759', '1610612762']

url = 'https://stats.nba.com/stats/commonteamroster?LeagueID=00&Season=2018-19&TeamID=1610612737'
rosters = requests.request('GET', url, headers=headers)
rosters = rosters.json()
pd.DataFrame(rosters['resultSets'][0]['rowSet'], columns=list(rosters['resultSets'][0]['headers']))


tmp = []
for t in teams:
    try:
        url = 'https://stats.nba.com/stats/commonteamroster?LeagueID=00&Season=2018-19&TeamID=' + t
        rosters = requests.request('GET', url, headers=headers)
        rosters = rosters.json()
        print(t)
        tmp.append(rosters['resultSets'][0]['rowSet'])
        pass

    except ValueError as e:
        print(e)


roster = pd.DataFrame(tmp, columns=list(rosters['resultSets'][0]['headers']))
