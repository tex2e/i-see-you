
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
# リツイート以外を検索
search_results = api.search_tweets(q="tex2e.github.io -filter:retweets", result_type="mixed", count=50)

conn = pg8000.connect(user='postgres',
                      host='psql13-server',
                      database='reputation',
                      password='password')
cur = conn.cursor()

try:
    for result in search_results:
        tweet_id = result.id  # Tweetのidを取得
        tweet_info = result._json  # REST APIのデータ

        if tweet_info['truncated'] == True:
            # Replace truncated text to full text.
            status = api.get_status(tweet_id, tweet_mode='extended')
            tweet_info['text'] = status.full_text

        name = tweet_info['user']['name']
        print('[+] tweet by %s (https://twitter.com/i/web/status/%s)' % (name, tweet_id))
        print('%s' % tweet_info['text'])
        print('')

        cur.execute('''
        INSERT INTO tweet_my_site(tweet_id, info, created_at)
            VALUES(%s, %s, current_timestamp)
            ON CONFLICT (tweet_id) DO UPDATE SET info = %s;
        ''', (tweet_id, tweet_info, tweet_info))
    conn.commit()

except Exception as e:
    print(e)
finally:
    cur.close()
    conn.close()
