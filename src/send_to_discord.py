
import json
import requests
import pg8000  # pip install pg8000


def send_msg_to_discord(msg: str, debug=True):
    webhook_url = 'https://discord.com/api/webhooks/1033297217718587454/4fAlAto_dYs8A0LGv3eoDHCWRIuZS9o8GnKAHddPacZYfZljkE7S6XXCMYFQm0hniqw1'

    main_content = {'content': msg}

    response = requests.post(webhook_url,
                            json.dumps(main_content),
                            headers={'Content-Type': 'application/json'})
    if debug:
        print(response)
        print(response.text)
    return response


def make_msg(tweet_id: str, name: str, text: str, pos: str, neg: str, word_count: int):
    score = len(pos) / word_count - len(neg) / word_count
    sign  = '+' if score >= 0 else '-'
    res  = '[%s] score=%f, pos=%s, neg=%s\nhttps://twitter.com/i/web/status/%s\n' % (sign, score, pos, neg, tweet_id)
    return res


conn = pg8000.connect(user='postgres',
                      host='psql13-server',
                      database='reputation',
                      password='password')
cur = conn.cursor()

sql_select_tweets = '''
SELECT TW.tweet_id, (info::json->>'user')::json->>'name', info::json->>'text', pos, neg, word_count
  FROM tweet_my_site AS TW
  LEFT JOIN tweet_my_site_pos_neg AS PN ON PN.tweet_id = TW.tweet_id
  WHERE TW.checked IS FALSE;
'''

sql_update_tweet_checked = '''
UPDATE tweet_my_site SET checked = TRUE WHERE tweet_id = %s;
'''

try:
    cur.execute(sql_select_tweets)
    rows = cur.fetchall()

    msgs: list[str] = []

    for row in rows:
        print(row)
        tweet_id, name, text, pos, neg, word_count, *_ = row
        if (pos is None) or (neg is None) or (word_count is None):
            continue
        msg = make_msg(tweet_id, name, text, pos, neg, word_count)
        msgs.append(msg)

        # 送信済みフラグをTrueで確定させる
        cur.execute(sql_update_tweet_checked, (tweet_id,))

    print('----------------------')
    response = None
    for msg in msgs:
        print(msg)
        response = send_msg_to_discord(msg)
    else:
        # 最後のツイートをDiscordに送信できた場合、送信済みフラグをTrueで確定させる
        if response and response.status_code in (200, 204):
            conn.commit()

finally:
    cur.close()
    conn.commit()
    conn.close()
