# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 15:40:23 2019

@author: ngrif
"""
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