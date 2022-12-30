import json, os
from pathlib import Path
def setup_api_key():
    with open(Path(__file__).parent.absolute()/'credential.json') as data_file:
        data = json.load(data_file)
    OPENAI_API_KEY = data["OPENAI_API_KEY"]
    TWITTER_CONSUMER_KEY = data["TWITTER_CONSUMER_KEY"]
    TWITTER_CONSUMER_SERCET = data["TWITTER_CONSUMER_SERCET"]
    TWITTER_ACCESS_TOKEN = data["TWITTER_ACCESS_TOKEN"]
    TWITTER_ACCESS_SERCET = data["TWITTER_ACCESS_SERCET"]
    os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
    os.environ['TWITTER_CONSUMER_KEY'] = TWITTER_CONSUMER_KEY
    os.environ['TWITTER_CONSUMER_SERCET'] = TWITTER_CONSUMER_SERCET
    os.environ['TWITTER_ACCESS_TOKEN'] = TWITTER_ACCESS_TOKEN
    os.environ['TWITTER_ACCESS_SERCET'] = TWITTER_ACCESS_SERCET