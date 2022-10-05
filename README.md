
# I-See-You

### 目的
- Twitterで自分のブログやコンテンツに対してコメントしているツイートを収集し、フィードバックに活用する。
- ポシネガ判定ができればなお良い
- 検知した結果はDiscordへ通知する

### 開発者向け

```bash
docker-compose up -d
docker-compose exec python3-server python src/main.py
```

```sql
USE tweets;
DROP TABLE tex2e_github_io;
CREATE TABLE tex2e_github_io (
    tweet_id VARCHAR(32) PRIMARY KEY,
    info JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

