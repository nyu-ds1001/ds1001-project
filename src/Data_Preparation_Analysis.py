# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# Load basic libraries
import os
import pandas as pd
import numpy as np
from sklearn import preprocessing

# Change directory for functions
os.chdir(r"..\src")

# Load local libraries
from clean_functions import *
from featgen_functions import MovAveTeam, EloTeam

# Change directory for data
os.chdir(r"..\data")

# Load the data
df = pd.read_csv('merged.csv')

# Split and clean the weather data
new = df['weather_info'].str.split(",", expand = True)

# Clean temperature
df['temperature'] = new[0].astype(str).apply(clean_temp)

# Clean wind speed and direction
df['wind_speed'] = new[1].astype(str).apply(clean_wSpeed)
df['wind_direction'] = new[1].astype(str).apply(clean_wDirection)
labelenc_wind = preprocessing.LabelEncoder()
df['wind_direction'] = labelenc_wind.fit_transform(df['wind_direction'].astype(str))

# Clean weather
df['weather'] = new[2].astype(str).apply(clean_weather)
labelenc_weather = preprocessing.LabelEncoder()
df['weather'] = labelenc_weather.fit_transform(df['weather'].astype(str))

# Drop weather info
df = df.drop(columns=['weather_info'])

# Clean time and date data
df['start_time'] = pd.to_datetime(df['start_time'].astype(str).apply(clean_time)).dt.strftime('%H:%M:%S')
df['date_time'] = pd.to_datetime(df['date'] + ' ' + df['start_time'])
df = df.drop(columns=['start_time', 'date'])

# Encode the team variables
labelenc_team = preprocessing.LabelEncoder()
df['home_team'] = labelenc_team.fit_transform(df['home_team'].astype(str))
df['away_team'] = labelenc_team.transform(df['away_team'].astype(str))

# Encode the venue variable
labelenc_venue = preprocessing.LabelEncoder()
df['venue'] = labelenc_team.fit_transform(df['venue'].astype(str))

# Encode the pitcher variables
labelenc_pitcher = preprocessing.LabelEncoder()
labelenc_pitcher.fit(df['home_pitcher'].append(df['away_pitcher']).astype(str))
df['home_pitcher'] = labelenc_pitcher.transform(df['home_pitcher'].astype(str))
df['away_pitcher'] = labelenc_pitcher.transform(df['away_pitcher'].astype(str))

# Drop empty variables
df = df.drop(['IR_player_away', 
              'IS_player_away', 
              'IR_player_home', 
              'IS_player_home'], axis = 1) 

# Create new continental odd variables for over/under
df['open_under_cont'] = df['open_under'].apply(ContinentalOdds)
df['open_over_cont'] = df['open_over'].apply(ContinentalOdds)
df['close_under_cont'] = df['close_under'].apply(ContinentalOdds)
df['close_over_cont'] = df['close_over'].apply(ContinentalOdds)

# Get descriptive statistics
df_des = df.describe().transpose()
df_des.to_csv(r'data_description.csv')

# Generate histograms per variable
#try:
#    os.mkdir("exploration/histograms")
#except OSError:
#    print('No new directory created')
#    
#for (columnName, columnData) in df.iteritems():
#    ax = df[columnName].hist(bins='auto')
#    fig = ax.get_figure()
#    fig.savefig(f'exploration/histograms/{columnName}.pdf')

# =============================================================================
# # Generate moving averages per team for 30, 60 and 90 games. 'RE24_team_home'
# for x in [30,60,90]:
#     for (columnName, columnData) in df.loc[:,'AB_home':'SLG_home'].iteritems():
#         y = columnName[:-5]
#         print(y)
#         df[f'{y}_MovAve{x}_home'], df[f'{y}_MovAve{x}_away'] = MovAveTeam(df, y, lngth=x)
# =============================================================================

# Calculate the elo of the teams
df = EloTeam(df, start_elo = 1000, K = 30)
