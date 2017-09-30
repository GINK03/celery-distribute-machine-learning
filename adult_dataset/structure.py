

structure = { 'age': 'continuous',
  'workclass': 'categorical', 
  'fnlwgt': 'continuous',
  'education': 'categorical',
  'education-num': 'continuous',
  'marital-status': 'categorical',
  'occupation': 'categorical',
  'relationship': 'categorical',
  'race': 'categorical',
  'sex': 'categorical',
  'capital-gain': 'continuous',
  'capital-loss': 'continuous',
  'hours-per-week': 'continuous',
  'native-country': 'categorical' }

header = ['age', 'workclass', 'fnlwgt', 'education', 'education-num', 'marital-status', 'occupation', 'relationship', 'race', 'sex', 'capital-gain', 'capital-loss', 'hours-per-week', 'native-country', 'ANS']

remaps = []
with open('adult.data') as f:
  for line in f:
    vals = line.strip().split(', ')
    if len(vals) != len(header):
      continue
    obj = dict(zip(header, vals))
    
    ans = 1.0 if obj['ANS'] == '>50K' else 0.0
    del obj['ANS']

    remap = {}
    for key, val in obj.items():
      if structure[key] == 'continuous':
        remap[key] = float( val )
        continue

      if structure[key] == 'categorical':
        next_key = key + '_' + val
        remap[next_key] = 1.0
    remap['ans'] = ans
    print( remap )

    remaps.append( remap )

feat_index = {}
for remap in remaps:
  for key in remap.keys():
    if key == 'ans':
      continue
    if feat_index.get(key) is None:
      feat_index[key] = len(feat_index)
import pickle
print( feat_index )
open('feat_index.pkl', 'wb').write( pickle.dumps(feat_index) )
# make vector 
data = []
for remap in remaps:
  ans = remap['ans']
  del remap['ans']
  base = [0.0]*(len(feat_index))
  for key, val in remap.items():
    index = feat_index[key]
    base[index] = val
  data.append( [ans, base] )

open('data.pkl','wb').write( pickle.dumps(data) )

