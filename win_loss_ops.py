import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import mysql.connector
import numpy as np
import networkx
import csv

def pythagorean_win_loss(team_id,curr_game_dt,cnx,look_back=50,power=1.81):
    query_home = "select * from games where (home_team_id = '" + team_id \
        + "' or away_team_id = '" + team_id + "') and game_dt < " + str(curr_game_dt) \
        + " order by game_dt desc limit " + str(look_back) + ";"
    print(query_home)
    games = pd.read_sql(query_home,con=cnx)
    runs_for = 0
    runs_against = 0
    for index,row in games.iterrows():
        if(row['HOME_TEAM_ID'] == team_id):
            runs_for += row['HOME_SCORE_CT']
            runs_against += row['AWAY_SCORE_CT']
        else:
            runs_for += row['AWAY_SCORE_CT']
            runs_against += row['HOME_SCORE_CT']
    return (runs_for**power)/float(runs_for**power + runs_against**power)


def actual_win_loss(team_id,curr_game_dt,cnx,look_back=50):
        query_home = "select * from games where (home_team_id = '" + team_id \
            + "' or away_team_id = '" + team_id + "') and game_dt < " + str(curr_game_dt) \
            + " order by game_dt desc limit " + str(look_back) + ";"
        print(query_home)
        games = pd.read_sql(query_home,con=cnx)
        wins = 0
        losses = 0
        for index,row in games.iterrows():
            if(row['HOME_TEAM_ID'] == team_id):
                if(row['HOME_SCORE_CT'] > row['AWAY_SCORE_CT']):
                    wins += 1
                else:
                    losses += 1
            else:
                if(row['AWAY_SCORE_CT'] > row['HOME_SCORE_CT']):
                    wins += 1
                else:
                    losses += 1
        return wins/float(wins+losses)

def actual_win_loss_df(team_id,games):
    wins = 0
    losses = 0
    for index,row in games.iterrows():
        if(row['HOME_TEAM_ID'] == team_id):
            if(row['HOME_SCORE_CT'] > row['AWAY_SCORE_CT']):
                wins += 1
            else:
                losses += 1
        else:
            if(row['AWAY_SCORE_CT'] > row['HOME_SCORE_CT']):
                wins += 1
            else:
                losses += 1
    return wins/float(wins+losses)


def pythagorean_win_loss_df(team_id,games,power=2):
    runs_for = 0
    runs_against = 0
    for index,row in games.iterrows():
        if(row['HOME_TEAM_ID'] == team_id):
            runs_for += row['HOME_SCORE_CT']
            runs_against += row['AWAY_SCORE_CT']
        else:
            runs_for += row['AWAY_SCORE_CT']
            runs_against += row['HOME_SCORE_CT']
    return (runs_for**power)/float(runs_for**power + runs_against**power)
