from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from django.views.generic import TemplateView
from search.views import ZhihuSearchSuggest, ZhihuSearchResult

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api/v1/zhihu_suggest/$', ZhihuSearchSuggest.as_view(), name="zhihu_suggest"),
    url(r'^api/v1/zhihu_search_result/$', ZhihuSearchResult.as_view(), name="zhihu_search_result")
]
