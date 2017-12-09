# BaseballRankingSTAT
This is a project written in Python to predict baseball series using several methods. Python uses a MySQL database containing [Retrosheet](http://www.retrosheet.org/) data gotten from scripts [here](https://github.com/wellsoliver/py-retrosheet).

## Set Up
#### Configuration
To set up this repo, there needs to be a file in the top level of the repository named "config.csv". This file contains the information Python needs to connect to your MySQL database. There is an example file called "configEXAMPLE.csv". You can copy that file, rename it and only change the second line to be the database name, database username, and password respectively.
#### FLO/MIA
To run the analysis correctly, the updateFLOMIA.sql script needs to be run in MySQL to change the team id for the Marlins since there is data that goes back to when they were the Florida Marlins.

## Methods
The methods used include the Pythagorean win loss, regular win loss, the Oracle method, and Google Page Rank.
