"""
Script that runs HoeffdingTreeClassifier and SGDClassifier on datasets with different number
of states, different sets of sensors and with different window sizes. It creates csv file
with the measurements. If data is scaled before learning, the csv is called
'results_stream_normalized.csv', otherwise it is called 'results_stream.csv'.
"""

import pandas as pd
from skmultiflow.data import TemporalDataStream, DataStream
from skmultiflow.evaluation import EvaluatePrequential
from skmultiflow.trees import HoeffdingTreeClassifier
from skmultiflow.bayes import NaiveBayes
from skmultiflow.meta import OnlineCSB2Classifier
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler


DATA_LOCATION = '../data/'
MODEL_NAMES = ['HoeffdingTreeClassifier', 'SGDClassifier']

def train(name, clusters, window, normalize=False):
    input_csv = '{}{}_clusters={}_window={}_prepared.csv'.format(DATA_LOCATION, name, clusters, window)
    data = pd.read_csv(input_csv, index_col=0)

    if normalize:
        states = data.filter(['current_state', 'next_state'])
        sensors = data.drop(columns=['current_state', 'next_state'])
        scaler = StandardScaler()
        data = pd.DataFrame(data=scaler.fit_transform(X=sensors), index=data.index, columns=sensors.columns)
        data = pd.concat([data, states], axis='columns')

    stream = DataStream(data)

    hf = HoeffdingTreeClassifier()
    sgd = SGDClassifier()

    evaluator = EvaluatePrequential()
    evaluator.evaluate(stream=stream, model=[hf, sgd])
    # print('---------------------------------------------')
    # measurements = evaluator.get_mean_measurements()[0]
    # print(measurements.confusion_matrix)
    # print(measurements.accuracy_score())
    data = []
    for i, measurements in enumerate(evaluator.get_mean_measurements()):
        data.append([name, clusters, window, MODEL_NAMES[i], normalize, measurements.accuracy_score(),
                    measurements.precision_score(), measurements.recall_score(), measurements.f1_score()])
    return pd.DataFrame(data=data,
                        columns=['name', 'clusters', 'window', 'model', 'normalized', 'accuracy', 'precision', 'recall', 'f1'])


def train_all_datasets(normalize=False):
    results = pd.DataFrame(columns=['name', 'clusters', 'window', 'model', 'normalized', 'accuracy', 'precision', 'recall', 'f1'])
    counter = 0
    for name in ['B100', 'B200', 'B200_subset', 'B300']:
        for clusters in [5, 10, 15, 20]:
            for window in [5, 10, 20, 50, 100]:
                print('\n{} / 80'.format(counter + 1))
                output = train(name, clusters, window, normalize)
                results = results.append(output, ignore_index=True)
                counter += 1
    if normalize:
        results.to_csv('../../results/results_stream_normalized.csv')
    else:
        results.to_csv('../../results/results_stream.csv')


if __name__ == '__main__':
    train_all_datasets()
    train_all_datasets(normalize=True)
