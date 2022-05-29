import datetime
from django.shortcuts import render
from django.views.generic.base import View
from search.models import ZhihuType
from django.http import HttpResponse, JsonResponse
from elasticsearch import Elasticsearch
from utils.message_helper import zh_cn as MessageHelper
import utils.config as Config
import utils.versatile_helper as VersatileHelper
import json

client = Elasticsearch(hosts=["127.0.0.1"])


class ZhihuSearchSuggest(View):
    def get(self, request):
        key_words = request.GET.get("key_words", "")
        suggest_data = []
        if key_words:
            s = ZhihuType.search()
            s = s.suggest("my-suggest", key_words, completion={
                "field": "suggest",
                "fuzzy": {
                    "fuzziness": 2,
                },
                "size": 10
            })
            suggestions = s.execute_suggest()
            for match in suggestions["my-suggest"][0].options:
                source = match["_source"]
                suggest_data.append(source["title"])
        return JsonResponse({
            "code": 200,
            "message": MessageHelper["success"],
            "info": {
                "key_words": key_words,
                "suggest_data": suggest_data
            }
        })


class ZhihuSearchResult(View):
    def get(self, request):
        key_words = request.GET.get("key_words", "")
        page_index = request.GET.get("page_index", "1")
        try:
            page_index = int(page_index)
        except:
            page_index = 1
        start_time = datetime.datetime.now()
        response = client.search(index="zhihu", body={
            "query": {
                "multi_match": {
                    "query": key_words,
                    "fields": ["topics", "title", "content"]
                }
            },
            "from": 10 * (page_index - 1),
            "size": Config.search_result_batch,
            "highlight": {
                "pre_tags": ["<span style='color: red;'>"],
                "post_tags": ["</span>"],
                "fields": {
                    "title": {},
                    "topics": {},
                    "content": {}
                }
            }
        })
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        total_result = response["hits"]["total"]
        total_pages = VersatileHelper.get_pages_from_result(total_result)
        search_data = []
        for hit in response["hits"]["hits"]:
            hit_dict = {}
            if "title" in hit["highlight"]:
                hit_dict["title"] = "".join(hit["highlight"]["title"])
            else:
                hit_dict["title"] = hit["_source"]["title"]
            if "content" in hit["highlight"]:
                hit_dict["content"] = "".join(hit["highlight"]["content"])[:500]
            else:
                hit_dict["content"] = hit["_source"]["content"][:500]
            hit_dict["url"] = hit["_source"]["url"]
            hit_dict["score"] = hit["_score"]
            search_data.append(hit_dict)
        return JsonResponse({
            "code": 200,
            "message": MessageHelper["success"],
            "info": {
                "duration": duration,
                "key_words": key_words,
                "page_size": Config.search_result_batch,
                "page_index": page_index,
                "total_result": total_result,
                "total_pages": total_pages,
                "search_data": search_data
            }
        })
