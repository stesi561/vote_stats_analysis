#! /usr/bin/env python

import numpy as np
import pandas as pd

import sys

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.cluster import KMeans

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D



filename = sys.argv[1]
df_survey = pd.read_csv(filename)

X, y  = df_survey.iloc[:,4:].values, df_survey.iloc[:, 0:4].values

pipeline = Pipeline([('scaling',StandardScaler()), ('pca', PCA(n_components=3))])

X2 = pipeline.fit_transform(X)



clusters = 3

estimators = {"Clusters: %d" % x: KMeans(n_clusters=x) for x in range(2,10)}

fignum = 1
for name, est in estimators.items():
    fig = plt.figure(fignum, figsize = (4,3))
    plt.clf()
    ax = Axes3D(fig)
    est.fit(X2)
    labels = est.labels_
    ax.scatter(X[:,0], X[:,1], X[:, 4], c=labels.astype(np.float))
    ax.set_xlabel("Green")
    ax.set_ylabel("Labour")
    ax.set_zlabel("NZ First")
    ax.set_title(name)
    fignum+= 1
    

plt.show()
