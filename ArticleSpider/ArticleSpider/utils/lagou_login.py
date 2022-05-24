from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as Ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import time
import requests
import os
import random
import cv2
import numpy as np
import undetected_chromedriver.v2 as uc
from ArticleSpider.settings import BAIDU_REC_APIKEY, BAIDU_REC_APPSECRET

BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

class Login(object):

    def __init__(self, browser, user, password, retry):

        self.browser = browser
        self.wait = WebDriverWait(self.browser, 20)
        self.url = 'https://passport.lagou.com/login/login.html?service=https%3a%2f%2fwww.lagou.com%2f'
        self.user = user
        self.password = password
        self.retry = retry

    def click(self, css_selector, timeout):
        element = self.browser.find_element_by_css_selector(css_selector)
        self.browser.execute_script('arguments[0].click();', element)
        time.sleep(timeout)

    def login(self, use_baidu=False):

        self.browser.get(self.url)
        time.sleep(3)

        # click on agreement
        self.click('#lg-passport-box > div > div.sc-khQegj.dccqlI > div > div.sc-gKclnd.hrZfTH > div.sc-iCfMLu.eKQdwl > div', 1)

        # input username & password
        username = self.wait.until(
            Ec.element_to_be_clickable((By.CSS_SELECTOR, '#lg-passport-box > div > div > div > div > div > div:nth-child(1) > div:nth-child(1) > input'))
        )
        username.send_keys(self.user)
        # input password
        password = self.wait.until(
            Ec.element_to_be_clickable((By.CSS_SELECTOR, '#lg-passport-box > div > div > div > div > div > div:nth-child(1) > div:nth-child(2) > input'))
        )
        password.send_keys(self.password)

        for i in range(60):
            time.sleep(1)
            count = 60 - i
            print("Plz finish login operation in {0} second(s)".format(count))

        end_url = self.browser.current_url
        if end_url == "https://www.lagou.com/":
            return self.get_cookies()

    def get_cookies(self):
        # save cookies
        cookies = self.browser.get_cookies()
        self.cookies = ''
        for cookie in cookies:
            self.cookies += '{}={};'.format(cookie.get('name'), cookie.get('value'))
        return cookies

    def __del__(self):
        self.browser.close()
        print('lagou manual login module closed')
        # self.display.stop()
