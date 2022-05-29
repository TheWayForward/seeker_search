from django.db import models
from elasticsearch_dsl import DocType, Date, Nested, Boolean, analyzer, Completion, Keyword, Text, Integer
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import CustomAnalyzer as ca

connections.create_connection(hosts=["http://127.0.0.1:9200/"])


class CustomAnalyzer(ca):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])


class ZhihuType(DocType):
    suggest = Completion(analyzer=ik_analyzer)
    zhihu_id = Integer()
    topics = Text(analyzer="ik_max_word")
    url = Keyword()
    title = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")
    create_time = Date()
    update_time = Date()
    answers = Integer()
    comments = Integer()
    total_view = Integer()

    class Meta:
        index = "zhihu"
        doc_type = "question"
