class TransitionModel:
    """
    !!! It assumes fully imputed and evenly timed data. !!!

    Data received must be DataFrame with raw measurements and columns 'timestamp' and 'label'. Timestamp must be in same
    format as for stream story. Label is an integer denoting state of the measurement.

    For each feature it calculates average and delta (slope of the least squares linear fit) on last window_size
    measurements. Every time before model is fitted, it is tested on the input.

    Attributes:
        window_size (int): Size of window for rolling average and delta
        history (DataFrame of shape (window_size, n_features)): Last window_size rows of data
        accuracy (float): Accuracy of the model
    """
    def __init__(self, window_size):
        self.window_size = window_size
        self.history = None
        self.accuracy = None
        self.model = None

    def average(self):
        pass

    def delta(self):
        pass

    def check_data(self):
        pass

    def prepare_data(self):
        pass

    def partial_fit(self):
        pass

    def predict(self):
        pass

    def save_model(self):
        pass
