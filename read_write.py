import numpy as np
import sys
import random

if '--leveldb_write' in sys.argv:
  for i in range(10000000):
    if i%1000 == 0:
      print('now iter {}'.format(i))
    key = np.random.bytes(1000)
    val = np.random.bytes(1000)
    tasks.flashLevel.delay(key,val).get()

if '--rocksdb_write' in sys.argv:
  for hostname in ['192.168.15.3', '192.168.15.37']:
    tasks.write_client_memory_talbe(hostname)
    for i in range(1000):
      if i%100 == 0:
        print('now iter {}'.format(i))
      key = np.random.bytes(1000)
      val = np.random.bytes(1000)
      # delayは同期？
      #res = flashRocks.delay(key,val).get()
      res = tasks.flashRocks.delay(key,val)


if '--add' in sys.argv:
  for hostname in ['192.168.15.80', '192.168.15.81', '192.168.15.43', '192.168.15.44', '192.168.15.45', '192.168.15.46', '192.168.15.48']:
    import tasks
    import copy
    tasks.write_client_memory_talbe(hostname)
    a, b = random.randint(0, 100), random.randint(0, 100)
    c = tasks.add.delay(a, b).get()
    print('{} {} + {} = {}'.format(hostname,a, b, c))

if '--random_forest' in sys.argv:
  # 192.168.15.44 -> ArchLinuxで特定ライブラリが入らない
  import pickle
  hostname_params = {'192.168.15.80':[3, 5], '192.168.15.81':[10, 15], '192.168.15.43':[20, 25], '192.168.15.45':[30, 35], '192.168.15.46':[40, 45], '192.168.15.48':[50,55]}

  Xys = pickle.loads(open('adult_dataset/data.pkl', 'rb').read() )                                                
  y = [xy[0] for xy in Xys]                        
  X = [xy[1] for xy in Xys]                        
  X = np.array(X)                                  
  y = np.array(y) 

  task_que = []
  for hostname, params in hostname_params.items():
    parameters = {
      #'n_estimators'      : [5, 10, 20, 30, 50, 100, 300],
      'max_features'      : params,
      'min_samples_split' : [3, 5, 10, 15, 20, 25, 30, 40, 50, 100],
      'min_samples_leaf'  : [1, 2, 3, 5, 10, 15, 20],
      'max_depth' : [10, 20, 25, 30]
    }
    from sklearn.ensemble import RandomForestClassifier                                               
    from sklearn.datasets import make_classification 
    from sklearn import grid_search 
    clf = grid_search.GridSearchCV(RandomForestClassifier(), parameters, n_jobs=4)
    import tasks
    tasks.write_client_memory_talbe(hostname)
    task = tasks.gridSearch.delay(X, y, clf)
    task_que.append( (hostname, clf, task) )
  for hostname, clf, task in task_que:
    estimator, best_param, best_score = task.get()
    print('{} best_score={}, best_param={} '.format(hostname, best_score, best_param))

if '--rocksdb_get' in sys.argv:
  res = tasks.getKeysRocks.delay().get()
  print( res )
