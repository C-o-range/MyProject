# -*- coding:utf-8 -*-
# @FileName  :answers.py
# @Time      :2022-08-05 23:35
# @Author    :C_Orange
"""
功能：根据get_question_info.py得到的txt文件，爬取关键词相关问题的回答时间，点赞数，评论数，内容，并上传数据库

"""

# 导入第三方库
import random
import time

import requests
import pymysql
from bs4 import BeautifulSoup


# 随机选择浏览器伪装头
def get_headers():
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) Gecko/20100101 Firefox/61.0",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
        "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",
        ]
    headers = {'User-Agent': random.choice(user_agent_list)}
    return headers


# 连接数据库
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


# 获取页面数据
def get_page(url):
    headers = get_headers()
    return requests.get(url=url, headers=headers).json()


# 问题浏览量
def question_look(url):  # txt文件中的url
    headers = get_headers()
    res = requests.get(url, headers=headers).text
    time.sleep(1)
    soup = BeautifulSoup(res, 'lxml')
    look_number = soup.find_all('strong')[1]
    return look_number['title']


# 得到关键词相关问题的回答时间，点赞数，评论数，内容
def get_info(key_word, title, b, url, table=None):
    res = get_page(url)
    for data in res['data']:
        global total_index
        total_index += 1
        print("关键词总索引: ", total_index, end='; ')
        global content_index
        content_index += 1
        time.sleep(0.7)
        # 回答时间
        try:
            time_num = data['target']['updated_time']
            tup_time = time.localtime(time_num)
            create_time = time.strftime("%Y-%m-%d", tup_time)
        except:
            create_time = ''
        print(create_time, end='; ')

        print("问题索引: ", content_index, end=' ---- ')
        if content_index > 650:
            return False

        # 回答点赞数
        likes = str(data['target']['voteup_count'])
        print("点赞数: ", likes, end='; ')
        if int(likes) == 0:
            print("点赞数: ", likes)
            continue

        # 回答评论数
        comments = str(data['target']['comment_count'])
        print("评论数: ", comments, end='; ')
        if int(comments) == 0:
            print("评论数: ", comments)
            continue

        # 回答内容
        try:
            content = data['target']['content']
            soup = BeautifulSoup(content, 'lxml')
            content = soup.get_text()
        except:
            content = ''
        print(content[:5], end='; ')

        try:
            # 向 zhihu_data表 插入数据
            cursor.execute(
                f'insert into {table} values(%s, %s, %s, %s, %s, %s, %s);',
                (key_word, title, b, create_time, likes, comments, content))
            connect.commit()
            global index_for
            index_for += 1
            print(" 有效数:", index_for)
            time.sleep(0.1)
        except:
            continue

    if not res['paging']['is_end']:
        next_url = res['paging']['next']
        return next_url
    else:
        return False


if __name__ == '__main__':
    key_words = ['女权', '追星', '单身主义', '丁克', '双减政策']
    table_list = ['zhihu_data_nvquan', 'zhihu_data_zhuixing', 'zhihu_data_danshen', 'zhihu_data_dingke', 'zhihu_data_shuangjian']
    connect, cursor = con_sql('zhihu')
    for key_word_index in range(len(key_words)):
        print("----------" * 10)
        print(key_words[key_word_index] + '开始')

        with open(f'./网址/{key_words[key_word_index]}/zhihu_title.txt', 'r', encoding='utf-8') as f1:
            title_list = f1.readlines()
            f1.close()
        print("总条目数：" + str(len(title_list)))
        with open(f'./网址/{key_words[key_word_index]}/zhihu_url.txt', 'r', encoding='utf-8') as f2:
            url_list = f2.readlines()
            f2.close()

        table = table_list[key_word_index]
        total_index = 0
        for index in range(len(title_list)):
            index_for = 0
            print("标题：" + title_list[index].strip())
            # 问题浏览量
            looks = question_look(url_list[index].strip())
            print(f"总浏览量：{looks}")
            sets = 'include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cattachment%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Cis_labeled%2Cpaid_info%2Cpaid_info_content%2Creaction_instruction%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_recognized%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cvip_info%2Cbadge%5B%2A%5D.topics%3Bdata%5B%2A%5D.settings.table_of_content.enabled&limit=5&offset=0&order=default&platform=desktop'
            n_url = 'https://www.zhihu.com/api/v4/questions/' + url_list[index].split('question/')[
                1].strip() + '/feeds?' + sets

            if int(looks) >= 100000:
                new_url = n_url
                content_index = 0
                while new_url:
                    time.sleep(2.4)
                    try:
                        new_url = get_info(key_words[key_word_index], title_list[index], looks, new_url, table=table)
                    except:
                        continue

    print('爬取完成。')
