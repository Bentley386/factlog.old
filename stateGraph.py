"""
StateGraph - the Python version of some of SS functionality.

Support:
Clustering
    - cluster a set of sensor data streams into "typical states"
    - use k-means (anything better?)
    - normalisation should not be forgotten - but keep reference to original
        value for inspection
    - long term: can we "inform" the clustering with expert knowledge? One
        option is to modify distance measure by weighting individual sensor
        streams
    - technical: the clustering should build a practical object - streamline
        work and inspection/visualisation, but not bloated

State transition model
    - model transition from one state to another
    - supports running simulations
    - at simplest this can simply be a sampling ditribution
    - test out ML approaches to modeling
    - long term: can we use ML models along side process models provided by
        expert where available?

"""

import pandas as pd
import numpy as np
import argparse

import sklearn
from sklearn.cluster import KMeans
from sklearn import preprocessing
import plotly.express as px
import plotly.graph_objects as go

from transitionModel import TransitionModel


class StateGraph(object):
    """
    Has information about clusters/states and transitions between them.

    Attributes:
        centroids: DataFrame of shape (n_centroids, n_features): Coordinates of centroids.
        transitions: ndarray of shape (n_clusters, n_clusters): Distribution of transitions where number in row i and
            column j represents transition from state i to state j. Numbers on diagonal are 0.
        transition_model: TransitionModel that can predict next state.
    """
    # TODO: Should also support inspection and visualisation for convenience

    # I would propose we follow a sklearn-type code organisation: init just
    # builds the object; a `fit` function needs to be called to process the data

    def __init__(self, n_clusters: int) -> None:
        """
        Prepare the object.
        """
        self.n_clusters = n_clusters
        self.clustering = KMeans(n_clusters=n_clusters)
        self.normalisation = preprocessing.MinMaxScaler()

        # DataFrame where each row is coordinate of a centroid
        self.centroids = None
        # Matrix of transitions with values between 0 and 1
        self.transitions = None
        # Model that can predict next state. Must be initialized manually.
        self.transition_model = None

    def fit(self, data: pd.DataFrame) -> None:
        """Fit to data. Expect Pandas DataFrame as input."""
        if 'timestamp' not in data:
            raise RuntimeError("Expecting column called `timestamp`.")

        timestamp = data['timestamp']
        without_time = data.drop(labels='timestamp', axis='columns')

        norm_data = pd.DataFrame(data=self.normalisation.fit_transform(without_time),
                                 index=timestamp,
                                 columns=without_time.columns)

        self.clustering.fit(norm_data)

        self.centroids = pd.DataFrame(data=self.normalisation.inverse_transform(self.clustering.cluster_centers_),
                                      columns=norm_data.columns)

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """" Returns data with column `label` which has index of the closest cluster for each sample. """
        if 'timestamp' not in data:
            raise RuntimeError("Expecting column called `timestamp`.")

        timestamp = data['timestamp']
        without_time = data.drop(labels='timestamp', axis='columns')

        norm_data = pd.DataFrame(data=self.normalisation.transform(without_time),
                                 index=timestamp,
                                 columns=without_time.columns)

        labels = pd.DataFrame(self.clustering.predict(norm_data), columns=['label'])

        # Calculate transitions between states
        self.transitions = np.zeros([self.n_clusters, self.n_clusters])
        prev = -1
        for index, row in labels.iterrows():
            if index > 0 and prev != row['label']:
                self.transitions[prev, row['label']] += 1
            prev = row['label']
        self.transitions = np.apply_along_axis(lambda row : row / row.sum(), 1, self.transitions)

        return pd.concat([data, labels], axis=1)

    def fit_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        self.fit(data)
        return self.transform(data)

    def get_figure(self) -> go.Figure:
        """Returns plotly object Figure displaying centroids' coordinates."""
        fig = px.parallel_coordinates(
            self.centroids,
            color=self.centroids.index,
            dimensions=self.centroids.columns
        )
        return fig


def create_state_graph(n_clusters):
    """
    Prepares data for clustering, creates clusters and returns StateGraph object.
    """
    # read arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-csv', help="Path to input csv with sensor data formatted for StreamStory.")
    # parser.add_argument('-sl', '--sensor-list', nargs='+', help="List of senors that will be used for clustering.")
    args = parser.parse_args()
    sensor_values = pd.read_csv(open(args.input_csv))
    graph = StateGraph(n_clusters=n_clusters)
    graph.fit(sensor_values)
    return graph


if __name__ == "__main__":
    graph = create_state_graph()

    # sensor_list = ["50", "53", "55", "62", "63", "64", "65", "97", "98"]
    # graph = StateGraph(n_clusters=5)
    # sensor_values = pd.read_csv(open('../B100_hour_SS_input.csv'))
    # values = sensor_values.filter(items=["timestamp"] + sensor_list)
    # graph.fit(values)
    # result = graph.transform(values)
    # result = graph.fit_transform(values)
    # result.to_csv('../output.csv', index=False)
    # print(result)
    # print(graph.transitions)
    # graph.get_figure().show()
