from flask import Flask, request, jsonify

import pickle
with open('./mecab-ko-dic-2.1.1-20180720_DEV/Inflect_dictionary.pickle', 'rb') as fr: # <Inflect.CSV 사전을 dictionary화 한 pickle 데이터 로드>
    inflect_data = pickle.load(fr)
    
from konlpy.tag import Mecab
mecab = Mecab('./mecab-ko-dic-2.1.1-20180720_DEV') # mecab-ko-dic-2.1.1-20180720_DEV 폴더
#사전 경로를 주지 않으면 /usr/local/lib/mecab/dic/mecab-ko-dic을 찾습니다.
#mecab = Mecab(
#print(mecab.pos('배달의민족 승민골프'))


# 키워드 추출 함수 (B)
import re

final_pattern = '((NNG@)*(VA@ETN@|_VA@ETM@_|VV\+ETM@_|VV\+ETN@_|VA\+ETN@_)+(NNG@)+)|((XPN@)*(SN@|SN@_|NR@|NR@_|^MM@|^MM@_|_MM@|_MM@_)*(NNG@|NNP@|NNBC@|NNB@)+(NNG@|NNP@|NNBC@)*(VV@ETM@|VV@ETN@|VA@ETN@|VA@ETM@)*(XSN@)*)|((XPN@)*(XR@)*(XSN@))|((VA\+ETM@|XSV@ETM@)+(_NNG@)+(NNG@|NNP@|NNBC@|NNB@)*)|(_NP@JKS@|^NP@JKS@|NP\+JKS@|MAG@JKS@)|(^MAG@|_MAG@)|(^NP@|_NP@|NP@)|(VA@)|(VV@)|(VV\+ETM@|VV\+ETN@|VV\+EP@|VV\+EF@|VV\+EC@|VV\+EC\+VX\+EC@|VA\+ETM@|VA\+ETN@|VA\+EP@|VA\+EF@|VA\+EC@)+|(SN@|SL@)|(MM@)'

def B(sentence):
    index_lt = []
    keyword_lt = []
    
    print('# 질의문:  ', sentence)
    ###print('형태소분석 결과:  ', mecab.morphs(sentence))
    result = mecab.pos(sentence)
    print('# 품사 태깅 결과:  ', result)
    # Post Processing
    space_lt = []
    temp = sentence[:]

    for idx in range(len(result)):
        w, t = result[idx]  
        l = len(w)

        if idx==0:
            space_lt.append('F')
            temp = temp[l:][:]
            continue
        if temp[0] == ' ':
            space_lt.append('T')
            temp = temp[l+1:][:]
        else:
            space_lt.append('F')
            temp = temp[l:][:]


    word_string = ''.join(result[idx][0]+'@' if space_lt[idx+1]=='F' else result[idx][0]+'@_' for idx in range(len(result)-1))
    word_string += result[-1][0] + '@'
    tag_string = ''.join(result[idx][1]+'@' if space_lt[idx+1]=='F' else result[idx][1]+'@_' for idx in range(len(result)-1))
    tag_string += result[-1][1] + '@'    
    word_lt = word_string.split('@')[:-1][:]
    ###print(word_string) # 2023@년@_설날@은@_몇@_일@이@야@?@
    print(tag_string) # SN@NNBC@_NNG@JX@_MM@_NNG@VCP@EF@SF@
    ###print(word_lt) # ['2023', '년', '_설날', '은', '_몇', '_일', '이', '야', '?']
    

    rex4 = re.finditer(final_pattern, tag_string)
    #####print(rex4)
    for s in rex4:
        ###print(s)
        ###print(s.start(), s.end())
        ###print(s.group())
        tag = s.group()
          
        
        start_cnt = len(tag_string[:s.start()].split('@'))
        end_cnt = len(tag_string[:s.end()].split('@'))
        #print(start_cnt, end_cnt)
        #print(word_lt[start_cnt-1:end_cnt-1])
        keyword = ''.join(word_lt[start_cnt-1:end_cnt-1])
        keyword = keyword.replace('_', ' ')
        keyword = keyword.rstrip()
        keyword = keyword.lstrip()
        
        if tag in ['VV+ETM@', 'VV+ETN@',  'VV+EP@', 'VV+EF@', 'VV+EC@', 'VV+EC+VX+EC@',
                   'VA+ETM@', 'VA+ETN@', 'VA+EP@', 'VA+EF@', 'VA+EC@']:
            token = keyword
            origin_inflect = inflect_data[(token, tag[:-1])]
            first_token = origin_inflect.split('+')[0].split('/')[0]
            #print(origin_inflect)
            #keyword_lt.append((first_token, tag_lt[0]))  
            ###print('# 각 추출된 키워드: ', first_token)
            keyword_lt.append(first_token)
        
        else:
            ###print('# 각 추출된 키워드: ', keyword)
            keyword_lt.append(keyword)
    
    ###print()
    return keyword_lt


    


app = Flask("api_test")

@app.route('/keyword', methods=['GET', 'POST'])
def keyword_extractor():
    data = request.get_json(force=True, silent=True)
    query = data['Query']
    keyword_lt = B(query)

    return keyword_lt

if __name__ == '__main__':
    app.run('0.0.0.0', port=8887, debug=True)