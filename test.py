from requests import get, post, put, delete


'''print(get('http://localhost:5000/api/users').json())
# несуществующий ключ
print(post('http://localhost:5000/api/users',
           json={'title': 'Заголовок'}).json())

# Переданы не все ключи
print(post('http://localhost:5000/api/users',
           json={'surname': '123',
                 'name': '456',
                 'age': 12,
                 'position': 'hi',
                 'speciality': 'qe',
                 'address': 'asd',
                 'email': 'scott_chief@mars.org',
                 'hashed_password': '123'}).json())'''

print(get('http://localhost:5000/api/users_show/1').json())