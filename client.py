import requests

url = 'http://127.0.0.1:5000/api/v1/track'
# url = 'https://6a68a7c98c72.ngrok.app/api/v1/track'

data = {
    "tracks": [[14.25037667,124.84238,10.4,20.4,22,0,0,1702700160,311000296]]
}

headers = {
    'Content-Type': 'application/json'
}

response = requests.post(url, json=data, headers=headers)

print(response)

with open("output.zip", 'wb') as f:
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:  # filter out keep-alive new chunks
            f.write(chunk)
