# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 12:24:42 2019

@author: ngrif
"""

# import potentially relevant libraries 
import pandas as pd
import numpy as np
import math 
from sklearn import preprocessing
import os 
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

# Change directory for data
os.chdir(r"..\data")

# Read in the file
df_15 = pd.read_csv('MovAve15_Data.csv')

# split into train and test where test is 2019 season
df_15['year'] = df_15['date_time'].apply(lambda x: int(x.split('-')[0]))
# dropping nans
df_15.drop(list(df_15[df_15.isna().any(axis=1)].index), inplace = True)

# Split into train and test sets by year
train = df_15.loc[df_15['year'] != 2019]
test = df_15.loc[df_15['year'] == 2019]

# Drop the year and date_time variables since they cannot be features
train.drop(['year', 'date_time'], axis = 1, inplace = True)
test.drop(['year', 'date_time'], axis = 1, inplace = True)

#split into X & Y
X_train = train.drop('Target_Var', axis = 1)
X_test = test.drop('Target_Var', axis = 1)
Y_train = train['Target_Var']
Y_test = test['Target_Var']

#scale the datasets
X_train_scl = preprocessing.scale(X_train, axis=0)
X_test_scl = preprocessing.scale(X_test, axis=0)

# build initial version of model 
forest = RandomForestClassifier(max_features= None, min_samples_split=30, 
                                criterion='entropy')
forest_pred = forest.fit(X_train, Y_train).predict(X_test)
pred = forest_pred == Y_test
accuracy = pred.value_counts()[1]/len(pred)

# =============================================================================
# # build better version of model
# clf = SVC(gamma = 'scale',
#           verbose = True,
#           kernel = 'poly',
#           degree = 3)
# clf.fit(X_train_scl, Y_train) 
# pred = clf.predict(X_test_scl) == Y_test
# accuracy = pred.value_counts()[1]/len(pred)
# =============================================================================
