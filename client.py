import requests

data = requests.post('http://127.0.0.1:5000/user',
                     json={
                         'name': 'user1',
                         'password': 'user'
                     })
print(data.status_code)
print(data.text)

data = requests.get('http://127.0.0.1:5000/user/1')
print(data.status_code)
print(data.text)

data = requests.patch('http://127.0.0.1:5000/user/1', json={'name': 'user_1'})
print(data.status_code)
print(data.text)

data = requests.post('http://127.0.0.1:5000/login/',
                     json={
                         'name': 'user_1',
                         'password': 'user'
                     })

print(data.status_code)
print(data.text)

data = requests.post('http://127.0.0.1:5000/token/1',
                     json={
                         'name': 'user1',
                         'password': 'user'
                     })

print(data.status_code)
token = data.text[1:-2]

data = requests.post('http://127.0.0.1:5000/ad',
                     headers={'token': token},
                     json={
                         'title': 'Cow',
                         'text': 'Slow slow cow'
                     })
print(data.status_code)
print(data.text)

data = requests.patch('http://127.0.0.1:5000/ad/5',
                      headers={'token': token},
                      json={
                         'title': 'Cow',
                         'text': 'Fast cow'
                      })
print(data.status_code)
print(data.text)

data = requests.get('http://127.0.0.1:5000/ad/1')
print(data.status_code)
print(data.text)

data = requests.get('http://127.0.0.1:5000/user/1')
print(data.status_code)
print(data.text)

data = requests.delete('http://127.0.0.1:5000/ad/1',
                       headers={'token': token}
                       )
print(data.status_code)
print(data.text)

data = requests.get('http://127.0.0.1:5000/ad/1')
print(data.status_code)
print(data.text)
