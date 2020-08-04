import pandas as pd
import numpy as np
from skmultiflow.trees import HoeffdingTreeClassifier
from skmultiflow.data import DataStream
from typing import List


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
        # Number of all predictions and correct predictions for calculating accuracy
        self.predictions = 0
        self.correct_predictions = 0

    def delta(self, y: pd.Series) -> np.float64:
        """ Return slope of least squares linear fit. """
        x = np.arange(len(y))
        return np.polyfit(x, y, 1)[0]

    def check_data(self):
        pass

    def prepare_data(self, data: pd.DataFrame, drop_last_row: bool = True, use_history: bool = True) -> pd.DataFrame:
        """ Take raw data and return data stream with running average and running delta. For the last row there is no
            next state, so drop_last_row should be True for learning, but False for predicting. If use_history is set
            to true function will add history to the data and update history."""
        if use_history:
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
        if drop_last_row:
            prepared_data.drop(prepared_data.tail(1).index, inplace=True)
        prepared_data.drop(prepared_data.head(self.window_size-1).index, inplace=True)
        return prepared_data

    def partial_fit(self, data: pd.DataFrame) -> None:
        """ The most basic working version for now.
        TODO: improve, calculate accuracy, maybe add possibility to learn in batches? """
        stream = DataStream(self.prepare_data(data))
        n = stream.n_remaining_samples()
        for i in range(n):
            x, y = stream.next_sample()
            if self.model.predict(x)[0] == y[0]:
                self.correct_predictions += 1
            self.model.partial_fit(x, y)
        self.predictions += n
        self.accuracy = self.correct_predictions / self.predictions

    def predict(self, data: pd.DataFrame = pd.DataFrame(), use_history: bool = True) -> List[int]:
        """ Argument data is a DataFrame with shape (n_samples, n_features).
        use_history tells whether or not history will be included in data before making prediction. If use_history is
        set to true, function will make n_samples+1 predictions, otherwise n_samples-window_size+1 predictions."""
        if not use_history and data.shape[0] < self.window_size:
            raise RuntimeError("Not enough measurements to make a prediction.")
        prepared_data = self.prepare_data(data, drop_last_row=False, use_history=use_history)
        prepared_data.drop(columns="next_state", inplace=True)
        return self.model.predict(prepared_data.values)

    def save_model(self):
        pass


if __name__ == '__main__':
    data = pd.read_csv("../data/stateGraphOutput.csv", index_col=0)
    tm = TransitionModel(5)
    tm.partial_fit(data[:-10])
    print(tm.predict(data[-10:]))
    print(tm.accuracy)
    # print(tm.predict(data[-10:], use_history=False))
    # tm.predict(data[-1:], use_history=False)  # Runtime error
