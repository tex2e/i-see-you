
from janome.tokenizer import Tokenizer
import pandas as pd
import pg8000

### 形態素解析器 ###
tokenizer = Tokenizer()

### 日本語評価極性辞書によるポジネガ判定 ###
# http://www.cl.ecei.tohoku.ac.jp/Open_Resources-Japanese_Sentiment_Polarity_Dictionary.html
# 辞書の読み込み
df_dic = pd.read_csv('data/pn.csv.m3.120408.trim', sep='\t', names=("名詞", "感情", "動詞句"), encoding='utf-8')
# 感情のうち、p/nの項目のみを抽出
df_dic = df_dic[(df_dic["感情"] == 'p') | (df_dic["感情"] == 'n')]
# 動詞句を削除
df_dic = df_dic.iloc[:,0:2]
# 各名詞が辞書にあるか確認し、あれば感情とともに配列に格納

### DB接続 ###
conn = pg8000.connect(
    user='postgres',
    host='psql13-server',
    database='tweets',
    password='password'
)
cur = conn.cursor()

sql = '''
SELECT tweet_id, (info::json->>'user')::json->>'name', info::json->>'text'
  FROM tex2e_github_io;
'''

cur.execute(sql)
rows = cur.fetchall()

for row in rows:
    print(row)
    text = row[2]

    pos_neg_score = 0
    pos_words = []
    neg_words = []
    words_count = 0

    for token_i, token in enumerate(tokenizer.tokenize(text), start=1):
        # print(token.surface)
        dict_word = df_dic[df_dic['名詞'] == token.surface]
        if len(dict_word) == 0:
            continue
        token_type = dict_word.iloc[0]['感情']
        if token_type == 'p':
            pos_neg_score += 1
            pos_words.append(token.surface)
        elif token_type == 'n':
            pos_neg_score -= 1
            neg_words.append(token.surface)

    words_count = token_i
    print('[+] score=%f, pos=%s, neg=%s, words=%d' % (pos_neg_score / words_count, pos_words, neg_words, words_count))

cur.close()
conn.close()
