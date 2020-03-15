from shared_modules import SqlConnection
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from sklearn import cluster, metrics
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

np.set_printoptions(precision=4)
sns.set()
pd.set_option('max_rows', 200)
pd.set_option('max_columns', 100)
pd.set_option('display.width', 200)

def kmeans(reduced_data, n_clusters):
    """
    performs kmeans clustering and returns labels, centroids, inertia, and silhouette score
    """
    kmeans = cluster.KMeans(n_clusters=n_clusters, random_state=42)
    kmeans = kmeans.fit(reduced_data)
    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_
    inertia = kmeans.inertia_
    sil_score = metrics.silhouette_score(reduced_data, kmeans.labels_, metric='euclidean')

    data_dictionary = {
        "labels": labels,
        "centroids": centroids,
        "inertia": inertia,
        "silhouette_score": sil_score
    }

    return data_dictionary


def find_best_cluster(data, a, b):
    """
    plots and finds the best silhouette score for range(a,b)
    """
    scores = []
    for i in range(a, b):
        print('Processing cluster size:', i)
        i_clusters = kmeans(data, i)
        sil_score_i = i_clusters['silhouette_score']
        scores.append(sil_score_i)

    sns.set_context('poster', font_scale=1)
    plt.plot(range(a, b), scores)
    plt.title("""Measuring Silhouette Score to Find Best Cluster""")
    print("best silhouette score:", np.max(scores))


def feature_importance(cluster_data, league_data):
    """
    takes reduced data and performs Principal Component Analysis
    returns feature importance dataframe
    """
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(cluster_data)

    pca = PCA(n_components=2)
    PCA_reduced_df = pca.fit(scaled_data).transform(scaled_data)

    features = pd.DataFrame(zip(cluster_data.columns, pca.components_[0], np.mean(cluster_data), np.mean(league_data)),
                            columns=['Feature', 'Importance', 'Cluster Average', 'League Average']).sort_values('Importance', ascending=False)

    print(features)

    return features


def plot_kmeans_cluster(reduced_data, k_clusters, plot_title):
    kmeans = KMeans(init='k-means++', n_clusters=k_clusters, n_init=10)
    kmeans.fit(reduced_data)

    # Step size of the mesh. Decrease to increase the quality of the VQ.
    h = .02     # point in the mesh [x_min, x_max]x[y_min, y_max].

    # Plot the decision boundary. For that, we will assign a color to each
    x_min, x_max = reduced_data[:, 0].min() - 1, reduced_data[:, 0].max() + 1
    y_min, y_max = reduced_data[:, 1].min() - 1, reduced_data[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))

    # Obtain labels for each point in mesh. Use last trained model.
    Z = kmeans.predict(np.c_[xx.ravel(), yy.ravel()])

    # Put the result into a color plot
    Z = Z.reshape(xx.shape)
    plt.figure(1, figsize=(15, 10))
    plt.clf()
    plt.imshow(Z, interpolation='nearest',
               extent=(xx.min(), xx.max(), yy.min(), yy.max()),
               cmap=plt.cm.Paired,
               aspect='auto', origin='lower')

    plt.plot(reduced_data[:, 0], reduced_data[:, 1], 'k.', markersize=10)
    # Plot the centroids as a white X
    centroids = kmeans.cluster_centers_
    plt.scatter(centroids[:, 0], centroids[:, 1],
                marker='x', s=169, linewidths=3,
                color='w', zorder=10)
    plt.title(plot_title)
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.xticks(())
    plt.yticks(())
    plt.show()


query = '''
SELECT 
    g.[season]
    ,gs.[pid]
    ,r.[player]
    ,r.[position] AS [position specific]
    ,CASE WHEN r.[position] LIKE '%-%' THEN SUBSTRING(r.[position], 1, 1) ELSE r.[position] END AS [position group]
    ,SUM([ast])
    ,SUM([blk])
    ,SUM([blka])
    ,SUM([dreb])
    ,SUM([fbpts])
    ,SUM([fbptsa])
    ,SUM([fbptsm])
    ,SUM([fga])
    ,SUM([fgm])
    ,SUM([fta])
    ,SUM([ftm])
    ,SUM([oreb])
    ,SUM([pf])
    ,SUM([pip])
    ,SUM([pipa])
    ,SUM([pipm])
    ,SUM([pm])
    ,SUM(CASE WHEN [pos] = '' THEN 0 ELSE 1 END) AS [starts]
    ,SUM([pts])
    ,SUM([reb])
    ,SUM([stl])
    ,SUM([tf])
    ,SUM([totsec]) / 60.0
    ,SUM([tov])
    ,SUM([tpa])
    ,SUM([tpm])
FROM [nba].[dbo].[game_stats] gs
JOIN [nba].[dbo].[rosters] r ON r.player_id = gs.pid
JOIN [nba].[dbo].[games] g ON g.game_id = gs.gid
JOIN (
    SELECT 
    [season]
    ,[pid]
    ,COUNT([gid]) AS [appearances]
    FROM [nba].[dbo].[game_stats] gs
    JOIN games g ON g.game_id = gs.gid
    GROUP BY [season], [pid]
    HAVING COUNT([gid]) > 10
) a
    ON a.[season] = g.[season] AND a.pid = gs.pid

GROUP BY     
    g.[season]
    ,gs.[pid]
    ,r.[player]
    ,r.[position]
'''

columns = ['season', 'pid', 'player', 'position specific', 'position group', 'ast', 'blk', 'blka', 'dreb',
           'fbpts', 'fbptsa', 'fbptsm', 'fga', 'fgm', 'fta', 'ftm', 'oreb', 'pf', 'pip', 'pipa', 'pipm',
           'pm', 'starts', 'pts', 'reb', 'stl', 'tf', 'game_mins', 'tov', 'tpa', 'tpm']


def main():
    sql = SqlConnection('nba')
    data = sql.load_data(query, columns)
    print('Data loaded from SQL..')

    dims = ['season', 'pid', 'player', 'position specific', 'position group']
    X = data.drop(dims, axis=1)
    y = data['position specific']

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    pca = PCA(n_components=2)
    pca.fit(X_scaled)
    X_pca = pca.transform(X_scaled)
    print("Cumulative Explained Variance:", pca.explained_variance_ratio_.sum())

    LDA = LinearDiscriminantAnalysis(n_components=2, shrinkage='auto', solver='eigen')
    LDA_reduced_df = LDA.fit(X_scaled, y).transform(X_scaled)
    print('LDA score:', LDA.score(X_scaled, y))

    find_best_cluster(LDA_reduced_df, 5, 21)

    k_means = kmeans(LDA_reduced_df, 10)
    data['cluster'] = k_means['labels']
    print("Silhouette score:", k_means['silhouette_score'])

    y = k_means['labels']
    df = pd.DataFrame({'X1':LDA_reduced_df[:,0],'X2':LDA_reduced_df[:,1], 'labels':y})
    plot_kmeans_cluster(LDA_reduced_df, k_clusters=8, plot_title="""KMeans Clustering on NBA Players in 2016-2019""")

    mask = (data['cluster'] == 7)
    print(data[mask][['player', 'season']])
    cluster_data = data[mask].drop(dims, axis=1)
    league_data = data.drop(dims, axis=1)
    feature_importance(cluster_data, league_data).reset_index().drop('index', axis=1)

    player_list = list(data['player'])
    playerid_list = list(data['pid'])
    season_list = list(data['season'])

    df['Player'] = player_list
    df['Season'] = season_list
    df['Player_ID'] = playerid_list
    df['tags'] = df['labels'].map({0: 'Defensive Centers',
                                    1: '3-and-D Wings',
                                    2: 'Scoring Wings',
                                    3: 'Versatile Forwards',
                                    4: 'Floor Generals',
                                    5: 'Shooting Wings',
                                    6: 'Combo Guards',
                                    7: 'Offensive Centers'})

    sql.load_data('''IF OBJECT_ID('position_clusters') IS NOT NULL 
                    TRUNCATE TABLE [position_clusters]''')

    sql.insert_data('position_clusters', df.to_dict('records'))


if __name__ == "__main__":
    main()
