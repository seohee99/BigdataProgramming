from naverhotel_crawling import CrawlingNaver
from expedia_crawling import CrawlingExpedia
from datetime import datetime, timedelta
import time
crawling_naver = CrawlingNaver()
crawling_expedia = CrawlingExpedia()

crawling_naver.run()
crawling_expedia.run()
