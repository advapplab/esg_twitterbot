import boto3, json
from pathlib import Path

with open(Path(__file__).parent.absolute()/'modules/credential.json') as data_file:
    data = json.load(data_file)
BUCKET = data["BUCKET"]
AWS_ACCESS_KEY = data["AWS_ACCESS_KEY"]
AWS_SERCET_KEY = data["AWS_SERCET_KEY"]

s3_client = boto3.client("s3", aws_access_key_id = AWS_ACCESS_KEY, aws_secret_access_key = AWS_SERCET_KEY)

s3_client.download_file(BUCKET, "finetune_model_latest_twitterbot/finetune_model_latest_twitterbot.tar.gz", "./finetune_model_latest_twitterbot.tar.gz")
print("Download Finished!")