"""
dp means clustering algorithm.
Implemented as described on https://arxiv.org/pdf/1111.0352.pdf (page 6)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class DPMeans():
    """
    Maintains information on clustering parameters and provides methods
    for fitting and predicting data.
    """
    
    def __init__(self,lambd: float, tol: float=1e-5) -> None:
        """
        Arguments:
            lambd -- effectively the "minimum distance between clusters".
            tol -- error tolerance.
        """
        self.lambd = lambd
        self.tol = tol
        self.cluster_centers_ = None
        self.numclusters =  None
    
    def fit(self, data : pd.DataFrame) -> None:
        """Fits the clustering algorithm with the data.
        """
        data = data.to_numpy()
        n = len(data)
        numclusters=1
        means = np.array([np.mean(data,axis=0)])
        labels = np.zeros(n)
        
        prevcost=0
        currcost=1
        
        while abs(prevcost-currcost)>self.tol:
            prevcost = currcost
            
            for i in range(n):
                distances=np.zeros(numclusters)
                
                for j in range(numclusters):
                    distances[j] = np.sum(np.abs(data[i]-means[j])**2)
                    
                if np.amin(distances) > self.lambd:
                    labels[i] = numclusters
                    means = np.vstack((means,data[i]))
                    numclusters += 1
                else:
                    labels[i] = np.argmin(distances)
            
            for i in range(numclusters):
                means[i] = np.mean(data[labels==i],axis=0)
                
            currcost = 0
            for i in range(n):
                currcost += np.sum(np.abs(means[int(labels[i])]-data[i])**2)
                
        self.cluster_centers_ = means
        self.numclusters = numclusters
        
    def predict(self,data : pd.DataFrame) -> np.ndarray:
        """Clusters the data with the previously fitted parameters.
        Returns a one dimensional numpy array containing the cluster indices for 
        each record in data.
        """
        
        data = data.to_numpy()
        labels =[np.argmin(np.sum(np.abs(self.cluster_centers_ - data[i])**2,axis=1)) for i in range(len(data))]
        return np.array(labels)
    
    
if __name__ == '__main__':

    data = pd.DataFrame(np.random.rand(500,2)*100)

    cluster = DPMeans(2000)
    cluster.fit(data)
    labels = cluster.predict(data)
    print(f"Number of clusters: {cluster.numclusters} \n")
    for i in range(cluster.numclusters):
        print(f"Cluster {i}: {cluster.cluster_centers_[i]}\n")
    plt.scatter(data.to_numpy()[:,0], data.to_numpy()[:,1], c=cluster.predict(data))
    plt.show()
    
            
            
                    