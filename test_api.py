import requests

url = "http://127.0.0.1:1234/v1/chat/completions"
headers = {"Content-Type": "application/json"}
data = {
    "model": "mistralai/mistral-7b-instruct-v0.3",
    "messages": [{"role": "user", "content": "Bonjour, qui es-tu ?"}],
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
