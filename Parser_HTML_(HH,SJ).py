import requests
import re
import pandas as pd
from bs4 import BeautifulSoup as bs
from pprint import pprint

main_link_HH = 'https://hh.ru/'
main_link_SJ = 'https://russia.superjob.ru/'
key = input('Введите ключевое слово: ')


class HHParser:
    '''Парсинг вакансий'''

    def __init__(self, link, key):
        '''берём основную ссылку'''

        self.path = link
        self.key = key

    def create_links(self, key, num):
        '''адресс вокансий и параметры'''

        addition = 'search/vacancy'

        params = f'?L_save_area=true&clusters=true&enable_snippets=true&text={key}&showClusters=true&page={num}'
        link = self.path + addition + params

        return link

    def get_html(self, link):
        '''получение html кода'''

        headers = {'User-Agent':
                       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}

        html = requests.get(link, headers=headers).text

        return html

    def tasty_soup(self, html):
        '''супирование html кода))'''

        soup = bs(html, 'lxml')

        vacancy_block = soup.find('div', {'class': 'vacancy-serp'})
        vacancy_list = vacancy_block.find_all('div', {'class': 'vacancy-serp-item vacancy-serp-item_premium'})

        return vacancy_list

    def create_dict(self, soup):
        '''формаирование списка'''

        vacancy = []  # объявляем список
        for s in soup:  # заполняем список

            vac_data = {}  # объявляем словарь

            # данные по имени и ссылке
            name_link = s.find('a')
            name = name_link.getText()
            link = name_link['href']
            # данные по описанию
            describe = s.find('div', {'class': 'g-user-content'}).getText()
            # данные по зрплате
            salary_html = s.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})

            # формируем словарь
            vac_data['name'] = name
            vac_data['link'] = link
            vac_data['describe'] = describe

            # обрабатываем данные по завплате
            if salary_html is None:
                vac_data['min_salary'] = None
                vac_data['max_salary'] = None
                vac_data['currency'] = None

            else:
                salary_text = salary_html.getText()
                salary = re.sub('\xa0', '', salary_text)

                part = ['от ', 'до ', '-']
                if part[0] in salary:
                    min_sal_cur = re.sub(part[0], '', salary).split()
                    vac_data['min_salary'] = int(min_sal_cur[0])
                    vac_data['max_salary'] = None
                    vac_data['currency'] = min_sal_cur[1]
                elif part[1] in salary:
                    max_sal_cur = re.sub(part[1], '', salary).split()
                    vac_data['min_salary'] = None
                    vac_data['max_salary'] = int(max_sal_cur[0])
                    vac_data['currency'] = max_sal_cur[1]
                else:
                    min_max_sal_cur = re.sub(part[2], ' ', salary).split()
                    vac_data['min_salary'] = int(min_max_sal_cur[0])
                    vac_data['max_salary'] = int(min_max_sal_cur[1])
                    vac_data['currency'] = min_max_sal_cur[2]

            vacancy.append(vac_data)  # закидываем всё в список

        return vacancy

    def collect_data(self):
        '''финальная сборка'''

        data = []
        for n in range(40):
            link = self.create_links(self.key, n)
            html = self.get_html(link)
            soup = self.tasty_soup(html)
            result = self.create_dict(soup)
            for r in result:
                data.append(r)

        return data

    def create_df(self):
        '''сохдаём базу данных и сохраняем'''

        df = pd.DataFrame(self.collect_data())
        df.to_csv('HHVacancy.csv', index=False)
        df_read = pd.read_csv('HHVacancy.csv')

        return df_read


class SJParser:
    '''Парсер вакансий на SuperJob'''

    def __init__(self, link, key):
        '''берём основную ссылку'''

        self.path = link
        self.key = key

    def create_link(self, key, num):
        '''формируем точный адресс'''

        addiction = 'vacancy/search/'
        params = f'?keywords={key}&page={num}'

        result = self.path + addiction + params

        return result

    def get_html(self, link):
        '''собираем html код'''

        html = requests.get(link).text

        return html

    def tasty_soup(self, html):
        '''проводим супирование))'''

        soup = bs(html, 'html.parser')

        vacansy_block = soup.find_all('div', {'class': '_3zucV undefined'})[1]
        local_vacansy = vacansy_block.find_all('div', {'class': 'iJCa5 _2gFpt _1znz6 _2nteL'})

        return local_vacansy

    def clean_soup(self, soup):
        '''удаляем лишнее'''

        data = []
        for i in range(len(soup)):
            result = soup[i].find('div', {'class': 'QiY08 LvoDO'})
            if result is not None:
                data.append(result)

        return data

    def create_dict(self, soup):
        '''формирем ловари'''

        vacansy = []  # объявляем список
        for s in soup:

            vac_data = {}  # объявляем словарь

            # название, ссылка
            name_link = s.find('a')
            name = name_link.getText()
            link = main_link_SJ + name_link['href']
            # описание
            describe = s.find('div', {'class': '_3cLIl _3C76h _10Aay _2_FIo _1tH7S'}).getText()
            # ЗП
            salary_text = s.find('span', {
                'class': '_3mfro _2Wp8I _31tpt f-test-text-company-item-salary PlM3e _2JVkc _2VHxz'}).getText()

            vac_data['name'] = name
            vac_data['link'] = link
            vac_data['describe'] = describe

            # обрабатываем данные по завплате
            if salary_text == 'По договорённости':
                vac_data['min_salary'] = None
                vac_data['max_salary'] = None
                vac_data['currency'] = None

            else:
                salary = re.sub('\xa0', ' ', salary_text)

                part = ['от ', 'до ', '-']
                if part[0] in salary:
                    min_sal_cur = re.sub(part[0], '', salary).split()
                    vac_data['min_salary'] = int(min_sal_cur[0] + min_sal_cur[1])
                    vac_data['max_salary'] = None
                    vac_data['currency'] = min_sal_cur[2]
                elif part[1] in salary:
                    max_sal_cur = re.sub(part[1], '', salary).split()
                    vac_data['min_salary'] = None
                    vac_data['max_salary'] = int(max_sal_cur[0] + max_sal_cur[1])
                    vac_data['currency'] = max_sal_cur[2]
                else:
                    min_max_sal_cur = re.sub(part[2], ' ', salary).split()
                    vac_data['min_salary'] = int(min_max_sal_cur[0] + min_max_sal_cur[1])
                    vac_data['max_salary'] = int(min_max_sal_cur[3] + min_max_sal_cur[4])
                    vac_data['currency'] = min_max_sal_cur[5]

            vacansy.append(vac_data)

        return vacansy

    def collect_pages(self):
        '''собираем данные со всех страниц'''

        data = []
        for i in range(1, 4):
            link = self.create_link(self.key, i)
            html = self.get_html(link)
            soup = self.tasty_soup(html)
            clean = self.clean_soup(soup)
            result = self.create_dict(clean)
            for r in result:
                data.append(r)

        return data

    def create_df(self):
        '''сохдаём базу данных и сохраняем'''

        df = pd.DataFrame(self.collect_pages())
        df.to_csv('SJVacancy.csv', index=False)
        df_read = pd.read_csv('SJVacancy.csv')

        return df_read


result_SJ = SJParser(main_link_SJ, key).create_df()
result_HH = HHParser(main_link_HH, key).create_df()

print(f'\nКоличество объектов: {len(result_SJ)}\n')

result_SJ.info()
pprint(result_SJ)

print(f'\nКоличество объектов: {len(result_HH)}\n')

result_HH.info()
pprint(result_HH)
