import json

import boto3
import tweepy

region = "ap-northeast-3"
secret_name = "prod/demo-secrets"

client = boto3.client("secretsmanager", region_name=region)
response = client.get_secret_value(SecretId=secret_name)
secret = json.loads(response["SecretString"])

auth = tweepy.OAuth1UserHandler(
    consumer_key=secret["X_ConsumerKey"],
    consumer_secret=secret["X_ConsumerSecret"],
)

print(auth.get_authorization_url())

verifier = input("Verifierを入力してください: ")

access_token, access_token_secret = auth.get_access_token(verifier)
print("\nSuccess!")
print("access_token:", access_token)
print("access_token_secret:", access_token_secret)
