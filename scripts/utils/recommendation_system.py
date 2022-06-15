from typing import List
from pandas import DataFrame
from sklearn.cluster import KMeans, BisectingKMeans, SpectralClustering
from sklearn.mixture import GaussianMixture
from scripts.clusters.helpers import plot_elbow_test, get_clusters, combine_data,\
get_clusters_count, get_sum_of_square_errors, cluster_predict, vectorize_data, show_clusters
from scripts.clusters.kwargs import kmeans_kwargs, bisecting_kmeans_kwargs, \
    spectral_kwargs, gaussian_mixture_kwargs

class RecommendationSystem:

    def __init__(
        self, 
        dataset: DataFrame) -> None:
        self.__dataset = dataset


    def build_system(self, x_cols: list):
        features = self.__dataset[x_cols]
        cluster_algo = KMeans
        kwargs = kmeans_kwargs

        max_kernels = 30
        sse = get_sum_of_square_errors(features, cluster_algo, max_kernels, **kwargs)
        
        n_clusters= get_clusters_count(sse)
        self.__model = get_clusters(features, cluster_algo, n_clusters=n_clusters, **kwargs)

        clusters = cluster_predict(features, self.__model)
        self.__dataset['Cluster_Prediction']=list(clusters)  
        # self.show_clusters_info(sse, features)     


    def recommend(self, elements: DataFrame, x_cols: list, count: int = 10) -> DataFrame:
        prediction = self.__dataset.loc[self.__dataset['Rank'] == int(elements['Rank'])]['Cluster_Prediction']

        recommendations = self.__dataset.loc[
            self.__dataset['Rank'] != int(elements['Rank'])]
        recommendations = recommendations.loc[
            self.__dataset['Cluster_Prediction'] == int(prediction)]
        recommendations = recommendations.sample(count)

        return DataFrame(recommendations)


    def show_clusters_info(self, sse: list, features):
        plot_elbow_test(sse)
        show_clusters(features, cols = ['Platform', 'Genre', 'Publisher'], 
                    y_kmeans = list(self.__dataset['Cluster_Prediction']))
