import re
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from pprint import pprint
from pymongo import MongoClient
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class CollectHits:
    '''Сбор хитов продаж с M.video'''

    driver = webdriver.Chrome()
    driver.get('https://www.mvideo.ru/')
    assert 'М.Видео' in driver.title

    def scrolling(self):
        '''прогружаем данные на страничке'''

        hits = self.driver.find_element_by_xpath("//div[@class='gallery-layout'][2]")
        hits.click()

        time.sleep(3)
        button = self.driver.find_element_by_class_name("next-btn")
        button.click()

        return hits

    def pipeline(self):
        '''выполнение действий'''

        return self.scrolling()

CollectHits = CollectHits().scrolling()

print(CollectHits)
