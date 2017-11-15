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
            overall_df = update_series_id(last_game_ids,overall_df,series_id,last_game_home)
    return overall_df


def update_series_id(last_games,overall_df,series_id,at_home):
    series = 'AWAY_SERIES_ID'
    if(at_home):
        series = 'HOME_SERIES_ID'
    for row in last_games:
        print("Changing the series: " + row + " " + series)
        overall_df.loc[overall_df['GAME_ID'] == row,series] = series_id
        print("changed to: " + str(overall_df.loc[overall_df['GAME_ID'] == row, series]))
    return overall_df
