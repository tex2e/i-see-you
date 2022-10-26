
import os
import tweepy  # pip install tweepy
import pg8000  # pip install pg8000
from dotenv import load_dotenv # pip install python-dotenv

# Twitterのアクセスキーは .env ファイルから読み込む
load_dotenv()

consumer_api_key = os.getenv('consumer_api_key')
consumer_api_secret_key = os.getenv('consumer_api_secret_key')
access_token = os.getenv('access_token')
access_token_secret = os.getenv('access_token_secret')

# ツイートの検索
auth = tweepy.OAuthHandler(consumer_api_key, consumer_api_secret_key)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
# 検索対象はリツイート以外で自分のコンテンツに言及しているもの
my_content_keyword = 'tex2e.github.io'
search_results = api.search_tweets(q=f"{my_content_keyword} -filter:retweets", result_type="mixed", count=25)

# PostgreSQLへの接続
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
            # 省略された(truncated)ツイートは、内容を全文に修正する
            status = api.get_status(tweet_id, tweet_mode='extended')
            tweet_info['text'] = status.full_text

        # デバッグ出力
        name = tweet_info['user']['name']
        print('[+] tweet by %s (https://twitter.com/i/web/status/%s)' % (name, tweet_id))
        print('%s' % tweet_info['text'])
        print('')

        # ツイートをDBに登録する
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
