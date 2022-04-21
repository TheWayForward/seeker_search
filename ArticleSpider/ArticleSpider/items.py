import datetime
import re
import redis
from ArticleSpider.utils.common import extract_num
import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import Join, MapCompose, TakeFirst, Identity


class ArticlespiderItem(scrapy.Item):
    pass


def date_convert(value):
    match_regexp = re.match('.*?(\d+.*)', value)
    if match_regexp:
        return match_regexp.group(1)
    else:
        return '0000-00-00'


def get_nums(value):
    match_re = re.match('.*?(\d+).*', value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums


def remove_comment_tags(value):
    if '评论' in value:
        return ''
    else:
        return value


def return_value(value):
    return value


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class CnblogsArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_time = scrapy.Field(input_processor=MapCompose(date_convert))
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    tag_list = scrapy.Field()
    front_image_url = scrapy.Field(output_processor=Identity())
    front_image_path = scrapy.Field()
    likes = scrapy.Field()
    comments = scrapy.Field()
    total_view = scrapy.Field()
    tags = scrapy.Field(output_processor=Join(separator=','))
    content = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = 'INSERT INTO cnblogs_article (title, url ,url_object_id, front_image_url, front_image_path, likes, comments, total_view, tags, content, create_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE front_image_url = VALUES(front_image_url)'
        params = list()
        params.append(self.get('title', '')[0])
        params.append(self.get('url', '')[0])
        params.append(self.get('url_object_id', '')[0])
        params.append(self.get('front_image_url', '')[0])
        params.append(self.get('front_image_path', ''))
        params.append(self.get('likes', 0)[0])
        params.append(self.get('comments', 0)[0])
        params.append(self.get('total_view', 0)[0])
        params.append(self.get('tags', ''))
        params.append(self.get('content', '')[0])
        params.append(self.get('create_time', '1970-07-01')[0])
        return insert_sql, params


class ZhihuQuestionItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    answers = scrapy.Field()
    comments = scrapy.Field()
    total_view = scrapy.Field()
    clicks = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = "insert into zhihu_question(zhihu_id, topics, url, title, content, answers, comments, total_view, clicks) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE content = VALUES(content), answers = VALUES(answers), comments = VALUES(comments), total_view = VALUES(total_view), clicks = VALUES(clicks)"
        zhihu_id = self["zhihu_id"][0]
        topics = ",".join(self["topics"])
        url = self["url"][0]
        title = "".join(self["title"])
        content = "".join(self["content"])
        answers = extract_num("".join(self["answers"]))
        comments = extract_num("".join(self["comments"]))

        if len(self["total_view"]) == 2:
            total_view = int(self["total_view"][0].replace(",", ""))
            clicks = int(self["total_view"][1].replace(",", ""))
        else:
            total_view = int(self["total_view"][0].replace(",", ""))
            clicks = 0

        params = (zhihu_id, topics, url, title, content, answers, comments,
                  total_view, clicks)

        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    question_id = scrapy.Field()
    content = scrapy.Field()

    # zhihu_id = scrapy.Field()
    # url = scrapy.Field()
    # question_id = scrapy.Field()
    # author_id = scrapy.Field()
    # content = scrapy.Field()
    # likes = scrapy.Field()
    # comments = scrapy.Field()
    # create_time = scrapy.Field()
    # update_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = 'INSERT INTO zhihu_answer (question_id, content) VALUES (%s, %s)'
        params = list()
        params.append(self.get("question_id", "")[0])
        params.append(" ".join(self.get("content", "")))
        return insert_sql, params
