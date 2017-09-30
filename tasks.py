from celery import Celery
import redis
import plyvel
import rocksdb
import os
from datetime import datetime
import msgpack
app = Celery('tasks', backend='amqp', broker='amqp://guest@localhost//')

pid = os.getpid()
ldb = plyvel.DB('{pid}.map.ldb'.format(pid=pid), create_if_missing=True)
rdb = rocksdb.DB("{pid}.map.rdb".format(pid=pid), rocksdb.Options(create_if_missing=True))

que = []
@app.task
def enque(x):
  que.append(x)

@app.task
def deque():
  x = que.pop(0)
  # call http request
  print( x )

@app.task
def add(x, y):
    return x + y

r = redis.StrictRedis(host='localhost', port=6379, db=0)
@app.task
def flashMemory(k, v):
  r.set(k, v)

@app.task
def flashLevel(k, v):
  ldb.put( bytes(k), bytes(v) )

@app.task
def flashRocks(k, v):
  timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  vb = msgpack.packb( {timestamp : v} )
  rdb.put( bytes(k), vb )
  return True

@app.task
def getKeysRocks():
  it = rdb.iterkeys()
  it.seek_to_first()
  return list(it)



