# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 16:08:29 2019

@author: Jonas
"""

def MovAveTeam(df, stat, lngth):
    # Import the required python libraries
    import numpy as np
    import pandas as pd
    
    # Configure variables and results data frame
    stat_h, stat_a = stat + "_home", stat + "_away"
    rslt = pd.DataFrame(np.nan,
                        index=range(len(df)), 
                        columns=['home','away'])
    rslt['UID'] = df['UID']
    
    # Calculate the rolling for every team
    for i in sorted(df['home_team'].unique()):
    #for i in [1]:
        # Get conditions for the team being either home or away and retrieve
        # the related index
        team_cond = (df['home_team'] == i) | (df['away_team'] == i)
        index = df.index[team_cond].tolist()
        # Generate a temporary data frame to do the calculations in
        tmp = df[['UID',
                  'date_time',
                  'home_team',
                  'away_team',
                  stat_h,
                  stat_a]].loc[index].copy()
        # Sort by date
        tmp = tmp.sort_values(['date_time'], ascending=1)
        # Get conditions for teams being either home or away
        home_cond, away_cond = (tmp['home_team'] == i), (tmp['away_team'] == i)
        index_home = tmp.index[home_cond].tolist()
        index_away = tmp.index[away_cond].tolist()
        # Collect the desired stat in one column and calculate the rolling ave
        tmp[stat] = tmp[stat_h]*home_cond + tmp[stat_a]*away_cond
        tmp['MovA'] = tmp[stat].rolling(window=lngth).mean()
        # Shift the rolling average with one back to prevent data leakage
        tmp['MovA'] = tmp['MovA'].shift(periods=1)
        # Sort moving average in respective home or away columns
        tmp['home'], tmp['away'] = np.nan, np.nan
        tmp['home'].loc[index_home] = tmp['MovA'].loc[index_home]
        tmp['away'].loc[index_away] = tmp['MovA'].loc[index_away]
        
        # Sort both rslt and tmp to make sure the UIDs align
        tmp = tmp.sort_values(['UID'], ascending=1)
        rslt = rslt.sort_values(['UID'], ascending=1)
        
        # Fill the results data frame with the team specific moving average
        rslt = rslt.combine_first(tmp[['UID','home','away']])
        
    return rslt['home'], rslt['away']

def EloTeam(df, start_elo, K, lower_bound = 100, reset = True):
    import numpy as np
    
    df = df.sort_values(['date_time'], ascending=1)
    df['elo_home'], df['elo_away'] = np.nan, np.nan
    df['home_win'] = (df['R_home'] >= df['R_away'])

    year = np.nan
    d = {i:start_elo for i in sorted(df['home_team'].unique())}
    for j, row in df.iterrows():
        if row['date_time'].year != year and reset:
            d = {i:start_elo for i in sorted(df['home_team'].unique())}
            year = row['date_time'].year
        
        home, away = row['home_team'], row['away_team']
        df.at[j,'elo_home'], df.at[j,'elo_away'] = d[home], d[away]
        prob = 1 / (1 + np.power(10, (d[away] - d[home]) / 400))
        
        chng = int(row['home_win'])-prob
        d[home] = max(d[home] + K * chng, lower_bound)
        d[away] = max(d[away] - K * chng, lower_bound)
        
    return df

def MatchUpPitcher(df, stat, lngth_pt=5, lngth_p=30):
    import numpy as np
    import datetime as dt
    
    df = df.sort_values(['date_time'], ascending=1).copy(deep=True)
    df[f'pit_{stat}_home'], df[f'pit_{stat}_away'] = np.nan, np.nan
    stat_h, stat_a = stat + "_home", stat + "_away"
    
    # Create matchup ID
    df['pt_ha'] = df['home_pitcher'].astype(str) + '_' + df['away_team'].astype(str)
    df['pt_ah'] = df['away_pitcher'].astype(str) + '_' + df['home_team'].astype(str)
    
    for j, row in df.iterrows():
        print(row['date_time'])
        for w in ['ha','ah']:
            
            match = row[f'pt_{w}']
            print('matchup: ' + match)
            
            if w[0] == 'h':
                pitcher = row['home_pitcher']
            else:
                pitcher = row['away_pitcher']
            print('pitcher: ' + str(pitcher))
            if pitcher == 1059: continue 
            
            tmp_pt = df.query('pt_ha == @match | pt_ah == @match')
            tmp_pt[stat] = (tmp_pt['pt_ha'] == row[f'pt_{w}'])*(tmp_pt[stat_h]) + (tmp_pt['pt_ah'] == row[f'pt_{w}'])*(tmp_pt[stat_a])
            tmp_pt = tmp_pt[(tmp_pt['date_time'] < row['date_time'])]
            print('#n matchups: ' + str(len(tmp_pt)))
            
            nom = tmp_pt[stat][-lngth_pt:].mean()
            if np.isnan(nom):
                print(f'Match-up {lngth_pt} average unavailable')
                continue
            
            tmp_p = df.query('home_pitcher == @pitcher | away_pitcher == @pitcher')
            tmp_p[stat] = (tmp_p['home_pitcher'] == pitcher)*(tmp_p[stat_h]) + (tmp_p['away_pitcher'] == pitcher)*(tmp_p[stat_a])
            tmp_p = tmp_p[(tmp_p['date_time'] < row['date_time'])]
            print('#n pitches: ' + str(len(tmp_p)))
            
            den = tmp_p[stat][-lngth_p:].mean()
            if np.isnan(den) or den == 0:
                print(f'Pitcher {lngth_p} average unavailable')
                continue
            
            if w[0] == 'h':
                df.at[j,f'pit_{stat}_home'] = nom/den
                print('home: ' + str(nom/den))
            else:
                df.at[j,f'pit_{stat}_away'] = nom/den
                print('away: ' + str(nom/den))
        print('\n')
            
    df[f'pit_{stat}_home'] = df[f'pit_{stat}_home'].fillna(1)
    df[f'pit_{stat}_away'] = df[f'pit_{stat}_away'].fillna(1)
    
    df.drop(columns = ['pt_ha','pt_ah'])
    return df