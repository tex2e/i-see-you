
# I-See-You

### 目的
- Twitterで自分のブログやコンテンツに対してコメントしているツイートを収集し、フィードバックに活用する。
    - 自分の記事に対する間違いの指摘や理解できなかったなどの感想をツイッターでつぶやくだけで終わっている人が見受けられるため。
- 各ツイートに対してポシネガ判定をする。
    - ネガティブ判定は早めに修正対応できるようにする。
    - ポジティブ判定はどの記事やコンテンツの保守に注力すれば良いかの指針にする。
- 検知した結果はDiscordで通知する。

### 開発者向け

起動＆実行
```bash
docker-compose up -d
docker-compose exec python3-server python src/fetch_tweets.py
docker-compose exec python3-server python src/pos_neg_tweets.py
docker-compose exec python3-server python src/send_to_discord.py
```

ビルド
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

ツイートIDから元のTweetを見る場合のURL：`https://twitter.com/i/web/status/<ID>`
