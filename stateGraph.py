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


class StateGraph(object):
    """
    Has information about clusters/states and transitions between them.
    """
    # TODO: Should also support inspection and visualisation for convenience

    # I would propose we follow a sklearn-type code organisation: init just
    # builds the object; a `fit` function needs to be called to process the data

    # def __init__(self, n_clusters: int) -> None:
    #     """
    #     Prepare the object.
    #     """
    #     self.clustering = KMeans(n_clusters = n_clusters)
    #     self.normalisation = preprocessing.MinMaxScaler()
    #     # TODO: ...
    #
    #
    # def fit(self, data: pd.DataFrame):
    #     """Fit to data. Expect Pandas DataFrame as input."""
    #     # fit normaliser to data and scale dataset
    #     # TODO: !!! data will typically contain a timestamp column - check for
    #     #       it, remember it and handle it appropriatly (it shouldn't be
    #     #       normalised etc.)
    #     # TODO: this is just a draft - check if this normalisation is ok
    #     norm_data = self.normalisation.fit_transform(data)
    #     self.clustering.fit(norm_data)
    #     # TODO: ...



    def __init__(self, sensor_values, sensor_list):
        """
        input_csv must be formatted for StreamStory.
        """
        self.sensor_values = sensor_values
        self.sensor_list = sensor_list
        self.create_clusters()

    def create_clusters(self):
        # filter out just needed sensor values
        values = self.sensor_values.filter(items=["timestamp"] + self.sensor_list)

        # TODO normalization

        clustering = KMeans(n_clusters=5).fit(values.filter(items=self.sensor_list))
        centroids = pd.DataFrame(clustering.cluster_centers_, columns=self.sensor_list)
        print(centroids)

        # label states with cluster and print cluster sizes
        cluster_labels = clustering.predict(values.filter(items=self.sensor_list))
        print(sorted(Counter(cluster_labels).items()))


def create_state_graph():
    """
    Prepares data for clustering, creates clusters and returns StateGraph object.
    """
    # read arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-csv', help="Path to input csv with sensor data formatted for StreamStory.")
    parser.add_argument('-sl', '--sensor-list', nargs='+', help="List of senors that will be used for clustering.")
    args = parser.parse_args()
    sensor_values = pd.read_csv(open(args.input_csv))
    return StateGraph(sensor_values, args.sensor_list)


if __name__ == "__main__":
    graph = create_state_graph()