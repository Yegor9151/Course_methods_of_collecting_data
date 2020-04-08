import requests

# Задача 2
# Выполнить запрос методом GET к ресурсам, использующим любой тип авторизации через Postman, Python.

main_link = 'https://oauth.vk.com/authorize'

client_id = 'client_id=7399273'
score = 'scope=photos,audio,video,docs,notes,pages,status,offers,questions,wall,groups,email,notifications,stats,ads,offline,docs,pages,stats,notifications'
response_type = 'response_type=token'

first_link = f'{main_link}?{client_id}&{score}&{response_type}'

test = requests.get(first_link)
print(test)

methods = ['account.getInfo', 'users.get']
token = 'здесь будет токен))'

last_link = f'https://api.vk.com/method/{methods[1]}'
params = {
    'access_token': f'{token}',
    'v': '5.103'
}

response = requests.get(last_link, params=params).json()
result = response['response'][0]

print(f"{result['first_name']} {result['last_name']}")
