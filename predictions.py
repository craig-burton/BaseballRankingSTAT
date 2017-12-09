import pandas as pd
import numpy as np
#Custom
import series_id
import incidence_ops
import analysis

#Predict games using the Oracle method (created by Dr. Eduardo Balreira)
def predict_oracle(start_date,end_date,cnx,team_id_dict,tolerance=0.00001,window=200):
    series = series_id.create_series_dataframe(start_date,end_date,cnx,team_id_dict)
    incidence = [[0 for x in range(len(team_id_dict))] for y in range(len(team_id_dict))]

    #Initial Oracle matrix and ranking
    oracle = incidence_ops.create_oracle_incidence(incidence,team_id_dict)
    oracle_r = incidence_ops.page_rank(oracle,team_id_dict)

    #Keep track of how many we got correct
    #Currently not predicting ties, but merely treating tie as home team win
    #Ties are still used in the ranking however.
    correct_num = 0
    count = 0
    num_predicted = 0

    #Use win_diff for the edges from the Oracle to the team
    win_diff = [0 for x in range(len(team_id_dict))]

    #Start predicting series
    for index,row in series.iterrows():
        home_team = row['HOME_TEAM_ID']
        away_team = row['AWAY_TEAM_ID']
        predict = 0.0
        if(count > window):
            num_predicted += 1
            if(abs(oracle_r[home_team] - oracle_r[away_team]) <= tolerance and row['NUM_GAMES']%2 == 0):
                predict = 1.0
            elif(oracle_r[home_team] > oracle_r[away_team]):
                predict = 1.0
            if(predict == row['HOME_WIN']):
                correct_num += 1

        #Update the incidence matrix with actual results
        count += 1
        if(row['HOME_WIN'] == 1):
            incidence[team_id_dict[home_team]][team_id_dict[away_team]] += 1
            win_diff[team_id_dict[home_team]] += 2*row['HOME_WINS'] - row['NUM_GAMES']
        elif(row['HOME_WIN'] == 0.5):
            incidence[team_id_dict[home_team]][team_id_dict[away_team]] += .5
            incidence[team_id_dict[away_team]][team_id_dict[home_team]] += .5
        else:
            incidence[team_id_dict[away_team]][team_id_dict[home_team]] += 1
            win_diff[team_id_dict[away_team]] += row['NUM_GAMES'] - 2*row['HOME_WINS']

        #Update Oracle matrix and ranking
        oracle = incidence_ops.create_oracle_incidence_win_diff(incidence,team_id_dict,win_diff)
        oracle_r = incidence_ops.page_rank(oracle,team_id_dict)
    return correct_num/float(num_predicted)


def predict_page_rank(start_date,end_date,cnx,team_id_dict,tolerance=0.001,window=200):
    series = series_id.create_series_dataframe(start_date,end_date,cnx,team_id_dict)
    incidence = [[0 for x in range(len(team_id_dict))] for y in range(len(team_id_dict))]
    ranking = incidence_ops.page_rank(np.matrix(incidence),team_id_dict)
    correct_num = 0
    count = 0
    num_predicted = 0
    for index,row in series.iterrows():
        home_team = row['HOME_TEAM_ID']
        away_team = row['AWAY_TEAM_ID']
        if(count > window):
            num_predicted += 1
            predict = 0.0
            if(abs(ranking[home_team] - ranking[away_team]) <= tolerance and row['NUM_GAMES']%2 == 0):
                predict = 1.0
                # print("Predicted tie!")
            elif(ranking[home_team] > ranking[away_team]):
                predict = 1.0
            if(predict == row['HOME_WIN']):
                correct_num += 1
        if(row['HOME_WIN'] == 1):
            incidence[team_id_dict[home_team]][team_id_dict[away_team]] += 1
        elif(row['HOME_WIN'] == 0):
            incidence[team_id_dict[home_team]][team_id_dict[away_team]] += .5
            incidence[team_id_dict[away_team]][team_id_dict[home_team]] += .5
        else:
            incidence[team_id_dict[away_team]][team_id_dict[home_team]] += 1
        ranking = incidence_ops.page_rank(np.matrix(incidence),team_id_dict)
        count += 1
    return correct_num/float(num_predicted)

#Computes pythagorean_win_loss
def get_py_wl(team,team_id_runs,power):
    runs_for = team_id_runs[team][0]
    runs_against = team_id_runs[team][1]
    return (runs_for**power)/float(runs_for**power + runs_against**power)


def predict_pythagorean_w_l(start_date,end_date,cnx,team_id_dict,window=200,interval_alpha=.1):
    series = series_id.create_series_dataframe(start_date,end_date,cnx,team_id_dict)
    prev_year = int(start_date/10000)-1
    alpha = analysis.optimize_alpha(team_id_dict,prev_year,cnx,interval_alpha)
    # team -> (runs for, runs against)
    team_id_runs = {}
    for team in team_id_dict:
        team_id_runs[team] = [0,0]
    count = 0
    correct_num = 0
    num_predicted = 0
    for index,row in series.iterrows():
        home_team = row['HOME_TEAM_ID']
        away_team = row['AWAY_TEAM_ID']
        if(count > window):
            num_predicted += 1
            home_py = get_py_wl(home_team,team_id_runs,alpha)
            away_py = get_py_wl(away_team,team_id_runs,alpha)
            predict = 0.0
            if(home_py == away_py and row['NUM_GAMES'] % 2 == 0):
                predict = 1.0
            elif(home_py >= away_py):
                predict = 1.0
            if(predict == row['HOME_WIN']):
                correct_num += 1
        team_id_runs[home_team][0] += row['HOME_RUNS']
        team_id_runs[home_team][1] += row['AWAY_RUNS']
        team_id_runs[away_team][0] += row['AWAY_RUNS']
        team_id_runs[away_team][1] += row['HOME_RUNS']
        count += 1
    return correct_num/float(num_predicted)

def predict_w_l(start_date,end_date,cnx,team_id_dict,window=200,interval_alpha=.1):
    series = series_id.create_series_dataframe(start_date,end_date,cnx,team_id_dict)
    # team -> (wins, total)
    team_id_wins = {}
    for team in team_id_dict:
        team_id_wins[team] = [0,0]
    count = 0
    correct_num = 0
    num_predicted = 0
    for index,row in series.iterrows():
        home_team = row['HOME_TEAM_ID']
        away_team = row['AWAY_TEAM_ID']
        if(count > window):
            num_predicted += 1
            home_rec = team_id_wins[home_team][0]/float(team_id_wins[home_team][1])
            away_rec = team_id_wins[away_team][0]/float(team_id_wins[away_team][1])
            predict = 0.0
            if(home_rec == away_rec and row['NUM_GAMES'] % 2 == 0):
                predict = 1.0
            elif(home_rec >= away_rec):
                predict = 1.0
            if(predict == row['HOME_WIN']):
                correct_num += 1
        team_id_wins[home_team][0] += row['HOME_WINS']
        team_id_wins[home_team][1] += row['NUM_GAMES']
        team_id_wins[away_team][0] += row['AWAY_WINS']
        team_id_wins[away_team][1] += row['NUM_GAMES']
        count += 1
    return correct_num/float(num_predicted)
