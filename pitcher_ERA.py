import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import mysql.connector
import numpy as np
import networkx
import csv

np.set_printoptions(linewidth=np.inf)

config = pd.read_csv('config.csv')
cnx = mysql.connector.connect(user=config.loc[0]['USER'],password=config.loc[0]['PASSWORD'],database=config.loc[0]['DATABASE'])
#Start by trying to calculate one pitcher's ERA
#Derek Holland - holld003 = player_id
#first step, get all games started within a date range



#TODO: team average
#TODO: pitcher ERA
#TODO: incidence matrices

#first step: find all the teams, assign them id in a dictionary
query = "select distinct home_team_id from games where game_yr = 2015 order by home_team_id;"
team_ids = pd.read_sql(query,con=cnx)
team_id_dict = {}
for index,row in team_ids.iterrows():
    team_id_dict[row['home_team_id']] = index
    print(row['home_team_id'] + ": " + str(index))
incidence = [[0 for x in range(len(team_id_dict))] for y in range(len(team_id_dict))]

def update_incidence(array_of_rows,incidence):
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

#second step: loop through team's home series
for team,num in team_id_dict.items():
    #check the teams home series
    query = "select * from games where home_team_id = '" \
        + team + "' and game_yr = 2015 order by game_dt;"
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
            incidence = update_incidence(last_games,incidence)
            team_count += 1
            last_game_dt = row['GAME_DT']
            last_team_played = row['AWAY_TEAM_ID']
            last_games = [row]

incidence_np = np.matrix(incidence)
print(incidence_np)

def create_incidence(start_date,end_date):
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
                incidence = update_incidence(last_games,incidence)
                team_count += 1
                last_game_dt = row['GAME_DT']
                last_team_played = row['AWAY_TEAM_ID']
                last_games = [row]

    incidence_np = np.matrix(incidence)
    return incidence_np
# with open("incidence.csv", "w", newline='') as f:
#     writer = csv.writer(f)
#     writer.writerow([' '] + team_id_dict.keys())
#     for i in range(len(team_id_dict)):
#         for key, value in team_id_dict.items():
#             if value == i:
#                 writer.writerow(key + str(incidence[i]))

# print('\n'.join([''.join(['{:4}'.format(item) for item in row])
#       for row in incidence]))
# print(len(incidence))

#
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
        if(row['HOME_TEAM_ID'] == team_id):
            runs_for += row['HOME_SCORE_CT']
            runs_against += row['AWAY_SCORE_CT']
        else:
            runs_for += row['AWAY_SCORE_CT']
            runs_against += row['HOME_SCORE_CT']
    return (runs_for**power)/float(runs_for**power + runs_against**power)

def actual_win_loss(team_id,curr_game_dt,look_back=50):
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

# print(pythagorean_win_loss("TEX",20161201,look_back=162,power=2))
# print(actual_win_loss("TEX",20161201,look_ back=162))

#Pick 2015 and plot all of teams pythagorean_win_loss
# win_loss = [0 for x in range(len(team_id_dict))]
# pythag = [0 for x in range(len(team_id_dict))]
# line = [.35,.65]
# diff = [0 for x in range(len(team_id_dict))]
# for team, num in team_id_dict.items():
#     win_loss[num] = actual_win_loss(team,20151201,look_back=162)
#     pythag[num] = pythagorean_win_loss(team,20151201,look_back=162,power=2)
#     diff[num] = win_loss[num] - pythag[num]
# style.use('ggplot')

# x = sorted(team_id_dict.values())
# plt.scatter(x,win_loss,label="Actual",color='b')
# xticks = sorted(team_id_dict,key=team_id_dict.get)
# plt.scatter(x,pythag,label="Pythagorean",color='r')
# plt.plot(x,line, color='k', linestyle='--', label='.500')
# plt.xticks(x,xticks)
# plt.legend()
# plt.title('Actual vs. Expected Win-Loss 2015')

# x = sorted(team_id_dict.values())
# plt.scatter(win_loss,pythag,color='b')
# xticks = sorted(team_id_dict,key=team_id_dict.get)
# plt.xlabel('Actual Win-Loss')
# plt.ylabel('Pythagorean Win-Loss')
# plt.plot(line,line, color='k', linestyle='--', label='Act = Pythag')
# plt.title('Actual vs. Expected Win-Loss 2015')

# zero = [0 for i in range(len(team_id_dict))]
# plt.figure()
# print(len(x),len(diff))
# plt.scatter(x,diff,label='Difference',color='g')
# plt.xticks(x,xticks)
# plt.plot(x,zero,color='k',linestyle='--',label='Zero')
# plt.legend()
# plt.title('Difference Between Actual and Expected Win-Loss 2015')
# # plt.show()

# Compute errors of Pythag to win/loss and minimize using different alphas
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
        sum_of_error += (actual_win_loss_df(team,df_team_dict[team]) - pythagorean_win_loss_df(team,df_team_dict[team],i))**2
    alphas_df.loc[alphas_df[0] == i,"error"] = sum_of_error
print(alphas_df)

plt.plot(alphas_df[0],alphas_df["error"])
plt.xlabel('Error')
plt.ylabel('Alpha')
plt.title('Pythagorean alpha optimization 2015')
print(alphas_df.loc[alphas_df.idxmin()]) #1.71
plt.show()



#PageRank
def page_rank(incidence,team_id_dict):
    incidence = incidence_np.tolist()
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


#Test page ranking model
incidence = create_incidence(20150101,20150714)
print(incidence)
ranking = page_rank(incidence,team_id_dict)
ranking_sorted = sorted(ranking,key=ranking.get,reverse=True)
for x in ranking_sorted:
    print x + " " + str(ranking[x])

#Next make predictions based on these rankings
#predict a game, save the result, update the incidence matrix using the actual result







#TODO: Team Hit to Run






#EOF
