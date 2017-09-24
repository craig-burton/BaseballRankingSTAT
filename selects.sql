--This is examples of how to query mySQL
--Use the baseball database
USE baseball;

--Show the tables
SHOW tables;

--Describe some tables
DESCRIBE games;
DESCRIBE events;
DESCRIBE teams;

--Select all of the teams
SELECT * FROM teams;

--Select 10 games ordered by the game date
SELECT game_dt,home_team_id,away_team_id,home_score_ct,away_score_ct,
  home_start_pit_id,away_start_pit_id,home_hits_ct,away_hits_ct
FROM games WHERE game_yr > 2010 ORDER BY game_dt LIMIT 15;

--Select the pitchers in Texas in 2014
SELECT * FROM rosters WHERE Year=2014 AND team_tx="TEX" AND pos_tx="P";
