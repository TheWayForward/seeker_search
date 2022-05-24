from selenium import webdriver
import undetected_chromedriver as uc
from scrapy.selector import Selector
import time

browser = uc.Chrome(use_subprocess=True)
browser.get("https://www.bilibili.com/video/BV1vF41137sE")
text_selector = Selector(text=browser.page_source)

# result = text_selector.css("div.bili-video-card__wrap.__scale-wrap > div > div > a > h3").extract()

for i in range(3):
    time.sleep(3)
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight); let page_length = document.body.scrollHeight; return page_length;")

browser.quit()