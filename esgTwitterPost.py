import pandas as pd
import numpy as np
import pysbd # Sentence segmenter
import openai # GPT-3
import tweepy # Post tweet
import time, random, os, sys

# Import mongodb_forRead.py & PredictModel.py & secret.py
from modules.mongodb_forRead import MongoDB
from modules.PredictModel import PredictModel
from modules.secret import setup_api_key

# Database connection
mongoDB_connection = MongoDB()
currTime = int(time.time())
today = time.localtime(currTime)
today_to_timestamp = time.mktime((today.tm_year, today.tm_mon, today.tm_mday,8,0,0,0,0,0)) # mktime -> GTC+0 timestamp
prevDayNews = mongoDB_connection.read_prev24hrs_news(today_to_timestamp)
if not prevDayNews: 
    print("There is no esg-related news today!")
    sys.exit()

# ESG News sentence segmenter
esgNews = pd.Series([],dtype=pd.StringDtype()) 
seg = pysbd.Segmenter(language="en", clean=False)
for eachNew in prevDayNews:
    newSentences = seg.segment(eachNew)
    esgNews = pd.concat([esgNews, pd.Series([sentence.replace('\xa0',' ') for sentence in newSentences])], ignore_index=True)

# Write to TSV file
date = str(today.tm_year) + str(today.tm_mon) + str(today.tm_mday)
esgNews.to_csv("./esgBERT_input/esgNews_{}.tsv".format(date), sep='\t', header=False)
print("esgBERT input is ready!")

# Build the predict model
model = PredictModel()
model.get_config()
# Predict and Combine the result
predict_msg = model.run_model("esgNews_{}.tsv".format(date))
predict_msg = model.combine_predict_result("esgNews_{}.tsv".format(date))

result_df = pd.read_csv("./esgBERT_output/esgNews_{}_table.csv".format(date), index_col=0)
result_df['max'] = result_df.max(axis=1)
filter_df = result_df[result_df['max'] >= 0.9].iloc[:,:-1] # Threshold set to 0.9

one_hot_df = pd.DataFrame(np.where(filter_df.T == filter_df.T.max(), 1, 0),index=filter_df.columns).T
all_df = one_hot_df.sum().to_frame(name="ESGNews")
all_df.index.name = "ESG news"

esgNews = pd.read_csv("./esgBERT_input/esgNews_{}.tsv".format(date), sep='\t', names=['idx', 'sentence'], index_col=0)
most_ky_sentences = [esgNews.iloc[idx]["sentence"] for idx in one_hot_df.loc[one_hot_df[all_df.idxmax().values[0]] == 1].index]
most_ky_sentences = random.sample(most_ky_sentences,30) # Choose random 30 sentences from most counts key issue

# Add api key to env (including GPT-3 & Tweet API token)
setup_api_key()

openai.organization = "org-hpKR7cri3YnOlgPZqIAZXtZv"
openai.api_key = os.getenv("OPENAI_API_KEY")
prompt_input = '\n'.join(most_ky_sentences) + "\nPost a brief tweet to summarize the news above [IMPORTANT: Less than 280 characters]:\n"
error_flag = True
for _ in range(10):
  try:
      response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt_input,
        temperature=0.7,
        max_tokens=200,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
      )
      error_flag = False
      break
  except Exception: 
    time.sleep(60)
    continue
if error_flag:
  print("GPT-3 is not calling success, please check!")
  sys.exit()
tweet = response['choices'][0].text

#Variables for accessing twitter API
consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
consumer_secret = os.getenv("TWITTER_CONSUMER_SERCET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_SERCET")

client = tweepy.Client(
    consumer_key=consumer_key, consumer_secret=consumer_secret,
    access_token=access_token, access_token_secret=access_token_secret
)

# Replace the text with whatever you want to Tweet about
response = client.create_tweet(text=tweet[:280])
print(response)