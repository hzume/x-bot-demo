import json
from pathlib import Path

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import tweepy
import questionary
from http.server import BaseHTTPRequestHandler, HTTPServer


def check_aws_credentials():
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        region_name = session.region_name or "未設定"
        profile_name = session.profile_name or "デフォルト"

        if credentials is None:
            raise Exception("AWSの認証情報が設定されていません。")

        access_key_masked = f"{credentials.access_key[:4]}****"
        print("AWSの認証情報が設定されています。")
        print(f"使用中のプロファイル: {profile_name}")
        print(f"設定されたリージョン: {region_name}")
        print(f"アクセスキーID: {access_key_masked}\n")

    except (NoCredentialsError, PartialCredentialsError):
        raise Exception("AWS認証情報が不完全、または無効です。")


def check_secret_name_not_duplicate(
    secret_client: boto3.client, secret_name: str
) -> bool:
    try:
        response = secret_client.get_secret_value(SecretId=secret_name)
        return response["SecretString"] is None
    except Exception:
        return True


class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """HTTPサーバーが認可後のリクエストを受け取る部分"""
        query = self.path.split("?")[-1]
        params = dict(x.split("=") for x in query.split("&"))
        oauth_verifier = params.get("oauth_verifier")

        if oauth_verifier:
            self.server.oauth_verifier = oauth_verifier
            self.send_response(200)
            self.end_headers()
            self.wfile.write("認証が成功しました！このページは閉じても大丈夫です。".encode("shift_jis"))
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write("認証が失敗しました。手動での認証を試してみてください。(参考：https://developer.x.com/ja/docs/authentication/oauth-1-0a/obtaining-user-access-tokens)".encode("shift_jis"))


def start_server():
    server_address = ("127.0.0.1", 8080)
    httpd = HTTPServer(server_address, OAuthHandler)
    httpd.handle_request()
    return httpd.oauth_verifier


def main():
    check_aws_credentials()

    aws_config_path = Path(__file__).parent / "terraform/aws_config.tfvars.json"
    with open(aws_config_path, "r") as f:
        config = json.load(f)

    region_name = config["region"]
    region_choices = ["ap-northeast-1", "ap-northeast-2", "ap-northeast-3"]
    region2region_name = {
        "ap-northeast-1": "東京",
        "ap-northeast-2": "ソウル",
        "ap-northeast-3": "大阪",
    }
    regions_with_name = [f"{region_name} ({region2region_name[region_name]})" for region_name in region_choices]
    region_with_name = f"{region_name} ({region2region_name[region_name]})"

    region_with_name = questionary.select("リージョンを選択してください", choices=regions_with_name, default=region_with_name).ask()
    region_name = region_with_name.split(" (")[0]

    secret_client = boto3.client("secretsmanager", region_name=region_name)
    secret_name = questionary.text(
        "シークレット名を入力してください",
        validate=lambda text: True if check_secret_name_not_duplicate(secret_client, text) else "シークレット名が重複しています。",
    ).ask()

    x_consumer_key = questionary.text("XのConsumer API Keyを入力してください").ask()
    x_consumer_secret = questionary.text("XのConsumer API Secretを入力してください").ask()
    x_bearer_token = questionary.text("XのBearer Tokenを入力してください").ask()
    openai_api_key = questionary.text("OpenAIのAPI Keyを入力してください").ask()

    auth = tweepy.OAuth1UserHandler(
        consumer_key=x_consumer_key,
        consumer_secret=x_consumer_secret,
        callback="http://localhost:8080/callback",
    )

    redirect_url = auth.get_authorization_url()
    print(f"\nURLを開き、認証してください: {redirect_url}")

    # verifierをローカルサーバーで取得
    oauth_verifier = start_server()

    x_access_token, x_access_token_secret = auth.get_access_token(oauth_verifier)
    print("\nSuccess!")
    print("X_AccessToken:", x_access_token)
    print("X_AccessTokenSecret:", x_access_token_secret)

    secret_client.create_secret(
        Name=secret_name,
        SecretString=json.dumps({
            "X_ConsumerKey": x_consumer_key,
            "X_ConsumerSecret": x_consumer_secret,
            "X_BearerToken": x_bearer_token,
            "X_AccessToken": x_access_token,
            "X_AccessTokenSecret": x_access_token_secret,
            "OpenAI_ApiKey": openai_api_key,
        }),
    )

    print("シークレットが正常に作成されました。")

    config["secret_name"] = secret_name
    config["region"] = region_name
    with open(aws_config_path, "w") as f:
        json.dump(config, f, indent=4)

    print("\n🎊初期設定が完了しました🎉")
    print("README.mdに従って、aws_config.tfvars.jsonとconfig.yamlを編集し、デプロイしてください。")
    
if __name__ == "__main__":
    main()
