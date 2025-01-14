import json
import os
from pathlib import Path
from typing import Literal

import boto3
import tweepy
import yaml
from botocore.exceptions import ClientError
from openai import OpenAI
from pydantic import BaseModel, field_validator


class FollowFilterConfig(BaseModel):
    min_followers: int
    allow_protected: bool

    @field_validator("min_followers")
    def validate_min_followers(cls, v):
        if v < 0:
            raise ValueError("min_followers must be greater than 0")
        return v


class FollowConfig(BaseModel):
    post_search_query: str
    max_follow_count: int
    filter: FollowFilterConfig

    @field_validator("max_follow_count")
    def validate_max_follow_count(cls, v):
        if v < 0:
            raise ValueError("max_follow_count must be greater than 0")
        return v


class PostConfig(BaseModel):
    source_account_name: Literal["livedoornews"]
    max_lookback_hours: int
    post_search_query: str
    post_instruction_prompt: str
    post_style_examples: list[str]


class Config(BaseModel):
    secret_name: str
    follow: FollowConfig
    post: PostConfig


def load_config(path: Path) -> Config:
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    return Config(**config)


def get_clients(config: Config):
    region = os.environ["REGION"]
    session = boto3.session.Session()
    sm_client = session.client(
        service_name="secretsmanager", region_name=region
    )

    try:
        get_secret_value_response = sm_client.get_secret_value(SecretId=config.secret_name)
    except ClientError as e:
        raise e

    secrets = json.loads(get_secret_value_response["SecretString"])

    X_client = tweepy.Client(
        bearer_token=secrets["X_BearerToken"],
        consumer_key=secrets["X_ConsumerKey"],
        consumer_secret=secrets["X_ConsumerSecret"],
        access_token=secrets["X_AccessToken"],
        access_token_secret=secrets["X_AccessTokenSecret"],
    )

    openai_client = OpenAI(api_key=secrets["OpenAI_ApiKey"])

    return X_client, openai_client
