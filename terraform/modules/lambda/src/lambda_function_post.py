import re
from datetime import timedelta
from logging import getLogger
from pathlib import Path

import requests
import tweepy
from bs4 import BeautifulSoup
from utils import Config, get_clients, load_config


def parse_article_url(text: str, source_account_name: str) -> str:
    """
    source_account_nameに応じて、ツイート本文から記事のURLを抽出する

    text: str
        記事URLを含むツイート本文
    source_account_name: str
        記事のソースのアカウント名
    """
    if source_account_name == "livedoornews":
        # example: https://news.livedoor.com/article/detail/27882963/
        print(text)
        url = re.search(r"https://news\.livedoor\.com/article/detail/\d+/", text)
        if url is None:
            raise ValueError("Article URL not found")
        return url.group(0)
    else:
        raise ValueError(f"Unsupported source account name: {source_account_name}")


def parse_article_html(article_html: str, source_account_name: str) -> tuple[str, str]:
    """
    source_account_nameに応じて、記事のHTMLからタイトルと本文を抽出する

    article_html: str
        記事のHTML
    source_account_name: str
        記事のソースのアカウント名
    """
    if source_account_name == "livedoornews":
        article_soup = BeautifulSoup(article_html, "html.parser")
        article_body = article_soup.find("span", itemprop="articleBody")
        if article_body is None:
            raise ValueError("Article body not found")
        article_body_text = article_body.text.replace("\n", "")

        article_title = article_soup.find("h1", itemprop="headline")
        if article_title is None:
            raise ValueError("Article title not found")
        article_title = article_title.text.replace("\n", "")
    else:
        raise ValueError(f"Unsupported source account name: {source_account_name}")
    return article_title, article_body_text


def build_system_prompt(config: Config) -> str:
    """
    configからシステムプロンプトを作成する

    config: Config
        設定ファイル
    """
    system_prompt = config.post.post_instruction_prompt
    system_prompt += "\n\n以下に、記事とそれに対する反応ツイート例をいくつか示します。この例を参考にして、記事に対する反応ツイートを作成してください。"
    for i, example in enumerate(config.post.post_style_examples):
        system_prompt += f"\n\n参考例{i+1}:\n{example}"
    return system_prompt


def build_search_query(config: Config) -> str:
    """
    configから記事ツイート検索クエリを作成する

    config: Config
        設定ファイル
    """
    query = f"from:{config.post.source_account_name}"
    if len(config.post.post_search_query) > 0:
        query += f" AND ({config.post.post_search_query})"
    return query


def filter_tweets(tweets: list[tweepy.Tweet], config: Config) -> list[tweepy.Tweet]:
    """
    configに応じて、ツイートをフィルタリングする
    最新のツイートから、config.post.max_lookback_hours時間前までのツイートを抽出

    tweets: list[tweepy.Tweet]
        フィルタリング前のツイート
    config: Config
        設定ファイル
    """
    tweets = sorted(tweets, key=lambda x: x.created_at, reverse=True)
    latest_tweet = tweets[0]

    tweets = [
        tweet
        for tweet in tweets
        if tweet.created_at
        > latest_tweet.created_at - timedelta(hours=config.post.max_lookback_hours)
    ]
    return tweets


def find_article(X_client: tweepy.Client, config: Config) -> tuple[str, str, str]:
    """
    記事ツイートを検索して、記事のタイトル、本文、ツイートIDを取得する

    X_client: tweepy.Client
        XのAPIクライアント
    config: Config
        設定ファイル
    """
    search_query = build_search_query(config)

    tweets: list[tweepy.Tweet] = X_client.search_recent_tweets(
        query=search_query,
        max_results=10,
        tweet_fields=["public_metrics", "created_at"],
    ).data

    tweets = filter_tweets(tweets, config)
    tweets = sorted(tweets, key=lambda x: x.public_metrics["like_count"], reverse=True)

    for tweet in tweets:
        try:
            url = re.search(r"https?://[^\s]+", tweet.text)
            if url is None:
                raise ValueError("URL not found")
            url = url.group(0)

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers)

            article_url = parse_article_url(response.text, config.post.source_account_name)
            break
        except Exception:
            continue

    if article_url is None:
        raise ValueError("Article URL not found")
        
    article_html = requests.get(article_url, headers=headers).text

    article_title, article_body_text = parse_article_html(
        article_html, config.post.source_account_name
    )
    return article_title, article_body_text, tweet.id


def handler(event, context):
    config = load_config(Path(__file__).parent / "config.yaml")
    X_client, openai_client = get_clients(config)

    system_prompt = build_system_prompt(config)

    article_title, article_body_text, quote_tweet_id = find_article(X_client, config)
    user_prompt = f"""
    タイトル: {article_title}
    本文: {article_body_text}
    """

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    post_text = response.choices[0].message.content

    response = X_client.create_tweet(text=post_text, quote_tweet_id=quote_tweet_id)

    return "post OK"
