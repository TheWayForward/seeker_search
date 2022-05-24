from scrapy import selector
from scrapy import Request
from scrapy.loader import ItemLoader
from pydispatch import dispatcher
from scrapy import signals
from urllib import parse
import undetected_chromedriver as uc
import time
import scrapy
import json
import requests
import pickle
import os
import re

from ArticleSpider.items import CnblogsArticleItem
from ArticleSpider.utils import common

BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

class CnblogsSpider(scrapy.Spider):
    name = 'cnblogs_spider'
    allowed_domains = ['news.cnblogs.com']
    start_urls = ['http://news.cnblogs.com/']
    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.browser = uc.Chrome(use_subprocess=True)
        # onClose cycle function
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def start_requests(self):
        cookies = []
        if os.path.exists(BASE_DIR + '/cookies/cnblogs.cookie'):
            cookies = pickle.load(open(BASE_DIR + '/cookies/cnblogs.cookie', 'rb'))
        if not cookies:
            browser = uc.Chrome(use_subprocess=True)
            browser.get("https://account.cnblogs.com/signin")
            browser.find_element_by_css_selector('#mat-input-0').send_keys("951947409@qq.com")
            browser.find_element_by_css_selector('#mat-input-1').send_keys("Sam_2019")
            browser.find_element_by_css_selector(
                'body > app-root > app-sign-in-layout > div > div > app-sign-in > app-content-container > div > div > div > form > div > button').click()
            time.sleep(1)
            cookies = browser.get_cookies()
            pickle.dump(cookies, open(BASE_DIR + '/cookies/cnblogs.cookie', 'wb'))
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']
        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True, cookies=cookie_dict)

    def parse(self, response, **kwargs):
        # get news urls, pass them to scrapy, then parse
        post_nodes = response.css('div#news_list .news_block')
        for post_node in post_nodes:
            image_url = post_node.css('div.content div.entry_summary a img.topic_img::attr(src)').extract_first('')
            post_url = post_node.css('h2 a::attr(href)').extract_first('')
            yield Request(url=parse.urljoin(response.url, post_url), meta={'front_image_url': image_url},
                          callback=self.parse_detail)

        next_url = response.xpath('//a[contains(text(), "Next >")]/@href').extract_first('')
        yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_url(self, value, secure=True):
        if secure:
            if 'https' not in value:
                return 'https:' + value
            return value
        else:
            if 'http' not in value:
                return 'http:' + value
            return value

    def parse_detail(self, response):
        # get news id via regexp, matches a series of number
        match_regexp = re.match(".*?(\d+)", response.url)
        if match_regexp:
            # initialize article object
            article_item = CnblogsArticleItem()
            post_id = match_regexp.group(1)

            # use item_loader to initialize article_item
            item_loader = ItemLoader(item=article_item, response=response)
            item_loader.add_css('title', '#news_title > a::text')
            item_loader.add_css('create_time', '#news_info > span.time::text')
            item_loader.add_css('content', '#news_body')
            item_loader.add_css('tags', '#news_more_info > div > a::text')
            item_loader.add_value('url', response.url)

            item_loader.add_value('front_image_url', self.parse_url(response.meta.get('front_image_url', '')))
            yield Request(url=parse.urljoin(response.url, '/NewsAjax/GetAjaxNewsInfo?contentId={}'.format(post_id)),
                          meta={"article_item": item_loader, 'url': response.url}, callback=self.parse_nums)

    def parse_nums(self, response):
        json_data = json.loads(response.text)

        item_loader = response.meta.get('article_item', '')

        item_loader.add_value('likes', json_data['DiggCount'])
        item_loader.add_value('comments', json_data['CommentCount'])
        item_loader.add_value('total_view', json_data['TotalView'])
        item_loader.add_value("url_object_id", common.get_md5(response.meta.get("url", "")))

        article_item = item_loader.load_item()
        yield article_item

    def spider_closed(self):
        print("zhihu spider closed")
        self.browser.close()
