from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
import urllib.request
import urllib.parse
import pandas as pd
import numpy as np
import openpyxl
import re

from area_config import AddressConfig

class CrawlingExpedia():

    start_day = datetime.today().day
    start_month = datetime.today().month
    start_hour = datetime.today().hour 
    
    driver = webdriver.Chrome("./chromedriver_win32/chromedriver.exe")
    def init_url(self,area_big_idx:int):
        # url 앞 주소
        API = "https://www.expedia.co.kr/"

        check_in = datetime.today().strftime("%Y-%m-%d")     #체크인 날짜 : 현재 날짜 
        check_out = (datetime.today()+timedelta(1)).strftime("%Y-%m-%d") #체크아웃 날짜 : 다음날
 
        area = AddressConfig.AREA_EXPEDIA[area_big_idx]

        values = {
            "destination":"place:" + area,
            "checkin" : check_in,
            "checkout" : check_out,
            "rooms" : 2,
            "sortField" : "rating",
            "sortDirection" : "descending"
        }

        #url parsing
        params = urllib.parse.urlencode(values) 
        url = API + "?" + params 
    
        return url

    def get_info(self,url,area_big_idx:int):
        driver = webdriver.Chrome("./chromedriver_win32/chromedriver.exe")
        actions = ActionChains(driver) 

        #url connect
        driver.get(url) 
        sleep(5)
        print("loading complete")

        data_list = []
        count = 0
        while True:
            content= BeautifulSoup(driver.page_source, 'html.parser')
            hotels = content.select("ul.lst_hotel li.ng-scope") #작은박스 ("#prdReview > div > div.bbsListWrap.reviewAll > ul > li")

            for hotel in hotels:  
                
                try:
                    hotel_id = hotel.attrs["id"]
                    count += 1
                except:
                    continue

                name = hotel.select_one("div.info_wrap > div a > strong").text

                price_list = []
                for num in range(1,4):
                    try:
                        site = hotel.select_one("#hotel\\" + hotel_id[5:] + " > div.hotel_info > ul > li:nth-child(%d) > div > a.ota_title.ng-binding" % num).text 
                        price = hotel.select_one("#hotel\\" + hotel_id[5:] + " > div.hotel_info > ul > li:nth-child(%d) > div > a.price.sp_hotel_af.ng-binding" % num).text
                        price = re.sub(r'[^0-9]', '', price)
                        price_list.append([site,price])
                    except :
                        pass
                area_big = AddressConfig.AREA_BIG[area_big_idx]
                address = hotel.select_one("div > span > a:nth-child(6)").text

                try:
                    stars = int(hotel.select_one("span.grade.ng-binding").text[0])
                except:
                    stars = 0

                year = datetime.today().year
                month = datetime.today().month
                day = datetime.today().day
                weekday = datetime.today().weekday()
                source_site = AddressConfig.SOURCE_SITE[0]
                hotel_url = "https://www.expedia.co.kr/" + hotel_id
                etc = ""
                for num in range(1,4):
                    try:
                        etc += hotel.select_one("#hotel\\" + hotel_id[5:] + " > div.hotel_info > div.info_wrap > div > div > span.review_list.ng-scope > span:nth-child(%d)"% num).text + ' '
                    except:
                        etc = None
                            

                for _ in price_list:
                    price = _[1]
                    site = _[0]
                    data = [count,name,site,price,area_big,address,stars, year, month, day, weekday,source_site, hotel_url, etc ]
                    data_list.append(data)
                    print(data)
                
    
            actions.send_keys(Keys.SPACE).perform() 
            

            if area_big_idx == 9:
                break

            try:
                #페이지 끝까지 로딩되면 break
                driver.find_element_by_css_selector('a.direction.sp_hotel_bf.next.disabled').click()
                break
            except:
                try:
                    #다음페이지 이동
                    driver.find_element_by_css_selector('a.direction.sp_hotel_bf.next').click()
                #단일 페이지인 경우 
                except:
                    actions.send_keys(Keys.SPACE).perform() 
                    actions.send_keys(Keys.SPACE).perform() 
                    actions.send_keys(Keys.SPACE).perform() 
                    actions.send_keys(Keys.SPACE).perform() 
                    sleep(5)
                    driver.find_element_by_css_selector('a.direction.sp_hotel_bf.next').click()
                    
        
        driver.close()
        return data_list

    def save_file(self,data_list):
        wb =  openpyxl.load_workbook("D:/bigdata/project/data/hotel_%d.xlsx" % int(datetime.now().strftime('%Y%m%d')))
        sheet = wb.active

        for data in data_list:
            sheet.append(data)

        wb.save("D:/bigdata/project/data/hotel_%d.xlsx" % int(datetime.now().strftime('%Y%m%d')))
        print("file save")

    def run(self):
        crawling_expedia = CrawlingExpedia()
        for area_idx, area in enumerate(AddressConfig.AREA_EXPEDIA):
            if area_idx >= 0:
                url = crawling_expedia.init_url(area_idx)
                data_list = crawling_expedia.get_info(url,area_idx)
                crawling_expedia.save_file(data_list)
        return
    