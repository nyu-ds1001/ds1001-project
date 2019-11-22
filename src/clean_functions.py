# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 16:02:51 2019

@author: Jonas
"""

def clean_temp(x):
    import numpy as np
    if x == 'nan':
        return np.nan
    else:
        return int(x[:-2])
    
def clean_wSpeed(x):
    import numpy as np
    if x.find('mph') != -1:
        return int(x[:x.index('mph')][5:])
    else:
        return np.nan

def clean_wDirection(x):
    if x.find('Left to Right') != -1:
        return 'East'
    elif x.find('Right to Left') != -1:
        return 'West'
    elif x.find('out to Centerfield') != -1:
        return 'North'
    elif x.find('out to Rightfield') != -1:
        return 'North-East'
    elif x.find('out to Leftfield') != -1:
        return 'North-West'
    elif x.find('in from Leftfield') != -1:
        return 'South-East'
    elif x.find('in from Rightfield') != -1:
        return 'South-West'
    elif x.find('in from Centerfield') != -1:
        return 'South'
    else:
        return 'Unknown'
    
def clean_weather(x):
    x = x.replace('.', '')
    if x == ' Cloudy':
        return x.replace(' ','')
    elif x == ' Sunny':
        return x.replace(' ','')
    elif x == ' In Dome':
        return x.replace(' ','')
    elif x == ' Overcast':
        return x.replace(' ','')
    elif x == ' Night':
        return x.replace(' ','')
    else:
        return 'Unknown'
    
def clean_time(x):
    return x.replace('Local','').replace('ET','')

def ContinentalOdds(x):
    if x > 0:
        return (x + 100)/100
    else:
        return -(100 - x)/x
    
    










