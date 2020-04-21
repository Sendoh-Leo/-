"""
FileName: 10_基于requests和正则的猫眼电影TOP100定向爬虫
Date: 11 11
Author: lvah
Connect: 976131979@qq.com
Description:

"""
import csv

import requests
from colorama import Fore
from fake_useragent import UserAgent
from lxml import etree
from requests import HTTPError


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
    """
    编程语言的去年名次、今年名次、编程语言名称、评级Rating和变化率Change等信息。
    :param html:
    :return:
    """
    # 1). 通过lxml解析器解析页面信息， 返回Element对象
    html = etree.HTML(html)
    # 2). 根据Xpath路径寻找语法获取编程语言相关信息
    # 获取每一个编程语言的Element对象
    # <table id="top20" class="table table-striped table-top20">
    languages = html.xpath('//table[@id="top20"]/tbody/tr')
    print('languages:',languages)
    # 依次获取每个语言的去年名次、今年名次、编程语言名称、评级Rating和变化率Change等信息。
    for language in languages:
        # 注意: Xpath里面进行索引时，从1开始
        print(language)
        now_rank = language.xpath('./td[1]/text()')[0]
        last_rank = language.xpath('./td[2]/text()')[0]
        name = language.xpath('./td[4]/text()')[0]
        rating = language.xpath('./td[5]/text()')[0]
        change = language.xpath('./td[6]/text()')[0]
        yield {
            'now_rank': now_rank,
            'last_rank': last_rank,
            'name': name,
            'rating': rating,
            'change': change
        }


def save_to_csv(data, filename):
    # 1). data是yield返回的字典对象
    # 2). 以追加的方式打开文件并写入
    # 3). 文件的编码格式是utf-8
    # 4). 默认csv文件写入会有空行， newline=''
    with open(filename, 'a', encoding='utf-8', newline='') as f:
        csv_writer = csv.DictWriter(f, ['now_rank', 'last_rank', 'name', 'rating', 'change'])
        # 写入csv文件的表头
        # csv_writer.writeheader()
        csv_writer.writerow(data)


def get_one_page(page=1):
    url = 'https://www.tiobe.com/tiobe-index/'
    filename = 'tiobe.csv'
    html = download_page(url)
    items = parse_html(html)
    for item in items:
        save_to_csv(item, filename)
    print(Fore.GREEN + '[+] 写入文件%s成功' %(filename))


if __name__ == '__main__':
    get_one_page()
