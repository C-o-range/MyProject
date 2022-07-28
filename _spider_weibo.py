import re
import datetime
import os.path
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import pandas as pd


class WeiBo:
    def __init__(self):  # 属性
        self.session = requests.Session()
        self.url = "https://m.weibo.cn/"
        self.driver = webdriver.Edge()
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Mobile Safari/537.36 Edg/103.0.1264.71',

        }
        self.url_list = []

    def get_keywords_hot_url(self, keywords):  # 使用selenium模拟用户操作根据keywords拿到搜索页并返回url
        self.driver.get(url=self.url)
        search_button = self.driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[1]/div[1]/a/aside/label/div')
        search_button.click()

        time.sleep(1)
        search = self.driver.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[1]/div[1]/div/div/div[2]/form/input')
        search.send_keys(keywords + '\n')

        time.sleep(3)
        keywords_hot_url = 'https://m.weibo.cn/api/container/getIndex?' + self.driver.current_url[
                                                                          26:] + '&page_type=searchall'
        # 当前：https://m.weibo.cn/search?containerid=100103type%3D1%26q%3D%E5%A5%B3%E6%9D%83&page_type=searchall
        # 目标：https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D1%26q%3D%E5%A5%B3%E6%9D%83&page_type=searchall
        # print(keywords_hot_url)
        self.driver.close()
        return keywords_hot_url

    def get_all_hot_wb_pages_url(self, keywords_hot_url):  # 获取热门-key页面的url
        all_hot_wb_pages_url = ''  # 热门-keywords的url
        res_content = self.session.get(url=keywords_hot_url, headers=self.headers).json()  # 热点
        # 获取热门-keywords的url
        for url in res_content['data']['cards'][1:9]:
            # print(url)
            if url['card_type'] == 11:
                # print(url)
                if url['card_group'][1]['card_type'] == 6 and url['card_group'][1]['desc'] == '更多热门微博':
                    all_hot_wb_pages_url = url['card_group'][1]['scheme']
                    # print('url = ' + url['card_group'][1]['scheme'])
                    break
        return all_hot_wb_pages_url

    def get_wb_info(self, wb_info_url):  # 获取每条微博的详情页url以获取评论
        info = []
        content = self.session.get(wb_info_url).json()
        page_detail_urls = content['data']['cards']

        for i in range(len(page_detail_urls)):
            detail = {'author': [], 'time': [], 'thumbs_up': [], 'transfor': [], 'text': [], 'url': []}
            # 获取当前微博作者、时间、内容、点赞数、转发数
            # 作者
            author = page_detail_urls[i]['mblog']['user']['screen_name']
            detail['author'].append(author)
            # 时间
            time_ = page_detail_urls[i]['mblog']['created_at']
            detail['time'].append(self.get_time(time_))
            # 点赞数
            thumbs_up = page_detail_urls[i]['mblog']['attitudes_count']
            detail['thumbs_up'].append(thumbs_up)
            # 转发数
            transfor = page_detail_urls[i]['mblog']['reposts_count']
            detail['transfor'].append(transfor)
            # 文章内容
            text = page_detail_urls[i]['mblog']['text']
            print(text)
            rc = re.compile(r'<[^>]+>', re.S)
            # for text in texts:
            #
            detail['text'].append(text)
            # 详情页地址
            # print('url = ' + detail_url['scheme'])
            url = page_detail_urls[i]['scheme']
            detail['url'].append(url)
            #
            # self.save_data(file_path='./weiBo.csv', dic_list=detail, mode='w')
            info.append(detail)
        return info

    # def get_wb_content(self, ):  # 获取当前微博时间、内容、点赞数、转发数
    #     # 返回地址：https://m.weibo.cn/status/LDXSki88O?mblogid=LDXSki88O&luicode=10000011&lfid=100103type%3D60%26q%3D%E5%A5%B3%E6%9D%83%26t%3D0
    #     content = self.session.get(wb_info_url).json()
    #     page_detail_urls = content['data']['cards']

    def get_time(self, Gmt_time):  # 获取发布时间
        """转换GMT时间为标准格式"""
        GMTformat = '%a %b %d %H:%M:%S +0800 %Y'
        time_array = datetime.datetime.strptime(Gmt_time, GMTformat)
        trans_time = time_array.strftime("%Y-%m-%d %H:%M:%S")
        return trans_time

    def get_comments(self):  # 获取当前微博评论数、评论详情
        pass

    def save_data(self, dic_list, file_path, mode, header):  # 持久化存储数据
        for dic in dic_list:  # [{}, {}, {} ]
            pf = pd.DataFrame(dic)
            # print(pf)
        # order = ['author', 'time', 'thumbs_up', 'tra-nsfor', 'text', 'url']
        # pf = pf[order]
            pf.to_csv(file_path, mode=mode, encoding='utf-8', index=False, header=header, index_label=False)


if __name__ == '__main__':  # 主函数，定义搜索关键字
    wb = WeiBo()
    keywordurl = wb.get_keywords_hot_url('女权')
    # search_pages = int(input('请输入爬取页数（2-20）:'))
    search_pages = 3
    file_path = './weiBo.csv'
    # 页面数据url
    header = ['author', 'time', 'thumbs_up', 'transfor', 'text', 'url']
    for index in range(1, search_pages):
        ll = 'https://m.weibo.cn/api/container/getIndex?' + wb.get_all_hot_wb_pages_url(keywordurl)[
                                                            27:] + f'&page={index}'
        dic = wb.get_wb_info(ll)  # 调用get_wb_info函数
        if os.path.exists(file_path):
            wb.save_data(dic_list=dic, file_path=file_path, mode='a', header=False)
        else:
            wb.save_data(dic_list=dic, file_path=file_path, mode='a', header=header)
