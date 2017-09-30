import tasks
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
    tasks.write_client_memory_talbe(hostname)
    a, b = random.randint(0, 100), random.randint(0, 100)
    c = tasks.add.delay(a, b).get()

    print('{} {} + {} = {}'.format(hostname, a, b, c))
if '--rocksdb_get' in sys.argv:
  res = tasks.getKeysRocks.delay().get()
  print( res )
