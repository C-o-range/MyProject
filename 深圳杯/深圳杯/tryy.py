# -*- coding:utf-8 -*-
# @FileName  :tryy.py
# @Time      :2022-08-02 16:58
# @Author    :C_Orange

# 引入必要的库
import os.path

import pymysql
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import urllib.parse

option = EdgeOptions()
option.add_experimental_option('excludeSwitches', ['enable-automation'])
option.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Edge(options=option)
driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
    'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
})


def con_sql(db):
    try:
        # 链接数据库
        connect = pymysql.connect(host='127.0.0.1', port=3306, user='root', charset='utf8')
        cursor = connect.cursor()
        print('连接成功')
        # 切换数据库
        cursor.execute(f'use {db};')
        return connect, cursor
    except Exception as e:
        print(e)


# 得到登录的cookie
def login_cookie():
    pa = 'D:/爬虫/cookies/zhihu_cookies.txt'
    if os.path.exists(pa):
        return True
    else:
        # driver = get_driver()
        driver.set_page_load_timeout(20)
        driver.set_script_timeout(20)
        LOGIN_URL = 'https://www.zhihu.com/'
        driver.get(LOGIN_URL)
        time.sleep(4)
        input("请登录后按 Enter")
        cookies = driver.get_cookies()
        json_cookies = json.dumps(cookies)
        # 下面的文件位置需要自己改
        with open(pa, 'w') as f:
            f.write(json_cookies)
            f.close()
        driver.quit()


# 再次登录
def login():
    driver.set_page_load_timeout(20)
    driver.set_script_timeout(20)
    LOGIN_URL = 'https://www.zhihu.com/'
    driver.get(LOGIN_URL)
    time.sleep(5)
    # 下面的文件位置需要自己改，与上面的改动一致
    f = open('D:/爬虫/cookies/zhihu_cookies.txt', 'r')
    cookies = f.read()
    f.close()
    json_cookies = json.loads(cookies)
    for co in json_cookies:
        driver.add_cookie(co)
    driver.refresh()
    time.sleep(3)


# 爬取问题标题及问题url，返回title列表，中是(问题标题)
# 有问题!!!!!!!!!!!!
def get_questions(key_word, pages):  # pages是多少个问题
    # 转到《关键词》网址
    question_u = f'https://www.zhihu.com/search?type=content&q={key_word}'
    driver.get(question_u)
    # time.sleep(3)
    begin = 1
    end = pages
    # 休眠，以用来手动滑动页面，直到页面出现足够(pages)的问题
    WebDriverWait(driver, 1000).until(EC.presence_of_element_located((By.XPATH,
                                                                      '//*[@id="SearchMain"]/div/div/div/div/div[11]/div/div/div/h2/div/a/span')))
    title = []
    while pages:
        # 开始爬取《关键词》问题
        for i in range(begin, end):
            try:
                type_ = driver.find_element(By.XPATH,
                                            f'//*[@id="SearchMain"]/div/div/div/div/div[{i}]/div/div/div').get_attribute(
                    'itemprop')
                print(str(i) + ': ')
                if type_ == 'answer':
                    try:
                        pages -= 1
                        # 问题标题
                        title_location = f'//*[@id="SearchMain"]/div/div/div/div/div[{i}]/div/div/div/h2/div/a/span'
                        title_text = driver.find_element(By.XPATH, title_location).text
                        title.append(title_text)
                        print(title_text, end='; ')

                        # 保存《问题》到sql
                        f = open(f'./网址/{key_word}/zhihu_title.txt', 'a', encoding='utf-8')
                        f.write(title_text + ',')
                        f.close()

                        # 问题url
                        url_location = f'//*[@id="SearchMain"]/div/div/div/div/div[{i}]/div/div/div/h2/div/a'
                        question_url = \
                            driver.find_element(By.XPATH, url_location).get_attribute('href').split('/answer')[0]
                        print(question_url)

                        # 保存《url》到txt文件
                        f2 = open(f'./网址/{key_word}/zhihu_url.txt', 'a', encoding='utf-8')
                        f2.write(question_url + '\n')
                        f2.close()
                        # 向下滑动页面
                        l = 150
                        driver.execute_script('window.scrollBy(0,' + str(l) + ')')
                        time.sleep(1)
                    except:
                        continue
                else:
                    continue
            except:
                continue
        begin += 20
        end += 20
        time.sleep(2)
    return title


# 爬取某问题下的所有答案, 返回Return列表， 内容：b, create_time, likes, comments, answer
def get_answers(start, question_url, key_word, title):
    # 初始化
    driver.get(question_url)

    time.sleep(1)
    number_text = driver.find_element(By.XPATH, '//*[@id="QuestionAnswers-answers"]/div/div/div/div[1]/h4/span').text[
                  : -4]
    number_text = int(number_text.replace(',', ''))

    print("总回答数：" + str(number_text))
    b = driver.find_elements(By.CLASS_NAME, 'NumberBoard-itemValue')[1].text

    b = int(b.replace(',', ''))
    create_time = ''
    likes = 0
    comments = 0
    answer = ''

    if b > 100000:
        WebDriverWait(driver, 1000).until(EC.presence_of_element_located((By.XPATH,
                                                                          f'//*[@id="QuestionAnswers-answers"]/div/div/div/div[2]/div/div[{start}]/div/div/div[2]/span[1]/div/span')))
        try:
            # 被浏览数, 并保存到sql
            print('被浏览数：' + str(b))
            for k in range(start, number_text):
                # for k in range(25):
                k += 1
                try:
                    # driver.find_element(By.XPATH,
                    #                               f'//*[@id="QuestionAnswers-answers"]/div/div/div/div[2]/div/div[{k}]/div/div/div[1]/div[3]/span/span/button')
                    WebDriverWait(driver, 1000).until(EC.presence_of_element_located((By.XPATH,
                                                                                      f'//*[@id="QuestionAnswers-answers"]/div/div/div/div[2]/div/div[{start}]/div/div/div[2]/div[1]/div[1]/a/span')))
                    # 回答赞同数
                    likes = int(driver.find_element(By.XPATH,
                                                    f'//*[@id="QuestionAnswers-answers"]/div/div/div/div[2]/div/div[{k}]/div/div/div[1]/div[3]/span/span/button').text[
                                :-8].replace(',', ''))
                except:
                    likes = 0
                print(str(likes), end='; ')

                # 回答时间
                create_time = driver.find_element(By.XPATH,
                                                  f'//*[@id="QuestionAnswers-answers"]/div/div/div/div[2]/div/div[{k}]/div/div/div[2]/div[1]/div[1]/a/span').text[
                              4:14]
                print(create_time, end='; ')

                # 回答评论数
                comments = driver.find_element(By.XPATH,
                                               f'//*[@id="QuestionAnswers-answers"]/div/div/div/div[2]/div/div[{k}]/div/div/div[2]/div[2]/button[1]').text
                if len(comments) > 8:
                    comments = int(comments[:-4].replace(',', ''))

                elif len(comments) > 4:
                    comments = int(comments[:-4])
                else:
                    comments = 0
                print(comments, end='; ')

                # 回答内容
                xpath = f'//*[@id="QuestionAnswers-answers"]/div/div/div/div[2]/div/div[{k}]/div/div/div[2]/span[1]/div/span'
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
                answer = element.text[:100]
                print(answer[:3])

                # 下面的文件位置需要自己改，保存到你想要的位置
                # 保存回答内容到sql

                # file = open('D:/爬虫/回答/answer{}.txt'.format(k + 1), 'w', encoding='utf-8')
                # file.write(answer)
                # file.close()
                print('answer ' + str(k) + ' collected!')
                if k % 10 == 0:
                    # 向下滑动页面
                    js = "window.scrollTo(0,document.body.scrollHeight)"
                    driver.execute_script(js)
                time.sleep(1)

                # print(key_word, title, str(b), create_time, str(likes), str(comments), answer)
                # 向 zhihu_data表 插入数据
                cursor.execute(
                    'insert into zhihu_data values(%s, %s, %s, %s, %s, %s, %s);',
                    (key_word, title, b, create_time, likes, comments, answer))
                connect.commit()
        except Exception as e:
            print(e)
    else:
        return ''

    # return Return  # b, create_time, likes, comments, answer


if __name__ == "__main__":
    # 设置你想要搜索的问题
    key_wprds = ['女权', '追星', '偶像崇拜']
    connect, cursor = con_sql('zhihu')

    for key_wprd_index in range(len(key_wprds)):
        print("------------" * 10)
        print(str(key_wprd_index + 1) + ':' + key_wprds[key_wprd_index])

        login_cookie()
        # driver = get_driver()
        login()
        # # 需要自己修改需要爬取的问题个数，只爬取id="QuestionAnswers-answers的问题
        key = key_wprds[key_wprd_index]
        key_encode = urllib.parse.quote(key)
        # title_list = get_questions(key_encode, 150)

        f_titles = open(f'./网址/{key_wprds[key_wprd_index]}/zhihu_title.txt', 'r', encoding='utf-8')
        title_list = f_titles.readlines()
        print("总条目数：" + str(len(title_list)))
        f_titles.close()

        f_urls = open(f'./网址/{key_wprds[key_wprd_index]}/zhihu_url.txt', 'r', encoding='utf-8')
        urls = f_urls.readlines()
        f_urls.close()

        for index in range(len(urls)):
            content = get_answers(start=134, question_url=urls[index], key_word=key_wprds[key_wprd_index], title=title_list[index])

    driver.quit()
