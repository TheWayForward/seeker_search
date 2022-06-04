from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from django.views.generic import TemplateView
from search.views import SearchSuggest, SearchResult

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api/v1/suggest/$', SearchSuggest.as_view(), name="zhihu_suggest"),
    url(r'^api/v1/search_result/$', SearchResult.as_view(), name="zhihu_search_result")
]
