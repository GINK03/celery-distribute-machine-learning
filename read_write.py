from tasks import *
import numpy as np
import sys

if '--leveldb_write' in sys.argv:
  for i in range(10000000):
    if i%1000 == 0:
      print('now iter {}'.format(i))
    key = np.random.bytes(1000)
    val = np.random.bytes(1000)
    flashLevel(key,val)

if '--rocksdb_write' in sys.argv:
  for i in range(10000):
    if i%1000 == 0:
      print('now iter {}'.format(i))
    key = np.random.bytes(1000)
    val = np.random.bytes(1000)
    res = flashRocks(key,val)
    print( res )

if '--rocksdb_get' in sys.argv:
  res = getKeysRocks()
  print( res )
