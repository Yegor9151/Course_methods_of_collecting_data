import pandas as pd
from pymongo import MongoClient
from pprint import pprint


class ManagerMongoDB:
    '''менеджер mongoDB'''

    def __init__(self):
        '''читаем данные'''

        self.HH_df = pd.read_csv('HHVacancy.csv')
        self.SJ_df = pd.read_csv('SJVacancy.csv')

    def dict(self):
        '''соединаяем HH + SJ'''

        con_df = pd.concat([self.HH_df, self.SJ_df], axis=0, ignore_index=True)
        dict = con_df.to_dict('records')

        return dict

    def into_mongoDB(self):
        '''добавление данных в MongoDB'''

        client = MongoClient('localhost', 27017)  # Объявляем mongoDB
        db = client['db_vacancy']  # создание БД
        vacancy = db.vacancy

        vacancy_list = []
        for d in self.dict():
            vacancy.insert_one(d)
            vacancy_list.append(d)

        return vacancy_list, vacancy

    def delete(self, data):
        '''удаляем повторы'''

        for d in data.find({}, {'_id': 0}):
            count = data.count_documents(d)
            if count > 1:
                data.delete_one(d)

        return data

    def salary(self, data, key):
        '''обрабатываем ЗП'''

        salary_list = []
        for d in data.find({'min_salary': {'$gt': key}}).sort('min_salary'):
            salary_list.append(d)

        return salary_list

    def result(self):
        '''выполнение'''

        key = int(input('Введите минимальную суммуЖ '))

        vacancy = self.into_mongoDB()
        delete = self.delete(vacancy[1])
        salary = self.salary(delete, key)

        return vacancy[0], salary


result = ManagerMongoDB().result()

pprint(result[0])
print(f'\nКоличество объектов: {len(result[0])}\n')

pprint(result[1])
print(f'\nКоличество объектов: {len(result[1])}\n')
