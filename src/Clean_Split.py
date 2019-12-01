# -*- coding: utf-8 -*-
"""
Created on Sun Dec  1 12:29:58 2019

@author: Jonas
"""

import numpy as np
import pandas as pd 
from sklearn import preprocessing
import os

# Change directory for functions
os.chdir(r"..\src")

# import moving average function 
from featgen_functions import *

# Change directory for data
os.chdir(r"..\data")

# importing data set 
df = pd.read_csv('merged_and_cleaned_dataset.csv')

#Dropping variables we cannot define well enough to use 
df = df.drop(['WPA_home',
              'WPA_away',
              'WPA+_home',
              'WPA+_away',
              'WPA-_home',
              'WPA-_away', 
              'RE24_home',
              'RE24_away',
              'RE24_player_away',
              'RE24_player_home',
              'RE24_team_away',
              'RE24_team_home',
              'WPA_team_home',
              'WPA_team_away',
              'aLI_team_home',
              'aLI_team_away',
              'WPA_player_home',
              'WPA_player_away',
              'aLI_player_home',
              'aLI_player_away',
              'IP_team_home',
              'IP_team_away',
              'IR_team_away', 
              'IS_team_away', 
              'IR_team_home', 
              'IS_team_home',
              'Unk_player_home',
              'Unk_player_away',
              'Unk_team_home',
              'Unk_team_away',
              'BB_team_home',
              'BB_team_away',
              'SO_team_home',
              'SO_team_away',
              'BF_team_home',
              'BF_team_away'], axis = 1)

# Turn of warnings
pd.options.mode.chained_assignment = None

# Run over different moving average lengths
for i in [15,30,60,90]:
    df_tmp = df.copy(deep=True)
    for (columnName, columnData) in df.loc[:,'AB_home':'GSc_team_home'].iteritems():
        if 'away' in columnName: continue 
        y = columnName[:-5]
        print(y)
        df_tmp[f'{y}_home'], df_tmp[f'{y}_away'] = MovAveTeam(df_tmp, y, lngth=i)
    
    df_tmp = df_tmp.drop(columns = ['home_team','away_team','UID'])
    df_tmp = df_tmp.drop(list(df.loc[df_tmp['over_under'].isna()].index))
    df_tmp.to_csv(f'MovAve{i}_Data.csv', index = False)