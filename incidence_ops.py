import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import mysql.connector
import numpy as np
import networkx
import csv



def update_incidence(array_of_rows,incidence,team_id_dict):
    #if home team won, add 1 to win_loss, if away_team_id won substract 1
    if(len(array_of_rows) == 0):
        return;
    # print(len(array_of_rows))
    win_loss = 0
    home_team_id = team_id_dict[array_of_rows[0]['HOME_TEAM_ID']]
    away_team_id = team_id_dict[array_of_rows[0]['AWAY_TEAM_ID']]
    for row in array_of_rows:
        if(row['HOME_SCORE_CT'] > row['AWAY_SCORE_CT']):
            win_loss += 1
        elif(row['HOME_SCORE_CT'] < row['AWAY_SCORE_CT']):
            win_loss -= 1
    if(win_loss >= 1):
        #home team won
        incidence[home_team_id][away_team_id] += 1
    elif(win_loss < 0):
        incidence[away_team_id][home_team_id] += 1
    else:
        incidence[home_team_id][away_team_id] += .5
        incidence[away_team_id][home_team_id] += .5
    return incidence

def create_incidence(start_date,end_date,cnx,team_id_dict):
    incidence = [[0 for x in range(len(team_id_dict))] for y in range(len(team_id_dict))]
    for team,num in team_id_dict.items():
        #check the teams home series
        query = "select * from games where home_team_id = '" \
            + team + "' and game_dt >= " + str(start_date) + \
            " and game_dt <= " + str(end_date) +  " order by game_dt;"
        home_series = pd.read_sql(query,con=cnx)
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
                incidence = update_incidence(last_games,incidence,team_id_dict)
                team_count += 1
                last_game_dt = row['GAME_DT']
                last_team_played = row['AWAY_TEAM_ID']
                last_games = [row]
    return incidence

def page_rank(incidence,team_id_dict):
    incidence = incidence.A
    for j in range(len(incidence[0])):
        total = 0
        for i in range(len(incidence)):
            total += incidence[i][j]
        if(total == 0):
            for i in range(len(incidence)):
                incidence[i][j] = 1/float(len(incidence))
        else:
            for i in range(len(incidence)):
                incidence[i][j] = incidence[i][j] / float(total)

    stochastic = np.matrix(incidence)
    new = np.matrix(incidence)
    for i in range(5000):
        new = new * stochastic

    ranking = {}
    final = new.A
    for x in team_id_dict:
        ranking[x] =  final[team_id_dict[x]][0]

    return ranking

def create_oracle_incidence(incidence,team_id_dict):
    oracle = np.matrix([[0 for x in range(len(team_id_dict)+1)] for y in range(len(team_id_dict)+1)],dtype=float).A
    # wins = [0 for x in range(len(team_id_dict))]
    for i in range(len(incidence)):
        wins = np.matrix(incidence).sum(1)[i]
        oracle[i][len(incidence)] = wins+1
        oracle[len(incidence)][i] = wins+1
        for j in range(len(incidence)):
            oracle[i][j] = incidence[i][j]
    return np.matrix(oracle)
