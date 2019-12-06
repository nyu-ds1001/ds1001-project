# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 10:33:48 2019

@author: Jonas
"""

import os
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import scale
from sklearn.model_selection import RandomizedSearchCV
from sklearn.svm import SVC
from sklearn.metrics import roc_curve, auc
from boilerplate_modeling import CustomKFold
import matplotlib.pyplot as plt

os.chdir(r"..\data")

# Read in the file
dfs = {f'df_{i}' : pd.read_csv(f'MovAve{i}_Data.csv') for i in [15,30,60,90]}

# Create empty dictionaries for train and test sets
x_trains, x_tests, y_trains, y_tests = {}, {}, {}, {}

# Load from pickle
results, models = {}, {}
with open("svm_rslts.pickle","rb") as pickle_out:
    results = pickle.load(pickle_out)
with open("svm_mdls.pickle","rb") as pickle_out:
    models = pickle.load(pickle_out)

for key in dfs:
    # dropping nans
    dfs[key].drop(list(dfs[key][dfs[key].isna().any(axis=1)].index),\
       inplace = True)
    
    # getting training and testing sets
    x_trains[key] = dfs[key].query('year < 2019').drop(['Target_Var'], axis=1)
    x_tests[key] = dfs[key].query('year == 2019').drop(['Target_Var'], axis=1)

    y_trains[key] = dfs[key].query('year < 2019')['Target_Var']
    y_tests[key] = dfs[key].query('year == 2019')['Target_Var']
    
    # scaling X-variables
    scale(x_trains[key], copy=False)
    scale(x_tests[key], copy=False)

svm = SVC(random_state=0, 
          verbose=True,
          probability=True)

params = {'C': [0.1, 1, 10],
          'gamma': ['scale', 'auto'],
          }

cv = RandomizedSearchCV(svm,
                        params,
                        n_iter=4,
                        cv=CustomKFold(),
                        scoring='roc_auc',
                        random_state=0,
                        n_jobs=-1,
                        verbose=10
                        )

for ds in dfs:
    print(ds)
    cv.fit(x_trains[ds], y_trains[ds])
    
    results[ds] = pd.DataFrame(cv.cv_results_)[['mean_test_score',\
           'std_test_score','params']]
    models[ds] = cv

    pickle_out = open("svm_rslts.pickle","wb")
    pickle.dump(results, pickle_out)
    pickle_out.close()
    
    pickle_out = open("svm_mdls.pickle","wb")
    pickle.dump(models, pickle_out)
    pickle_out.close()
    
fig = plt.figure(figsize = (12,8))    
for ds in dfs:
    clf = models[ds].best_estimator_
    pred, prob = clf.predict(x_tests[ds]), clf.predict_proba(x_tests[ds])
    fpr, tpr, thresholds = roc_curve(y_tests[ds], prob[:,1]) #pred
    roc_auc = np.round(auc(fpr,tpr), decimals = 4)
    c = (np.random.rand(), np.random.rand(), np.random.rand())
    plt.plot(fpr, tpr, color = c, label = ds + f' (AUC: {roc_auc})')
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.title('AUC')
plt.legend(loc='lower right')
plt.show()