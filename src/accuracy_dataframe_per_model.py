# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 15:40:23 2019

@author: ngrif
"""
def check_accuracy_data(threshold, prediction, actual):
    '''
    This function will take two series of equal length and only calculate 
    accuracy for predictions that meet the threshold criteria. 
    '''
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


'''
For the below, update predictions list to be your list of predict probas in
15,30,60,90 order and same for tests list being actual outcomes. 
Change 'your_model_type' (2 serperate inputs) below to some 2-4 character string
that describes your model. (RF, NN, GB, LR, etc etc)
Please push csv to git once complete.
'''
thresholds = [.52, .54, .55, .56]
predictions = [pred_15, pred_30, pred_60, pred_90]
tests = [y_test_15,y_test_30,y_test_60,y_test_90]
mov_avs = [15,30,60,90]
lists_ = []
for p, a, m in zip(predictions, tests, mov_avs):
    for t in thresholds:
        lists_.append(check_accuracy_data(t, p, a) + [m, 'your_model_type'])

df = pd.DataFrame(lists_)
df.columns = ['Threshold', 'Accuracy', 'Percent_of_Samples', 'Dataset', 'Model']

# Change directory for data
os.chdir(r"..\data")

# Save file with your model name 
df.to_csv('accuracy_dataframe_your_model_type.csv')
