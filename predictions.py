import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import mysql.connector
import numpy as np
#Custom
import series_id
import incidence_ops

def predict_oracle(start_date,end_date,cnx,team_id_dict,tolerance=0.001):
    series = series_id.create_series_dataframe(start_date,end_date,cnx,team_id_dict)
    incidence = [[0 for x in range(len(team_id_dict))] for y in range(len(team_id_dict))]
    oracle = incidence_ops.create_oracle_incidence(incidence,team_id_dict)
    oracle_r = incidence_ops.page_rank(oracle,team_id_dict)
    correct_num = 0
    for index,row in series.iterrows():
        home_team = row['HOME_TEAM_ID']
        away_team = row['AWAY_TEAM_ID']
        predict = 0.0
        if(abs(oracle_r[home_team] - oracle_r[away_team]) <= tolerance and row['NUM_GAMES']%2 == 0):
            predict = 0.5
            # print("Predicted tie!")
        elif(oracle_r[home_team] > oracle_r[away_team]):
            predict = 1.0
        if(predict == row['HOME_WIN']):
            correct_num += 1
            # print("Right!")
        # else:
            # print("Wrong :(")

        if(row['HOME_WIN'] == 1):
            incidence[team_id_dict[home_team]][team_id_dict[away_team]] += 1
        elif(row['HOME_WIN'] == 0):
            incidence[team_id_dict[home_team]][team_id_dict[away_team]] += .5
            incidence[team_id_dict[away_team]][team_id_dict[home_team]] += .5
        else:
            incidence[team_id_dict[away_team]][team_id_dict[home_team]] += 1
        oracle = incidence_ops.create_oracle_incidence(incidence,team_id_dict)
        oracle_r = incidence_ops.page_rank(oracle,team_id_dict)
        # print("New rankings: ")
        # for x in sorted(oracle_r,key=oracle_r.get,reverse=True):
        #     print(x + " " + str(oracle_r[x]))
    return correct_num/float(len(series))


def predict_page_rank(start_date,end_date,cnx,team_id_dict,tolerance=0.001):
    series = series_id.create_series_dataframe(start_date,end_date,cnx,team_id_dict)
    incidence = [[0 for x in range(len(team_id_dict))] for y in range(len(team_id_dict))]
    ranking = incidence_ops.page_rank(np.matrix(incidence),team_id_dict)
    correct_num = 0
    for index,row in series.iterrows():
        home_team = row['HOME_TEAM_ID']
        away_team = row['AWAY_TEAM_ID']
        predict = 0.0
        if(abs(ranking[home_team] - ranking[away_team]) <= tolerance and row['NUM_GAMES']%2 == 0):
            predict = 0.5
            # print("Predicted tie!")
        elif(ranking[home_team] > ranking[away_team]):
            predict = 1.0
        if(predict == row['HOME_WIN']):
            correct_num += 1
            # print("Right!")
        # else:
            # print("Wrong :(")

        if(row['HOME_WIN'] == 1):
            incidence[team_id_dict[home_team]][team_id_dict[away_team]] += 1
        elif(row['HOME_WIN'] == 0):
            incidence[team_id_dict[home_team]][team_id_dict[away_team]] += .5
            incidence[team_id_dict[away_team]][team_id_dict[home_team]] += .5
        else:
            incidence[team_id_dict[away_team]][team_id_dict[home_team]] += 1
        ranking = incidence_ops.page_rank(np.matrix(incidence),team_id_dict)
        # print("New rankings: ")
        # for x in sorted(oracle_r,key=oracle_r.get,reverse=True):
        #     print(x + " " + str(oracle_r[x]))
    return correct_num/float(len(series))








#EOF
