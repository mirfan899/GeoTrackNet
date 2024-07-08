import requests

url = 'http://127.0.0.1:5000/api/v1/track'

data = {
    'tracks': [[1,2,3,4]]
}

headers = {
    'Content-Type': 'application/json'
}

response = requests.post(url, json=data, headers=headers)

print(response.json())
