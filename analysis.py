import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import mysql.connector
import numpy as np
import networkx
import csv
from sqlalchemy import create_engine

#Custom imports
import incidence_ops
import win_loss_ops
import series_id
import predictions

#This is the main file for running analyses

#Plot the optimized alpha for Pythagorean win loss
def plot_alphas(team_id_dict,cnx):
    alphas = np.arange(1,3,.1)
    alphas_df = pd.DataFrame(alphas)
    alphas_df["error"] = np.nan
    print(alphas_df)
    df_team_dict = {}
    curr_game_dt = 20151201
    look_back = 162
    for team,num in team_id_dict.items():
        query = "select * from games where (home_team_id = '" + team \
                + "' or away_team_id = '" + team + "') and game_dt < " + str(curr_game_dt) \
                + " order by game_dt desc limit " + str(look_back) + ";"
        df_team_dict[team] = pd.read_sql(query,con=cnx)

    for i in alphas:
        sum_of_error = 0
        print("Alpha=" + str(i))
        for team, num in team_id_dict.items():
            sum_of_error += (win_loss_ops.actual_win_loss_df(team,df_team_dict[team]) \
                    - win_loss_ops.pythagorean_win_loss_df(team,df_team_dict[team],i))**2
        alphas_df.loc[alphas_df[0] == i,"error"] = sum_of_error
    print(alphas_df)

    plt.plot(alphas_df[0],alphas_df["error"])
    plt.xlabel('Alpha')
    plt.ylabel('Error')
    plt.title('Pythagorean alpha optimization 2015')
    print(alphas_df.loc[alphas_df.min()[1] == alphas_df["error"]][0]) #1.71
    plt.show()

#Optimize the alpha for Pythagorean win loss
def optimize_alpha(team_id_dict,year,cnx,interval=.1):
    alphas = np.arange(1,3,interval)
    alphas_df = pd.DataFrame(alphas)
    alphas_df["error"] = np.nan
    df_team_dict = {}
    curr_game_dt = year * 10000 + 1201
    look_back = 162
    for team,num in team_id_dict.items():
        query = "select * from games where (home_team_id = '" + team \
                + "' or away_team_id = '" + team + "') and game_dt < " + str(curr_game_dt) \
                + " order by game_dt desc limit " + str(look_back) + ";"
        df_team_dict[team] = pd.read_sql(query,con=cnx)

    for i in alphas:
        sum_of_error = 0
        print("Alpha=" + str(i))
        for team, num in team_id_dict.items():
            sum_of_error += (win_loss_ops.actual_win_loss_df(team,df_team_dict[team]) \
                    - win_loss_ops.pythagorean_win_loss_df(team,df_team_dict[team],i))**2
        alphas_df.loc[alphas_df[0] == i,"error"] = sum_of_error
    return alphas_df.loc[alphas_df.min()[1] == alphas_df["error"],0].values[0]


#Plot win loss for teams given a date
def plot_win_loss(team_id_dict,cnx,end_date=20151201):
    win_loss = [0 for x in range(len(team_id_dict))]
    pythag = [0 for x in range(len(team_id_dict))]
    line = [.5 for y in range(len(team_id_dict))]
    diff = [0 for x in range(len(team_id_dict))]
    for team, num in team_id_dict.items():
        win_loss[num] = win_loss_ops.actual_win_loss(team,end_date,cnx,look_back=162)
        pythag[num] = win_loss_ops.pythagorean_win_loss(team,end_date,cnx,look_back=162,power=2)
        diff[num] = win_loss[num] - pythag[num]
    style.use('ggplot')

    x = sorted(team_id_dict.values())
    plt.scatter(x,win_loss,label="Actual",color='b')
    xticks = sorted(team_id_dict,key=team_id_dict.get)
    plt.scatter(x,pythag,label="Pythagorean",color='r')
    plt.plot(x,line, color='k', linestyle='--', label='.500')
    plt.xticks(x,xticks)
    plt.legend()
    plt.title('Actual vs. Expected Win-Loss 2015')

    x = sorted(team_id_dict.values())
    plt.scatter(win_loss,pythag,color='b')
    xticks = sorted(team_id_dict,key=team_id_dict.get)
    plt.xlabel('Actual Win-Loss')
    plt.ylabel('Pythagorean Win-Loss')
    plt.plot(line,line, color='k', linestyle='--', label='Act = Pythag')
    plt.title('Actual vs. Expected Win-Loss 2015')

    zero = [0 for i in range(len(team_id_dict))]
    plt.figure()
    print(len(x),len(diff))
    plt.scatter(x,diff,label='Difference',color='g')
    plt.xticks(x,xticks)
    plt.plot(x,zero,color='k',linestyle='--',label='Zero')
    plt.legend()
    plt.title('Difference Between Actual and Expected Win-Loss 2015')
    plt.show()

#Create a dictionary of team ids
def create_team_ids(cnx,year):
    query = "select distinct home_team_id from games where game_yr = " + str(year) + " order by home_team_id;"
    team_ids = pd.read_sql(query,con=cnx)
    team_id_dict = {}
    for index,row in team_ids.iterrows():
        team_id_dict[row['home_team_id']] = index
        print(row['home_team_id'] + ": " + str(index))
    return team_id_dict

def main():

    np.set_printoptions(linewidth=np.inf)

    config = pd.read_csv('config.csv')
    cnx = mysql.connector.connect(user=config.loc[0]['USER'],password=config.loc[0]['PASSWORD'],database=config.loc[0]['DATABASE'])

    #first step: find all the teams, assign them id in a dictionary
    team_id_dict = create_team_ids(cnx,2015)

    #Test page ranking model
    incidence = incidence_ops.create_incidence(20150101,20151231,cnx,team_id_dict)
    oracle = incidence_ops.create_oracle_incidence(incidence,team_id_dict)
    print(oracle)
    # print(incidence)
    ranking = incidence_ops.page_rank(np.matrix(incidence),team_id_dict)
    ranking_sorted = sorted(ranking,key=ranking.get,reverse=True)
    oracle_r = incidence_ops.page_rank(oracle,team_id_dict)
    oracle_r_sorted = sorted(oracle_r,key=oracle_r.get,reverse=True)
    for x in ranking_sorted:
        print(x + " " + str(ranking[x]))

    print("ORACLE DUDE")
    for x in oracle_r_sorted:
        print(x + " " + str(oracle_r[x]))

    #Next make predictions based on these rankings
    #predict a game, save the result, update the incidence matrix using the actual result

    min_num = 20100000;
    max_num = 20101210;

    predictions_lst = {'Oracle':[],'Pythagorean':[],'WinLoss':[],'PageRank':[]}
    for i in range(6):
        predictions_lst['Pythagorean'].append(predictions.predict_pythagorean_w_l(min_num,max_num,cnx,team_id_dict))
        predictions_lst['WinLoss'].append(predictions.predict_w_l(min_num,max_num,cnx,team_id_dict))
        predictions_lst['Oracle'].append(predictions.predict_oracle(min_num,max_num,cnx,team_id_dict))
        predictions_lst['PageRank'].append(predictions.predict_page_rank(min_num,max_num,cnx,team_id_dict))
        min_num += 10000
        max_num += 10000
    for x in predictions_lst:
        print(x)
        predictions_lst[x] = sum(predictions_lst[x])/float(len(predictions_lst[x]))
    print(predictions_lst)

if __name__ == '__main__':
    main()
