# -*- coding:utf-8 -*-
# @FileName  :most_count_comments.py
# @Time      :2022-08-16 17:28
# @Author    :C_Orange
"""
功能：使用requests爬取相关关键词的excel表中问题下的回答中评论数最多的相关评论的时间，评论内容以及点赞数，并上传数据库存储

"""


# 导入第三方库
import time

import pymysql
import requests
from bs4 import BeautifulSoup


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


# 解析回答时间
def c_time(item):
    # 回答时间
    try:
        time_num = item['created_time']
        tup_time = time.localtime(time_num)
        create_time = time.strftime("%Y-%m-%d", tup_time)
    except:
        create_time = ''
    print(create_time, end=', ')
    return create_time


# 解析点赞数
def Likes(item):
    # 点赞数
    try:
        likes = item['like_count']
    except:
        likes = 0
    print(likes, end=', ')
    return likes


# 解析评论内容
def contents(datas):
    # 回答内容
    try:
        content = datas['content']
        soup = BeautifulSoup(content, 'lxml')
        content = soup.get_text()
    except:
        content = ''
    print(content[:5])
    return content


# 获取评论的id，以获取评论下的评论
def get_id(data_):
    id_ = data_['id']
    return id_


def se_data(second_url_):
    return requests.get(second_url_, headers=headers).json()


# 两个关键词的对应excel表中问题回答下评论数最多的第一条评论id
# 通过链式链接逐级爬取
key_url = ['1307342893', '2301336357']
for i in range(len(key_url)):
    key = ['zhihu_insert_nvquan', 'zhihu_insert_zhuixing']
    url = f'https://www.zhihu.com/api/v4/comment_v5/answers/{key_url[i]}/root_comment?'  # 第一级评论
    connect, cursor = con_sql('zhihu')

    flag1 = True
    while flag1:
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        }

        data = requests.get(url, headers=headers).json()

        # 解析数据
        for item_ in data['data']:
            # 第一级回答的数据
            # 回答时间
            created_time = c_time(item_)
            # 回答点赞数
            like = Likes(item_)
            # 回答内容
            comment = contents(item_)

            try:
                table = key[i]
                # 向 zhihu_insert表 插入数据
                cursor.execute(
                    f'insert into {table} values(%s, %s, %s);',
                    (created_time, like, comment))
                connect.commit()
            except Exception as e:
                print(e)
                pass

            user_id = get_id(item_)
            # 第二级回答内容
            second_url = f'https://www.zhihu.com/api/v4/comment_v5/comment/{user_id}/child_comment?'
            flag2 = True
            while flag2:
                second_data = se_data(second_url)
                for second_item in second_data['data']:
                    # 回答时间
                    s_created_time = c_time(second_item)
                    # 回答点赞数
                    s_like = Likes(second_item)
                    # 回答内容
                    s_comment = contents(second_item)

                    try:
                        table = key[i]
                        # 向 zhihu_insert表 插入数据
                        cursor.execute(
                            f'insert into {table} values(%s, %s, %s);',
                            (s_created_time, s_like, s_comment))
                        connect.commit()
                    except Exception as e:
                        print(e)
                        pass
                    time.sleep(0.2)

                # 判断循环结束条件
                if second_data['paging']['is_end'] is not True:
                    second_url = second_data['paging']['next']
                else:
                    flag2 = False

                time.sleep(0.5)

        if data['paging']['is_end'] is not True:
            url = data['paging']['next']
        else:
            flag1 = False
    time.sleep(1.5)

print('抓取完成！！！！！！！！！！！！！')
