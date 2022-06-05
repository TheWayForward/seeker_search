# seeker_search
Search engine practice.

1. Clone the project
2. Create Database
  Run MySQL, import ArticleSpider/ArticleSpider/database/scrapy_spider.sql
3. Run Scrapy Server
  Import ArticleSpider to PyCharm, pip install, find main.py, click "Run"
4. Run Search Server
  ES: cd server/elasticsearch/bin, run elasticsearch.bat
  ES-Head: cd server/elasticsearch_head, npm install, npm run start
  Kibana: cd server/kibana/bin, run kibana.bat
5. Run WEBAPP Server
  Import server/seeker_server to PyCharm, pip install, click "Run"
6. Run Vue Search App Server
   cd client, npm install, npm run dev
7. Enjoy!

