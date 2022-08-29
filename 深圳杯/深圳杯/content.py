# -*- coding:utf-8 -*-
# @FileName  :content.py
# @Time      :2022-08-04 11:49
# @Author    :C_Orange

import time

import pymysql
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)


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


# chrome.exe --remote-debugging-port=9222 --user-data-dir="D:\selenum\AutomationProfile"
# 爬取某问题下的所有答案, 返回Return列表， 内容：b, create_time, likes, comments, answer
def get_answers(url, start, end, key_word, title):
    # 初始化
    driver.get(url)

    time.sleep(1)
    b = driver.find_elements(By.CLASS_NAME, 'NumberBoard-itemValue')[1].text
    b = int(b.replace(',', ''))
    print('被浏览数：' + str(b))

    number_text = driver.find_element(By.XPATH, '//*[@id="QuestionAnswers-answers"]/div/div/div/div[1]/h4/span').text[
                  : -4]
    number_text = int(number_text.replace(',', ''))
    print("总回答数：" + str(number_text))

    if b > 100000:
        # 滚动至元素ele可见位置
        if end == 0:
            end = number_text
        if start == 0:
            start = 0
        click_count = end - start // 5
        if click_count == 0:
            pass
        else:
            for count_ in range(click_count):
                time.sleep(1.5)
                length = len(
                    driver.find_elements(By.XPATH, '//*[@id="QuestionAnswers-answers"]/div/div/div/div[2]/div/div'))
                ele = driver.find_element(By.XPATH,
                                          f'//*[@id="QuestionAnswers-answers"]/div/div/div/div[2]/div/div[{length}]')
                driver.execute_script("arguments[0].scrollIntoView();", ele)
                if count_ == 0:
                    driver.execute_script('window.scrollBy(0,-100)')
                    time.sleep(0.5)
                try:
                    WebDriverWait(driver, 0.1).until(EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="root"]/div/main/div/div/div[3]/div[1]/div/div[2]/a/button')))
                    break
                except:
                    pass
                wait_xpath = f'//*[@id="QuestionAnswers-answers"]/div/div/div/div[2]/div/div[{length + 5}]'
                WebDriverWait(driver, 360 * 3).until(EC.presence_of_element_located((By.XPATH, wait_xpath)))
        run(start, end, b, key_word, title)
        return ''


def run(start, end, b, key_word, title):
    # input("完成后请按'enter'键")
    try:
        interval = 0  # 间距
        data = []
        # 被浏览数, 并保存到sql
        for k in range(start, end):
            h_data = []
            k += 1
            try:
                #  回答赞同数
                likes = int(driver.find_element(By.XPATH,
                                                f'//*[@id="QuestionAnswers-answers"]/div/div/div/div[2]/div/div[{k}]/div/div/div[1]/div[3]/span/span/button').text[
                            :-8].replace(',', ''))
            except:
                likes = 0
            h_data.append(likes)
            print(str(likes), end='; ')

            # 回答时间
            # 发布于：//*[@id="QuestionAnswers-answers"]/div/div/div/div[2]/div/div[176]/div/div/div[2]/div[1]/div[1]/a/span
            # 编辑于：//*[@id="QuestionAnswers-answers"]/div/div/div/div[2]/div/div[176]/div/div/div[5]/div[1]/div/a/span
            try:
                create_time = driver.find_element(By.XPATH,
                                                  f'//*[@id="QuestionAnswers-answers"]/div/div/div/div[2]/div/div[{k}]/div/div/div[2]/div[1]/div[1]/a/span').text[
                              4:14]
            except:
                create_time = driver.find_element(By.XPATH,
                                                  f'//*[@id="QuestionAnswers-answers"]/div/div/div/div[2]/div/div[{k}]/div/div/div[5]/div[1]/div/a/span').text[
                              4:14]
            h_data.append(create_time)
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
            h_data.append(comments)
            print(comments, end='; ')

            # 回答内容
            xpath = f'//*[@id="QuestionAnswers-answers"]/div/div/div/div[2]/div/div[{k}]/div/div/div[2]/span[1]/div/span'
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
            answer = element.text[:100]
            h_data.append(answer)
            print(answer[:3])

            data.append(h_data)
            # 下面的文件位置需要自己改，保存到你想要的位置
            # 保存回答内容到sql

            print('answer ' + str(k) + ' collected!')
            if k % 15 == 0:
                # 向下滑动页面
                # js = "window.scrollTo(0,document.body.scrollHeight)"
                driver.execute_script('window.scrollBy(0,500)')
                # driver.execute_script(js)

                # 向 zhihu_data表 插入数据
            cursor.execute(
                'insert into zhihu_data values(%s, %s, %s, %s, %s, %s, %s);',
                (key_word, title, b, create_time, likes, comments, answer))
            connect.commit()
            time.sleep(3)
        time.sleep(3)
        driver.refresh()
        time.sleep(1)
    except Exception as e:
        print(e)

    else:
        return ''


if __name__ == "__main__":
    key_wprds = ['女权', '追星', '偶像崇拜']  # '女权', '追星', '偶像崇拜'
    connect, cursor = con_sql('zhihu')

    for key_wprd_index in range(len(key_wprds)):
        print("------------" * 10)
        print(str(key_wprd_index + 1) + ':' + key_wprds[key_wprd_index])
        f_titles = open(f'./网址/{key_wprds[key_wprd_index]}/zhihu_title.txt', 'r', encoding='utf-8')
        title_list = f_titles.readlines()
        print("总条目数：" + str(len(title_list)))
        f_titles.close()

        f_urls = open(f'./网址/{key_wprds[key_wprd_index]}/zhihu_url.txt', 'r', encoding='utf-8')
        urls = f_urls.readlines()
        f_urls.close()

        for index in range(len(urls)):
            content = get_answers(url=urls[index], start=95, end=0, key_word=key_wprds[key_wprd_index],
                                  title=title_list[index])
