"""
Script that runs RandomForest, GradientBoosting and DecisionTree on datasets with different
number of states, different sets of sensors and with different window sizes. It creates csv
file with the measurements. If data is scaled before learning, the csv is called
'results_batch_normalized.csv', otherwise it is called 'results_batch.csv'.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn import metrics


DATA_LOCATION = '../data/'


def train(name, clusters, window, model, model_name, normalize=False):
    input_csv = '{}{}_clusters={}_window={}_prepared.csv'.format(DATA_LOCATION, name, clusters, window)
    data = pd.read_csv(input_csv, index_col=0)

    if normalize:
        states = data.filter(['current_state', 'next_state'])
        sensors = data.drop(columns=['current_state', 'next_state'])
        scaler = StandardScaler()
        data = pd.DataFrame(data=scaler.fit_transform(X=sensors), index=data.index, columns=sensors.columns)
        data = pd.concat([data, states], axis='columns')

    y = data.filter(['next_state'])
    x = data.drop(columns='next_state')

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3)

    model.fit(x_train, np.transpose(y_train.values)[0])
    y_pred = model.predict(x_test)

    report = metrics.classification_report(y_test, y_pred, output_dict=True)

    results = []
    results.append([name, clusters, window, model_name, normalize, report['accuracy'],
                    report['macro avg']['precision'], report['macro avg']['recall'], report['macro avg']['f1-score']])
    return pd.DataFrame(data=results,
                        columns=['name', 'clusters', 'window', 'model', 'normalized', 'accuracy', 'precision', 'recall', 'f1'])


def train_all_datasets(normalize=False):
    results = pd.DataFrame(columns=['name', 'clusters', 'window', 'model', 'normalized', 'accuracy', 'precision', 'recall', 'f1'])
    counter = 0
    for name in ['B100', 'B200', 'B200_subset', 'B300']:
        for clusters in [5, 10, 15, 20]:
            for window in [5, 10, 20, 50, 100]:
                print('\n{} / 80'.format(counter + 1))
                output = train(name, clusters, window, RandomForestClassifier(), 'RandomForestClassifier', normalize)
                results = results.append(output, ignore_index=True)
                output = train(name, clusters, window, GradientBoostingClassifier(), 'GradientBoostingClassifier', normalize)
                results = results.append(output, ignore_index=True)
                output = train(name, clusters, window, DecisionTreeClassifier(), 'DecisionTreeClassifier', normalize)
                results = results.append(output, ignore_index=True)
                #output = train(name, clusters, window, LogisticRegression(), 'LogisticRegression', normalize)
                #results = results.append(output, ignore_index=True)
                counter += 1
    if normalize:
        results.to_csv('../../results/results_batch_normalized.csv')
    else:
        results.to_csv('../../results/results_batch.csv')

if __name__ == '__main__':
    # print(train('B100', 5, 5, RandomForestClassifier(), 'RandomForestClassifier'))
    # print('----------------------------------------------')
    # print(train('B100', 5, 5, True))
    train_all_datasets()
    print('----------------------------------------------')
    train_all_datasets(normalize=True)
