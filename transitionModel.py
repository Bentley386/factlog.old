import pandas as pd
import numpy as np
from skmultiflow.trees import HoeffdingTreeClassifier
from skmultiflow.data import DataStream


class TransitionModel:
    """
    !!! It assumes fully imputed and evenly timed data. !!!

    Data received must be DataFrame with raw measurements and column 'label'. Timestamp must be index of DataFrame and
    it must be in same format as for stream story. Label is an integer denoting state of the measurement. Function fit
    from StateGraph returns data in right format.

    For each feature it calculates average and delta (slope of the least squares linear fit) on last window_size
    measurements. Every time before model is fitted, it is tested on the input.

    Attributes:
        window_size (int): Size of window for rolling average and delta
        history (DataFrame of shape (window_size, n_features)): Last window_size rows of data
        accuracy (float): Accuracy of the model
    """
    def __init__(self, window_size):
        self.window_size = window_size
        self.model = HoeffdingTreeClassifier()
        self.history = None
        self.accuracy = None

    def delta(self, y: pd.Series) -> np.float64:
        """ Return slope of least squares linear fit. """
        x = np.arange(len(y))
        return np.polyfit(x, y, 1)[0]

    def check_data(self):
        pass

    def prepare_data(self, data: pd.DataFrame) -> DataStream:
        """ Take raw data and return data stream with running average and running delta. """
        data = pd.concat([self.history, data])
        # Update self.history to have last self.window_size measurements
        self.history = data.tail(self.window_size)

        sensor_values = data.drop(columns='label')
        labels = data['label']

        prepared_data = pd.DataFrame()
        for col in sensor_values.columns:
            prepared_data[col+'_mean'] = sensor_values[col].rolling(window=self.window_size).mean()
            prepared_data[col+'_delta'] = sensor_values[col].rolling(window=self.window_size).apply(self.delta, raw=True)
        prepared_data['current_state'] = labels
        prepared_data['next_state'] = labels.shift(periods=-1, fill_value=-1)

        # Drop last row, because we don't know next state yet
        prepared_data.drop(prepared_data.tail(1).index, inplace=True)
        prepared_data.drop(prepared_data.head(self.window_size-1).index, inplace=True)
        return DataStream(prepared_data)

    def partial_fit(self, data: pd.DataFrame) -> None:
        """ The most basic working version for now.
        TODO: improve, calculate accuracy, maybe add possibility to learn in batches? """
        stream = self.prepare_data(data)
        n = stream.n_remaining_samples()
        # Test
        # count_right = 0
        # count_changes = 0
        # count_wrong = 0
        # count_same = 0
        # count_success = 0
        for i in range(n):
            x, y = stream.next_sample()
            # Test
            # if self.model.predict(x)[0] == y[0]: count_right += 1
            # else: count_wrong += 1
            # if x[0][-1] != y[0]: count_changes += 1
            # else: count_same += 1
            # if self.model.predict(x)[0] == y[0] and x[0][-1] != y[0]: count_success += 1
            self.model.partial_fit(x, y)
        # Test
        # print("Right:", count_right)
        # print("Wrong:", count_wrong)
        # print("Changes:", count_changes)
        # print("Same:", count_same)
        # print("Success:", count_success)
        # Results
        # Right: 7874 (number of correct predictions)
        # Wrong: 1279 (number of wrong predictions)
        # Changes: 438 (number of changes of states)
        # Same: 8715 (number of times a state stays the same)
        # Success: 125 (number of correct predictions when state changed)

    def predict(self):
        pass

    def save_model(self):
        pass


if __name__ == '__main__':
    data = pd.read_csv("../stateGraphOutput.csv", index_col=0)
    tm = TransitionModel(5)
    tm.partial_fit(data)
