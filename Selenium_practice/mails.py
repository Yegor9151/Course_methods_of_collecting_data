import LogNPass
import re
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pprint import pprint
from pymongo import MongoClient


class CollectMails:
    '''Сбор писем с Mail.ru'''

    driver = webdriver.Chrome()
    driver.get('https://mail.ru/')
    assert 'Mail' in driver.title

    def login(self, login, password):
        '''Заходим на почту'''

        lin = self.driver.find_element_by_id('mailbox:login')
        lin.send_keys(login)
        lin.send_keys(Keys.ENTER)

        self.driver.implicitly_wait(5)
        passwd = self.driver.find_element_by_id('mailbox:password')
        passwd.send_keys(password)
        passwd.send_keys(Keys.ENTER)

    def start(self):
        '''Заходим в первое письмо'''

        later = self.driver.find_element_by_class_name('llc')
        self.driver.get(later.get_attribute('href'))

    def treatment_data(self):
        '''Собираем данные'''

        def edit_text(text):
            '''редактируем полученный текст'''

            del_n = re.sub('\n', '', text)
            del_u200c = re.sub('\u200c', '', del_n)

            return del_u200c

        data = {}
        pattern = self.driver.find_element_by_class_name

        data['_id'] = re.findall(':(\w+):', self.driver.current_url)[0]
        data['from_who'] = pattern('letter-contact').text
        data['address'] = pattern('letter-contact').get_attribute('title')
        data['subject'] = pattern('thread__subject').text
        data['link'] = self.driver.current_url
        data['data_time'] = pattern('letter__date').text

        text = self.driver.find_element_by_class_name('js-readmsg-msg').text
        data['text'] = edit_text(text)

        return data

    def result(self):
        '''следуюшее письмо'''

        result = []
        while True:
            time.sleep(1)
            result.append(self.treatment_data())
            arrow_down = self.driver.find_element_by_class_name('button2_arrow-down')

            try:
                arrow_down.click()
            except Exception:
                break

        return result

    def mongo(self, data):
        '''сохраняем в MongoDB'''

        client = MongoClient('localhost', 27017)
        mondo_base = client.mails
        collect = mondo_base['mail_ru']

        for dat in data:
            collect.update_one({'link': dat['link']}, {'$set': dat}, upsert=True)

        return data

    def pipeline(self):
        '''выполнение действий'''

        self.login(LogNPass.login, LogNPass.password)
        self.start()
        data = self.result()
        return self.mongo(data)


CollectMails = CollectMails().pipeline()

pprint(CollectMails)
