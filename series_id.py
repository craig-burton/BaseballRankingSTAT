import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import mysql.connector
import numpy as np
import networkx
import csv

def create_series_ids(start_date,end_date,cnx,team_id_dict):
    overall_query = "select * from games where game_dt >= " + str(start_date) + \
        " and game_dt <= " + str(end_date) + " order by game_dt;"
    overall_df = pd.read_sql(overall_query,con=cnx)
    overall_df["AWAY_SERIES_ID"] = np.nan
    overall_df["HOME_SERIES_ID"] = np.nan
    #add columns for series_id, home and away
    for team,num in team_id_dict.items():
        query = "select * from games where (home_team_id = '" \
            + team + "' or away_team_id = '" + team + "') and game_dt >= " \
            + str(start_date) + \
            " and game_dt <= " + str(end_date) + \
             " order by game_dt;"
        print(query)
        all_series = pd.read_sql(query,con=cnx)
        print("Total games: " + str(len(all_series.index)))
        last_team_played = all_series.loc[0,'AWAY_TEAM_ID']
        if(last_team_played == team):
            last_team_played = all_series.loc[0,'HOME_TEAM_ID']
        last_game_dt = 0
        last_game_ids = []
        series_count = 0
        series_id = ""
        last_game_home = (all_series.loc[0,'HOME_TEAM_ID'] == team)
        for index,row in all_series.iterrows():
            #two cases: played the last team you played, or not
            home_game = (row['HOME_TEAM_ID'] == team)
            team_against = row['HOME_TEAM_ID']
            if(home_game):
                team_against = row['AWAY_TEAM_ID']
            if(team_against == last_team_played and home_game == last_game_home):
                #keep adding to the array of last_games
                last_game_ids.append(row['GAME_ID'])
                last_game_dt = row['GAME_DT']
                last_game_home = home_game
            else:
                #stop adding to the array of last_game_ids
                if(len(last_game_ids) > 0):
                    series_count += 1
                series_id = str(team) + str(series_count)
                overall_df = update_series_id(last_game_ids,overall_df,series_id,last_game_home)
                last_game_dt = row['GAME_DT']
                last_team_played = team_against
                last_game_ids = [row['GAME_ID']]
                last_game_home = home_game
        series_id = str(team) + str(series_count+1)
        overall_df = update_series_id(last_game_ids,overall_df,series_id,last_game_home)
    return overall_df

def create_series_dataframe(start_date,end_date,cnx,team_id_dict):
    overall_query = "select * from games where game_dt >= " + str(start_date) + \
        " and game_dt <= " + str(end_date) + " order by game_dt;"
    overall_df = pd.DataFrame()
    #add columns for series_id, home and away
    for team,num in team_id_dict.items():
        query = "select * from games where (home_team_id = '" \
            + team + "' or away_team_id = '" + team + "') and game_dt >= " \
            + str(start_date) + \
            " and game_dt <= " + str(end_date) + \
             " order by game_dt;"
        print(query)
        all_series = pd.read_sql(query,con=cnx)
        print("Total games: " + str(len(all_series.index)))
        last_team_played = all_series.loc[0,'AWAY_TEAM_ID']
        if(last_team_played == team):
            last_team_played = all_series.loc[0,'HOME_TEAM_ID']
        last_game_dt = 0
        last_games = []
        last_game_home = (all_series.loc[0,'HOME_TEAM_ID'] == team)
        for index,row in all_series.iterrows():
            #two cases: played the last team you played, or not
            home_game = (row['HOME_TEAM_ID'] == team)
            team_against = row['HOME_TEAM_ID']
            if(home_game):
                team_against = row['AWAY_TEAM_ID']
            if(team_against == last_team_played and home_game == last_game_home):
                #keep adding to the array of last_games
                last_games.append(row)
                last_game_dt = row['GAME_DT']
                last_game_home = home_game
            else:
                #stop adding to the array of last_game_ids
                overall_df = update_series_df(last_games,overall_df)
                last_game_dt = row['GAME_DT']
                last_team_played = team_against
                last_games = [row]
                last_game_home = home_game
        overall_df = update_series_df(last_games,overall_df)
    return overall_df.sort_values("END_DATE")


def update_series_id(last_games,overall_df,series_id,at_home):
    series = 'AWAY_SERIES_ID'
    if(at_home):
        series = 'HOME_SERIES_ID'
    for row in last_games:
        overall_df.loc[overall_df['GAME_ID'] == row,series] = series_id
    return overall_df

#returns 1 if home_team won series, 0 if away won, .5 if tied
def determine_win_loss_series(games):
    home_w = 0
    home_runs = 0
    away_runs = 0
    for row in games:
        if(row['HOME_SCORE_CT'] > row['AWAY_SCORE_CT']):
            home_w += 1
        home_runs += row['HOME_SCORE_CT']
        away_runs += row['AWAY_SCORE_CT']
    away_w = len(games) - home_w
    if(home_w > away_w):
        return (1,home_runs,away_runs,home_w,away_w)
    elif(home_w < away_w):
        return (0,home_runs,away_runs,home_w,away_w)
    else:
        return (1,home_runs,away_runs,home_w,away_w)

def update_series_df(last_games,overall_df):
    win_loss_home = determine_win_loss_series(last_games)
    overall_df = overall_df.append({'HOME_WIN':win_loss_home[0],'AWAY_TEAM_ID':last_games[0]['AWAY_TEAM_ID'] \
        ,'HOME_TEAM_ID':last_games[0]['HOME_TEAM_ID'],'END_DATE':int(last_games[len(last_games)-1]['GAME_DT'])
        ,'NUM_GAMES':len(last_games),'HOME_RUNS':win_loss_home[1],'AWAY_RUNS':win_loss_home[2]\
        ,'HOME_WINS':win_loss_home[3],'AWAY_WINS':win_loss_home[4]}\
        ,ignore_index=True)
    return overall_df



#EOF
