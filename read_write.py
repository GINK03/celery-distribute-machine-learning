import tasks
import numpy as np
import sys

if '--leveldb_write' in sys.argv:
  for i in range(10000000):
    if i%1000 == 0:
      print('now iter {}'.format(i))
    key = np.random.bytes(1000)
    val = np.random.bytes(1000)
    tasks.flashLevel.delay(key,val).get()

if '--rocksdb_write' in sys.argv:
  for i in range(1000):
    if i%100 == 0:
      print('now iter {}'.format(i))
    key = np.random.bytes(1000)
    val = np.random.bytes(1000)
    # delayは同期？
    #res = flashRocks.delay(key,val).get()
    res = tasks.flashRocks.delay(key,val)

    #print( res )

if '--rocksdb_get' in sys.argv:
  res = tasks.getKeysRocks.delay().get()
  print( res )
