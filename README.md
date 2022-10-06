
# I-See-You

### 目的
- Twitterで自分のブログやコンテンツに対してコメントしているツイートを収集し、フィードバックに活用する。
    - 自分の記事に対する間違いの指摘や理解できなかったなどの感想をツイッターでつぶやくだけで終わっている人が見受けられるため。
- 各ツイートに対してポシネガ判定をする。
    - ネガティブ判定は早めに修正対応できるようにする。
    - ポジティブ判定はどの記事やコンテンツの保守に注力すれば良いかの指針にする。
- 検知した結果はDiscordで通知する。

### 開発者向け

```bash
docker-compose up -d
docker-compose exec python3-server python src/fetch_tweets.py
```

```sql
USE tweets;
CREATE TABLE tex2e_github_io (
    tweet_id VARCHAR(32) PRIMARY KEY,
    info JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
CREATE TABLE pos_neg (
    tweet_id VARCHAR(32) PRIMARY KEY,
    pos TEXT[] NOT NULL,
    neg TEXT[] NOT NULL,
    words INTEGER NOT NULL,
    foreign key (tweet_id) references tex2e_github_io(tweet_id)
)
```

ツイートIDから元のTweetを見る場合のURL：`https://twitter.com/i/web/status/<ID>`
