import requests
import re
import pandas as pd
from bs4 import BeautifulSoup as bs
from pprint import pprint

main_link = 'https://hh.ru/'


class HHParser:
    '''Парсинг вакансий'''

    def __init__(self, link):
        '''берём основную ссылку'''
        self.path = link

    def create_links(self, key, num):
        '''адресс вокансий и параметры'''

        addition = 'search/vacancy'

        params = f'?text={key}&page={num}'
        link = self.path + addition + params

        return link

    def get_html(self, link):
        '''получение html кода'''

        html = requests.get(link, headers='').text

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

            # дынные по имени, ссылке и зарплате
            local_data = s.find('div', {'class': 'vacancy-serp-item__row vacancy-serp-item__row_header'})
            # данные по имени и ссылке
            name_link = local_data.find('a')
            name = name_link.getText()
            link = name_link['href']
            # данные по зрплате
            salary_html = local_data.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})

            # данные по описанию
            describe = s.find_all('div', {'class': 'vacancy-serp-item__info'})[1].getText()

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

    def compile(self):
        '''финальная сборка'''

        key = input('Введите ключевое слово: ')

        data = []
        for n in list(range(0, 40)):
            link = self.create_links(key, n)
            html = self.get_html(link)
            soup = self.tasty_soup(html)
            result = self.create_dict(soup)
            for r in result:
                data.append(r)

        return data

    def create_df(self):
        '''сохдаём базу данных и сохраняем'''

        df = pd.DataFrame(self.compile())
        df.to_csv('vacancy.csv', index=False)
        df_read = pd.read_csv('vacancy.csv')

        return df_read


result = HHParser(main_link).create_df()

print(f'\nКоличество объектов: {len(result)}\n')

result.info()
pprint(result)
