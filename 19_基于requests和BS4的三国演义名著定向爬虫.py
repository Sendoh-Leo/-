"""
FileName: 19_基于requests和BS4的三国演义名著定向爬虫
Date: 12 11
Author: lvah
Connect: 976131979@qq.com
Description:
    1. 根据网址http://www.shicimingju.com/book/sanguoyanyi.html获取三国演义主页的章节信息.
    2. 分析章节信息的特点， 提取章节的详情页链接和章节的名称。
    <div class="book-mulu"><ul><li>，li的详情信息如下:
    <li><a href="/book/sanguoyanyi/1.html">第一回·宴桃园豪杰三结义  斩黄巾英雄首立功</a></li>
    3. 根据章节的详情页链接访问章节内容
    <div class="chapter_content">
    4. 提取到的章节内容包含特殊的标签, eg: <br/> ==> '\n'  <p>, </p> => ''
    5. 将章节信息存储到文件中
"""

import csv
import os
import re

import requests
from colorama import Fore
from fake_useragent import UserAgent
from lxml import etree
from requests import HTTPError
from bs4 import  BeautifulSoup


def download_page(url, parmas=None):
    """
    根据url地址下载html页面
    :param url:
    :param parmas:
    :return: str
    """
    try:
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random,
        }
        # 请求https协议的时候， 回遇到报错: SSLError
        # verify=Flase不验证证书
        response = requests.get(url, params=parmas, headers=headers)
    except  HTTPError as e:
        print(Fore.RED + '[-] 爬取网站%s失败: %s' % (url, str(e)))
        return None
    else:
        # content返回的是bytes类型, text返回字符串类型
        return response.text


def parse_html(html):
    # 实例化BeautifulSoup对象， 并通过指定的解析器(4种)解析html字符串的内容
    soup = BeautifulSoup(html, 'lxml')
    # 根据bs4的选择器获取章节的详情页链接和章节的名称
    book = soup.find('div', class_='book-mulu') # 获取该书籍对象
    chapters = book.find_all('li')              # 获取该数据的所有章节对应的li标签， 返回的是列表
    # 依次遍历每一个章节的内容
    for chapter in chapters:
        detail_url  = chapter.a['href']
        chapter_name = chapter.a.string
        yield  {
            'detail_url': detail_url,
            'chapter_name': chapter_name
        }


def parse_detail_html(html):
    # 实例化BeautifulSoup对象， 并通过指定的解析器(4种)解析html字符串的内容
    soup = BeautifulSoup(html, 'lxml')
    # 根据章节的详情页链接访问章节内容, string只拿出当前标签的文本信息， get_text返回当前标签和子孙标签的所有文本信息
    #     <div class="chapter_content">
    chapter_content = soup.find('div', class_='chapter_content').get_text()
    return  chapter_content.replace(' ', '')



def get_one_page():
    base_url = 'http://www.shicimingju.com'
    url = 'http://www.shicimingju.com/book/sanguoyanyi.html'
    dirname = "三国演义"
    if not os.path.exists(dirname):
        os.mkdir(dirname)
        print(Fore.GREEN + "创建书籍目录%s成功" %(dirname))

    html = download_page(url)
    items = parse_html(html)
    for item in items:
        # 访问详情页链接
        detail_url = base_url + item['detail_url']
        # 生成文件存储的路径: 三国演义/第一回.xxxxx.txt
        chapter_name = os.path.join(dirname, item['chapter_name'] + '.txt')
        chapter_html = download_page(detail_url)
        chapter_content = parse_detail_html(chapter_html)

        # 写入文件
        with open(chapter_name, 'w', encoding='utf-8') as f:
            f.write(chapter_content)
            print(Fore.GREEN + "写入文件%s成功" %(chapter_name))


if __name__ == '__main__':
    get_one_page()

