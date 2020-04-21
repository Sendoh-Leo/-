# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os


class ScrapyprojectPipeline(object):
    def process_item(self, item, spider):
        #写入文件的文件名为书籍的名称
        dirname = os.path.join('books',item['book_name'])
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        name = item['name']
        filename = os.path.join(dirname,name)
        with open(filename,'w',encoding='utf-8') as f:
            f.write(item['content'])

        return item
