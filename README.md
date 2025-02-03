# skyway-python-client

SkyWayに接続するためのPythonのクライアント

## **❗注意**

これはSkyWayのSDKとは無関係の非公式の実装です。
動作は保証しておらず、SkyWayの仕様変更により動かなくなる可能性があります。
また、コードや動作についての質問などはSkyWayのサポートへの連絡は行わず、本リポジトリのissueに投稿してください。

## 実装済みの機能

- Channelへのjoin
- SFU Botの作成
- VideoStreamのPublicationのSFU BotによるForwarding

## 未実装の機能(抜粋)

- P2PでのVideoStream、AudioStream、DataStreamのPublish / Subscribe
- SFU経由でのAudioStreamのPublish / Subscribe
- SFU経由でのVideoStreamのSubscribe
- PublicationのReplaceStream
- Streamのenable / disable
- Simulcast
- GetStats
- STUN / TURNの利用
- 再接続処理
- エラーハンドリング
- SkyWay Auth Tokenの更新
- Metadataの取得・更新

## 利用方法

### セットアップ

```shell
git clone git@github.com:kadoshita/skyway-python-client.git
cd skyway-python-client
uv venv .venv
source bin/activate
uv sync
cp .env.example .env
vi .env # SKYWAY_APP_IDとSKYWAY_SECRET_KEYを記述する
```

### Subscriber側

1. Webアプリケーションの起動

```shell
cd skyway-python-client/public
cp ../.env .
npm install
npm start
```

2. Channelの作成
   1. [http://localhost:1234/](http://localhost:1234/)にアクセスする
   2. Startボタンをクリックする
   3. Create Channelボタンをクリックする
   4. Join Channelボタンをクリックする
   5. Channel IDをコピーする
3. Publisher側の実行
4. SFU BotからのPublicationのSubscribe
   1. コンソールに出力されたSFU BotからのPublicationのIDをコピーする
   2. 「Publication ID:」のテキストボックスにPublicationのIDをペーストする
   3. Subscribe Mediaボタンをクリックする

### Publisher側

```shell
$ uv run src/main.py
channel_id: # Subscriber側で作成したChannel IDをペーストし、Enterを押す
```

## 動作環境

- macOS Sonoma 14.6.1
- Python 3.10.2
- uv 0.5.26
- Node.js v20.10.0
