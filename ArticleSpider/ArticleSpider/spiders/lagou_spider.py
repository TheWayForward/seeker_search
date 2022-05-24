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
from ArticleSpider.middlewares import RandomUserAgentMiddleware
import scrapy
from scrapy.loader import ItemLoader
import json
import requests
import datetime
import time
import pickle
import os
import re
from urllib import parse

from ArticleSpider.utils import lagou_login

BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

class LagouSpider(scrapy.Spider):
    name = 'lagou_spider'
    allowed_domains = ['www.lagou.com']
    custom_settings = {
        "COOKIES_ENABLED": True
    }
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    }
    start_urls = ['https://www.lagou.com/']
    cookie = {}

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.browser = uc.Chrome(use_subprocess=True)
        self.wait = WebDriverWait(self.browser, 20)

    def start_requests(self):
        cookies = []
        if os.path.exists(BASE_DIR + '/cookies/lagou.cookie'):
            cookies = pickle.load(open(BASE_DIR + '/cookies/lagou.cookie', 'rb'))
        if not cookies:
            login_operation = lagou_login.Login(self.browser, "18810559476", "Sam_2019")
            login_operation.login(use_baidu=False)
            time.sleep(1)
            cookies = login_operation.get_cookies()
            pickle.dump(cookies, open(BASE_DIR + '/cookies/lagou.cookie', 'wb'))
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']
        self.cookie = cookie_dict
        for url in self.start_urls:
            headers = {
                'User-Agent': RandomUserAgentMiddleware.get_ua()
            }
            yield scrapy.Request(url, headers=headers, dont_filter=True, cookies=cookie_dict)

    def parse(self, response, **kwargs):
        return

    def parse_url(self, value, secure=True):
        if secure:
            if 'https' not in value:
                return 'https:' + value
            return value
        else:
            if 'http' not in value:
                return 'http:' + value
            return value

    def spider_closed(self, spider):
        print("spider closed")
        self.browser.quit()

