import datetime
import re
import redis
from ArticleSpider.utils.common import extract_num
import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import Join, MapCompose, TakeFirst, Identity
from ArticleSpider.models.elasticsearch_types import ZhihuType
from elasticsearch_dsl.connections import connections

es = connections.create_connection(ZhihuType._doc_type.using)


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


def generate_suggests(index, info_tuple):
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={"filter": ["lowercase"]}, body=text)
            print(words)
            analyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"]) > 1])
            new_words = analyzed_words - used_words
        else:
            new_words = set()
    if new_words:
        suggests.append({"input": list(new_words), "weight": weight})
    return suggests

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
        insert_sql = "insert into zhihu_question(zhihu_id, topics, url, title, content, answers, comments, total_view) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE content = VALUES(content), answers = VALUES(answers), comments = VALUES(comments), total_view = VALUES(total_view)"
        zhihu_id = self["zhihu_id"]
        topics = self["topics"]
        url = self["url"]
        title = self["title"]
        content = self["content"]
        answers = self["answers"]
        comments = self["comments"]
        total_view = self["total_view"]

        params = (zhihu_id, topics, url, title, content, answers, comments, total_view)

        return insert_sql, params

    def save_to_es(self):
        zhihu = ZhihuType()
        zhihu.zhihu_id = self.get("zhihu_id", "")
        zhihu.topics = self.get("topics", "")
        zhihu.url = self.get("url", "")
        zhihu.title = self.get("title", "")
        zhihu.content = self.get("content", "")
        zhihu.create_time = self.get("create_time", "")
        zhihu.update_time = self.get("update_time", "")
        zhihu.answers = self.get("answers", "")
        zhihu.comments = self.get("comments", "")
        zhihu.total_view = self.get("total_view", "")
        zhihu.suggest = generate_suggests(ZhihuType._doc_type.index, ((zhihu.title, 10), (zhihu.topics, 7)))
        zhihu.save()
        return


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
