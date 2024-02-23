# esport-analysis

## 実行方法

`hand`ディレクトリに移動して以下のコマンドを実行

```shell
python show_graphs.py --movie XXXXX --method XXXXX --keypoints XXXXX --range XXXXX XXXXX
```

実行結果（グラフ）は`track`,`distance`,`angle`ディレクトリ内にPNG形式で保存される

## オプション

- --movie: 動画の名前
    - `hand_1`, `hand_2`, `sync_1`, `sync_2`, `sync_3`のいずれか
- --method: グラフの種類
    - `track`: あるキーポイントの軌跡を描画
    - `distance`: ある2つのキーポイント間の距離の変化を描画
    - `angle`: ある3つのキーポイントを結んだ角度の変化を描画
- --keypoints: キーポイント番号
    - `0`から`20`のいずれかを半角スペース区切りで指定
        - methodが`track`の場合は1つのキーポイントのみ指定
        - methodが`distance`の場合は2つのキーポイントを指定
        - methodが`angle`の場合は3つのキーポイントを指定
    - キーポイントと番号の対応は下図を参照
- --range: 動画の時間範囲
    - `開始時刻` `終了時刻`の順で指定
    - 1分5秒なら`1m5s`と書く

![image](https://developers.google.com/static/mediapipe/images/solutions/hand-landmarks.png)

## コマンド例
**動画「hand_1」の0:00～1:05における、手首（WRIST）の軌跡を描画する**
```shell
python show_graphs.py --movie hand_1 --method track --keypoints 0 --range 0m0s 1m5s
```
**動画「hand_1」の0:00～1:05における、親指先（THUMB_TIP）と小指先（PINKY_TIP）の距離の変化を描画する**

```shell
python show_graphs.py --movie hand_1 --method distance --keypoints 4 20 --range 0m0s 1m5s
```
**動画「hand_1」の0:00～1:05における、親指の角度の変化を描画する**
```shell
python show_graphs.py --movie hand_1 --method angle --keypoints 2 3 4 --range 0m0s 1m5s
```

## Google Colabでの実行方法
1. 以下のコマンドで本リポジトリをcloneする
```bash
!git clone https://github.com/matsuda-tkm/esport-analysis.git
```
2. 上記の実行方法に従ってコマンドを実行する（.pyのパス名に注意するだけ）
```bash
!python /content/esport-analysis/hand/show_graphs.py --movie hand_1 --method track --keypoints 0 --range 0m0s 1m5s
```
3. 結果は、左タブの「ファイル」内`esport-analysis`内に保存される。ランタイムを削除するとデータは消えるため、保管したい場合はダウンロードする。