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
today_to_timestamp = time.mktime((today.tm_year, today.tm_mon, today.tm_mday,0,0,0,0,0,0)) # mktime -> GTC+0 timestamp
prevDayNews = mongoDB_connection.read_prev24hrs_news(today_to_timestamp)
if not prevDayNews: 
    print("There is no esg-related news today!")
    sys.exit()

# ESG News sentence segmenter
esgNews = pd.DataFrame(columns=["content", "url", "datasource"])
seg = pysbd.Segmenter(language="en", clean=False)
for eachNew in prevDayNews:
    newSentences = seg.segment(eachNew["content"])
    esgNews = pd.concat([esgNews, pd.DataFrame([{"content": sentence.replace('\xa0',' '), "url": eachNew["url"], "datasource": eachNew["datasource"]} for sentence in newSentences])], ignore_index = True)

# Write to TSV file
date = time.strftime("%Y%m%d", today)
esgNews.to_csv("./esgBERT_input/esgNews_{}_full.tsv".format(date), sep='\t', header=False) # Columns contain content, url, datasource
esgNews["content"].to_csv("./esgBERT_input/esgNews_{}.tsv".format(date), sep='\t', header=False) # Column only content
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

#Choose most key issues sentences
esgNews = pd.read_csv("./esgBERT_input/esgNews_{}_full.tsv".format(date), sep='\t', names=['idx', 'sentence','url','datasource'], index_col=0)
most_ky_indexes = list(one_hot_df.loc[one_hot_df[all_df.idxmax().values[0]] == 1].index)
most_ky_sentences = esgNews.iloc[most_ky_indexes]
most_ky_sentences.to_csv("./esgBERT_output/esgNews_{}_choose_sentences.csv".format(date))

choose_count = 30 if len(most_ky_sentences) >= 30 else len(most_ky_sentences)
most_ky_sentences = random.sample(list(most_ky_sentences["sentence"]),choose_count) # Choose random 30 sentences from most counts key issue

# Add api key to env (including GPT-3 & Tweet API token)
setup_api_key()

openai.api_key = os.getenv("OPENAI_API_KEY")
prompt_input = '\n'.join(most_ky_sentences) + "\nPost a brief tweet to summarize the news above [IMPORTANT: Less than 280 characters]:\n"
response, error_flag = None, True
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
      if len(response['choices'][0].text) > 280: continue
      error_flag = False
      break
  except Exception: 
    time.sleep(60)
    continue
if error_flag:
  print("GPT-3 is not calling success or Generated-text is too long, please check!")
  print("GPT API response: ",response)
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