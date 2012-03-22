## EC2用のデプロイ補助スクリプトです。

このスクリプトでdeployを実行すると  
1.指定したNameを持つインスタンスを探して、起動しているかチェック。Stopしていればたたき起こす。  
2.デプロイが終了したらスナップショットを取るか尋ね、OKでスナップショットを作成。  
ということを行います。

Capistranoのrollbackもできます。  
1.指定Nameのインスタンスの起動チェック、ロールバック実行。  
2.以前作成したスナップショットも一緒に削除(削除実行前に確認アリ)。

※スナップショット作成/削除機能は[botoを使ってEBSをバックアップ(世代管理つき)](http://heartbeats.jp/hbblog/2011/04/botoebs.html)のスクリプトを使わせてもらいました。

### 環境

- Capistrano, Capistrano-extを使ったデプロイができるようになっていること(capコマンドをそのまま利用します)
- Python2.6 以上
- botoパッケージがインストールされていること (easy_install boto OR pip install boto)

### 使う前の準備

1. Githubから一式をダウンロード
2. ec2helperの中に入っているconfig.pyを開きます。  
辞書AWS_DATAの'default'欄にAWSアカウントのアクセスキー、シークレットキーを記入します。  
regionは、AWS_DATAの上にある辞書REGIONのキーを入力して下さい。(東京なら"t")  
複数アカウントがある場合は、AWS_DATAに追加して下さい。
3. deploy_example.pyを開きます。  
「Edit ===」で囲まれている部分を編集して下さい。

```python
# 接続先のAWSアカウント (AWS_DATAに記述したアカウントのキー)
conf.aws_account = 'default'
# pには本番環境のインスタンス名、dには開発環境のインスタンス名を記述します
conf.instances = {
    'p' : ['production_server1', 'production_server2'],
    'd' : ['dev_server'],
}

# capコマンドを実行するディレクトリのパス
conf.cap_path = '/path/to/cap/directory'

# capistrano-extで使用する環境別引数を記述します。p:本番向け d:開発環境向け
# 例：capコマンドを「cap production deploy」と打つのであれば、第一引数の"production"を記述
conf.cap_deploy_to = {
    'p' : 'production',
    'd' : 'dev',
}

# デプロイ後にスナップショットを取る場合はコメントアウトを外します
#conf.create_snapshot = True

# スナップショット名。スナップショットを取る場合、コメントアウトを外して名前を記述します。
#conf.snap_description = 'snapshot test'

# 開発環境へデプロイする時もスナップショットを取る場合は、このコメントアウトを外します。
#conf.create_snap_only_production = False
```


4. deploy.rbを編集します。デプロイ先サーバーを動的に変更できるようにします。role定義部分を下記のように書き換えて下さい。(role名は好きにつけてＯＫです)

```ruby
role :app do
    "#{host}".split(',')
end
```


### 使い方

$ python deploy_example.py [本番/開発環境指定] [deployの挙動指定]

環境指定：  
・p 本番環境  
・d 開発環境

deployの挙動指定: (Capコマンドそのまんまです）  
・deploy  
・deploy:rollback  
・deploy:cleanup

開発環境へデプロイ  
$ python deploy_example.py d deploy

本番環境へデプロイ  
$ python deploy_example.py p deploy

開発環境 ロールバック  
$ python deploy_example.py d deploy:rollback

開発環境 世代数整理  
$ python deploy_example.py d deploy:cleanup

ちなみにスナップショットを取るだけであれば、  
ec2helper/snapshot.py実行でOKです。
$ python snapshot.py [snapshot名] -v volume名(vol-xxxxx)

-dオプションをつけると、指定したsnapshot名をもつ、最後に作成したスナップショットを削除(削除前に確認アリ)  
$ python snapshot.py [snapshot名] -d

-rオプションをつけるとリージョンを変更して実行
$ python snapshot.py [snapshot名] -v volume名(vol-xxxxx) -r s  
<small>※シンガポールリージョンにあるvolumeのスナップショットを作成</small>
