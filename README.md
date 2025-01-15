# 新しくアカウントを作成する場合の手順

1. Xアカウントを作成・ログイン
2. 本リポジトリを`git clone`
3. `uv sync`で仮想環境を作成（[uvのインストール方法](https://docs.astral.sh/uv/getting-started/installation/)）
4. `uv run setup.py`で初期設定を行う
5. 下記「設定ファイルについて」を参照し、自動フォロー・ポストの設定を行う
6. 下記「デプロイ方法」を参照し、デプロイする

# 概要

## ディレクトリ構成

編集頻度が高そうなファイルのみ記載

```
.
├── setup.py # 初期設定を行うスクリプト
└── terraform/
    ├── aws_config.tfvars.json # インフラに関する設定ファイル 
    └── modules/
        └── lambda/
            └── src/
                ├── config.yaml # Lambda関数の設定ファイル
                ├── follow.Dockerfile # 自動フォローLambda関数のDockerfile
                ├── lambda_function_follow.py # 自動フォローLambda関数のソースコード
                ├── utils.py # ユーティリティ関数
                └── requirements.txt
```

## 構成

- SecretsManager: X APIのAPIキーやOpenAIのAPIキーなどを保存
- ECR: 自動フォローLambda関数と自動投稿Lambda関数のイメージを保存
- Lambda: ECRに保存されたイメージをデプロイ
- EventBridge Scheduler: Lambda関数を定期実行



## 各種Lambda関数の処理概要
### 自動フォローLambda関数
1. ツイートをなんらかのワードで検索
2. 検索結果のツイート主をフィルタリング
3. フィルタリング結果のユーザーを決められた人数までフォロー

### 自動投稿Lambda関数

1. あるアカウントのツイートを検索
2. 最もいいねされたツイートを取得
3. 取得したツイートをもとにツイートを作成し、投稿

# デプロイ方法

terraformでインフラをデプロイする。

1. 後述する設定ファイル（`aws_config.tfvars.json`と`config.yaml`）を編集
2. AWS CLIにログイン
3. `cd terraform`
4. `terraform init`
5. `terraform apply -var-file=aws_config.tfvars.json`

## SecretsManagerの設定
SecretsManagerはterraformでは管理していないので、AWSコンソールから手動で設定する。
初期設定は`setup.py`で行う。

- X_BearerToken
- X_ConsumerKey
- X_ConsumerSecret
- X_ClientID (現状不要)
- X_ClientSecret (現状不要)

X API developer portalから取得可能

- X_AccessToken
- X_AccessTokenSecret

Xアカウント毎に取得・設定する必要がある。取得方法は下記の「新しくアカウントを作成する場合の手順」を参照。

- OpenAI_ApiKey

# 設定ファイルについて

## aws_config.tfvars.json

AWSリソースに関する設定ファイル。
- app_name: アプリケーション名
- region: リージョン
- secret_name: SecretsManagerのシークレット名
- schedule_expression_follow: 自動フォローLambda関数の定期実行スケジュール
- schedule_expression_post: 自動投稿Lambda関数の定期実行スケジュール

## config.yaml

Lambda関数の設定ファイル。
- follow: 自動フォローに関する設定
    - post_search_query: ツイートの検索クエリ（参照：https://developer.x.com/en/docs/x-api/tweets/search/integrate/build-a-query）
    - max_follow_count: 一度にフォローするユーザーの最大数
    - filter: フォローするユーザーのフィルター条件
        - min_followers: フォローするユーザーのフォロワー数の最小値
        - allow_protected: 保護されたアカウントをフォローするかどうか 保護されたアカウントをフォローするとフォローリクエストが送信される
- post: 自動投稿に関する設定
    - source_account_name: 記事のソースアカウント名
    - max_lookback_hours: 記事のさかのぼる最大時間 1に設定すると1時間前までの記事を参照する
    - post_search_query: 記事の検索クエリ 追加すると、source_account_nameのツイートを検索する際にこのクエリも検索する
    - post_instruction_prompt: 投稿するツイートの指示プロンプト 文字数やフォーマットを指定
    - post_style_examples: 投稿するツイートのツイート例 文体などを参考にさせるために指定

# For Developer
## Python仮想環境の設定
uvを用いて管理しています。`uv sync`で仮想環境を作成できます。

## ローカルテスト
https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/python-image.html#python-image-instructions
を参照してください

## 機能の変更・追加実装
- 新しくライブラリを追加したい
    - `terraform/modules/lambda/src/requirements.txt`に追記してください
- 自動フォローのフィルタリング条件を追加したい
    1. `config.yaml`の`follow.filter`に条件を追加
    2. `utils.py`の`FollowFilterConfig`にフィールドを追加
    3. `lambda_function_follow.py`の`filter_user`関数に条件を追加
- 自動投稿で、記事のソースアカウントを変更したい
    1. `config.yaml`の`post.source_account_name`を変更
    2. `utils.py`の`PostConfig.source_account_name`に新たなソースアカウント名を追加
    3. `lambda_function_post.py`の`parse_article_url`と`parse_article_html`に新たなソースアカウント名に対応した処理を追加
