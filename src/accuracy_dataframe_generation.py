# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 15:03:04 2019

@author: nlgri
"""
import pandas as pd
import numpy as np
import os 
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import roc_auc_score
from sklearn.metrics import auc
from sklearn.metrics import roc_curve
from boilerplate_modeling import CustomKFold
import pickle


# Change directory for pickle
os.chdir(r"..\models")
with open("RF_15_model.pckl", "rb") as f:
        model_15 = pickle.load(f)
with open("RF_30_model.pckl", "rb") as f:
        model_30 = pickle.load(f)
with open("RF_60_model.pckl", "rb") as f:
        model_60 = pickle.load(f)
with open("RF_90_model.pckl", "rb") as f:
        model_90 = pickle.load(f)
        

# Change directory for data
os.chdir(r"..\data")
        
#dataset
df_15 = pd.read_csv('MovAve15_Data.csv')
df_30 = pd.read_csv('MovAve30_Data.csv')
df_60 = pd.read_csv('MovAve60_Data.csv')
df_90 = pd.read_csv('MovAve90_Data.csv')

#split train/test for each data set
#15
train_15 = df_15[df_15['year'] < 2019]
test_15 = df_15[df_15['year'] == 2019]
x_train_15 = train_15.drop(['Target_Var'], axis=1)
y_train_15 = train_15['Target_Var']
x_test_15 = test_15.drop(['Target_Var'], axis=1)
y_test_15 = test_15['Target_Var']

#30
train_30 = df_30[df_30['year'] < 2019]
test_30 = df_30[df_30['year'] == 2019]
x_train_30 = train_30.drop(['Target_Var'], axis=1)
y_train_30 = train_30['Target_Var']
x_test_30 = test_30.drop(['Target_Var'], axis=1)
y_test_30 = test_30['Target_Var']

#60
train_60 = df_60[df_60['year'] < 2019]
test_60 = df_60[df_60['year'] == 2019]
x_train_60 = train_60.drop(['Target_Var'], axis=1)
y_train_60 = train_60['Target_Var']
x_test_60 = test_60.drop(['Target_Var'], axis=1)
y_test_60 = test_60['Target_Var']

#90
train_90 = df_90[df_90['year'] < 2019]
test_90 = df_90[df_90['year'] == 2019]
x_train_90 = train_90.drop(['Target_Var'], axis=1)
y_train_90 = train_90['Target_Var']
x_test_90 = test_90.drop(['Target_Var'], axis=1)
y_test_90 = test_90['Target_Var']

#Predict the test set
pred_15 = model_15.predict_proba(x_test_15)[:,1]
pred_30 = model_30.predict_proba(x_test_30)[:,1]
pred_60 = model_60.predict_proba(x_test_60)[:,1]
pred_90 = model_90.predict_proba(x_test_90)[:,1]

# Write a function to plot the ROC of each model
def plotROC(prediction, true_value, label_str):
    # Get the values that will be plotted
    fpr, tpr, thresh = roc_curve(true_value, prediction)
    AUC_value = auc(fpr, tpr)
    accuracies = []
    for p, t in zip(prediction, true_value):
        if p >= .5:
            accuracies.append(1 == t)
        else:
            accuracies.append(0 == t)
    accuracy = accuracies.count(True)/len(accuracies)            
    # Plot values returned above
    plt.plot(fpr, tpr, label = label_str + ' (AUC= {0:2.3f}, Accuracy= {1:2.3f})'\
             .format(AUC_value, accuracy))
    # Add diagnoal to show random prediction 
    plt.plot([0, 1], [0, 1], 'k--')
    # Add labels and title
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Cross Dataset Comparison of RF Models')
    plt.legend()
    
plt.figure(figsize= (7,5))
plotROC(pred_15, y_test_15, '15 Dataset')
plotROC(pred_30, y_test_30, '30 Dataset')
plotROC(pred_60, y_test_60, '60 Dataset')
plotROC(pred_90, y_test_90, '90 Dataset')    


# Def accuracy check function    
def check_accuracy(threshold, prediction, actual):
    accuracies = []
    for preds, truth in zip(prediction, actual):
        if preds >= threshold:
            accuracies.append(1 == truth)
        elif preds <= (1-threshold):
            accuracies.append(0 == truth)
        else:
            continue
    of_picks = len(accuracies)/len(prediction)
    if len(accuracies) == 0:
        print('No thresholds met criteria at level {}.'.format(threshold))
    else:
        accuracy = accuracies.count(True)/len(accuracies)
        print('Number of observation satisfying threshold criteria is {}'\
              .format(len(accuracies)))
        print('\t Precentage of preds that met {0} threshold critertia = {1:.3f}%'\
              .format(threshold, of_picks*100))
        print('\t Percentage accuracy of these subsamples is {0:.3f}%'\
              .format(accuracy*100))

def check_accuracy_data(threshold, prediction, actual):
    accuracies = []
    my_list = []
    for preds, truth in zip(prediction, actual):
        if preds >= threshold:
            accuracies.append(1 == truth)
        elif preds <= (1-threshold):
            accuracies.append(0 == truth)
        else:
            continue
    if len(accuracies) == 0:
        accuracy = None
        subsample_percent = 0
    else:
        accuracy = accuracies.count(True)/len(accuracies)
        subsample_percent = len(accuracies)/len(prediction)
    return [threshold, accuracy, subsample_percent]

thresholds = [.52, .54, .55, .56]
predictions = [pred_15, pred_30, pred_60, pred_90]
tests = [y_test_15,y_test_30,y_test_60,y_test_90]
mov_avs = [15,30,60,90]
lists_ = []
for p, a, m in zip(predictions, tests, mov_avs):
    for t in thresholds:
        lists.append(check_accuracy_data(t, p, a) + [m, 'your_model_type'])
        
df = pd.DataFrame(lists)
df.columns = ['Threshold', 'Accuracy', 'Percent_of_Samples', 'Dataset', 'Model']

# Change directory for data
os.chdir(r"..\data")

# Save file with your model name 
df.to_csv('your_file_name')
        
        

        
        
            


        
