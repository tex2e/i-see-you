
import os
from pprint import pprint
import tweepy  # pip install tweepy
import pg8000  # pip install pg8000
from dotenv import load_dotenv # pip install python-dotenv
load_dotenv()

consumer_api_key = os.getenv('consumer_api_key')
consumer_api_secret_key = os.getenv('consumer_api_secret_key')
access_token = os.getenv('access_token')
access_token_secret = os.getenv('access_token_secret')

auth = tweepy.OAuthHandler(consumer_api_key, consumer_api_secret_key)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
search_results = api.search_tweets(q="tex2e.github.io", result_type="mixed", count=25)

conn = pg8000.connect(
    user='postgres',
    host='psql13-server',
    database='tweets',
    password='password'
)
cur = conn.cursor()

sql = '''
INSERT INTO tex2e_github_io(tweet_id, info, created_at)
  VALUES(%s, %s, current_timestamp)
  ON CONFLICT DO NOTHING
'''

try:
    for result in search_results:
        tweet_id = result.id  # Tweetのidを取得
        tweet_info = result._json  # REST APIのデータ

        print('[+] tweet (%d)' % tweet_id)
        print('  name=%s' % result._json['user']['name'])
        print('  text=%s' % result._json['text'])
        print('')

        cur.execute(sql, (tweet_id, tweet_info))
    conn.commit()
except Exception as e:
    print(e)

cur.close()
conn.close()
