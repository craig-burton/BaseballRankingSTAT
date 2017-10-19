import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import mysql.connector
import numpy as np
import networkx


config = pd.read_csv('config.csv')
cnx = mysql.connector.connect(user=config.loc[0]['USER'],password=config.loc[0]['PASSWORD'],database=config.loc[0]['DATABASE'])
#Start by trying to calculate one pitcher's ERA
#Derek Holland - holld003 = player_id
#first step, get all games started within a date range



#TODO: team average
#TODO: pitcher ERA
#TODO: incidence matrices

#first step: find all the teams, assign them id in a dictionary
query = "select distinct home_team_id from games where game_yr = 2016 order by home_team_id;"
team_ids = pd.read_sql(query,con=cnx)
team_id_dict = {}
for index,row in team_ids.iterrows():
    team_id_dict[row['home_team_id']] = index
    print(row['home_team_id'] + ": " + str(index))

incidence = [[0 for x in range(len(team_id_dict))] for y in range(len(team_id_dict))]

def update_incidence(array_of_rows):

    #if home team won, add 1 to win_loss, if away_team_id won substract 1
    if(len(array_of_rows) == 0):
        return;
    # print(len(array_of_rows))
    win_loss = 0
    home_team_id = team_id_dict[array_of_rows[0]['HOME_TEAM_ID']]
    away_team_id = team_id_dict[array_of_rows[0]['AWAY_TEAM_ID']]
    for row in array_of_rows:
        # print(str(row['HOME_SCORE_CT']) + " " + str(row['AWAY_SCORE_CT']))
        if(row['HOME_SCORE_CT'] > row['AWAY_SCORE_CT']):
            win_loss += 1
        elif(row['HOME_SCORE_CT'] < row['AWAY_SCORE_CT']):
            win_loss -= 1
    if(win_loss >= 1):
        #home team won
        incidence[home_team_id][away_team_id] += 1
        # print("home team: " + str(home_team_id) + " won against " + str(away_team_id))
    elif(win_loss < 0):
        incidence[away_team_id][home_team_id] += 1
        # print("away team: " + str(away_team_id) + " won against " + str(home_team_id))
    else:
        incidence[home_team_id][away_team_id] += .5
        incidence[away_team_id][home_team_id] += .5

        # print("ITS A TIE home: " + str(home_team_id) + " away: " + str(away_team_id))

#second step: loop through team's home series
for team,num in team_id_dict.iteritems():
    #check the teams home series
    query = "select * from games where home_team_id = '" \
        + team + "' and game_yr = 2016 order by game_dt;"
    home_series = pd.read_sql(query,con=cnx)
    # print("TEAM = " + team + " ID = " + str(team_id_dict[team]))
    last_team_played = home_series.loc[0]['AWAY_TEAM_ID']
    last_game_dt = 0
    last_games = []
    team_count = 0
    for index,row in home_series.iterrows():
        #two cases: played the last team you played, or not

        if(row['AWAY_TEAM_ID'] == last_team_played):
            #keep adding to the array of last_games
            last_games.append(row)
            last_game_dt = row['GAME_DT']
        else:
            #stop adding to the array of last_games
            update_incidence(last_games)
            team_count += 1
            last_game_dt = row['GAME_DT']
            last_team_played = row['AWAY_TEAM_ID']
            last_games = [row]
    # print(team_count)


for r in incidence:
    print(r)

print('\n'.join([''.join(['{:4}'.format(item) for item in row])
      for row in incidence]))
print(len(incidence))


#TODO: Pythagorean Win/Loss
team_pythag = {}
team_totals = []
def pythagorean_win_loss(team_id,curr_game_dt,look_back=50,power=1.81):
    query_home = "select * from games where (home_team_id = '" + team_id \
        + "' or away_team_id = '" + team_id + "') and game_dt < " + str(curr_game_dt) \
        + " order by game_dt desc limit " + str(look_back) + ";"
    print(query_home)
    games = pd.read_sql(query_home,con=cnx)
    runs_for = 0
    runs_against = 0
    for index,row in games.iterrows():
        print(row['GAME_DT'])
        if(row['HOME_TEAM_ID'] == team_id):
            runs_for += row['HOME_SCORE_CT']
            runs_against += row['AWAY_SCORE_CT']
        else:
            runs_for += row['AWAY_SCORE_CT']
            runs_against += row['HOME_SCORE_CT']
    return (runs_for**power)/float(runs_for**power + runs_against**power)

print(pythagorean_win_loss("TEX",20161201,look_back=162,power=2))

#Pick 2016 and plot all of teams pythagorean_win_loss



#TODO: Team Hit to Run

#EOF
