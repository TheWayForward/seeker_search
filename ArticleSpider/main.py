from scrapy.cmdline import execute
import sys
import os

sys.path.append(os.path.dirname(__file__))

execute(["scrapy","crawl","lagou_spider"])
