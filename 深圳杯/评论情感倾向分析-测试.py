import time
import json

import pandas as pd
import requests


def load_data(filepath):
    data_list = pd.read_excel(io=filepath, header=None, usecols='G', skiprows=1).values
    # print(data_list)
    return data_list


class Analyse:
    def my_token(self):
        # 获取ak, sk
        ak = 'b7wjlNnMSAOoKozykuDyylBF'
        sk = "PFLtyaAB7jkUNr1M6BvyND92QZmK2XmX"

        # client_id 为官网获取的AK， client_secret 为官网获取的SK
        source_url = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={ak}&client_secret={sk}'
        response = requests.get(source_url)
        return response.json()["access_token"]

    def text_analyse(self, sentence):
        # 发送post请求，分析文本倾向
        # header
        my_header = {
            "Content-Type": "application/json",
        }

        # post url
        url = "https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify?charset=UTF-8&access_token="
        my_url = url + self.my_token()
        # print(my_url)

        res = requests.post(url=my_url, headers=my_header, data=sentence)
        return res.json()


if __name__ == '__main__':
    file = r'./zhihu_data_zhuixing.xlsx'
    txt_list = load_data(file)
    data_list = []
    for i in range(len(txt_list)):
        if i % 10 == 0:
        	time.sleep(2)
        # print(txt_list[i][0])
        txt = json.dumps({
            "text": txt_list[i][0]
        })

        analyse = Analyse()
        attitude = analyse.text_analyse(txt)
        # for item in attitude:
            # print(item, ': ', attitude[item])
            
        confidence = attitude['items'][0]['confidence']
        negative_prob = attitude['items'][0]['negative_prob']
        positive_prob = attitude['items'][0]['positive_prob']
        print(attitude)
        # print('confidence=', confidence)
        # print('negative_prob=', negative_prob)
        # print('positive_prob=', positive_prob)
        
        data_list.append([confidence, negative_prob, positive_prob])
        print(f'第{i + 1}条')
    df = pd.DataFrame(data=data_list, columns=['confidence', 'negative_prob', 'positive_prob'])
    df.to_csv('情感分类.csv', index=False)

