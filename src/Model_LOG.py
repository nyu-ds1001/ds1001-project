# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 10:33:48 2019

@author: Jonas
"""

import os
import pickle
import pandas as pd
import numpy as np
import datetime as dt
from sklearn.preprocessing import scale, MinMaxScaler
from sklearn.model_selection import RandomizedSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, auc
from boilerplate_modeling import CustomKFold
import matplotlib.pyplot as plt
from scipy.stats import kstest

os.chdir(r"..\data")

# Read in the file
dfs = {f'df_{i}' : pd.read_csv(f'MovAve{i}_Data.csv') for i in [15,30,60,90]}

# Create empty dictionaries for train and test sets
x_trains, x_tests, y_trains, y_tests = {}, {}, {}, {}

# Load from pickle
results, models = {}, {}
if os.path.getsize("log_rslts.pickle") > 0:
    with open("log_rslts.pickle","rb") as pickle_out:
        results = pickle.load(pickle_out)
if os.path.getsize("log_mdls.pickle") > 0:
    with open("log_mdls.pickle","rb") as pickle_out:
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
    
    scaler = MinMaxScaler(feature_range = (0,1))
    x_trains[key] = pd.DataFrame(scaler.fit_transform(x_trains[key]),
            columns = x_trains[key].columns)
    x_tests[key] = pd.DataFrame(scaler.fit_transform(x_tests[key]),
            columns = x_trains[key].columns)
    
# =============================================================================
#     # scaling X-variables
#     for feat in x_trains[key].columns:
#       D, pval = kstest(dfs[key][feat], 'norm')
#       if pval < 0.05: # Normalize
#         scaler = MinMaxScaler(feature_range=(0, 1))
#         x_trains[key][feat] = np.squeeze(scaler.fit_transform(x_trains[key][feat].values.reshape(-1,1)))
#         x_tests[key][feat] = np.squeeze(scaler.fit_transform(x_tests[key][feat].values.reshape(-1,1)))
#       else: # Standardize
#         print(f"{feat} is normally distributed.")
#         x_trains[key][feat] = scale(x_trains[key][feat])
#         x_tests[key][feat] = scale(x_tests[key][feat])
# =============================================================================

log = LogisticRegression(random_state=0,
                         verbose=True)

params = {'penalty': ['l1', 'l2'],
          'C': [0.1, 1, 10],
          'fit_intercept': [True, False]
          }

cv = RandomizedSearchCV(log,
                        params,
                        n_iter=10,
                        cv=CustomKFold(),
                        scoring='roc_auc',
                        random_state=0,
                        n_jobs=-1,
                        verbose=10
                        )

now = dt.datetime.now().strftime("%m%d")
for ds in dfs:
    print(ds)
    cv.fit(x_trains[ds], y_trains[ds])
    
    results[ds] = pd.DataFrame(cv.cv_results_)[['mean_test_score',\
           'std_test_score','params']]
    
    models[ds] = cv
    
    pickle_out = open(f"log_rslts_{now}.pickle","wb")
    pickle.dump(results, pickle_out)
    pickle_out.close()
    
    pickle_out = open("log_mdls_{now}.pickle","wb")
    pickle.dump(models, pickle_out)
    pickle_out.close()
   
# =============================================================================
# plt.figure(figsize = (12,8))    
# for ds in dfs:
#     clf = models[ds].best_estimator_
#     pred, prob = clf.predict(x_tests[ds]), clf.predict_proba(x_tests[ds])
#     fpr, tpr, thresholds = roc_curve(y_tests[ds], prob[:,1]) #pred
#     roc_auc = np.round(auc(fpr,tpr), decimals = 4)
#     c = (np.random.rand(), np.random.rand(), np.random.rand())
#     plt.plot(fpr, tpr, color = c, label = ds + f' (AUC: {roc_auc})')
# plt.ylabel('True Positive Rate')
# plt.xlabel('False Positive Rate')
# plt.title('AUC')
# plt.legend(loc='lower right')
# plt.show()
# 
# for ds in dfs:
#     clf = models[ds].best_estimator_
#     feats = clf.coef_
#     indices = np.argsort(feats)[::-1][:,:10]
#     varnames = dfs[ds].columns[indices][0]
#     plt.figure(figsize = (12,8))    
#     plt.bar(list(varnames), list(feats[:,indices][0][0]),
#             color="b", align="center")
#     plt.xticks(list(varnames), list(varnames), rotation='vertical')
#     plt.show()
#     input('Press any Key of Next Plot')
# =============================================================================
