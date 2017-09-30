from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn import grid_search
import pickle
import sys
import numpy as np
import json

Xys = pickle.loads(open('data.pkl', 'rb').read() )
y = [xy[0] for xy in Xys]
X = [xy[1] for xy in Xys]
X = np.array(X)
y = np.array(y)

if '--grid_search' in sys.argv:
  parameters = {
    'n_estimators'      : [5, 10, 20, 30, 50, 100, 300],
    'max_features'      : [3, 5, 10, 15, 20],
    'random_state'      : [0],
    'n_jobs'            : [1],
    'min_samples_split' : [3, 5, 10, 15, 20, 25, 30, 40, 50, 100],
    'max_depth'         : [3, 5, 10, 15, 20, 25, 30, 40, 50, 100]
  }
  clf = grid_search.GridSearchCV(RandomForestClassifier(), parameters)
  clf.fit(X, y)

  print( clf.best_estimator_)


#clf = RandomForestClassifier(max_depth=2, random_state=0)
#clf.fit(X, y)
#print( X, y )
#print(clf.feature_importances_)
#print( clf.score(X,y) )
#print(clf.predict([[0, 0, 0, 0]]))
