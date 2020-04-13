#coding:utf-8
#date:2020/4/1216:07
#author:CQ_Liu
import codecs
import json
import re
import time


from lxml import  etree

import requests
from colorama import Fore
from fake_useragent import UserAgent
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
            'Host': 'maoyan.com',
            'Origin': 'https://maoyan.com',
            'Cookie': '__mta=216365737.1586537270106.1586587968494.1586587974745.28; uuid_n_v=v1; uuid=FDFCF0307B4A11EA81A9FDE94F2697E46AE0BB693A874A189C91F0B6F3298114; Hm_lvt_703e94591e87be68cc8da0da7cbd0be2=1586537263,1586587448; mojo-uuid=290ecc97cc9252d9e67fddc2fdfba5ff; _lxsdk_cuid=17164fd7ca334-0cfe278836c8a7-4c302f7e-e1000-17164fd7cabc8; _lxsdk=FDFCF0307B4A11EA81A9FDE94F2697E46AE0BB693A874A189C91F0B6F3298114; __mta=216365737.1586537270106.1586575636717.1586587450776.15; _csrf=475c87b2782054e49dc109b59dc40641530b6b61ce9e007ba437dd7fc375b344; _lxsdk_s=17167f7d0b2-36e-60f-f57%7C%7C53; mojo-trace-id=46; mojo-session-id={"id":"fc93bad8aa704378a2e0ae28dfb31398","time":1586587226413}; Hm_lpvt_703e94591e87be68cc8da0da7cbd0be2=1586587975; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic'
        }
        # 请求https协议的时候， 回遇到报错: SSLError
        # verify=Flase不验证证书
        #requests.packages.urllib3.disable_warnings()
        response = requests.get(url, params=parmas, headers=headers)
    except  HTTPError as e:
        print(Fore.RED + '[-] 爬取网站%s失败: %s' % (url, str(e)))
        return None
    else:
        # content返回的是bytes类型, text返回字符串类型
        return response.text

def parse_html(html):
    """
    通过Xpath对html解析获取电影名称、时间、评分、图片等信息。
    :param html:
    :return:
    """

    global index,image,name,star,releasetime
    html = etree.HTML(html)

    movies = html.xpath('//dl[@class="board-wrapper"]/dd')
    print(movies)
    for movie in movies:
        index = movie.xpath('./i/text()')[0]
        #print(index)
        image = movie.xpath('./a/img[@class="board-img"]/@data-src')[0]
        print('image:',image)
        name = movie.xpath('./a/img[@class="board-img"]/@alt')[0]
        star = movie.xpath('.//p[@class="star"]/text()')[0]
        releasetime = movie.xpath('.//p[@class="releasetime"]/text()')[0]
        yield {
            'index':index,
            'image':image,
            'title':name,
            'star':star.strip().lstrip('主演：'),
            'releasetime':releasetime.lstrip('上映时间：')

        }

def save_to_json(data, filename):
    """将爬取的数据信息写入json文件中"""
    # 解决的问题:
    #       1. python数据类型如何存储到文件中? json将python数据类型序列化为json字符串
    #       2. json中中文不能存储如何解决?     ensure_ascii=False
    #       3. 存储到文件中的数据不是utf-8格式的，怎么解决?   ''.encode('utf-8')
    # with open(filename, 'ab')  as f:
    #     f.write(json.dumps(data, ensure_ascii=False,indent=4).encode('utf-8'))
    #     print(Fore.GREEN + '[+] 保存电影 %s 的信息成功' %(data['title']))

    with codecs.open(filename, 'a', 'utf-8') as f:
        #json.dumps将python字典型数据转化为json格式
        f.write(json.dumps(data, ensure_ascii=False, indent=4))
        print(Fore.GREEN + '[+] 保存电影 %s 的信息成功' % (data['title']))


def get_one_page(page=1):
    # url = 'https://maoyan.com/board/'   # 采集热映口碑榜， 只有一页。
    # 采集电影TOP100, 总共10页. url的规则: https://maoyan.com/board/4?offset=(page-1)*10
    url = 'https://maoyan.com/board/4?offset=%s' % ((page - 1) * 10)
    html = download_page(url)
    #print(html)
    items = parse_html(html)
    # item是字典
    for item in items:
        save_to_json(item, 'maoyan1.json')


if __name__ == '__main__':
    for page in range(1, 2):
        get_one_page(page)
        print(Fore.GREEN + '[+] 采集第[%s]页数据' % (page))
        # 反爬虫策略: 方式爬虫速度太快被限速， 在采集数据的过程中，休眠一段时间
        time.sleep(0.5)
