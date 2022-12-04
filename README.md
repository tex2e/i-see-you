
# I-See-You

### 目的
- Twitterで自分のブログやコンテンツに対するツイートを収集し、フィードバックに活用する
    - 自分の記事への間違いの指摘や理解が困難などの感想をツイッターでつぶやくだけで終わる人が見受けられるため
    - 各ツイートに対してポシネガ判定をする
        - ネガティブ判定は早めに修正対応できるようにする
        - ポジティブ判定はどの記事やコンテンツに注力するかの指針にできるようにする
    - 検知したツイートはDiscordで通知する

### 開発者向け

起動＆実行
```bash
docker-compose up -d
docker-compose exec -T python3-server python src/fetch_tweets.py
docker-compose exec -T python3-server python src/pos_neg_tweets.py
docker-compose exec -T python3-server python src/send_to_discord.py
```

ビルド（使用するライブラリの増加時などのみ）
```
docker-compose build python3-server
docker-compose down
docker-compose up -d
```

DDL (PostgreSQL)
```sql
CREATE DATABASE reputation;

USE reputation;

CREATE TABLE tweet_my_site (
    tweet_id VARCHAR(32) PRIMARY KEY,
    info JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
ALTER TABLE tweet_my_site ADD COLUMN checked BOOLEAN DEFAULT FALSE;

CREATE TABLE tweet_my_site_pos_neg (
    tweet_id VARCHAR(32) PRIMARY KEY,
    pos TEXT[] NOT NULL,
    neg TEXT[] NOT NULL,
    word_count INTEGER NOT NULL,
    FOREIGN KEY (tweet_id) REFERENCES tweet_my_site(tweet_id)
)
```

.envファイルの作成と秘密値の設定
```
consumer_api_key = 'xxxxxxxxxxxxxxxxxxxxxxxxx'
consumer_api_secret_key = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
access_token = 'nnnnnnnnnn-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
access_token_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
discord_webhook_url = 'https://discord.com/api/webhooks/nnnnn/xxxxxxxxxxxxx'
```

### その他

ツイートIDから元のTweetを見る場合のURL：`https://twitter.com/i/web/status/<ID>`
