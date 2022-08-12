#!/usr/bin/python3

import requests


def my_token():
    # 获取ak, sk
    ak = 'b7wjlNnMSAOoKozykuDyylBF'
    sk = "PFLtyaAB7jkUNr1M6BvyND92QZmK2XmX"

    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    source_url = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={}&client_secret={}'.format(ak, sk)
    response = requests.get(source_url)
    return response.json()["access_token"]


def text_analyse(sentence):
    # 发送post请求，分析文本倾向
    # header
    my_header = {
        "Content-Type": "application/json",
    }

    # post url 
    url = "https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify?access_token="
    my_url = url + my_token() + '&charset=UTF-8'
    print(my_url)
    
    res = requests.post(url=my_url, headers=my_header, data=sentence)
    return res.json()


txt = {
    "text": "我不支持女权"
}
attitude = text_analyse(txt)

print(attitude)
