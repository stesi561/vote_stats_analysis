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

pipeline = Pipeline([('scaling',StandardScaler()), ('pca', PCA(n_components=2))])

X2 = pipeline.fit_transform(X)
#clusters = 3

#kmeans = KMeans(n_clusters=clusters)
#kmeans.fit(X2)
#labels = kmeans.labels_

plt.subplot(111)
plt.scatter(X2[:,0], X2[:,1])#, c=labels.astype(np.float))
plt.show()
