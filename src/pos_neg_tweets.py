
from janome.tokenizer import Tokenizer  # pip install janome
import pandas as pd  # pip install pandas
import pg8000  # pip install pg8000

# 形態素解析器
tokenizer = Tokenizer()

# 日本語評価極性辞書によるポジネガ判定
#   http://www.cl.ecei.tohoku.ac.jp/Open_Resources-Japanese_Sentiment_Polarity_Dictionary.html
# 辞書の読み込み
df_dic = pd.read_csv('data/pn.csv.m3.120408.trim', sep='\t', names=("名詞", "感情", "動詞句"), encoding='utf-8')
# p(Positive)/n(Negative)の感情のみ抽出
df_dic = df_dic[(df_dic["感情"] == 'p') | (df_dic["感情"] == 'n')]
# 動詞句を削除
df_dic = df_dic.iloc[:,0:2]

# PostgreSQLへの接続
conn = pg8000.connect(user='postgres',
                      host='psql13-server',
                      database='reputation',
                      password='password')
cur = conn.cursor()

try:
    # DBからポジネガ未判定のツイート一覧を取得する
    cur.execute('''
    SELECT TW.tweet_id, (info::json->>'user')::json->>'name', info::json->>'text'
        FROM tweet_my_site AS TW
        LEFT JOIN tweet_my_site_pos_neg AS PN ON PN.tweet_id = TW.tweet_id
        WHERE PN.word_count IS NULL;
    ''')
    rows = cur.fetchall()

    # 各ツイートで処理を行う
    for row in rows:
        print(row)
        tweet_id, name, text, *_ = row

        pos_neg_score = 0
        pos_words = []
        neg_words = []
        words_count = 0

        # 各形態素で処理を行う
        for token_i, token in enumerate(tokenizer.tokenize(text), start=1):
            # print(token.surface)
            dict_word = df_dic[df_dic['名詞'] == token.surface]
            if len(dict_word) == 0:
                continue
            token_type = dict_word.iloc[0]['感情']
            # ポジティブのときはプラス、ネガティブのときはマイナスをスコアに加算する
            if token_type == 'p':
                pos_neg_score += 1
                pos_words.append(token.surface)
            elif token_type == 'n':
                pos_neg_score -= 1
                neg_words.append(token.surface)

        # デバッグ出力
        words_count = token_i
        print('[+] ----------------------------------------')
        print('[+] score=%f, pos=%s, neg=%s, words=%d' % (pos_neg_score / words_count, pos_words, neg_words, words_count))

        # ポジネガ判定結果をDBに登録
        try:
            cur.execute('''
            INSERT INTO tweet_my_site_pos_neg(tweet_id, pos, neg, word_count)
                VALUES(%s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            ''', (tweet_id, pos_words, neg_words, words_count))
            conn.commit()
        except Exception as e:
            print(e)

finally:
    cur.close()
    conn.commit()
    conn.close()
