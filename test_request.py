import requests


url = 'http://192.168.137.177/data'

r = requests.get(url)

data = r.json()

print(data)