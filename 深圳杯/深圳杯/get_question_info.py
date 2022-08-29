# -*- coding:utf-8 -*-
# @FileName  :get_question_info.py
# @Time      :2022-08-04 0:24
# @Author    :C_Orange
"""
功能：通过已经手动打开的chrom浏览器，手动加载数据，加载完成后进行数据获取并保存
    需要爬取的数据：问题标题(title_text), 问题url(question_url)
"""

# 导入第三方库
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# 初始化浏览器参数
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)


def get_looks(id_):
    # url = f'https://www.zhihu.com/question/301709847/answer{id_}'
    url = id_
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36',
    }
    res = requests.get(url=url, headers=header).text
    soup = BeautifulSoup(res, 'lxml')
    look_number = soup.find_all('strong')[1]
    return int(look_number['title'])


# 爬取相应数据并保存函数
def save_info(key_word, pages):
    title = []
    begin = 1
    end = pages
    # 开始爬取[关键词]的问题
    for i in range(begin, end):
        try:
            type_ = driver.find_element(By.XPATH,
                                        f'//*[@id="SearchMain"]/div/div/div/div/div[{i}]/div/div/div').get_attribute('itemprop')
            print(str(i) + ': ')
            if type_ == 'answer':
                try:
                    # 问题url
                    url_location = f'//*[@id="SearchMain"]/div/div/div/div/div[{i}]/div/div/div/h2/div/a'
                    question_url = driver.find_element(By.XPATH, url_location).get_attribute('href').split('/answer')[0]
                    looks = get_looks(question_url)
                    print(looks)

                    if looks >= 100000:
                        # 问题标题
                        title_location = f'//*[@id="SearchMain"]/div/div/div/div/div[{i}]/div/div/div/h2/div/a/span'
                        title_text = driver.find_element(By.XPATH, title_location).text
                        # title.append(title_text)
                        print(title_text, end='; ')

                        # 保存《问题》到txt文件
                        f = open(f'./网址/{key_word}/zhihu_title.txt', 'a', encoding='utf-8')
                        f.write(title_text + '\n')
                        f.close()

                        # 保存《url》到txt文件
                        print(question_url)
                        f2 = open(f'./网址/{key_word}/zhihu_url.txt', 'a', encoding='utf-8')
                        f2.write(question_url + '\n')
                        f2.close()

                        # 向下滑动页面
                        l = 150
                        driver.execute_script('window.scrollBy(0,' + str(l) + ')')
                    else:
                        continue
                except:
                    continue
            else:
                continue
        except:
            continue
    begin += 20
    end += 20

    return title


# key_ords = ['女权', '追星']  # 关键字
key_ords = ['单身主义', '丁克', '双减政策']
for key in key_ords:
    input("页面加载完请按任意键：")
    title_list = save_info(key, 200)
    for i in title_list:
        print(i)
