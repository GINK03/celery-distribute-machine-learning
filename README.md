# Pine64を10台と、Celeryで分散基盤を使って効率的に機械学習する

## Celeryでできる分散機械学習
コンピュータ一台ではできる機械学習のリソースが限られています。データ収集基盤については、Map Reduce, Apache Beams(Google Cloud DataFlow), Sparkなどの選択肢がありますが、学習するというものについてはそんなに多くありません  
LightGBMはそのソフトウェアに分散して学習する機能がありますが、他のシステムではあまり見かけないように見受けられます  
CeleryというRemote Proceadure Callを利用することで、効率的にグリッドサーチができることや、アンサンブル学習ができることを示します   

### グリッドサーチ

### アンサンブル学習


## rabbitmq-server

rabbitmq-serverをインストールする  
(deamon等は起動の必要はない)  
#### Ubuntu Linux
```console
$ sudo apt-get install rabbitmq-server
```
#### Arch Linux
```console
$ sudo pacman -S rabbitmq
$ sudo rabbitmq-server &
```

## rabbitmqへremoteからアクセスできるユーザを追加
remoteという名のユーザを追加
```cosnole
$ sudo rabbitmqctl add_user remote remote
```
任意のIPからアクセスできるように、設定
```console
$ sudo rabbitmqctl set_permissions -p / remote ".*" ".*" ".*"
```

## redisのインストール
(このサイト)[https://redis.io/download]から、最新版のソースコードをダウンロードする  
#### Ubuntu Linux
```console
$ cd redis-stable
$ make -j4
$ sudo make install
```
#### Arch Linux
```cosnole
$ sudo pacman -S redis
```

## redisサーバの起動
```console
$ redis-server &
```
## LevelDBのインストール
```cosnole
$ sudo pacman -S leveldb
```

## Pythonモジュールのインストール
```cosnole
$ sudo pip3 install celery redis  pyrocksdb
```

## RockDBのインストール
```cosnole
$ git clone https://github.com/facebook/rocksdb.git
$ cd rocksdb
$ cd camke 
$ cmake ..
$ make -j32
$ sudo make install
$ sudo cp lib* /usr/lib64/
```
面倒なことに、make installではsoは入らないので、手動で入れる

## PythonRocksDBのインストール
```console
$ wget https://pypi.python.org/packages/a2/99/382b48731aa307e5550a6bee706c13e5df73638f4188ae4fc2a455e3d26b/python-rocksdb-0.6.7.tar.gz
$ tar zxvf python-rocksdb-0.6.7.tar.gz
$ cd python-rocksdb
$ python3 setup.py build
$ sudo python3 setup.py install
```

## Celery Server processの起動
```console
$ celery -A tasks worker --loglevel=info
```
#### 例えば1processで起動したい場合
```console
$ celery -A tasks worker --loglevel=info --concurrency=1
```
#### コンカレンシー（multiprocessで動作させたい場合）
```console
$ celery -A tasks worker --loglevel=info --concurrency=16
```
　


