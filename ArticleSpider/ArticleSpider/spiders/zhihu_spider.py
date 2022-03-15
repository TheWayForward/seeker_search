from scrapy import selector
from scrapy import Request
from scrapy.loader import ItemLoader
from urllib import parse
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as Ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from ArticleSpider.settings import MY_PHONE, MY_PASSWORD, USER_AGENT
import scrapy
import json
import requests
import time
import pickle
import os
import re

from ArticleSpider.items import ZhihuArticleItem
from ArticleSpider.utils import zhihu_login
from ArticleSpider.utils import common

BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu_spider'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.browser = uc.Chrome(use_subprocess=True)
        self.wait = WebDriverWait(self.browser, 20)

    def start_requests(self):
        cookies = []
        if os.path.exists(BASE_DIR + '/cookies/zhihu.cookie'):
            cookies = pickle.load(open(BASE_DIR + '/cookies/zhihu.cookie', 'rb'))
        if not cookies:
            login_operation = zhihu_login.Login(self.browser, MY_PHONE, MY_PASSWORD, 5)
            login_operation.login(use_baidu=False)
            time.sleep(1)
            cookies = login_operation.get_cookies()
            pickle.dump(cookies, open(BASE_DIR + '/cookies/zhihu.cookie', 'wb'))
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']
        for url in self.start_urls:
            headers = {
                'User-Agent': USER_AGENT
            }
            yield scrapy.Request(url, headers=headers, dont_filter=True, cookies=cookie_dict)

    def parse(self, response, **kwargs):

        pass

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
        return

    def parse_nums(self, response):
        return
