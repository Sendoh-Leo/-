# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request

"""
spyder爬虫流程：
    1.确定起始的url---->start_url
    2.引擎将起始的URL交给调度器（存储到队列，去重）
    3.调度器将URL发送给Downloader, Downloader发起Request从网页上下载信息（response）
    4.将下载的页面交给spyder，进行解析（parse函数）,yield 数据（item）
    5.将返回的数据（item）发送给pipeline进行存储   使用命令行存储成csv或者json格式  scrapy crawl book -o book.csv/json
"""
class BookSpider(scrapy.Spider):
    name = 'book'
    base_url = 'http://shicimingju.com'
    #限制域名为xicimingju.com
    allowed_domains = ['shicimingju.com']
    #其实的域名可以有多个，有两种指定方法
    #1.列表放入多个url地址
    start_urls = ['http://shicimingju.com/book/sanguoyanyi.html',
                  'http://shicimingju.com/book/hongloumeng.html',
                  'http://shicimingju.com/book/xiyouji.html',
                  'http://shicimingju.com/book/shuihuzhuan.html',
                    ]



    def parse(self, response):
        #使用scrapy交互式环境scrapy shell url
        #通过yield返回解析数据的字典格式

        #1.获取所有章节的li标签
        chapters = response.xpath('//div[@class="book-mulu"]/ul/li')
        #2.遍历每一个li标签，提取每一个章节的名称和网址
        for chapter in chapters:
            # chapter.xpath('./a/@href')返回一个列表---> [<Selector xpath='./a/@href' data='/book/hongloumeng/1.html'>]
            detail_url = chapter.xpath('./a/@href').extract_first()
            #章节名称为a标签的文本信息----> [<Selector xpath='./a/text()' data='第 一 回 甄士隐梦幻识通灵 贾雨村风尘怀闺秀'>]
            name= chapter.xpath('./a/text()').extract_first()

            #将书籍名称作为元数据传入item，
            book_name = detail_url.split('/')[-2]
            #继续爬取详情页（detail_url）的内容,callback：返回给爬取详情页的解析函数
            #meta 作用：把当前的name属性传递给下一个解析器
            yield Request(self.base_url+detail_url,callback=self.parse_chapter_detail,meta={'name':name,'book_name':book_name})
            # yield {
            #     'detail_url':detail_url,
            #     'name':name
            # }

    def parse_chapter_detail(self,response):
        #1.xpath('string(.)获取该标签以及子孙标签的所有文本信息
        #2.如何将对象转换为字符串   extract_first/get()  将一个对象转换为字符串
        #                         extract/get_all()  转换列表中每一个对象为字符串
        content = response.xpath('//div[@class="chapter_content"]')[0].xpath('string(.)').get()
        #print('content:',content)
        yield  {
            'book_name':response.meta['book_name'],
            'name':response.meta['name'],
            'content':content
        }
