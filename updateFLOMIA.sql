use baseball;

select distinct team_tx from rosters;

SET SQL_SAFE_UPDATES=0;

update games
	set home_team_id = "MIA"
where home_team_id = "FLO";

update games 
	set away_team_id = "MIA"
where away_team_id = "FLO";


update events
	set home_team_id = "MIA"
where home_team_id = "FLO";

update events 
	set away_team_id = "MIA"
where away_team_id = "FLO";

update rosters
	set team_tx = "MIA"
where team_tx = "FLO";

select distinct home_team_id from games order by home_team_id;