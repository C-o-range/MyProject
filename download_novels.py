from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from lxml import html

li = []


class Novel(object):
    def __init__(self):
        self.url = 'http://www.waptxt.com/99222/30306225.html'  # 需要抓取的路径
        self.driver = webdriver.Edge()  # Edge浏览器驱动

    def click(self):  # 获取到地址
        self.driver.get(self.url)
        return self.driver.current_url  # 返回当前页面的地址

    def search(self):
        response = requests.get(url=Novel.click(self)).content  # 利用requests获取页面内容
        etree = html.etree
        data = etree.HTML(response)  # 转换为html格式
        elements_br = self.driver.find_elements(By.TAG_NAME, 'br')  # 确定循环次数，用于确定一共有多少行
        count = len(elements_br)
        print("开始程序！")

        for i in range(1, count // 2):
            title = data.xpath('/html/body/div[2]/text()[2]')  # 定位小说每一章的标题所在位置
            title = str(title)[5:-2]  # 需要自行确定标题的位置
            if ' ' not in title:
                item = title[:5] + ' ' + title[5:]  # 在”章“和 标题之间加一个空格，以便阅读器能够识别章节
            else:
                item = title
            contents = data.xpath('//*[@id="content"]/div[2]/text()[{}]'.format(i))  # 获取具体内容
            if item not in li:
                if len(li) != 0:
                    with open(r'C:\\Users\asus\Desktop\日常\小说\直播修仙.txt', 'a+', encoding='utf-8') as f:
                        f.write('---------------\n')
                li.append(item)
                with open(r'C:\\Users\asus\Desktop\日常\小说\直播修仙.txt', 'a+', encoding='utf-8') as f:
                    f.write(item + '\n')
                print(item)
            with open(r'C:\\Users\asus\Desktop\日常\小说\直播修仙.txt', 'a+', encoding='utf-8') as f:
                f.write(''.join(contents)[4:] + '\n')

    def next_click(self):  # 点击下一章
        search_btn = self.driver.find_element(By.XPATH, '//*[@id="xiazhang"]')
        search_btn.click()  # 点击
        return self.driver.current_url

    def next_search(self):  # 同于search功能
        response = requests.get(url=Novel.next_click(self)).content
        etree = html.etree
        data = etree.HTML(response)
        elements_br = self.driver.find_elements(By.TAG_NAME, 'br')
        count = len(elements_br)

        for i in range(1, count // 2):
            title = data.xpath('/html/body/div[2]/text()[2]')
            title = str(title)[5:-2]
            if ' ' not in title:
                item = title[:5] + ' ' + title[5:]
            else:
                item = title
            contents = data.xpath('//*[@id="content"]/div[2]/text()[{}]'.format(i))
            if item not in li:
                if len(li) != 0:
                    with open(r'C:\\Users\asus\Desktop\日常\小说\直播修仙.txt', 'a+', encoding='utf-8') as f:
                        f.write('---------------\n')
                li.append(item)
                with open(r'C:\\Users\asus\Desktop\日常\小说\直播修仙.txt', 'a+', encoding='utf-8') as f:
                    f.write(item + '\n')
                print(item)
            with open(r'C:\\Users\asus\Desktop\日常\小说\直播修仙.txt', 'a+', encoding='utf-8') as f:
                f.write(''.join(contents)[4:] + '\n')

    def run(self):
        self.search()
        for i in range(1, 9999):
            self.next_search()
        print("程序结束！")


if __name__ == '__main__':
    spider = Novel()
    spider.run()
