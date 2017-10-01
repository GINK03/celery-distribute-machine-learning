# Pine64を10台でクラスタ組んで、Celeryで分散基盤を使って効率的に機械学習する

## Pine64とRock64
Rasphberry Piを個人で５台ほど所有しているのですが、如何せん、機械学習や計算リソースが必要なプログラミングには向いていないしパワーが足りません。何よりメモリが圧倒的に足りないです  
Armと呼ばれるスマートフォンに入っているようなアーキテクチャのCPUが今後来るのではないか、という期待の元[1]、10台ほどネット通販にて、購入にしてクラスタを組んでみました  

[PINE64-LTS(2GB)](https://www.pine64.org/?product=pine-a64-lts)という撰品で64bitのArmアーキテクチャの製品で、一個$35程度です  
最近、さらに高速で大メモリのものが出ました  
[ROCK64(4GB)](https://www.pine64.org/?product=rock64-media-board-computer)で、これは$45程度です。ギリギリこれぐらいで遅い計算機として使えるという印象があり、やはりパワーは大事です  
<p align="center">
  <img width="400px" src="https://user-images.githubusercontent.com/4949982/31052231-f486c5da-a6b8-11e7-8a4a-c3ebba14843b.png">
</p>
<div align="center"> 図1. 組んだクラスタの写真 </div>

## Celeryでできる分散機械学習
コンピュータ一台ではできる機械学習のリソースが限られています。データ収集基盤については、Map Reduce, Apache Beams(Google Cloud DataFlow), Sparkなどの選択肢がありますが、学習するというものについてはそんなに多くありません  
LightGBMはそのソフトウェアに分散して学習する機能がありますが、他のシステムではあまり見かけないように見受けられます  
Celeryという分散タスクキューを利用することで、効率的にグリッドサーチができることや、（今回は試していませんが）アンサンブル学習ができることを示します   

分散タスクキューの定義をよくわかっていないのですが、Remote Procedure Callをラップアップしてリモートのサーバの関数を透過的に利用できるのが、このライブラリの最大のメリットのように思います  

データの通信に様々なシリアライズ方式を使うことができて、pickleなど、複雑でPythonのほとんどのデータ構造をサポートするのもの転送可能なので、モデルや、学習すべきnumpyのアレーなども転送可能なことから、今回、これを使いました  

### グリッドサーチ
機械学習には一般的に膨大なハイパーパラメータと呼ばれる多数のチューニングポイントが存在します。これらを賢く最適化するには、グリッドサーチや、それを改良したベイズ最適化や様々なアプローチが使えます  
パラメータを変化させて学習、評価をしていき、最もパフォーマンスが優れいている点をあぶり出すのですが、やっていることは単純ですが、計算量がひたすらにかかります  
分散コンピューティングをすることで、一台のマシンあたりの探索範囲を限定することで、効率よく、短時間て優れたパラメータを特定可能になります。  
<p align="center">
  <img width="500px" src="https://user-images.githubusercontent.com/4949982/31052751-8fdb4240-a6c8-11e7-906f-bcab83ff0e8d.png">
</p>
<div align="center"> 図2. グリッドサーチの探索範囲 </div>

### アンサンブル学習
アンサンブル学習にもいくつか手法があります  
複数の機械学習モデルの平均値をとる方法や、モデルに対して重要度を再度重み付けや、決定木をとることでアンサンブルにする方法があります  

RandomForestの出力結果の平均をとり、巨大なモデルであってもコンピュータ一台がそのリソースの範囲で扱えるモデルを超える巨大なモデルとして振る舞うことも可能です  

## Celeryの設定とコーディング
ごちゃごちゃとCeleryを触っていたのですけど、Pythonのコードの限界というか、デコレータと呼ばれるceleryの関数の引数になっているユーザ定義関数の制御が厄介で、モンキーパッチなどの、あまり好ましくない方法で制御する必要がありました  
clientとserverに機能を分けて、グリッドサーチではこのように定義しました  

### Celeryを動かすのに必要なソフトウェアとライブラリ
- celery
- rabbitmq
- scipy
- scikit-learn

rabbitmqにはメッセージをやり取りするのに、ユーザ名[remote]、パスワード[remote]を設定する必要があります  

### グリッドサーチ
#### Client
- データセットを整形してServerに送信
- 様々なパラメータを代入したモデルを構築し、学習と評価はせずにこの状態をpickleでシリアライズしてserverに送信
- Serverで評価した探索範囲内でのベストパフォーマンスを回収
- 各Serverの情報を統合して、最も良いパフォーマンスの結果を出力

```python
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
    tasks.write_client_memory_talbe(hostname) # ここでモンキーパッチを行なっている
    task = tasks.gridSearch.delay(X, y, clf)
    print( 'send task to', hostname )
    task_que.append( (hostname, clf, task) )
  for hostname, clf, task in task_que:
    estimator, best_param, best_score = task.get()
    print('{} best_score={}, best_param={} '.format(hostname, best_score, best_param))
    print( estimator )
```
#### Server
- clientからデータを受け取る  
- 受け取ったデータの中のpickleからモデルを復元して学習  
- 探索範囲のパラメータの中から発見した最良の結果を返却する  
```python3
  @app.task
  def gridSearch(X, y, clf): # dataとモデルを受け取って
    print('start to fit!')
    clf.fit(X, y) # 学習
    estimator = clf.best_estimator_ 
    best_param = clf.best_params_
    best_score = clf.best_score_ 
    return (etimator, best_param, best_score) # 最良のものを返却
```
モンキーパッチなどの実装は、コードに詳細が記述されています

## コード
[https://github.com/GINK03/celery-distribute-machine-learning:embed:cite]

## サンプルの実行
githubにあるものは、adultと呼ばれるデータセットでアメリカの人の学歴や人種やその他のパラメータで収入が$50kを上回るかどうかの判別問題をバンドルしています  
IPアドレスがハードコードされていますが、ご利用の環境に合わせて、編集してください  

Serverサイドでは、celeryをこのように起動します  
自分のIPアドレスを自動で検出しますが、まれに検出に失敗するときには、ホストネームを自分のサーバのホスト名に設定します  
```console
$ celery -A tasks worker --loglevel=info
```

サーバサイドのプロセスが全て起動したことを確認したら、Clientからグリッドサーチの命令を送ります  
 ```console
 $ python3 grid_search.py --random_forest
 {'max_depth': 30, 'min_samples_split': 30, 'min_samples_leaf': 1, 'max_features': 5} 0.8591873713952274 # <-最適値なパラメータ                                                                                               
RandomForestClassifier(bootstrap=True, class_weight=None, criterion='gini', # <- 最適なパラメータを適応したモデル
            max_depth=30, max_features=5, max_leaf_nodes=None,                                     
            min_impurity_decrease=0.0, min_impurity_split=None,                                    
            min_samples_leaf=1, min_samples_split=30,                                              
            min_weight_fraction_leaf=0.0, n_estimators=10, n_jobs=1,                               
            oob_score=False, random_state=None, verbose=0,                                         
            warm_start=False) 
 ```
 
 ## グリッドサーチを1台で行うのと、10分割して行うもののベンチーマクの差
 分散処理するサーバを一台に限定して行うと、この程度の時間がかかります　　
 ```cosnole
 elapsed 32714.200119832235 <- 32715秒、つまり、9.1時間
 ```
 これを5台に分散して処理すると、この程度になります。
 ```
using hostname is 192.168.15.37
send task to 192.168.15.80
send task to 192.168.15.81
send task to 192.168.15.45
send task to 192.168.15.46
send task to 192.168.15.48
{'min_samples_split': 50, 'min_samples_leaf': 2, 'max_depth': 30, 'max_features': 35} 0.8634869936427014
RandomForestClassifier(bootstrap=True, class_weight=None, criterion='gini',
            max_depth=30, max_features=35, max_leaf_nodes=None,
            min_impurity_decrease=0.0, min_impurity_split=None,
            min_samples_leaf=2, min_samples_split=50,
            min_weight_fraction_leaf=0.0, n_estimators=10, n_jobs=1,
            oob_score=False, random_state=None, verbose=0,
            warm_start=False)
elapsed 5459.255481719971 # <- 5460秒、つまり、1.5時間
 ```
 複数回サンプルして平均を取ると正確な値になるかと思いますが、一回の施行での例です  
 
## Adultデータセットのベンチマーク
データセット提供元の、UCIの詳細情報によると、エラー率に関して、様々なアルゴリズムのベンチマークが記されており、今回のエラー率は十分に低く、ほぼ理想的なパフォーマンスを発揮できたことがわかるかと思います  

今回GridSearchしたベンチマーク
```Console
ACCUR 86.34869936427014
ERROR 13.6513006357299
```

UCIによるベンチマーク
```console
|    Algorithm               Error
| -- ----------------        -----
| 1  C4.5                    15.54
| 2  C4.5-auto               14.46
| 3  C4.5 rules              14.94
| 4  Voted ID3 (0.6)         15.64
| 5  Voted ID3 (0.8)         16.47
| 6  T2                      16.84
| 7  1R                      19.54
| 8  NBTree                  14.10
| 9  CN2                     16.00
| 10 HOODG                   14.82
| 11 FSS Naive Bayes         14.05
| 12 IDTM (Decision table)   14.46
| 13 Naive-Bayes             16.12
| 14 Nearest-neighbor (1)    21.42
| 15 Nearest-neighbor (3)    20.35
| 16 OC1                     15.04
 ```
 
ベンチマーク時点が古いのもありますが、かなり余裕ですね。Armの安いマシンでの機械学習でもベンチマークを超えることはできました。

## Appendix. Install Celery and Denpendencies
これが結構ややこしく、rabbitmqなどのセットアップとか結構調べました  
ボリュームが多くなってしまったので、別途記載しました  
[https://github.com/GINK03/celery-distribute-machine-learning/blob/master/INSTALL_SETUP_CELERY.md:embed:cite]

## まとめ
Celeryなどの分散タスクキューを使うと、機械学習の例えばグリッドサーチなどの利用において、高速化することができることがわかりました  

この発想の延長線上に、Googleが作成したSibyl(シビュラ)という名のCTR, CVR予想システムがあるのですが、わかる感じの情報を拾っていくと、どうやら特徴量が2000万とかそういうレベルの予想機で、単独のマシンによる結果ではなくて、各マシンが返す結果を、Adaboostのようなアルゴリズムで、集約しているようなので、このような膨大な特徴量が必要な予想でも、マシンの台数さえ確保すれば行えそうであると言えそうです[2]  

あと、ARMのサーバを実際にいじってみて思ったんですが、とにかく重いですし、莫大な計算量が必要な機械学習にはあまり向いないかもしれないと思ったりしまた。しばらくは、x86_64アーキテクチャサーバでなんとかなるかもしれないのと、Ryzenのような多コアのCPUはうまく使えばものすごく強いので、無理にARMを採用する必要はないように思います  

Celeryはモンチーパッチして今回つかったため、個人でやるにはやはりこういうアドホックが許されるPythonは便利だなと思ったのと、コードが汚くなることを許容するため、何か製品として出す場合には使えない方法だなとも思ったりしました。Pythonに変わる言語、何かないかな

## 参考文献
- [1][Imagine that you could take advantage of 96 cores for just $.50/hr? ](https://www.packet.net/bare-metal/servers/type-2a/)
- [2][Sibyl: A system for large scale supervised machine learning](http://people.csail.mit.edu/romer/papers/TISTRespPredAds.pdf)
