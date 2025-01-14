from pathlib import Path

import tweepy
from utils import Config, get_clients, load_config


def filter_user(user: tweepy.User, config: Config) -> bool:
    """
    configに応じて、ユーザーをフィルタリングする
    
    user: tweepy.User
        フィルタリング前のユーザー
    config: Config
        設定ファイル
    """
    is_passed = True
    if config.follow.filter.allow_protected:
        is_passed = is_passed and (not user.protected)
    is_passed = is_passed and (
        user.public_metrics["followers_count"] > config.follow.filter.min_followers
    )
    return is_passed


def handler(event, context):
    config = load_config(Path(__file__).parent / "config.yaml")
    X_client, _ = get_clients(config)

    tweets: list[tweepy.Tweet] = X_client.search_recent_tweets(
        query=config.follow.post_search_query,
        max_results=10,
        tweet_fields=["author_id"],
    ).data

    user_ids = [tweet.author_id for tweet in tweets]
    users: list[tweepy.User] = X_client.get_users(
        ids=user_ids, user_fields=["public_metrics", "protected"]
    ).data

    # フィルタリング
    users = [user for user in users if filter_user(user, config)]

    for i, user in enumerate(users):
        if i >= config.follow.max_follow_count:
            break
        X_client.follow_user(target_user_id=user.id)

    return "follow OK"
