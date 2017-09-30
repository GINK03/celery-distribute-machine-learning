# Pine64を10台と、Celeryで分散基盤を使って効率的に機械学習する

## Pine64とRock64
Rasphberry Piを個人で５台ほど所有しているのですが、如何せん、機械学習や計算リソースが必要なプログラミングには向いていないしパワーが足りません  
Armと呼ばれるスマートフォンに入っているようなアーキテクチャのCPUが今後来るのではないか、という期待の元、10台ほどネット通販にて、購入にしてクラスタを組んでみました  

[PINE64-LTS(2GB)](https://www.pine64.org/?product=pine-a64-lts)という撰品で64bitのArmアーキテクチャの製品で、一個$35程度です  
最近、さらに高速で大メモリのものが出ました  
[ROCK64(4GB)](https://www.pine64.org/?product=rock64-media-board-computer)で、これは$45程度です。ギリギリこれぐらいで遅い計算機として使えるという印象があり、やはりパワーは大事です  

<div align="center"> 図1. 組んだクラスタの写真 </div>

## Celeryでできる分散機械学習
コンピュータ一台ではできる機械学習のリソースが限られています。データ収集基盤については、Map Reduce, Apache Beams(Google Cloud DataFlow), Sparkなどの選択肢がありますが、学習するというものについてはそんなに多くありません  
LightGBMはそのソフトウェアに分散して学習する機能がありますが、他のシステムではあまり見かけないように見受けられます  
Celeryという分散タスクキューを利用することで、効率的にグリッドサーチができることや、アンサンブル学習ができることを示します   

分散タスクキューの定義をよくわかっていないのですが、Remote Procedure Callをラップアップしてリモートのサーバの関数を透過的に利用できるのが、このライブラリの最大のメリットのように思います  

データの通信に様々なシリアライズ方式を使うことができて、pickleなど、複雑でPythonのほとんどのデータ構造をサポートするのもの転送可能なので、モデルや、学習すべきnumpyのアレーなども転送可能なことから、今回、これを使いました  

### グリッドサーチ
機械学習には一般的に膨大なハイパーパラメータと呼ばれる多数のチューニングポイントが存在します。これらを賢く最適化するには、グリッドサーチや、それを改良したベイズ最適化や様々なアプローチが使えます  
パラメータを変化させて学習、評価をしていき、最もパフォーマンスが優れいている点をあぶり出すのですが、やっていることは単純ですが、計算量がひたすらにかかります  
分散コンピューティングをすることで、一台のマシンあたりの探索範囲を限定することで、効率よく、短時間て優れたパラメータを特定可能になります。  
<div align="center"> 図2. グリッドサーチの探索範囲 </div>

### アンサンブル学習
アンサンブル学習にもいくつか手法があります  
複数の機械学習モデルの平均値をとる方法や、モデルに対して重要度を再度重み付けや、決定木をとることでアンサンブルにする方法があります  

RandomForestの出力結果の平均をとり、巨大なモデルであってもコンピュータ一台がそのリソースの範囲で扱えるモデルを超える巨大なモデルとして振る舞うことを示します  
<div align="center"> 図3. アンサンブル </div>


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
　


