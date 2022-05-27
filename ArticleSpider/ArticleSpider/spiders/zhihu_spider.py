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
from scrapy.loader import ItemLoader
from ArticleSpider.items import ZhihuQuestionItem, ZhihuAnswerItem
import json
import requests
import datetime
import time
import pickle
import os
import re
from urllib import parse

from ArticleSpider.utils import zhihu_login
from ArticleSpider.utils import common

BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu_spider'
    allowed_domains = ['www.zhihu.com']
    custom_settings = {
        "COOKIES_ENABLED": True
    }
    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhizhu.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    }
    start_urls = ['http://www.zhihu.com/']
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cattachment%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Cis_labeled%2Cpaid_info%2Cpaid_info_content%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_recognized%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics%3Bdata%5B%2A%5D.settings.table_of_content.enabled&limit={1}&offset={2}&platform=desktop&sort_by=default"
    start_answer_relative_url = "api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cattachment%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Cis_labeled%2Cpaid_info%2Cpaid_info_content%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_recognized%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics%3Bdata%5B%2A%5D.settings.table_of_content.enabled&limit={1}&offset={2}&platform=desktop&sort_by=default"

    cookie = {}
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
        self.cookie = cookie_dict
        for url in self.start_urls:
            headers = {
                'User-Agent': USER_AGENT
            }
            yield scrapy.Request(url, headers=headers, dont_filter=True, cookies=cookie_dict)

    def parse(self, response, **kwargs):
        # DFS strategy ,extract all urls and tract
        # if url contains /question/..., then parse

        all_urls = response.css("a::attr(href)").extract()

        # parse url & https filter
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls)
        for url in all_urls:
            # match /question/... with regexp
            # example: https://www.zhihu.com/question/319162653
            match_object = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_object:
                request_url = match_object.group(1)
                question_id = match_object.group(2)
                yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_question)
            else:
                # DFS
                yield scrapy.Request(url, headers=self.headers, callback=self.parse)

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

    def parse_question(self, response):
        # extract question item from question page
        result_xabpb = re.findall('"encodedParams":"(.*?)"', response.text, re.M | re.I)[0]
        match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
        if match_obj:
            # obtain question id
            question_id = int(match_obj.group(2))

        item_loader_question = ItemLoader(item=ZhihuQuestionItem(), response=response)
        item_loader_question.add_css("title", "h1.QuestionHeader-title::text")
        item_loader_question.add_css("content", "div.QuestionRichText > div > span::text")
        item_loader_question.add_value("url", response.url)
        item_loader_question.add_value("zhihu_id", question_id)
        item_loader_question.add_css("answers",
                            "#QuestionAnswers-answers > div > div > div > div.List-header > h4 > span:nth-child(1)::text")
        item_loader_question.add_css("comments", "div.QuestionHeader-Comment > button::text")
        item_loader_question.add_css("total_view",
                            "div.NumberBoard-item > div.NumberBoard-itemInner > strong.NumberBoard-itemValue::text")
        item_loader_question.add_css("topics", ".QuestionHeader-topics .Popover div::text")

        question_item = item_loader_question.load_item()

        print(question_item)

        question_item["answers"] = common.extract_num_from_separator(question_item["answers"][0])
        question_item["comments"] = common.zhihu_extract_num_from_comment(question_item["comments"][0])
        question_item["total_view"] = common.extract_num_from_separator(question_item["total_view"][0])
        question_item["url"] = question_item["url"][0]
        question_item["zhihu_id"] = question_item["zhihu_id"][0]
        if question_item["content"]:
            question_item["content"] = " ".join(question_item["content"]) + " "
        question_item["title"] = question_item["title"][0]
        question_item["topics"] = ",".join(question_item["topics"])

        yield question_item

        # item_loader_answer = ItemLoader(item=ZhihuAnswerItem(), response=response)
        # item_loader_answer.add_value("question_id", question_id)
        # item_loader_answer.add_css("content", "#QuestionAnswers-answers > div > div > div > div:nth-child(2) > div > div:nth-child(1) > div > div > div.RichContent.RichContent--unescapable > div.RichContent-inner > span > p::text")
        #
        # answer_item = item_loader_answer.load_item()
        #
        # yield answer_item

        # u()(f()(d))

        # xzse96_generator = "101_3_2.0+/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cattachment%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Cis_labeled%2Cpaid_info%2Cpaid_info_content%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_recognized%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics%3Bdata%5B%2A%5D.settings.table_of_content.enabled&limit={1}&offset={2}&platform=desktop&sort_by=default+{3}"
        # xzse96_d = xzse96_generator.format("67452946", 7, 0, self.cookie["d_c0"])

        # xzse96_generator = '101_3_2.0+/api/v4/questions/{0}/concerned_followers?limit=7&offset=0+{1}'
        # xzse96_d = xzse96_generator.format("67452946", self.cookie["d_c0"])
        # print(xzse96_d)
        #
        # xzse96_fd = EncryptHelper.md5(xzse96_d)
        # xzse96_ufd = "2.0_" + EncryptHelper.g_encrypt(xzse96_fd)

        # answer_headers = {
        #     "referer": "https://www.zhihu.com/question/{0}".format(question_id),
        #     "x-ab-pb": result_xabpb,
        #     "x-requested-with": "fetch",
        #     "x-api-version": "3.0.40",
        #     "x-zse-93": "101_3_2.0",
        #     "x-zse-96": xzse96_ufd,
        #     "x-zst-81": "3_2.0VhnTj77m-qofgh3TxTnq2_Qq2LYuDhV80wSL7eU0r6Ppb7tqXRFZQi90-LS9-hp1DufI-we8gGHPgJO1xuPZ0GxCTJHR7820XM20cLRGDJXfgGCBxupMuD_Ie8FL7AtqM6O1VDQyQ6nxrRPCHukMoCXBEgOsiRP0XL2ZUBXmDDV9qhnyTXFMnXcTF_ntRueTh7Vqhrg99wLV8ce8dgH0fce_pbHYkR2LlCFK1veBcQHVoMY1Kgx0S7SmZcOPv03KRhgBe4LmTgeMew28x9CK3CV_N9tf2re1YBo8hqx9UhxmZUtyWgOZ9Dc0nGwVtDcBwwLYSM71rTNs2RF9nwS8aJ9Kch28tqe_Rqg8C9XGyCc1fUtm4qfzqug1YDNpNCpfKHC1AgHmLckK6LeVKTNG2XHKEqNphcefTUefoGx9JCSKQuFmvCof1Jom_qxp6iOq8wgKCrxf1Gx_Q8YGJgHYYgx1YUC_WupG5weLuBLC"
        # }

        # answer_headers = {
        #     "accept": "*/*",
        #     "accept-language": "zh-CN,zh;q=0.9",
        #     "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"100\", \"Google Chrome\";v=\"100\"",
        #     "sec-ch-ua-mobile": "?0",
        #     "sec-ch-ua-platform": "\"Windows\"",
        #     "sec-fetch-dest": "empty",
        #     "sec-fetch-mode": "cors",
        #     "sec-fetch-site": "same-origin",
        #     "x-ab-param": "tp_topic_style=0;top_test_4_liguangyi=1;tp_zrec=1;pf_adjust=1;tp_contents=2;qap_question_visitor= 0;qap_question_author=0;pf_noti_entry_num=2;tp_dingyue_video=0;se_ffzx_jushen1=0",
        #     "x-ab-pb": "CowCUQV2CBsA2AfcBycITwMzBMUI3AvXAicHsgcxBvMDjQQzBVYFTwfRCVIL8QnXC1cE7AqiBgIIzALMCX0CKQWLBT8GZge0APYCtwPICaEDYQmgAxYGNAx0AYQCVAmmBEkJBAoBCzcMYAsGCj8A1gRSBesG2AJXB0IJ4AkqBuUIzwuYCEcAQQZ4B+EJDwtDANoIyQm5AokItQtWDPQLngXnBXsH3Qd6CD8JagEnCYQJdwcwBsUJaQERBeUJFgmbC6ID1giLCcQJygnLCSoDMgPgC5sHEglAAZQG3AiRCccJAQaMBXkIAQm0CjsCdAhQA4wEVQl1CY0JwwnGCekE4wWrCWcIown0A2wIpgbkChKGAQEBAAACAAAAAAAAAAABAAQAAAAAAQAAAQEEAQAAAQAAAAEAAAAAAAAAAAAAAAAAAQAAAQAAAAQEAAABAAAAAAsDAAAAAAEVAAAVAAMBAAEAAAICAAEDAAAAAAEAAAACAAADAAAAAgAAAAABAAABAAAABAAAAAAABAAAAAAAAAABAAAAAAAA",
        #     "x-requested-with": "fetch",
        #     "x-zse-93": "101_3_2.0",
        #     "x-zse-96": "2.0_a0x0SQ9yn9NXb_Y0mTYynv9yeH2XH9N8hCx06H9BFhtf",
        #     "x-zst-81": "3_2.0VhnTj77m-qofgh3TxTnq2_Qq2LYuDhV80wSL7eU0r6Ppb7tqXRFZQi90-LS9-hp1DufI-we8gGHPgJO1xuPZ0GxCTJHR7820XM20cLRGDJXfgGCBxupMuD_Ie8FL7AtqM6O1VDQyQ6nxrRPCHukMoCXBEgOsiRP0XL2ZUBXmDDV9qhnyTXFMnXcTF_ntRueThR31nUg_-9LszCLYYrOG2qxY6Bof39CO_D39PhO8S6Of6Dg81B2q_BLMJBCPv03KRhgBe4LmTgeMew28x9CK3CV_N9tf2re1YBo8hqx9UhxmZUtyWgOZ9Dc0nGwVtDcBwwLYSM71rTNs2RF9nwS8aJ9Kch28tqe_Rqg8C9XGyCc1fUtm4qfzogOCbHxLc9HBwGCYiqNqIh3s9hpBpMoL2gHmIhwfjbL0YeH0cAL8OCSVUwCK5UYGkeVmWDOsJgL00hVOycVZHbxsJ0FMFwcGpgwCbMCmrHLG-he82JUC",
        #     "referrer": "https://www.zhihu.com/question/67452946",
        #     "referrerPolicy": "no-referrer-when-downgrade",
        # }
        #
        # yield scrapy.Request("https://www.zhihu.com/api/v4/questions/67452946/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cattachment%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Cis_labeled%2Cpaid_info%2Cpaid_info_content%2Creaction_instruction%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_recognized%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cvip_info%2Cbadge%5B%2A%5D.topics%3Bdata%5B%2A%5D.settings.table_of_content.enabled&limit=5&offset=5&platform=desktop&sort_by=default", cookies=self.cookie,  headers=answer_headers, callback=self.parse_answer, errback=self.err_answer)

    # def err_answer(self, response):
    #     print("err")
    #     print(response)
    #
    # def parse_answer(self, response):
    #     print("result")
    #
    #     ans_json = json.loads(response.text)
    #     is_end = ans_json["paging"]["is_end"]
    #     next_url = ans_json["paging"]["next"]
    #
    #     # extract answers
    #     for answer in ans_json["data"]:
    #         answer_item = ZhihuAnswerItem()
    #         answer_item["zhihu_id"] = answer["id"]
    #         answer_item["url"] = answer["url"]
    #         answer_item["question_id"] = answer["question"]["id"]
    #         answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
    #         answer_item["content"] = answer["content"] if "content" in answer else None
    #         answer_item["likes"] = answer["voteup_count"]
    #         answer_item["comments"] = answer["comment_count"]
    #         answer_item["create_time"] = answer["created_time"]
    #         answer_item["update_time"] = answer["updated_time"]
    #         yield answer_item
    #
    #     # more answers
    #     if not is_end:
    #         yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)
    #     return

    def spider_closed(self, spider):
        print("spider closed")
        self.browser.quit()