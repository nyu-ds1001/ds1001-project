# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 18:40:49 2019

@author: nlgri
"""
#importing relevant libraries
import pandas as pd
import numpy as np
import math 
from sklearn import preprocessing
import os 

# Load local libraries
from clean_functions import *

#importing dataset
df = pd.read_csv('merged_var_generated.csv')

#finding games that were definitley rainouts and removing them 
df = df.drop(list(df.query('IP_team_home < 9 | IP_team_away < 8').index))

#dropping close_odds as we will only use open & renaming some variables
#for increased clarity 
df = df.drop(list(df.columns[-7:-4]), axis=1)

updated_cols = list(df.columns[:-7]) + ['over_under', 
                   'under_odds', 'over_odds'] + list(df.columns[-4:])
df.columns = updated_cols

#Dropping the obvious odds typos from dataset 
df = df.drop(list(df.loc[df['over_under'] >= 20].index))

#Dropping 4 variables empty variables/they do not exist
df = df.drop(['IR_player_away', 
              'IS_player_away', 
              'IR_player_home', 
              'IS_player_home',], axis = 1) 

#finding games where the would be no target variable
#because outcome = prediction
df['Game_score'] = df['R_home'] + df['R_away']
df['pushed_bets'] = df['Game_score'] == df['over_under']
df = df.drop(list(df.loc[df['pushed_bets'] == True].index))
#Defining Target Variable where 1 is over and 0 is under and dropping the 
#now unneeded variables
df['Target_Var'] = (df['Game_score'] > df['over_under']) * 1
df = df.drop(['pushed_bets',
              'Game_score'], axis = 1)

#make a DF with only games that have odds (about half the whole dataset)
odds_only = df.drop(list(df.loc[df['over_under'].isna()].index))
target_split = odds_only.loc[:,'Target_Var'].value_counts()[1] / (
        (odds_only.loc[:,'Target_Var'].value_counts()[0]) + (
                odds_only.loc[:,'Target_Var'].value_counts()[1]))
# ensure split of target var is rouhgly 50/50
assert(target_split >= .485 and target_split <= .515)

#Updating odds to European version for easier readability 
df['under_odds'] = df['under_odds'].apply(ContinentalOdds)
df['over_odds'] = df['over_odds'].apply(ContinentalOdds)

# Split and clean the weather data
new = df['weather_info'].str.split(",", expand = True)

# Clean temperature
df['temperature'] = new[0].astype(str).apply(clean_temp)

# Clean wind speed and direction
df['wind_speed'] = new[1].astype(str).apply(clean_wSpeed)
df['wind_direction'] = new[1].astype(str).apply(clean_wDirection)

# Clean weather
df['weather'] = new[2].astype(str).apply(clean_weather)
head2 = df.head()

#Encoding wind direction 
wind_dir = pd.get_dummies(df.wind_direction, prefix='Wind_Direction').iloc[:,1:]
df = pd.concat([df,wind_dir], axis=1)
df = df.drop('wind_direction', axis = 1)

#Encoding weather forecast
weather = pd.get_dummies(df.weather, prefix='Weather').iloc[:,1:]
df = pd.concat([df,weather], axis=1)
df = df.drop(['weather','weather_info'], axis = 1)

#Transforming home pitcher names/hands to managable columns
pitch_home = df['home_pitcher'].str.split('-', expand = True)
#some splits had three columns, ensuring all pitchers have a 'hand'
indexes = list(pitch_home[((pitch_home[1] == 'L') | (pitch_home[1] == 'R') \
                           == False).values].dropna().index)
replacements = list(pitch_home[((pitch_home[1] == 'L') | \
                                (pitch_home[1] == 'R') == False).values].dropna()[2])
for i, r in zip(indexes,replacements):
    pitch_home.loc[i,1] = r
#dropping the unneeded column, renaming columns
pitch_home = pitch_home.drop(2, axis = 1)
pitch_home.columns = ['home_pitcher_name', 'handed_home']
#Repeating the same process for away pitchers
pitch_away = df['away_pitcher'].str.split('-', expand = True)
indexes = list(pitch_away[((pitch_away[1] == 'L') | (pitch_away[1] == 'R') == False).values].dropna().index)
replacements = list(pitch_away[((pitch_away[1] == 'L') | (pitch_away[1] == 'R') == False).values].dropna()[2])
for i, r in zip(indexes,replacements):
    pitch_away.loc[i,1] = r
pitch_away = pitch_away.drop(2, axis = 1)
pitch_away.columns = ['away_pitcher_name', 'handed_away']

#Concating the two DFs to our main data and dropping now uneeded columns 
df = pd.concat([df, pitch_home, pitch_away], axis=1)
df = df.drop(['home_pitcher', 'away_pitcher'], axis = 1)

#encoding each home/away pitcher hand
home_pitch_hand = pd.get_dummies(df.handed_home, prefix='home_pitcher_hand').iloc[:,1:]
df = pd.concat([df,home_pitch_hand], axis=1)
df = df.drop('handed_home', axis = 1)
away_pitch_hand = pd.get_dummies(df.handed_away, prefix='away_pitcher_hand').iloc[:,1:]
df = pd.concat([df,away_pitch_hand], axis=1)
df = df.drop('handed_away', axis = 1)

#turns out we don't need pitcher names either, so dropping them as well
df = df.drop(['home_pitcher_name', 'away_pitcher_name'], axis = 1)

# Clean time and date data
df['start_time'] = pd.to_datetime(df['start_time'] \
  .astype(str).apply(clean_time)).dt.strftime('%H:%M:%S')
df['date_time'] = pd.to_datetime(df['date'] + ' ' + df['start_time'])
df = df.drop(columns=['start_time', 'date'])

# Adding column for rounded hour
df['hour'] = df['date_time'].apply(lambda x: x.hour)

# One hot encoding home team
home_team = pd.get_dummies(df.home_team, prefix = 'home_team').iloc[:,1:]
df = pd.concat([df,home_team], axis=1)
df = df.drop(['home_team'], axis = 1)

# One hot encoding away team
away_team = pd.get_dummies(df.away_team, prefix = 'away_team').iloc[:,1:]
df = pd.concat([df,away_team], axis=1)
df = df.drop(['away_team'], axis = 1)

# One hot encoding venues
venues = pd.get_dummies(df.venue, prefix = 'played_at').iloc[:,1:]
df = pd.concat([df,venues], axis=1)
df = df.drop(['venue'], axis = 1)

# Dropping home/away errors now as opposed to later, because we know
# there was an issue in the pull, and we do not want to mistakingly
# use them in any way.
df = df.drop(['away_errors', 'home_errors' ], axis = 1)

# exporting to csv file
df.to_csv('merged_and_cleaned_dataset.csv')
#recreating odds_only dataset for analysis that is needed and saving it
odds_only = df.drop(list(df.loc[df['over_under'].isna()].index))
odds_only.to_csv('merged_and_cleaned_odds_only_games_dataset.csv')




