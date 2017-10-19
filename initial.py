import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import mysql.connector

style.use('ggplot')


config = pd.read_csv('config.csv')
cnx = mysql.connector.connect(user=config.loc[0]['USER'],password=config.loc[0]['PASSWORD'],database=config.loc[0]['DATABASE'])

tex_home_runs = pd.read_sql("select home_score_ct as runs, game_dt,game_yr from games where home_team_id = 'TEX' order by game_dt;", con = cnx)
tex_away_runs = pd.read_sql("select away_score_ct as runs, game_dt,game_yr from games where away_team_id = 'TEX' order by game_dt;", con = cnx)
tex_total_runs = tex_home_runs.append(tex_away_runs).sort_values(by='game_dt')
print tex_total_runs.head(10)
plt.scatter(tex_total_runs.game_dt, tex_total_runs.runs)
#Plot one plot per year
maxyear = tex_total_runs.game_yr.max()
minyear = tex_total_runs.game_yr.min()

#plt.subplot();
plt.subplot(2,2,1)
plt.suptitle("Texas Rangers Runs Scored Over Time")
yearly = tex_total_runs[tex_total_runs.game_yr == 2000]
plt.scatter(yearly.index,yearly.runs)
plt.ylabel('Runs scored')
plt.title('2000')

plt.subplot(2,2,2)
yearly = tex_total_runs[tex_total_runs.game_yr == 2004]
plt.scatter(yearly.index,yearly.runs)
plt.title('2004')

plt.subplot(2,2,3)
yearly = tex_total_runs[tex_total_runs.game_yr == 2008]
plt.scatter(yearly.index,yearly.runs)
plt.ylabel('Runs scored')
plt.xlabel('Game number')
plt.title('2008')

plt.subplot(2,2,4)
yearly = tex_total_runs[tex_total_runs.game_yr == 2012]
plt.scatter(yearly.index,yearly.runs)
plt.xlabel('Game number')
plt.title('2012')
plt.show()


'''
print(maxyear);
print(minyear);

for i in range(minyear,maxyear+1):
    filtered = tex_total_runs[tex_total_runs.game_yr == i]
    plt.scatter(filtered.index,filtered.runs)
    plt.xlabel("GAME")
    plt.ylabel("RUNS")
    plt.title(i)
    plt.show()
print maxyear
print minyear
plt.show()
'''

#Plot descriptive statistics to show in presentation


cnx.close()
