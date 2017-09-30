from celery import Celery
import os
from datetime import datetime
import msgpack
try:
  import plyvel
  import rocksdb
except:
  ...
try:
  import redis
except:
  ...
def mapper(hostname):
  app = Celery('tasks', task_serializer = 'msgpack', result_serializer = 'msgpack', backend='amqp', broker='amqp://remote:remote@{hostname}/'.format(hostname=hostname) )
  app.conf.update( task_serializer = 'pickle', result_serializer = 'pickle', event_serializer = 'pickle', accept_content = ['pickle', 'json'] )

  @app.task
  def add(x, y):
    print('Add', x+y)
    return x + y

  @app.task
  def flashMemory(k, v):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
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

  return app, [add, flashMemory, flashLevel, flashRocks, getKeysRocks] 


import socket
hostname = socket.gethostbyname(socket.gethostname())
app, (add, flashMemory, flashLevel, flashRocks, getKeysRocks) = mapper(hostname)
add = add
flashMemory = flashMemory
flashRocks = flashRocks
getKeysRocks = getKeysRocks
def write_client_memory_talbe(hostname):
  global add
  global flashMemory
  global flashLevel
  global flashRocks
  global getKeysRocks
  app, (add, flashMemory, flashLevel, flashRocks, getKeysRocks) = mapper(hostname)
  add = add
  flashMemory = flashMemory
  flashRocks = flashRocks
  getKeysRocks = getKeysRocks

if __name__ == 'tasks':
  if hostname in ['192.168.15.37', '192.168.15.24']:
    pid = os.getpid()
    try:
      ldb = plyvel.DB('{pid}.map.ldb'.format(pid=pid), create_if_missing=True)
      rdb = rocksdb.DB("{pid}.map.rdb".format(pid=pid), rocksdb.Options(create_if_missing=True))
    except:
      ...
  
if __name__ == '__main__':
  app.start()

