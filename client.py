import requests

url = 'http://127.0.0.1:5000/api/v1/track'

data = {
    'tracks': [[1.3,2.4,3,4,4444,77.7777,8,1702700160,8]]
}

headers = {
    'Content-Type': 'application/json'
}

response = requests.post(url, json=data, headers=headers)

print(response.json())
