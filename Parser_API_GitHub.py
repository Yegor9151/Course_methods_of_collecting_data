# Парсер репозиториев юзера по API

import requests
import json

# записываем пример: "https://api.github.com/users/{user}/repos{?type,page,per_page,sort}"
main_link = 'https://api.github.com'    # создаём основную ссылку
user = 'Yegor9151'                      # записываем пользователя
repos = f'/users/{user}/repos'          # создаём путь к репозиторию

response = requests.get(main_link + repos)  # формируем доступ к данным

if response.ok:  # проверяем доступ

    data = json.loads(response.text)                    # преобразуем в json формат
    count = len(data)                                   # считаем количество объектов списка
    result = [data[i]['name'] for i in range(count)]    # генерируем список результатов

    print(
        f'У пользователя {user} найдено {count} репозитория:\n'
        f'{result}'
    )  # выводим на экран

    with open('data.json', 'w') as file:
        json_data = json.dump(data, file)   # полученные данные сохраняем в фаил json

else:
    pass
