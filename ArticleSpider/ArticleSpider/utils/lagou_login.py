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


class Operation():

    def __init__(self, slider_ele=None, background_ele=None, count=1, save_image=False):

        '''
        :param slider_ele: slide puzzle element
        :param background_ele: background element
        :param count: retry times
        :param save_image:  do save captchas verified
        '''

        self.count = count
        self.save_images = save_image
        self.slider_ele = slider_ele
        self.background_ele = background_ele

    def get_slide_locus(self, distance):

        distance += 8
        v = 0
        m = 0.3
        # save moves smaller than 0.3
        tracks = []
        current = 0
        mid = distance * 4 / 5
        while current <= distance:
            if current < mid:
                a = 2
            else:
                a = -3
            v0 = v
            s = v0 * m + 0.5 * a * (m ** 2)
            current += s
            tracks.append(round(s))
            v = v0 + a * m
        # return track array
        return tracks

    def slide_verification(self, driver, slide_element, distance):

        start_url = driver.current_url
        print('slide distance: ', distance)
        # generate slide track by slide distance
        locus = self.get_slide_locus(distance)

        print('slide track: {}, total distance: {}'.format(locus, distance))

        # mouse left key down
        ActionChains(driver).click_and_hold(slide_element).perform()

        time.sleep(0.5)

        # begin slide
        for loc in locus:
            time.sleep(0.01)
            ActionChains(driver).move_by_offset(loc, random.randint(-5, 5)).perform()
            ActionChains(driver).context_click(slide_element)

        # release mouse
        ActionChains(driver).release(on_element=slide_element).perform()

    def onload_save_img(self, url, filename="image.png"):
        try:
            response = requests.get(url)
        except Exception as e:
            print('failed to download image')
            raise e
        else:
            with open(filename, 'wb') as f:
                f.write(response.content)

    def get_element_slide_distance(self, slider_ele, background_ele, correct=0):

        # get puzzle and background images
        slider_url = slider_ele.get_attribute('src')
        background_url = background_ele.get_attribute('src')

        # rename & save
        slider = 'slider.jpg'
        background = 'background.jpg'
        self.onload_save_img(slider_url, slider)
        self.onload_save_img(background_url, background)

        # grayscale convertion
        slider_pic = cv2.imread(slider, 0)
        background_pic = cv2.imread(background, 0)

        # get shape of puzzle, array reversed
        width, height = slider_pic.shape[::-1]

        # save grayscale images
        slider01 = 'slider01.jpg'
        slider02 = 'slider02.jpg'
        background01 = 'background01.jpg'

        cv2.imwrite(slider01, slider_pic)
        cv2.imwrite(background01, background_pic)

        # read image
        slider_pic = cv2.imread(slider01)

        # convert to grayscale
        slider_pic = cv2.cvtColor(slider_pic, cv2.COLOR_BGR2GRAY)

        # get abs chromatic aberration
        slider_pic = abs(255 - slider_pic)

        # save abs chromatic aberration puzzle image
        cv2.imwrite(slider02, slider_pic)

        # read image above
        slider_pic = cv2.imread(slider02)

        # read background image
        background_pic = cv2.imread(background01)

        time.sleep(3)

        # using matching coefficient method to find one image in another
        result = cv2.matchTemplate(slider_pic, background_pic, cv2.TM_CCOEFF_NORMED)

        # get position of missing puzzle
        top, left = np.unravel_index(result.argmax(), result.shape)

        print('missing coordinate: ', (left, top, left + width, top + height))

        if self.save_images:
            loc = [(left + correct, top + correct), (left + width - correct, top + height - correct)]
            self.image_crop(background, loc)

        else:
            # remove temp files
            os.remove(slider01)
            os.remove(slider02)
            os.remove(background01)
            os.remove(background)
            os.remove(slider)
            # print('删除')
            # os.remove(slider)
        return left

    def image_crop(self, image, loc):
        cv2.rectangle(image, loc[0], loc[1], (7, 249, 151), 2)
        cv2.imshow('Show', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


class Login(object):

    def __init__(self, browser, user, password, retry):

        self.browser = browser
        self.wait = WebDriverWait(self.browser, 20)
        self.url = 'https://www.lagou.com/'
        self.sli = Operation()
        self.user = user
        self.password = password
        self.retry = retry

    def login(self, use_baidu=False):

        self.browser.get(self.url)
        time.sleep(3)
        # click '登录'
        # click '密码登录'
        # click '登录'
        login_element = self.browser.find_element_by_css_selector(
            'div.SignFlow-tab:nth-child(2)')
        self.browser.execute_script("arguments[0].click();", login_element)

        # input username
        username = self.wait.until(
            Ec.element_to_be_clickable((By.CSS_SELECTOR, '.SignFlow-account input'))
        )
        username.send_keys(self.user)

        # input password
        password = self.wait.until(
            Ec.element_to_be_clickable((By.CSS_SELECTOR, '.SignFlow-password input'))
        )
        password.send_keys(self.password)

        submit = self.wait.until(
            Ec.element_to_be_clickable((By.CSS_SELECTOR, '.Button.SignFlow-submitButton'))
        )

        time.sleep(3)
        # click '登录'
        submit.click()
        time.sleep(3)

        k = 1

        if not use_baidu:
            while k < self.retry:
                # https://www.zhihu.com/signin?next=%2F
                # slide puzzle captcha has 2 layers

                # background layer
                bg_img = self.wait.until(
                    Ec.presence_of_element_located((By.CSS_SELECTOR, '.yidun_bgimg .yidun_bg-img'))
                )

                # front puzzle layer
                front_img = self.wait.until(
                    Ec.presence_of_element_located((By.CSS_SELECTOR, '.yidun_bgimg .yidun_jigsaw'))
                )

                # get slide distance
                distance = self.sli.get_element_slide_distance(front_img, bg_img)
                print('captcha slide distance: ', distance)

                distance = distance - 4
                print('actual slide distance: ', distance)

                # slide puzzle element
                element = self.browser.find_element_by_css_selector(
                    '.yidun_slider')

                # start to recognize and slide
                self.sli.slide_verification(self.browser, element, distance)

                time.sleep(5)
                try:
                    submit = self.wait.until(
                        Ec.element_to_be_clickable((By.CSS_SELECTOR, '.Button.SignFlow-submitButton'))
                    )
                    submit.click()
                    time.sleep(3)
                except:
                    pass

                end_url = self.browser.current_url
                print(end_url)

                if end_url == "https://www.zhihu.com/":
                    return self.get_cookies()
                else:
                    time.sleep(3)
                    k += 1

            return None
        else:
            # use baidu
            while k < self.retry:
                # background layer
                bg_img = self.wait.until(
                    Ec.presence_of_element_located((By.CSS_SELECTOR, '.yidun_bgimg .yidun_bg-img'))
                )

                background_url = bg_img.get_attribute('src')
                image = "background.jpg"
                # get slide distance
                self.sli.onload_save_img(background_url, image)
                baidu_login = BaiduLogin()
                distance = baidu_login.recongnize(baidu_login.get_access_token(), image)
                print('captcha slide distance: ', distance)

                distance = distance - 4
                print('actual slide distance: ', distance)

                # slide puzzle element
                element = self.browser.find_element_by_css_selector(
                    '.yidun_slider')

                # start to recognize and slide
                self.sli.slide_verification(self.browser, element, distance)

                time.sleep(5)
                try:
                    submit = self.wait.until(
                        Ec.element_to_be_clickable((By.CSS_SELECTOR, '.Button.SignFlow-submitButton'))
                    )
                    submit.click()
                    time.sleep(3)
                except:
                    pass

                end_url = self.browser.current_url
                print(end_url)

                if end_url == "https://www.zhihu.com/":
                    return self.get_cookies()
                else:
                    time.sleep(3)
                    k += 1
            return None

    def get_captcha_image(self):

        # go to login page
        self.browser.get('https://www.zhihu.com/signin')
        # click '密码登录'
        login_element = self.browser.find_element_by_css_selector(
            '#root > div > main > div > div > div > div.SignContainer-content > div > div:nth-child(1) > form > div.SignFlow-tabs > div:nth-child(2)')
        self.browser.execute_script("arguments[0].click();", login_element)

        # input username
        username = self.wait.until(
            Ec.element_to_be_clickable((By.CSS_SELECTOR, '.SignFlow-account input'))
        )
        username.send_keys('18888888888')

        # input password
        password = self.wait.until(
            Ec.element_to_be_clickable((By.CSS_SELECTOR, '.SignFlow-password input'))
        )
        password.send_keys('abcdefghij')

        submit = self.wait.until(
            Ec.element_to_be_clickable((By.CSS_SELECTOR, '.Button.SignFlow-submitButton'))
        )
        submit.click()
        time.sleep(2)

        while True:
            captcha_background = self.browser.find_element_by_css_selector(
                'body > div.yidun_popup--light.yidun_popup > div.yidun_modal__wrap > div > div > div.yidun_modal__body > div > div.yidun_panel > div > div.yidun_bgimg > img.yidun_bg-img').get_attribute(
                'src')
            img_data = requests.get(url=captcha_background).content
            img_path = '/images/captcha/' + captcha_background[32:]
            with open(BASE_DIR + img_path, 'wb') as fp:
                fp.write(img_data)
                print('downloaded')
            time.sleep(0.5)
            # refresh captcha bg image
            self.browser.find_element_by_css_selector(
                'body > div.yidun_popup--light.yidun_popup > div.yidun_modal__wrap > div > div > div.yidun_modal__body > div > div.yidun_panel > div > div.yidun_top > div > button.yidun_refresh').click()

    def get_cookies(self):
        # save cookies
        cookies = self.browser.get_cookies()
        self.cookies = ''
        for cookie in cookies:
            self.cookies += '{}={};'.format(cookie.get('name'), cookie.get('value'))
        return cookies

    def __del__(self):
        self.browser.close()
        print('zhihu auto login module closed')
        # self.display.stop()


class BaiduLogin():

    def get_access_token(self):
        import requests

        # URL: https://aip.baidubce.com/rpc/2.0/ai_custom/v1/detection/puzzle_captcha_rec
        # client id & client secret key
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={}&client_secret={}'.format(
            BAIDU_REC_APIKEY, BAIDU_REC_APPSECRET)
        response = requests.get(host)
        if response.status_code == 200:
            return response.json()["access_token"]
        return None

    def recongnize(self, access_token, image_file):
        # convert image to base64, ask for recognition, result contains position information

        import base64
        import json

        request_url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/detection/puzzle_captcha_rec"

        with open(image_file, 'rb') as f:
            base64_data = base64.b64encode(f.read())
            s = base64_data.decode('UTF8')
        params = {"image": s}
        params = json.dumps(params)
        request_url = request_url + "?access_token=" + access_token
        headers = {'Content-Type': 'application/json'}
        response = requests.post(request_url, headers=headers, data=params)
        response_json = response.json()
        print(response_json)
        if "results" not in response_json:
            return None
        if len(response.json()["results"]) == 0:
            return None
        if "location" not in response.json()["results"][0]:
            return None
        return response.json()["results"][0]["location"]["left"]
