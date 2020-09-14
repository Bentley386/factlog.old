""" Visualization of states obtained from state_graph.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.offline import plot
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from state_graph import StateGraph


class Visualization():
    """
    Maintains information of a single dataset
    and provides methods for its visualization.
    """
    
    def __init__(self, raw_data : pd.DataFrame, n_clusters : int) -> None:
        """Initialize the object.
        
        Arguments:
            raw_data -- pandas DataFrame with timestamp as index.
            n_clusters -- number of clusters to be used in clustering.
        """
        
        self.graph = StateGraph(n_clusters)
        self.data = self.graph.fit_transform(raw_data)
        self.norm_data = pd.DataFrame(
                data=self.graph.normalisation.transform(raw_data),
                index=raw_data.index,
                columns=raw_data.columns)
        self.labels = np.array([self.data["label"].to_numpy()]).T
        
        
    def get_parallel_plot(self) -> go.Figure:
        """Returns a Figure containing the parallel plot of
        clusters' centroids.
        """
        
        fig = px.parallel_coordinates(
                self.graph.centroids,
                color=self.graph.centroids.index,
                dimensions=self.graph.centroids.columns
                )
        return fig
    
    def get_PCA(self) -> go.Figure:
        """Returns a Figure containing a PCA plot of clustered data."""
        
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(self.norm_data)
        plot_data = pd.DataFrame(
                np.concatenate((pca_result,self.labels),axis=1),
                columns=["pca_x","pca_y","cluster"])
        return px.scatter(plot_data,x="pca_x",y="pca_y",color="cluster")
    
    def get_TSNE(self, perplexity : int = 100, n_iter : int = 3000) -> go.Figure:
        """Returns a Figure containing a TSNE plot of clustered data.
        Function arguments correspond to standard TSNE arguments.
        """
        
        tsne = TSNE(n_components=2,
                    verbose=1,
                    perplexity=perplexity,
                    n_iter=n_iter)
        tsne_result = tsne.fit_transform(self.norm_data)
        plot_data = pd.DataFrame(
                np.concatenate((tsne_result,self.labels),axis=1),
                columns=["tsne_x","tsne_y","cluster"])
        return px.scatter(plot_data,x="tsne_x",y="tsne_y",color="cluster")
    
    def get_histograms(self,cluster : int) -> go.Figure:
        """Returns a figure containing a histogram for each sensor 
        for the data in a given cluster (cluster index starts at 0).
        """

        if cluster not in self.labels.flatten():
            raise ValueError(f"cluster must be between 0 and {np.amax(self.labels)}")
            
        filtered = self.data[self.data["label"] == cluster]
        cols = filtered.columns.values[:-1]
        
        fig = make_subplots(rows=len(cols)//2,cols=2,subplot_titles=cols)
        for index, sensor in enumerate(cols):
            x = filtered[sensor].values
            fig.append_trace(
                    go.Histogram(x=x, name=sensor),
                    row=index//2+1,
                    col=index%2+1
                    )
            fig.update_xaxes(title_text=sensor, row=index//2+1, col=index%2+1)
            fig.update_yaxes(title_text="Count", row=index//2+1, col=index%2+1)

        fig.update_layout(autosize=False,width=1500,height=200*len(cols),
                          showlegend=False)
        return fig
        
if __name__ == "__main__":
    sensor_list = ["50", "53", "55", "62", "63", "64", "65", "97", "98"]
    sensor_values = pd.read_csv(open('../data/B100_hour_SS_input.csv'), index_col=0)
    values = sensor_values.filter(items=["timestamp"] + sensor_list)
    visual = Visualization(values,5)
    plot(visual.get_histograms(2),auto_open=True)