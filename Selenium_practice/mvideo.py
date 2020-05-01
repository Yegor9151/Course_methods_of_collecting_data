import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pprint import pprint


class CollectHits:
    '''Сбор хитов продаж с M.video'''

    options = Options()
    options.add_argument('start-maximized')
    driver = webdriver.Chrome(options=options)
    driver.get('https://www.mvideo.ru/')
    assert 'М.Видео' in driver.title

    def find_hits(self):
        '''ищем Хиты продаж'''

        blocks = self.driver.find_elements_by_xpath("//div[@data-init='gtm-push-products']")

        for block in blocks:
            if 'Хиты продаж' in block.text:
                return block

    def turn_page(self, block):
        '''прогружаем данные'''

        while True:
            self.driver.implicitly_wait(5)
            scroll = block.find_element_by_class_name('sel-hits-button-next')
            scroll.click()

            if 'disabled' in scroll.get_attribute('class'):
                break

    def collect_data(self, block):
        '''сбор данных'''

        result = []
        tags = block.find_elements_by_tag_name('a')

        for tag in tags:
            data = tag.get_attribute('data-product-info')
            if data is not None:
                data = re.sub('\t', '', data)
                data = re.sub('\n', '', data)
                data = re.sub('"', '', data)
                data = re.sub('{', '', data)
                data = re.sub('}', '', data).split(',')
                if data not in result:
                    result.append(data)

        return result

    def create_dict(self, text):
        '''составляем словаль'''

        result = []

        for txt in text:
            data = {}
            for t in txt:
                t = t.split(': ')
                data[t[0]] = t[1]
            result.append(data)

        return result

    def pipeline(self):
        '''выполняем последовательность'''

        hits_block = self.find_hits()
        self.turn_page(hits_block)
        data = self.collect_data(hits_block)
        result = self.create_dict(data)

        return result


CollectHits = CollectHits().pipeline()

pprint(CollectHits)
print(len(CollectHits))
